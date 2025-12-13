# Eventify/Projeto/aulaweb/throttling.py

from rest_framework.throttling import UserRateThrottle

class ConsultaEventosThrottle(UserRateThrottle):
    """
    Limita consultas de eventos a 20 requisições por dia por usuário
    """
    scope = 'consulta_eventos'
    rate = '20/day'

class InscricaoThrottle(UserRateThrottle):
    """
    Limita inscrições em eventos a 50 requisições por dia por usuário
    """
    scope = 'inscricao'
    rate = '50/day'