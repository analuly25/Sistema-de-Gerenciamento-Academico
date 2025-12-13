# Eventify/Projeto/aulaweb/api_urls.py

from django.urls import path
from .api_views import (
    APILoginView,
    APILogoutView,
    EventosListAPIView,
    EventoDetailAPIView,
    InscricaoCreateAPIView,
    MinhasInscricoesAPIView,
    CancelarInscricaoAPIView
)

urlpatterns = [
    # Autenticação
    path('login/', APILoginView.as_view(), name='api_login'),
    path('logout/', APILogoutView.as_view(), name='api_logout'),
    
    # Eventos
    path('eventos/', EventosListAPIView.as_view(), name='api_eventos_list'),
    path('eventos/<int:evento_id>/', EventoDetailAPIView.as_view(), name='api_evento_detail'),
    
    # Inscrições
    path('inscricoes/', InscricaoCreateAPIView.as_view(), name='api_inscricao_create'),
    path('minhas-inscricoes/', MinhasInscricoesAPIView.as_view(), name='api_minhas_inscricoes'),
    path('inscricoes/<int:evento_id>/', CancelarInscricaoAPIView.as_view(), name='api_cancelar_inscricao'),
]