# Eventify/Projeto/aulaweb/authentication.py

from rest_framework.authentication import TokenAuthentication as BaseTokenAuth
from rest_framework import exceptions
from .models import Usuario

class CustomTokenAuthentication(BaseTokenAuth):
    """
    Autenticação customizada que usa o campo 'token' (UUID) do modelo Usuario.
    """
    
    def authenticate_credentials(self, key):
        try:
            # Busca o usuário diretamente pelo seu token UUID
            usuario = Usuario.objects.get(token=key)
        except (Usuario.DoesNotExist, ValueError):
            raise exceptions.AuthenticationFailed('Token inválido.')
        
        if not usuario.ativo:
            raise exceptions.AuthenticationFailed('Usuário inativo ou bloqueado.')
        
        # Retorna uma tupla (user, token)
        return (usuario, key)