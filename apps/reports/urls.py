from django.urls import path
from . import views

urlpatterns = [
    path('grupo/<int:pk>/', views.relatorio_grupo, name='relatorio_grupo'),
    path('grupo/<int:pk>/pdf/', views.relatorio_pdf, name='relatorio_pdf'),
]
