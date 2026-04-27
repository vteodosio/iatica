from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Licao, ProgressoLicao
from apps.groups.models import GrupoEstudo


def licao_detalhe(request, grupo_pk, licao_pk):
    aluno_id = request.session.get('aluno_id')
    if not aluno_id:
        return redirect('area_aluno')

    grupo = get_object_or_404(GrupoEstudo, pk=grupo_pk, status=GrupoEstudo.ATIVO)
    licao = get_object_or_404(Licao, pk=licao_pk, ativa=True)
    licoes = Licao.objects.filter(ativa=True).order_by('ordem')

    # Marca lição como lida
    ProgressoLicao.objects.get_or_create(
        aluno_id=aluno_id,
        licao=licao,
        grupo=grupo,
    )

    progresso_ids = list(
        ProgressoLicao.objects.filter(aluno_id=aluno_id, grupo=grupo).values_list('licao_id', flat=True)
    )

    # Próxima lição
    proxima = Licao.objects.filter(ativa=True, ordem__gt=licao.ordem).order_by('ordem').first()

    return render(request, 'content/licao_detalhe.html', {
        'grupo': grupo,
        'licao': licao,
        'licoes': licoes,
        'progresso': progresso_ids,
        'proxima': proxima,
        'aluno_nome': request.session.get('aluno_nome', 'Aluno'),
    })


def marcar_lida(request, grupo_pk, licao_pk):
    """AJAX endpoint para marcar lição como lida."""
    if request.method == 'POST':
        aluno_id = request.session.get('aluno_id')
        if not aluno_id:
            return JsonResponse({'ok': False})
        grupo = get_object_or_404(GrupoEstudo, pk=grupo_pk)
        licao = get_object_or_404(Licao, pk=licao_pk)
        ProgressoLicao.objects.get_or_create(aluno_id=aluno_id, licao=licao, grupo=grupo)
        total = Licao.objects.filter(ativa=True).count()
        lidas = ProgressoLicao.objects.filter(aluno_id=aluno_id, grupo=grupo).count()
        return JsonResponse({'ok': True, 'lidas': lidas, 'total': total})
    return JsonResponse({'ok': False})
