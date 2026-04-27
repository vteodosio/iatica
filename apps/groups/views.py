from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import GrupoEstudo, MembroGrupo
from apps.accounts.models import User


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


# ─── ÁREA DO ALUNO ────────────────────────────────────────────────────────────

def area_aluno(request):
    """Página inicial do aluno — sem login obrigatório para entrada simples via código."""
    return render(request, 'groups/area_aluno.html')


def entrar_grupo(request):
    """Aluno entra no grupo usando o código fornecido pelo professor."""
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        nome_aluno = request.POST.get('nome_aluno', '').strip()

        try:
            grupo = GrupoEstudo.objects.get(codigo=codigo, status=GrupoEstudo.ATIVO)
        except GrupoEstudo.DoesNotExist:
            messages.error(request, 'Código inválido ou grupo já finalizado. Verifique com seu professor.')
            return redirect('area_aluno')

        # Cria ou recupera usuário aluno temporário baseado no nome
        username = f"aluno_{codigo}_{nome_aluno.lower().replace(' ', '_')}"
        user, criado = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': nome_aluno.split()[0] if nome_aluno else 'Aluno',
                'last_name': ' '.join(nome_aluno.split()[1:]) if len(nome_aluno.split()) > 1 else '',
                'role': User.ALUNO,
            }
        )

        MembroGrupo.objects.get_or_create(aluno=user, grupo=grupo)

        # Salva dados do aluno na sessão
        request.session['aluno_id'] = user.id
        request.session['aluno_nome'] = nome_aluno or user.username
        request.session['grupo_id'] = grupo.id
        request.session['grupo_nome'] = grupo.nome

        return redirect('sala_estudo', pk=grupo.pk)

    return redirect('area_aluno')


def sala_estudo(request, pk):
    """Sala de estudo do aluno — exibe lições e quiz."""
    aluno_id = request.session.get('aluno_id')
    if not aluno_id:
        messages.warning(request, 'Acesse a área do aluno e insira o código do grupo.')
        return redirect('area_aluno')

    grupo = get_object_or_404(GrupoEstudo, pk=pk, status=GrupoEstudo.ATIVO)
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
