from django.contrib import admin
from .models import GrupoEstudo, MembroGrupo


@admin.register(GrupoEstudo)
class GrupoEstudoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'professor', 'status', 'criado_em')
    list_filter = ('status',)
    search_fields = ('nome', 'codigo')


@admin.register(MembroGrupo)
class MembroGrupoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'grupo', 'entrou_em')
