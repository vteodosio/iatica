from django.db import models
from django.conf import settings


class Pergunta(models.Model):
    texto = models.TextField(verbose_name='Texto da Pergunta')
    ordem = models.PositiveIntegerField(default=0)
    explicacao = models.TextField(
        blank=True,
        verbose_name='Explicação',
        help_text='Por que a resposta correta está certa. Exibida ao aluno no resultado.',
    )
    licao = models.ForeignKey(
        'content.Licao',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perguntas',
        verbose_name='Lição relacionada',
    )

    class Meta:
        verbose_name = 'Pergunta'
        verbose_name_plural = 'Perguntas'
        ordering = ['ordem']

    def __str__(self):
        return f"{self.ordem}. {self.texto[:60]}..."


class Alternativa(models.Model):
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE, related_name='alternativas')
    texto = models.CharField(max_length=400, verbose_name='Texto da Alternativa')
    correta = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Alternativa'
        verbose_name_plural = 'Alternativas'

    def __str__(self):
        return f"{'✅' if self.correta else '❌'} {self.texto[:50]}"


class Quiz(models.Model):
    grupo = models.ForeignKey(
        'groups.GrupoEstudo', on_delete=models.CASCADE, related_name='quizzes'
    )
    perguntas = models.ManyToManyField(Pergunta, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f"Quiz do grupo: {self.grupo}"


class TentativaQuiz(models.Model):
    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tentativas',
    )
    grupo = models.ForeignKey('groups.GrupoEstudo', on_delete=models.CASCADE)
    pontuacao = models.PositiveIntegerField(default=0)
    total_perguntas = models.PositiveIntegerField(default=0)
    iniciado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Tentativa de Quiz'
        verbose_name_plural = 'Tentativas de Quiz'

    def __str__(self):
        return f"{self.aluno} — {self.grupo} — {self.pontuacao}/{self.total_perguntas}"

    def percentual(self):
        if self.total_perguntas == 0:
            return 0
        return round((self.pontuacao / self.total_perguntas) * 100)


class RespostaAluno(models.Model):
    tentativa = models.ForeignKey(TentativaQuiz, on_delete=models.CASCADE, related_name='respostas')
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    alternativa_escolhida = models.ForeignKey(Alternativa, on_delete=models.SET_NULL, null=True, blank=True)
    correta = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Resposta do Aluno'
        verbose_name_plural = 'Respostas dos Alunos'
