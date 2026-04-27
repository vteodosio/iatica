from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    PROFESSOR = 'professor'
    ALUNO = 'aluno'
    ROLE_CHOICES = [
        (PROFESSOR, 'Professor'),
        (ALUNO, 'Aluno'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ALUNO)
    escola = models.CharField(max_length=200, blank=True, verbose_name='Escola')

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def is_professor(self):
        return self.role == self.PROFESSOR

    def is_aluno(self):
        return self.role == self.ALUNO

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
