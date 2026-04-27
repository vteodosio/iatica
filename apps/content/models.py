from django.db import models
from django.conf import settings


class Licao(models.Model):
    titulo = models.CharField(max_length=200, verbose_name='Título')
    subtitulo = models.CharField(max_length=300, blank=True, verbose_name='Subtítulo')
    conteudo_html = models.TextField(verbose_name='Conteúdo HTML')
    icone = models.CharField(max_length=50, default='🤖', verbose_name='Ícone/Emoji')
    cor_tema = models.CharField(max_length=20, default='#f59e0b', verbose_name='Cor do tema')
    ordem = models.PositiveIntegerField(default=0, verbose_name='Ordem')
    ativa = models.BooleanField(default=True, verbose_name='Ativa')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lição'
        verbose_name_plural = 'Lições'
        ordering = ['ordem']

    def __str__(self):
        return f"{self.ordem}. {self.titulo}"


class ProgressoLicao(models.Model):
    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progressos',
    )
    licao = models.ForeignKey(Licao, on_delete=models.CASCADE)
    grupo = models.ForeignKey('groups.GrupoEstudo', on_delete=models.CASCADE)
    lido_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('aluno', 'licao', 'grupo')
        verbose_name = 'Progresso de Lição'
        verbose_name_plural = 'Progressos de Lições'
