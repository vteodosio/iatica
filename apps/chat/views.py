from itertools import groupby

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.content.models import Licao
from apps.groups.access import require_aluno_membro
from apps.groups.models import GrupoEstudo

from .models import Interacao, PerguntaSugerida
from .services import responder_pergunta


def chat(request, grupo_pk):
    """Chat guiado do aluno — somente perguntas curadas, sem texto livre."""
    result = require_aluno_membro(request, grupo_pk)
    if not isinstance(result, tuple):
        return result
    aluno_id, grupo = result

    if request.method == 'POST':
        # Barreira principal: o ID precisa ser de uma pergunta ativa da lista
        # curada. Qualquer outra coisa resulta em 404 e nada é enviado à IA.
        pergunta = get_object_or_404(
            PerguntaSugerida.objects.select_related('licao'),
            pk=request.POST.get('pergunta_id'),
            ativa=True,
        )
        resposta, bloqueada, _motivo = responder_pergunta(pergunta.texto)
        Interacao.objects.create(
            aluno_id=aluno_id,
            grupo=grupo,
            pergunta=pergunta,
            resposta=resposta,
            bloqueada=bloqueada,
        )
        return redirect('chat', grupo_pk=grupo.pk)

    # Filtro opcional por lição (vem do botão "perguntar sobre esta lição").
    licao_atual = None
    licao_filtro = request.GET.get('licao', '')
    perguntas_qs = PerguntaSugerida.objects.filter(ativa=True).select_related('licao')
    if licao_filtro.isdigit():
        licao_atual = Licao.objects.filter(pk=licao_filtro).first()
        if licao_atual:
            perguntas_qs = perguntas_qs.filter(licao=licao_atual)

    # Agrupa por lição. A ordenação por licao_id garante que as perguntas da
    # mesma lição fiquem consecutivas (requisito do itertools.groupby).
    ordenadas = perguntas_qs.order_by('licao__ordem', 'licao_id', 'ordem', 'id')
    grupos_perguntas = [
        {'licao': licao, 'perguntas': list(itens)}
        for licao, itens in groupby(ordenadas, key=lambda p: p.licao)
    ]

    return render(request, 'chat/chat.html', {
        'grupo': grupo,
        'aluno_nome': request.session.get('aluno_nome', 'Aluno'),
        'grupos_perguntas': grupos_perguntas,
        'licao_atual': licao_atual,
        'interacoes': (
            Interacao.objects
            .filter(aluno_id=aluno_id, grupo=grupo)
            .select_related('pergunta')
        ),
    })


def registrar_feedback(request, grupo_pk, interacao_pk):
    """O aluno avalia a resposta da IA: ajudou / acho que a IA errou."""
    result = require_aluno_membro(request, grupo_pk)
    if not isinstance(result, tuple):
        return result
    aluno_id, grupo = result

    if request.method == 'POST':
        # Somente o dono da interação pode avaliá-la.
        interacao = get_object_or_404(
            Interacao, pk=interacao_pk, aluno_id=aluno_id, grupo=grupo)
        valor = request.POST.get('feedback', '')
        if valor in dict(Interacao.FEEDBACK_CHOICES):
            Interacao.objects.filter(pk=interacao.pk).update(feedback=valor)

    return redirect('chat', grupo_pk=grupo.pk)


@login_required
def painel(request, pk):
    """Visão do professor: o que a turma perguntou e o que a IA respondeu."""
    grupo = get_object_or_404(GrupoEstudo, pk=pk, professor=request.user)
    interacoes = (
        Interacao.objects
        .filter(grupo=grupo)
        .select_related('aluno', 'pergunta')
        .order_by('-criado_em')
    )
    return render(request, 'chat/painel.html', {
        'grupo': grupo,
        'interacoes': interacoes,
        'total': interacoes.count(),
        'total_bloqueadas': interacoes.filter(bloqueada=True).count(),
        'total_errou': interacoes.filter(feedback=Interacao.FEEDBACK_ERROU).count(),
    })
