import decimal
import random
import string
from django.db import models
from django.conf import settings


def gerar_codigo():
    """Gera um código único de 6 caracteres para o grupo."""
    while True:
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not GrupoEstudo.objects.filter(codigo=codigo).exists():
            return codigo


class GrupoEstudo(models.Model):
    ATIVO = 'ativo'
    FINALIZADO = 'finalizado'
    STATUS_CHOICES = [
        (ATIVO, 'Ativo'),
        (FINALIZADO, 'Finalizado'),
    ]

    nome = models.CharField(max_length=200, verbose_name='Nome do Grupo')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    codigo = models.CharField(max_length=6, unique=True, default=gerar_codigo, verbose_name='Código')
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grupos_criados',
        verbose_name='Professor'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ATIVO)
    criado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Grupo de Estudo'
        verbose_name_plural = 'Grupos de Estudo'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.nome} ({self.codigo})"

    def total_alunos(self):
        return self.membros.count()

    def alunos_que_completaram_quiz(self):
        from apps.quiz.models import TentativaQuiz
        return TentativaQuiz.objects.filter(
            grupo=self,
            finalizado_em__isnull=False
        ).values('aluno').distinct().count()


    def media_pontuacao(self):
        from apps.quiz.models import TentativaQuiz
        from django.db.models import Avg

        resultado = TentativaQuiz.objects.filter(
            grupo=self,
            finalizado_em__isnull=False
        ).aggregate(media=Avg('pontuacao'))

        perguntas = TentativaQuiz.objects.filter(
            grupo=self,
            finalizado_em__isnull=False
        ).aggregate(media=Avg('total_perguntas'))

        media_pontuacao = resultado['media'] or 0  # ✅ extrai o valor
        media_perguntas = perguntas['media'] or 0  # ✅ extrai o valor

        if media_perguntas == 0:
            return 0  # ✅ evita divisão por zero

        return round((media_pontuacao / media_perguntas) * 100)  # ✅ calcula o percentual



class MembroGrupo(models.Model):
    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grupos_participados',
        verbose_name='Aluno'
    )
    grupo = models.ForeignKey(
        GrupoEstudo,
        on_delete=models.CASCADE,
        related_name='membros',
        verbose_name='Grupo'
    )
    entrou_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Membro do Grupo'
        verbose_name_plural = 'Membros do Grupo'
        unique_together = ('aluno', 'grupo')

    def __str__(self):
        return f"{self.aluno} → {self.grupo}"
