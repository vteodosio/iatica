from django.urls import path
from . import views

urlpatterns = [
    path('grupo/<int:grupo_pk>/iniciar/', views.iniciar_quiz, name='iniciar_quiz'),
    path('grupo/<int:grupo_pk>/submeter/', views.submeter_quiz, name='submeter_quiz'),
    path('resultado/<int:tentativa_pk>/', views.resultado_quiz, name='resultado_quiz'),
]
