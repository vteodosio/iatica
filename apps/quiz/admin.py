from django.contrib import admin
from .models import Pergunta, Alternativa, Quiz, TentativaQuiz, RespostaAluno


class AlternativaInline(admin.TabularInline):
    model = Alternativa
    extra = 4


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('ordem', 'texto')
    inlines = [AlternativaInline]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('grupo', 'criado_em')
    filter_horizontal = ('perguntas',)


@admin.register(TentativaQuiz)
class TentativaQuizAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'grupo', 'pontuacao', 'total_perguntas', 'finalizado_em')
