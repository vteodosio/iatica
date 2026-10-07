from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.content.models import Licao
from apps.groups.models import GrupoEstudo, MembroGrupo
from apps.quiz.models import TentativaQuiz, Pergunta, Alternativa, RespostaAluno


class ResultadoQuizOwnershipTests(TestCase):
    """Só o dono da tentativa pode ver o resultado do quiz."""

    def setUp(self):
        self.professor = User.objects.create_user(username='prof', password='x', role=User.PROFESSOR)
        self.grupo = GrupoEstudo.objects.create(nome='Turma', professor=self.professor)
        self.aluno_a = User.objects.create_user(username='aluno_a', password='x', role=User.ALUNO, apelido='Ana')
        self.aluno_b = User.objects.create_user(username='aluno_b', password='x', role=User.ALUNO, apelido='Bia')
        MembroGrupo.objects.create(aluno=self.aluno_a, grupo=self.grupo)
        MembroGrupo.objects.create(aluno=self.aluno_b, grupo=self.grupo)
        self.tentativa = TentativaQuiz.objects.create(
            aluno=self.aluno_a, grupo=self.grupo, pontuacao=1, total_perguntas=1,
            finalizado_em=timezone.now(),
        )
        self.url = reverse('resultado_quiz', args=[self.tentativa.pk])

    def _session(self, aluno):
        s = self.client.session
        s['aluno_id'] = aluno.pk
        s.save()

    def test_dono_ve_resultado(self):
        self._session(self.aluno_a)
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_nao_dono_nao_ve_resultado(self):
        self._session(self.aluno_b)
        resp = self.client.get(self.url)
        self.assertRedirects(resp, reverse('area_aluno'))

    def test_sem_sessao_redireciona(self):
        resp = self.client.get(self.url)
        self.assertRedirects(resp, reverse('area_aluno'))


class IniciarQuizMembershipTests(TestCase):
    """Aluno de fora do grupo não consegue iniciar quiz no grupo."""

    def setUp(self):
        self.professor = User.objects.create_user(username='prof', password='x', role=User.PROFESSOR)
        self.grupo = GrupoEstudo.objects.create(nome='Turma', professor=self.professor)
        self.aluno = User.objects.create_user(username='aluno', password='x', role=User.ALUNO, apelido='Ana')
        self.url = reverse('iniciar_quiz', args=[self.grupo.pk])

    def test_nao_membro_nao_inicia_quiz(self):
        s = self.client.session
        s['aluno_id'] = self.aluno.pk  # aluno existe, mas NÃO é membro do grupo
        s.save()
        resp = self.client.get(self.url)
        self.assertRedirects(resp, reverse('area_aluno'))
        self.assertEqual(TentativaQuiz.objects.count(), 0)


class ResultadoQuizFeedbackTests(TestCase):
    """O resultado mostra a explicação e o link de revisão da lição."""

    def setUp(self):
        self.professor = User.objects.create_user(username='prof', password='x', role=User.PROFESSOR)
        self.grupo = GrupoEstudo.objects.create(nome='Turma', professor=self.professor)
        self.aluno = User.objects.create_user(username='aluno', password='x', role=User.ALUNO, apelido='Ana')
        MembroGrupo.objects.create(aluno=self.aluno, grupo=self.grupo)
        self.licao = Licao.objects.create(titulo='Lições de IA', conteudo_html='<p>x</p>', ordem=1, ativa=True)
        self.pergunta = Pergunta.objects.create(
            texto='O que é IA?', ordem=1,
            explicacao='A IA aprende com dados, como nós na escola.',
            licao=self.licao,
        )
        self.alt = Alternativa.objects.create(pergunta=self.pergunta, texto='Certa', correta=True)
        self.tentativa = TentativaQuiz.objects.create(
            aluno=self.aluno, grupo=self.grupo, pontuacao=1, total_perguntas=1,
            finalizado_em=timezone.now(),
        )
        RespostaAluno.objects.create(
            tentativa=self.tentativa, pergunta=self.pergunta,
            alternativa_escolhida=self.alt, correta=True,
        )
        self.url = reverse('resultado_quiz', args=[self.tentativa.pk])

    def test_resultado_mostra_explicacao_e_link_da_licao(self):
        s = self.client.session
        s['aluno_id'] = self.aluno.pk
        s.save()
        html = self.client.get(self.url).content.decode('utf-8', 'replace')
        self.assertIn('A IA aprende com dados', html)
        self.assertIn('Lições de IA', html)
        self.assertIn('Revisar lição', html)
        self.assertIn(reverse('licao_detalhe', args=[self.grupo.pk, self.licao.pk]), html)
