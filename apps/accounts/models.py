import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models


def gerar_username_aluno():
    """Gera um username aleatório e não-identificável para alunos.

    Não deriva do nome real, preservando a privacidade da criança.
    """
    while True:
        username = f"aluno_{secrets.token_hex(8)}"
        if not User.objects.filter(username=username).exists():
            return username


class User(AbstractUser):
    PROFESSOR = 'professor'
    ALUNO = 'aluno'
    ROLE_CHOICES = [
        (PROFESSOR, 'Professor'),
        (ALUNO, 'Aluno'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ALUNO)
    escola = models.CharField(max_length=200, blank=True, verbose_name='Escola')
    apelido = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='Apelido / Nome de exibição',
        help_text='Nome ou apelido exibido para os alunos (não precisa ser o nome real).',
    )
    consentiu_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Consentimento registrado em',
        help_text='Data/hora em que o aluno (ou responsável) aceitou o aviso de privacidade.',
    )

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def is_professor(self):
        return self.role == self.PROFESSOR

    def is_aluno(self):
        return self.role == self.ALUNO

    def nome_exibicao(self):
        """Nome usado para exibição: apelido do aluno ou nome completo do professor."""
        if self.apelido:
            return self.apelido
        return self.get_full_name() or self.username

    def __str__(self):
        return f"{self.nome_exibicao()} ({self.get_role_display()})"
