from django.urls import path
from apps.accounts import views as acc_views
from . import views

urlpatterns = [
    path('', acc_views.dashboard_professor, name='dashboard_professor'),
    path('criar-grupo/', views.criar_grupo, name='criar_grupo'),
    path('grupo/<int:pk>/', views.detalhe_grupo, name='detalhe_grupo'),
    path('grupo/<int:pk>/finalizar/', views.finalizar_grupo, name='finalizar_grupo'),
    path('alunos/', views.area_aluno, name='area_aluno'),
    path('alunos/entrar/', views.entrar_grupo, name='entrar_grupo'),
    path('alunos/sala/<int:pk>/', views.sala_estudo, name='sala_estudo'),
]
