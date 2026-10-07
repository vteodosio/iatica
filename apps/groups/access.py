"""Controle de acesso para a área do aluno.

Garante que o aluno da sessão é, de fato, membro do grupo que está tentando
acessar, antes de liberar lições, quiz e resultados. Fecha o acesso cruzado em
que um aluno de um grupo podia navegar para outro grupo pela URL.
"""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from .models import GrupoEstudo, MembroGrupo


def get_aluno_membro(request, grupo_pk):
    """Retorna ``(aluno_id, grupo)`` se o aluno da sessão é membro do grupo ativo.

    Retorna ``None`` quando a sessão não tem aluno ou o aluno não pertence ao
    grupo. Levanta ``Http404`` se o grupo não existir ou não estiver ativo.
    """
    aluno_id = request.session.get('aluno_id')
    if not aluno_id:
        return None
    grupo = get_object_or_404(GrupoEstudo, pk=grupo_pk, status=GrupoEstudo.ATIVO)
    if not MembroGrupo.objects.filter(aluno_id=aluno_id, grupo=grupo).exists():
        return None
    return (aluno_id, grupo)


def require_aluno_membro(request, grupo_pk):
    """Igual a :func:`get_aluno_membro`, mas redireciona à área do aluno se negado.

    No sucesso retorna a tupla ``(aluno_id, grupo)``; na negação retorna uma
    resposta de redirecionamento (não é tupla), pronta para ser devolvida.
    """
    result = get_aluno_membro(request, grupo_pk)
    if result is None:
        messages.error(request, 'Acesso restrito aos alunos deste grupo.')
        return redirect('area_aluno')
    return result
