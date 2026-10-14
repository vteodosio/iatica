from collections import defaultdict

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from apps.groups.models import GrupoEstudo, MembroGrupo
from apps.quiz.models import TentativaQuiz, RespostaAluno, Pergunta
from apps.content.models import ProgressoLicao, Licao


@login_required
def relatorio_grupo(request, pk):
    grupo = get_object_or_404(GrupoEstudo, pk=pk, professor=request.user)
    membros = MembroGrupo.objects.filter(grupo=grupo).select_related('aluno')
    tentativas = TentativaQuiz.objects.filter(
        grupo=grupo, finalizado_em__isnull=False
    ).select_related('aluno').order_by('-pontuacao')

    total_licoes = Licao.objects.filter(ativa=True).count()

    dados_alunos = []
    for membro in membros:
        tentativa = tentativas.filter(aluno=membro.aluno).first()
        licoes_lidas = ProgressoLicao.objects.filter(aluno=membro.aluno, grupo=grupo).count()
        dados_alunos.append({
            'aluno': membro.aluno,
            'entrou_em': membro.entrou_em,
            'licoes_lidas': licoes_lidas,
            'total_licoes': total_licoes,
            'tentativa': tentativa,
        })

    # Estatística por questão — mostra o que a turma mais errou.
    respostas = RespostaAluno.objects.filter(
        tentativa__grupo=grupo,
        tentativa__finalizado_em__isnull=False,
    ).select_related('pergunta__licao')

    por_questao = defaultdict(lambda: {'total': 0, 'corretas': 0})
    for resposta in respostas:
        por_questao[resposta.pergunta_id]['total'] += 1
        if resposta.correta:
            por_questao[resposta.pergunta_id]['corretas'] += 1

    dados_perguntas = []
    for pergunta in Pergunta.objects.filter(id__in=por_questao.keys()).select_related('licao'):
        est = por_questao[pergunta.id]
        total = est['total']
        corretas = est['corretas']
        dados_perguntas.append({
            'pergunta': pergunta,
            'total': total,
            'corretas': corretas,
            'percentual': round(corretas / total * 100) if total else 0,
            'licao': pergunta.licao,
        })
    # Ordena do mais errado para o menos errado (mais útil ao professor).
    dados_perguntas.sort(key=lambda d: d['percentual'])

    # Chat IA — uso por aluno e conceitos mais perguntados.
    from apps.chat.models import Interacao

    interacoes_chat = list(Interacao.objects.filter(grupo=grupo).select_related('pergunta'))
    chat_por_aluno = defaultdict(lambda: {'total': 0, 'errou': 0, 'bloqueadas': 0})
    conceitos_chat = defaultdict(int)
    for interacao in interacoes_chat:
        info = chat_por_aluno[interacao.aluno_id]
        info['total'] += 1
        if interacao.feedback == Interacao.FEEDBACK_ERROU:
            info['errou'] += 1
        if interacao.bloqueada:
            info['bloqueadas'] += 1
        if interacao.pergunta.conceito:
            conceitos_chat[interacao.pergunta.conceito] += 1

    for dado in dados_alunos:
        info = chat_por_aluno.get(dado['aluno'].id, {'total': 0, 'errou': 0, 'bloqueadas': 0})
        dado['chat_total'] = info['total']
        dado['chat_errou'] = info['errou']
        dado['chat_bloqueadas'] = info['bloqueadas']

    context = {
        'grupo': grupo,
        'dados_alunos': dados_alunos,
        'dados_perguntas': dados_perguntas,
        'total_membros': membros.count(),
        'total_concluiram': tentativas.values('aluno').distinct().count(),
        'media_pontuacao': grupo.media_pontuacao(),
        'chat_total': len(interacoes_chat),
        'chat_errou': sum(1 for i in interacoes_chat if i.feedback == Interacao.FEEDBACK_ERROU),
        'chat_bloqueadas': sum(1 for i in interacoes_chat if i.bloqueada),
        'chat_conceitos': sorted(conceitos_chat.items(), key=lambda kv: (-kv[1], kv[0])),
    }
    return render(request, 'reports/relatorio_grupo.html', context)


@login_required
def relatorio_pdf(request, pk):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import cm
    import io
    from django.utils import timezone

    grupo = get_object_or_404(GrupoEstudo, pk=pk, professor=request.user)
    membros = MembroGrupo.objects.filter(grupo=grupo).select_related('aluno')
    tentativas = TentativaQuiz.objects.filter(
        grupo=grupo, finalizado_em__isnull=False
    ).select_related('aluno')

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('title', parent=styles['Title'],
                                  fontSize=20, textColor=colors.HexColor('#f59e0b'))
    story.append(Paragraph(f"Relatório: {grupo.nome}", title_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(f"Professor: {request.user.get_full_name() or request.user.username}", styles['Normal']))
    story.append(Paragraph(f"Escola: {request.user.escola or '—'}", styles['Normal']))
    story.append(Paragraph(f"Gerado em: {timezone.localtime().now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))

    concluiram = tentativas.values('aluno').distinct().count()
    story.append(Paragraph("Resumo do Grupo", styles['Heading2']))
    resumo = [
        ['Total de Alunos', str(membros.count())],
        ['Concluíram o Quiz', str(concluiram)],
        ['Média de Pontuação', f"{grupo.media_pontuacao():.1f}%"],
        ['Status', grupo.get_status_display()],
    ]
    t = Table(resumo, colWidths=[8*cm, 8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef3c7')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#fffbeb')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Desempenho dos Alunos", styles['Heading2']))
    header = ['Aluno', 'Lições Lidas', 'Pontuação', 'Percentual']
    rows = [header]
    total_licoes = Licao.objects.filter(ativa=True).count()
    for membro in membros:
        tentativa = tentativas.filter(aluno=membro.aluno).first()
        licoes_lidas = ProgressoLicao.objects.filter(aluno=membro.aluno, grupo=grupo).count()
        nome = membro.aluno.nome_exibicao()
        pontuacao = f"{tentativa.pontuacao}/{tentativa.total_perguntas}" if tentativa else "—"
        percentual = f"{tentativa.percentual()}%" if tentativa else "—"
        rows.append([nome, f"{licoes_lidas}/{total_licoes}", pontuacao, percentual])

    tbl = Table(rows, colWidths=[6*cm, 4*cm, 4*cm, 4*cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fffbeb')]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(tbl)

    # Chat IA — resumo do uso da turma
    from apps.chat.models import Interacao
    interacoes_chat = list(Interacao.objects.filter(grupo=grupo).select_related('pergunta'))
    if interacoes_chat:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Chat com a IA", styles['Heading2']))
        erros_chat = sum(1 for i in interacoes_chat if i.feedback == Interacao.FEEDBACK_ERROU)
        bloqueadas_chat = sum(1 for i in interacoes_chat if i.bloqueada)
        resumo_chat = [
            ['Perguntas feitas', str(len(interacoes_chat))],
            ['Avaliadas como erro pela turma', str(erros_chat)],
            ['Respostas bloqueadas pelo filtro', str(bloqueadas_chat)],
        ]
        tabela_chat = Table(resumo_chat, colWidths=[8*cm, 8*cm])
        tabela_chat.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#eef2ff')]),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(tabela_chat)

    doc.build(story)
    buf.seek(0)
    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{grupo.codigo}.pdf"'
    return response
