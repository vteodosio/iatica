import json
import random

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from apps.groups.access import get_aluno_membro, require_aluno_membro
from .models import Quiz, Pergunta, Alternativa, TentativaQuiz, RespostaAluno


def iniciar_quiz(request, grupo_pk):
    result = require_aluno_membro(request, grupo_pk)
    if not isinstance(result, tuple):
        return result
    aluno_id, grupo = result

    # Verifica se já concluiu
    tentativa_anterior = TentativaQuiz.objects.filter(
        aluno_id=aluno_id, grupo=grupo, finalizado_em__isnull=False
    ).first()
    if tentativa_anterior:
        return redirect('resultado_quiz', tentativa_pk=tentativa_anterior.pk)

    # Cria ou obtém quiz do grupo
    quiz, _ = Quiz.objects.get_or_create(grupo=grupo)
    if not quiz.perguntas.exists():
        perguntas = list(Pergunta.objects.all())
        random.shuffle(perguntas)
        quiz.perguntas.set(perguntas[:8])

    perguntas = list(quiz.perguntas.all().prefetch_related('alternativas'))
    random.shuffle(perguntas)

    # Cria tentativa
    tentativa = TentativaQuiz.objects.create(
        aluno_id=aluno_id,
        grupo=grupo,
        total_perguntas=len(perguntas)
    )
    request.session['tentativa_id'] = tentativa.pk

    perguntas_data = []
    for p in perguntas:
        alts = list(p.alternativas.all())
        random.shuffle(alts)
        perguntas_data.append({
            'id': p.pk,
            'texto': p.texto,
            'alternativas': [{'id': a.pk, 'texto': a.texto} for a in alts]
        })

    return render(request, 'quiz/quiz.html', {
        'grupo': grupo,
        'perguntas_json': json.dumps(perguntas_data, ensure_ascii=False),
        'tentativa': tentativa,
        'aluno_nome': request.session.get('aluno_nome', 'Aluno'),
    })


def submeter_quiz(request, grupo_pk):
    if request.method != 'POST':
        return redirect('area_aluno')

    result = get_aluno_membro(request, grupo_pk)
    if result is None:
        return redirect('area_aluno')
    aluno_id, _grupo = result

    tentativa_id = request.session.get('tentativa_id')
    if not tentativa_id:
        return redirect('area_aluno')

    tentativa = get_object_or_404(TentativaQuiz, pk=tentativa_id, aluno_id=aluno_id)

    if tentativa.finalizado_em:
        return redirect('resultado_quiz', tentativa_pk=tentativa.pk)

    respostas = json.loads(request.POST.get('respostas', '{}'))
    pontuacao = 0

    for pergunta_id_str, alternativa_id_str in respostas.items():
        try:
            pergunta = Pergunta.objects.get(pk=int(pergunta_id_str))
            alternativa = Alternativa.objects.get(pk=int(alternativa_id_str))
            correta = alternativa.correta
            if correta:
                pontuacao += 1
            RespostaAluno.objects.create(
                tentativa=tentativa,
                pergunta=pergunta,
                alternativa_escolhida=alternativa,
                correta=correta,
            )
        except (Pergunta.DoesNotExist, Alternativa.DoesNotExist, ValueError):
            continue

    tentativa.pontuacao = pontuacao
    tentativa.finalizado_em = timezone.now()
    tentativa.save()

    return redirect('resultado_quiz', tentativa_pk=tentativa.pk)


def resultado_quiz(request, tentativa_pk):
    aluno_id = request.session.get('aluno_id')
    if not aluno_id:
        messages.warning(request, 'Acesse a área do aluno e informe o código do grupo.')
        return redirect('area_aluno')

    tentativa = get_object_or_404(TentativaQuiz, pk=tentativa_pk)

    # Apenas o dono da tentativa pode visualizar o resultado.
    if tentativa.aluno_id != aluno_id:
        messages.error(request, 'Você não tem permissão para ver este resultado.')
        return redirect('area_aluno')

    respostas = tentativa.respostas.select_related('pergunta__licao', 'alternativa_escolhida').all()
    alternativas_corretas = {}
    for r in respostas:
        alt_correta = r.pergunta.alternativas.filter(correta=True).first()
        alternativas_corretas[r.pergunta.pk] = alt_correta

    return render(request, 'quiz/resultado.html', {
        'tentativa': tentativa,
        'respostas': respostas,
        'alternativas_corretas': alternativas_corretas,
        'aluno_nome': request.session.get('aluno_nome', 'Aluno'),
    })
