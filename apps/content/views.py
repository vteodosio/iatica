from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from apps.groups.access import get_aluno_membro, require_aluno_membro
from .models import Licao, ProgressoLicao


def licao_detalhe(request, grupo_pk, licao_pk):
    result = require_aluno_membro(request, grupo_pk)
    if not isinstance(result, tuple):
        return result
    aluno_id, grupo = result

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
        'chat_ativo': settings.CHAT_ATIVO,
    })


def marcar_lida(request, grupo_pk, licao_pk):
    """AJAX endpoint para marcar lição como lida."""
    if request.method != 'POST':
        return JsonResponse({'ok': False})

    result = get_aluno_membro(request, grupo_pk)
    if result is None:
        return JsonResponse({'ok': False})
    aluno_id, grupo = result

    licao = get_object_or_404(Licao, pk=licao_pk)
    ProgressoLicao.objects.get_or_create(aluno_id=aluno_id, licao=licao, grupo=grupo)
    total = Licao.objects.filter(ativa=True).count()
    lidas = ProgressoLicao.objects.filter(aluno_id=aluno_id, grupo=grupo).count()
    return JsonResponse({'ok': True, 'lidas': lidas, 'total': total})
