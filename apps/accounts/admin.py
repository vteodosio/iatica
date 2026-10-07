from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'escola', 'apelido')
    list_filter = ('role', 'escola')
    readonly_fields = UserAdmin.readonly_fields + ('consentiu_em',)
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('role', 'escola', 'apelido', 'consentiu_em')}),
    )
