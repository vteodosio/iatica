from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('contas/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.groups.urls')),
    path('conteudo/', include('apps.content.urls')),
    path('quiz/', include('apps.quiz.urls')),
    path('relatorios/', include('apps.reports.urls')),
    path('chat/', include('apps.chat.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
