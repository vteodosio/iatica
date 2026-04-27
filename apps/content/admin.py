from django.contrib import admin
from .models import Licao, ProgressoLicao


@admin.register(Licao)
class LicaoAdmin(admin.ModelAdmin):
    list_display = ('ordem', 'titulo', 'icone', 'ativa')
    list_display_links = ('titulo',)   # link de edição → libera 'ordem' para list_editable
    list_editable = ('ordem', 'ativa')
    ordering = ('ordem',)


@admin.register(ProgressoLicao)
class ProgressoLicaoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'licao', 'grupo', 'lido_em')