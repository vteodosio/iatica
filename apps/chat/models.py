from django.conf import settings
from django.db import models


class PerguntaSugerida(models.Model):
    """Pergunta curada que o aluno pode enviar à IA.

    O aluno NUNCA escreve texto livre: ele escolhe uma destas perguntas.
    Por isso o que chega ao provedor de LLM é texto curado por adultos.
    """

    texto = models.CharField(max_length=300, verbose_name='Pergunta')
    licao = models.ForeignKey(
        'content.Licao',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perguntas_sugeridas',
        verbose_name='Lição relacionada',
    )
    conceito = models.CharField(max_length=120, blank=True, verbose_name='Conceito demonstrado')
    ordem = models.PositiveIntegerField(default=0, verbose_name='Ordem')
    ativa = models.BooleanField(default=True, verbose_name='Ativa')

    class Meta:
        verbose_name = 'Pergunta sugerida'
        verbose_name_plural = 'Perguntas sugeridas'
        ordering = ['ordem', 'id']

    def __str__(self):
        return self.texto[:70]


class Interacao(models.Model):
    """Uma troca pergunta → resposta entre um aluno e a IA."""

    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interacoes_chat',
        verbose_name='Aluno',
    )
    grupo = models.ForeignKey(
        'groups.GrupoEstudo',
        on_delete=models.CASCADE,
        related_name='interacoes_chat',
        verbose_name='Grupo',
    )
    pergunta = models.ForeignKey(
        PerguntaSugerida,
        on_delete=models.PROTECT,
        verbose_name='Pergunta',
    )
    resposta = models.TextField(verbose_name='Resposta da IA')
    bloqueada = models.BooleanField(default=False, verbose_name='Bloqueada')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Interação do chat'
        verbose_name_plural = 'Interações do chat'
        ordering = ['criado_em', 'id']

    def __str__(self):
        return f'{self.aluno} → {self.pergunta.texto[:40]}'
