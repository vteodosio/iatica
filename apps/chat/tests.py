from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User
from apps.groups.models import GrupoEstudo, MembroGrupo

from .models import Interacao, PerguntaSugerida
from .services import (
    DeepSeekProvider,
    LLMError,
    RESPOSTAS_FALLBACK,
    filtrar_resposta,
    responder_pergunta,
)


@override_settings(LLM_PROVIDER='mock')
class ChatAccessTests(TestCase):
    """O chat exige que o aluno seja membro do grupo (mesma guarda das lições)."""

    def setUp(self):
        self.professor = User.objects.create_user(username='prof', password='x', role=User.PROFESSOR)
        self.grupo = GrupoEstudo.objects.create(nome='Turma', professor=self.professor)
        self.aluno = User.objects.create_user(username='aluno', password='x', role=User.ALUNO, apelido='Ana')
        self.url = reverse('chat', args=[self.grupo.pk])

    def _session(self, aluno):
        s = self.client.session
        s['aluno_id'] = aluno.pk
        s.save()

    def test_sem_sessao_redireciona(self):
        resp = self.client.get(self.url)
        self.assertRedirects(resp, reverse('area_aluno'))

    def test_nao_membro_redireciona(self):
        self._session(self.aluno)  # existe, mas não é membro do grupo
        resp = self.client.get(self.url)
        self.assertRedirects(resp, reverse('area_aluno'))

    def test_membro_acessa(self):
        MembroGrupo.objects.create(aluno=self.aluno, grupo=self.grupo)
        self._session(self.aluno)
        self.assertEqual(self.client.get(self.url).status_code, 200)


@override_settings(LLM_PROVIDER='mock')
class ChatPerguntaCuradaTests(TestCase):
    """Só perguntas curadas podem ser enviadas — não existe texto livre."""

    def setUp(self):
        self.professor = User.objects.create_user(username='prof', password='x', role=User.PROFESSOR)
        self.grupo = GrupoEstudo.objects.create(nome='Turma', professor=self.professor)
        self.aluno = User.objects.create_user(username='aluno', password='x', role=User.ALUNO, apelido='Ana')
        MembroGrupo.objects.create(aluno=self.aluno, grupo=self.grupo)

        self.pergunta = PerguntaSugerida.objects.create(
            ordem=1, texto='O que é inteligência artificial?')
        self.inativa = PerguntaSugerida.objects.create(
            ordem=2, texto='Pergunta desativada', ativa=False)

        self.url = reverse('chat', args=[self.grupo.pk])
        s = self.client.session
        s['aluno_id'] = self.aluno.pk
        s.save()

    def test_pergunta_valida_cria_interacao(self):
        resp = self.client.post(self.url, {'pergunta_id': self.pergunta.pk})
        self.assertRedirects(resp, self.url)
        self.assertEqual(Interacao.objects.count(), 1)

        interacao = Interacao.objects.first()
        self.assertEqual(interacao.pergunta, self.pergunta)
        self.assertTrue(interacao.resposta)
        self.assertFalse(interacao.bloqueada)

    def test_id_inexistente_nao_cria_interacao(self):
        resp = self.client.post(self.url, {'pergunta_id': 999999})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(Interacao.objects.count(), 0)

    def test_pergunta_inativa_e_recusada(self):
        resp = self.client.post(self.url, {'pergunta_id': self.inativa.pk})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(Interacao.objects.count(), 0)

    def test_texto_livre_enviado_e_ignorado(self):
        # Mesmo que alguém tente mandar texto livre, a view só olha para pergunta_id.
        resp = self.client.post(self.url, {
            'pergunta_id': self.pergunta.pk,
            'texto_livre': 'isto deve ser ignorado',
        })
        self.assertRedirects(resp, self.url)
        self.assertEqual(Interacao.objects.count(), 1)


@override_settings(LLM_PROVIDER='mock')
class ChatPainelTests(TestCase):
    """O professor enxerga as interações do próprio grupo (supervisão)."""

    def setUp(self):
        self.professor = User.objects.create_user(username='prof', password='x', role=User.PROFESSOR)
        self.outro = User.objects.create_user(username='prof2', password='x', role=User.PROFESSOR)
        self.grupo = GrupoEstudo.objects.create(nome='Turma', professor=self.professor)
        self.aluno = User.objects.create_user(username='aluno', password='x', role=User.ALUNO, apelido='Ana')
        MembroGrupo.objects.create(aluno=self.aluno, grupo=self.grupo)

        self.pergunta = PerguntaSugerida.objects.create(ordem=1, texto='Pergunta qualquer')
        Interacao.objects.create(
            aluno=self.aluno, grupo=self.grupo,
            pergunta=self.pergunta, resposta='Resposta gerada para o painel',
        )
        self.url = reverse('chat_painel', args=[self.grupo.pk])

    def test_login_obrigatorio(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

    def test_professor_ve_painel(self):
        self.client.force_login(self.professor)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Resposta gerada para o painel')

    def test_professor_de_outro_grupo_nao_ve(self):
        self.client.force_login(self.outro)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 404)


class GuardrailTests(TestCase):
    """Filtro da saída da IA (não precisa de banco)."""

    def test_bloqueia_termo_inadequado(self):
        texto, bloqueada, motivo = filtrar_resposta('Você é um idiota!')
        self.assertTrue(bloqueada)
        self.assertEqual(texto, '')
        self.assertIn('idiota', motivo)

    def test_filtro_ignora_acentos(self):
        _, bloqueada, _ = filtrar_resposta('que estúpido')
        self.assertTrue(bloqueada)

    def test_resposta_vazia_e_bloqueada(self):
        _, bloqueada, motivo = filtrar_resposta('   ')
        self.assertTrue(bloqueada)
        self.assertEqual(motivo, 'resposta vazia')

    def test_trunca_resposta_muito_longa(self):
        texto, bloqueada, _ = filtrar_resposta('palavra ' * 500, limite=100)
        self.assertFalse(bloqueada)
        self.assertLessEqual(len(texto), 101)

    def test_resposta_normal_passa_intacta(self):
        texto, bloqueada, _ = filtrar_resposta('A IA aprende com dados.')
        self.assertFalse(bloqueada)
        self.assertEqual(texto, 'A IA aprende com dados.')

    def test_nao_bloqueia_palavra_que_contem_termo(self):
        # "computadores" contém "puta" — o filtro não pode ser um simples substring.
        texto, bloqueada, _ = filtrar_resposta('Os computadores aprendem com dados.')
        self.assertFalse(bloqueada)
        self.assertIn('computadores', texto)


class ProviderTests(TestCase):
    """Comportamento dos provedores, sem tocar a rede."""

    @override_settings(LLM_PROVIDER='mock')
    def test_mock_responde_sem_rede(self):
        texto, bloqueada, _ = responder_pergunta('Quem escreveu Dom Casmurro?')
        self.assertFalse(bloqueada)
        self.assertIn('Machado de Assis', texto)

    @override_settings(LLM_PROVIDER='mock')
    def test_pergunta_fora_da_lista_usa_resposta_padrao(self):
        texto, bloqueada, _ = responder_pergunta('Uma pergunta que não está na lista')
        self.assertFalse(bloqueada)
        self.assertTrue(texto.strip())

    def test_deepseek_sem_chave_levanta_erro(self):
        with override_settings(LLM_PROVIDER='deepseek', LLM_API_KEY=''):
            with self.assertRaises(LLMError):
                DeepSeekProvider().responder('oi')

    @override_settings(LLM_PROVIDER='deepseek', LLM_API_KEY='')
    def test_falha_do_provedor_cai_no_fallback(self):
        # A demonstração nunca quebra: se o provedor falhar, vem a resposta de apoio.
        texto, bloqueada, _ = responder_pergunta('Quem escreveu Dom Casmurro?')
        self.assertFalse(bloqueada)
        self.assertIn('Machado de Assis', texto)


class FallbackCoberturaTests(TestCase):
    """Toda pergunta curada do seed precisa ter resposta de apoio."""

    def test_todas_as_perguntas_do_seed_tem_fallback(self):
        from apps.content.management.commands.seed_data import PERGUNTAS_CHAT

        self.assertGreater(len(PERGUNTAS_CHAT), 0)
        for item in PERGUNTAS_CHAT:
            self.assertIn(
                item['texto'], RESPOSTAS_FALLBACK,
                msg=f"Falta resposta de apoio para: {item['texto']}",
            )
