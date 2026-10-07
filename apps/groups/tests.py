from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.groups.models import GrupoEstudo, MembroGrupo


class EntrarGrupoPrivacyTests(TestCase):
    """Entrada do aluno: apelido em vez de nome real, consentimento e username aleatório."""

    def setUp(self):
        self.professor = User.objects.create_user(
            username='prof', password='x', role=User.PROFESSOR, first_name='Prof')
        self.grupo = GrupoEstudo.objects.create(nome='Turma A', professor=self.professor)
        self.url = reverse('entrar_grupo')

    def _post(self, nome='Maria', codigo=None, consentimento='on'):
        data = {
            'nome_aluno': nome,
            'codigo': codigo or self.grupo.codigo,
        }
        if consentimento is not None:
            data['consentimento'] = consentimento
        return self.client.post(self.url, data)

    def test_cria_aluno_com_apelido_e_sem_nome_real_no_username(self):
        resp = self._post(nome='Maria Silva')
        self.assertRedirects(resp, reverse('sala_estudo', args=[self.grupo.pk]))

        aluno = User.objects.get(role=User.ALUNO)
        self.assertEqual(aluno.apelido, 'Maria Silva')
        self.assertEqual(aluno.first_name, '')
        self.assertEqual(aluno.last_name, '')
        self.assertNotIn('maria', aluno.username.lower())
        self.assertTrue(aluno.username.startswith('aluno_'))
        self.assertIsNotNone(aluno.consentiu_em)
        self.assertTrue(MembroGrupo.objects.filter(aluno=aluno, grupo=self.grupo).exists())

    def test_retorno_reutiliza_mesmo_aluno(self):
        self._post(nome='Maria')
        self._post(nome='Maria')
        self.assertEqual(User.objects.filter(role=User.ALUNO).count(), 1)

    def test_sem_consentimento_nao_cria_aluno(self):
        resp = self._post(nome='Joao', consentimento=None)
        self.assertRedirects(resp, reverse('area_aluno'))
        self.assertEqual(User.objects.filter(role=User.ALUNO).count(), 0)
        self.assertEqual(MembroGrupo.objects.count(), 0)

    def test_codigo_invalido_nao_cria_aluno(self):
        resp = self._post(nome='Ana', codigo='XXXXXX')
        self.assertRedirects(resp, reverse('area_aluno'))
        self.assertEqual(User.objects.filter(role=User.ALUNO).count(), 0)


class RemoverAlunoTests(TestCase):
    """Remoção de aluno: apaga a participação e o usuário órfão (LGPD)."""

    def setUp(self):
        self.professor = User.objects.create_user(username='prof', password='x', role=User.PROFESSOR)
        self.grupo = GrupoEstudo.objects.create(nome='Turma', professor=self.professor)
        self.aluno = User.objects.create_user(
            username='aluno_a', password='x', role=User.ALUNO, apelido='Zeca')
        MembroGrupo.objects.create(aluno=self.aluno, grupo=self.grupo)

    def test_professor_remove_aluno_e_apaga_usuario_orfao(self):
        self.client.force_login(self.professor)
        url = reverse('remover_aluno', args=[self.grupo.pk, self.aluno.pk])
        resp = self.client.post(url)
        self.assertRedirects(resp, reverse('detalhe_grupo', args=[self.grupo.pk]))
        self.assertEqual(MembroGrupo.objects.filter(grupo=self.grupo).count(), 0)
        self.assertFalse(User.objects.filter(pk=self.aluno.pk).exists())

    def test_professor_de_outro_grupo_nao_pode_remover(self):
        outro = User.objects.create_user(username='prof2', password='x', role=User.PROFESSOR)
        self.client.force_login(outro)
        url = reverse('remover_aluno', args=[self.grupo.pk, self.aluno.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(MembroGrupo.objects.filter(grupo=self.grupo).exists())
