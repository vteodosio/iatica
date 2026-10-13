from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

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

    return render(request, 'chat/chat.html', {
        'grupo': grupo,
        'aluno_nome': request.session.get('aluno_nome', 'Aluno'),
        'perguntas': PerguntaSugerida.objects.filter(ativa=True).select_related('licao'),
        'interacoes': (
            Interacao.objects
            .filter(aluno_id=aluno_id, grupo=grupo)
            .select_related('pergunta')
        ),
    })


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
    })
