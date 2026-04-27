from django.urls import path
from . import views

urlpatterns = [
    path('grupo/<int:grupo_pk>/licao/<int:licao_pk>/', views.licao_detalhe, name='licao_detalhe'),
    path('grupo/<int:grupo_pk>/licao/<int:licao_pk>/marcar/', views.marcar_lida, name='marcar_lida'),
]
