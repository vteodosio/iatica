from django.urls import path

from . import views

urlpatterns = [
    path('grupo/<int:grupo_pk>/', views.chat, name='chat'),
    path('grupo/<int:grupo_pk>/feedback/<int:interacao_pk>/',
         views.registrar_feedback, name='chat_feedback'),
    path('grupo/<int:pk>/painel/', views.painel, name='chat_painel'),
]
