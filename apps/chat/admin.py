from django.contrib import admin

from .models import Interacao, PerguntaSugerida


@admin.register(PerguntaSugerida)
class PerguntaSugeridaAdmin(admin.ModelAdmin):
    list_display = ('ordem', 'texto', 'conceito', 'licao', 'ativa')
    list_filter = ('ativa', 'licao')
    list_editable = ('ativa',)
    ordering = ('ordem',)


@admin.register(Interacao)
class InteracaoAdmin(admin.ModelAdmin):
    list_display = ('criado_em', 'aluno', 'grupo', 'pergunta', 'bloqueada')
    list_filter = ('bloqueada',)
    readonly_fields = ('aluno', 'grupo', 'pergunta', 'resposta', 'bloqueada', 'criado_em')

    def has_add_permission(self, request):
        # Interações são geradas pelo uso do chat, não cadastradas à mão.
        return False
