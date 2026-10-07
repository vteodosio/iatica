from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.content.models import Licao
from apps.groups.models import GrupoEstudo, MembroGrupo


class LicaoMembershipTests(TestCase):
    """Lições só são acessíveis a alunos membros do grupo."""

    def setUp(self):
        self.professor = User.objects.create_user(username='prof', password='x', role=User.PROFESSOR)
        self.grupo = GrupoEstudo.objects.create(nome='Turma', professor=self.professor)
        self.aluno = User.objects.create_user(username='aluno', password='x', role=User.ALUNO, apelido='Ana')
        self.licao = Licao.objects.create(titulo='Lição', conteudo_html='<p>x</p>', ordem=1, ativa=True)

    def _session(self, aluno):
        s = self.client.session
        s['aluno_id'] = aluno.pk
        s.save()

    def test_membro_acessa_licao(self):
        MembroGrupo.objects.create(aluno=self.aluno, grupo=self.grupo)
        self._session(self.aluno)
        resp = self.client.get(reverse('licao_detalhe', args=[self.grupo.pk, self.licao.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_nao_membro_nao_acessa_licao(self):
        self._session(self.aluno)
        resp = self.client.get(reverse('licao_detalhe', args=[self.grupo.pk, self.licao.pk]))
        self.assertRedirects(resp, reverse('area_aluno'))

    def test_marcar_lida_nao_membro_retorna_ok_false(self):
        self._session(self.aluno)
        resp = self.client.post(reverse('marcar_lida', args=[self.grupo.pk, self.licao.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(resp.content, {'ok': False})
