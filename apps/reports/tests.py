from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.chat.models import Interacao, PerguntaSugerida
from apps.groups.models import GrupoEstudo, MembroGrupo
from apps.quiz.models import Pergunta, Alternativa, TentativaQuiz, RespostaAluno


class RelatorioPerQuestaoTests(TestCase):
    """O relatório do grupo mostra a estatística de acerto por questão."""

    def setUp(self):
        self.professor = User.objects.create_user(username='prof', password='x', role=User.PROFESSOR)
        self.grupo = GrupoEstudo.objects.create(nome='Turma', professor=self.professor)
        self.aluno_a = User.objects.create_user(username='aluno_a', password='x', role=User.ALUNO, apelido='Ana')
        self.aluno_b = User.objects.create_user(username='aluno_b', password='x', role=User.ALUNO, apelido='Bia')
        MembroGrupo.objects.create(aluno=self.aluno_a, grupo=self.grupo)
        MembroGrupo.objects.create(aluno=self.aluno_b, grupo=self.grupo)

        self.pergunta = Pergunta.objects.create(texto='O que é IA?', ordem=1)
        self.alt_correta = Alternativa.objects.create(pergunta=self.pergunta, texto='Certa', correta=True)
        self.alt_errada = Alternativa.objects.create(pergunta=self.pergunta, texto='Errada', correta=False)

        # aluno A acertou, aluno B errou
        t_a = TentativaQuiz.objects.create(
            aluno=self.aluno_a, grupo=self.grupo, pontuacao=1, total_perguntas=1,
            finalizado_em=timezone.now(),
        )
        RespostaAluno.objects.create(
            tentativa=t_a, pergunta=self.pergunta, alternativa_escolhida=self.alt_correta, correta=True,
        )
        t_b = TentativaQuiz.objects.create(
            aluno=self.aluno_b, grupo=self.grupo, pontuacao=0, total_perguntas=1,
            finalizado_em=timezone.now(),
        )
        RespostaAluno.objects.create(
            tentativa=t_b, pergunta=self.pergunta, alternativa_escolhida=self.alt_errada, correta=False,
        )

    def test_relatorio_agrega_acertos_por_questao(self):
        self.client.force_login(self.professor)
        resp = self.client.get(reverse('relatorio_grupo', args=[self.grupo.pk]))
        self.assertEqual(resp.status_code, 200)
        dados = resp.context['dados_perguntas']
        self.assertEqual(len(dados), 1)
        self.assertEqual(dados[0]['total'], 2)
        self.assertEqual(dados[0]['corretas'], 1)
        self.assertEqual(dados[0]['percentual'], 50)

    def test_relatorio_sem_quiz_nao_quebra(self):
        grupo_vazio = GrupoEstudo.objects.create(nome='Turma Vazia', professor=self.professor)
        self.client.force_login(self.professor)
        resp = self.client.get(reverse('relatorio_grupo', args=[grupo_vazio.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['dados_perguntas'], [])


class RelatorioChatTests(TestCase):
    """O relatório mostra o uso do chat pela turma (F3 item 3)."""

    def setUp(self):
        self.professor = User.objects.create_user(username='prof', password='x', role=User.PROFESSOR)
        self.grupo = GrupoEstudo.objects.create(nome='Turma', professor=self.professor)
        self.aluno = User.objects.create_user(username='aluno', password='x', role=User.ALUNO, apelido='Ana')
        MembroGrupo.objects.create(aluno=self.aluno, grupo=self.grupo)

        pergunta = PerguntaSugerida.objects.create(ordem=1, texto='Pergunta', conceito='Alucinação')
        Interacao.objects.create(
            aluno=self.aluno, grupo=self.grupo, pergunta=pergunta,
            resposta='R1', feedback=Interacao.FEEDBACK_ERROU,
        )
        Interacao.objects.create(
            aluno=self.aluno, grupo=self.grupo, pergunta=pergunta, resposta='R2',
        )

    def test_relatorio_agrega_uso_do_chat(self):
        self.client.force_login(self.professor)
        resp = self.client.get(reverse('relatorio_grupo', args=[self.grupo.pk]))
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.context['chat_total'], 2)
        self.assertEqual(resp.context['chat_errou'], 1)
        self.assertEqual(resp.context['chat_bloqueadas'], 0)
        self.assertEqual(dict(resp.context['chat_conceitos']), {'Alucinação': 2})

        # e também por aluno, na tabela
        dado = resp.context['dados_alunos'][0]
        self.assertEqual(dado['chat_total'], 2)
        self.assertEqual(dado['chat_errou'], 1)

    def test_pdf_inclui_secao_do_chat(self):
        self.client.force_login(self.professor)
        resp = self.client.get(reverse('relatorio_pdf', args=[self.grupo.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
