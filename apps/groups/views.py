from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .access import require_aluno_membro
from .models import GrupoEstudo, MembroGrupo
from apps.accounts.models import User, gerar_username_aluno


@login_required
def dashboard_professor(request):
    if not request.user.is_professor():
        return redirect('area_aluno')
    grupos = GrupoEstudo.objects.filter(professor=request.user)
    return render(request, 'accounts/dashboard_professor.html', {'grupos': grupos})


@login_required
def criar_grupo(request):
    if not request.user.is_professor():
        return redirect('area_aluno')

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        if nome:
            grupo = GrupoEstudo.objects.create(
                nome=nome,
                descricao=descricao,
                professor=request.user
            )
            messages.success(request, f'Grupo "{grupo.nome}" criado! Código: {grupo.codigo}')
            return redirect('detalhe_grupo', pk=grupo.pk)
        else:
            messages.error(request, 'O nome do grupo é obrigatório.')

    return render(request, 'groups/criar_grupo.html')


@login_required
def detalhe_grupo(request, pk):
    grupo = get_object_or_404(GrupoEstudo, pk=pk, professor=request.user)
    membros = MembroGrupo.objects.filter(grupo=grupo).select_related('aluno')
    from apps.quiz.models import TentativaQuiz
    tentativas = TentativaQuiz.objects.filter(grupo=grupo, finalizado_em__isnull=False).select_related('aluno')
    return render(request, 'groups/detalhe_grupo.html', {
        'grupo': grupo,
        'membros': membros,
        'tentativas': tentativas,
    })


@login_required
def finalizar_grupo(request, pk):
    grupo = get_object_or_404(GrupoEstudo, pk=pk, professor=request.user)
    if request.method == 'POST':
        grupo.status = GrupoEstudo.FINALIZADO
        grupo.finalizado_em = timezone.now()
        grupo.save()
        messages.success(request, f'Grupo "{grupo.nome}" finalizado com sucesso!')
    return redirect('detalhe_grupo', pk=pk)


@login_required
def remover_aluno(request, grupo_pk, aluno_pk):
    """Remove um aluno do grupo e apaga seus dados se ficar órfão (LGPD)."""
    grupo = get_object_or_404(GrupoEstudo, pk=grupo_pk, professor=request.user)
    membro = get_object_or_404(MembroGrupo, grupo=grupo, aluno_id=aluno_pk)
    aluno = membro.aluno

    if request.method == 'POST':
        nome = aluno.nome_exibicao()
        membro.delete()
        # Se o aluno não pertence a nenhum outro grupo, apaga seus dados.
        if not MembroGrupo.objects.filter(aluno=aluno).exists():
            aluno.delete()
        messages.success(request, f'"{nome}" foi removido(a) do grupo.')
        return redirect('detalhe_grupo', pk=grupo.pk)

    return redirect('detalhe_grupo', pk=grupo.pk)


# ─── ÁREA DO ALUNO ────────────────────────────────────────────────────────────

def area_aluno(request):
    """Página inicial do aluno — sem login obrigatório para entrada simples via código."""
    return render(request, 'groups/area_aluno.html')


def entrar_grupo(request):
    """Aluno entra no grupo usando o código fornecido pelo professor."""
    if request.method != 'POST':
        return redirect('area_aluno')

    codigo = request.POST.get('codigo', '').strip().upper()
    apelido = request.POST.get('nome_aluno', '').strip()

    try:
        grupo = GrupoEstudo.objects.get(codigo=codigo, status=GrupoEstudo.ATIVO)
    except GrupoEstudo.DoesNotExist:
        messages.error(request, 'Código inválido ou grupo já finalizado. Verifique com seu professor.')
        return redirect('area_aluno')

    if not apelido:
        messages.error(request, 'Informe seu nome ou apelido.')
        return redirect('area_aluno')

    if request.POST.get('consentimento') != 'on':
        messages.error(request, 'É necessário aceitar o aviso de privacidade para entrar.')
        return redirect('area_aluno')

    # Reaproveita o aluno quando o apelido já existe no grupo (retorno do mesmo aluno).
    membro = (
        MembroGrupo.objects
        .filter(grupo=grupo, aluno__role=User.ALUNO, aluno__apelido=apelido)
        .select_related('aluno')
        .first()
    )
    if membro:
        user = membro.aluno
    else:
        # Username aleatório, não derivado do nome real (privacidade).
        user = User.objects.create_user(
            username=gerar_username_aluno(),
            apelido=apelido,
            role=User.ALUNO,
            consentiu_em=timezone.now(),
        )
        MembroGrupo.objects.create(aluno=user, grupo=grupo)

    request.session['aluno_id'] = user.id
    request.session['aluno_nome'] = user.nome_exibicao()
    request.session['grupo_id'] = grupo.id
    request.session['grupo_nome'] = grupo.nome

    return redirect('sala_estudo', pk=grupo.pk)


def sala_estudo(request, pk):
    """Sala de estudo do aluno — exibe lições e quiz."""
    result = require_aluno_membro(request, pk)
    if not isinstance(result, tuple):
        return result
    aluno_id, grupo = result

    from apps.content.models import Licao, ProgressoLicao
    from apps.quiz.models import TentativaQuiz, Quiz

    licoes = Licao.objects.filter(ativa=True).order_by('ordem')
    progresso = ProgressoLicao.objects.filter(aluno_id=aluno_id, grupo=grupo).values_list('licao_id', flat=True)
    quiz = Quiz.objects.filter(grupo=grupo).first()
    tentativa_concluida = TentativaQuiz.objects.filter(
        aluno_id=aluno_id, grupo=grupo, finalizado_em__isnull=False
    ).first()

    return render(request, 'groups/sala_estudo.html', {
        'grupo': grupo,
        'licoes': licoes,
        'progresso': list(progresso),
        'quiz': quiz,
        'tentativa_concluida': tentativa_concluida,
        'aluno_nome': request.session.get('aluno_nome', 'Aluno'),
    })
