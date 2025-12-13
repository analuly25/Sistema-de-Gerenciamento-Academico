# Eventify/Projeto/aulaweb/serializers.py

from rest_framework import serializers
from .models import Usuario, Evento, Inscricao

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Usuario"""
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'login', 'perfil', 'instituicao', 'email', 'curso']
        # Não expor a senha na API

class EventoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Evento com informações do organizador"""
    organizador_nome = serializers.CharField(source='organizador.nome', read_only=True)
    organizador_instituicao = serializers.CharField(source='organizador.instituicao', read_only=True)
    
    class Meta:
        model = Evento
        fields = [
            'id', 
            'tipo', 
            'data_inicio', 
            'data_fim', 
            'horario', 
            'local', 
            'qtd_participantes',
            'organizador_nome',
            'organizador_instituicao',
            'banner'
        ]

class InscricaoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Inscricao"""
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    evento_tipo = serializers.CharField(source='evento.tipo', read_only=True)
    evento_local = serializers.CharField(source='evento.local', read_only=True)
    
    class Meta:
        model = Inscricao
        fields = [
            'id',
            'usuario',
            'usuario_nome',
            'evento',
            'evento_tipo',
            'evento_local',
            'data_inscricao'
        ]
        read_only_fields = ['data_inscricao']

class InscricaoCreateSerializer(serializers.Serializer):
    """Serializer simplificado para criar inscrições"""
    evento_id = serializers.IntegerField()
    
    def validate_evento_id(self, value):
        """Valida se o evento existe"""
        try:
            Evento.objects.get(id=value)
        except Evento.DoesNotExist:
            raise serializers.ValidationError("Evento não encontrado.")
        return value