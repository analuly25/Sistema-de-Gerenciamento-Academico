# Eventify/Projeto/aulaweb/api_views.py

import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

# Imports dos modelos
from .models import Usuario, Evento, Inscricao, LogAuditoria, Certificado
from .serializers import (
    EventoSerializer, 
    InscricaoSerializer, 
    InscricaoCreateSerializer
)
# Imports das configurações de limite de requisições
from .throttling import ConsultaEventosThrottle, InscricaoThrottle

class APILoginView(APIView):
    """
    Endpoint de autenticação da API
    POST /api/login/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        login = request.data.get('login')
        senha = request.data.get('senha')
        
        if not login or not senha:
            return Response(
                {'error': 'Login e senha são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Busca usuário
            usuario = Usuario.objects.get(login=login)
            
            if usuario.senha == senha:
                if not usuario.ativo:
                    return Response(
                        {'error': 'Conta inativa. Verifique seu email.'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                # LOG
                LogAuditoria.objects.create(
                    usuario=usuario,
                    acao="Login API",
                    detalhes="Autenticação realizada via API"
                )
                
                # Retorna o token UUID existente do usuário
                return Response({
                    'token': str(usuario.token),
                    'user_id': usuario.id,
                    'nome': usuario.nome,
                    'perfil': usuario.perfil,
                    'message': 'Login realizado com sucesso!'
                }, status=status.HTTP_200_OK)
            else:
                LogAuditoria.objects.create(
                    usuario=usuario,
                    acao="Falha Login API",
                    detalhes="Senha incorreta"
                )
                return Response(
                    {'error': 'Credenciais inválidas.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Credenciais inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class APILogoutView(APIView):
    """
    Endpoint de logout da API
    POST /api/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # O usuário já vem carregado na requisição pela autenticação customizada
            usuario = request.user 

            # Regenera o token (UUID) para invalidar o acesso anterior
            usuario.token = uuid.uuid4()
            usuario.save()
            
            # LOG
            LogAuditoria.objects.create(
                usuario=usuario,
                acao="Logout API",
                detalhes="Token regenerado via API"
            )

            return Response(
                {'message': 'Logout realizado com sucesso.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EventosListAPIView(APIView):
    """
    Endpoint para listar todos os eventos
    Rate Limit: 20 requisições por dia
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ConsultaEventosThrottle]
    
    def get(self, request):
        eventos = Evento.objects.all().order_by('data_inicio')
        serializer = EventoSerializer(eventos, many=True)
        
        # LOG (Usa request.user diretamente)
        try:
            LogAuditoria.objects.create(
                usuario=request.user,
                acao="Consulta Eventos API",
                detalhes="Listagem geral de eventos"
            )
        except Exception as e:
            print(f"Erro ao salvar log: {e}")
        
        return Response({
            'count': eventos.count(),
            'eventos': serializer.data
        }, status=status.HTTP_200_OK)


class EventoDetailAPIView(APIView):
    """
    Endpoint para detalhes de um evento específico
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ConsultaEventosThrottle]
    
    def get(self, request, evento_id):
        try:
            evento = Evento.objects.get(id=evento_id)
            serializer = EventoSerializer(evento)
            
            # Verifica se o usuário autenticado está inscrito
            inscrito = Inscricao.objects.filter(
                usuario=request.user,
                evento=evento
            ).exists()
            
            response_data = serializer.data
            response_data['usuario_inscrito'] = inscrito
            
            # LOG
            LogAuditoria.objects.create(
                usuario=request.user,
                acao="Detalhe Evento API",
                detalhes=f"Consultou evento ID {evento.id}: {evento.tipo}"
            )
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Evento.DoesNotExist:
            return Response(
                {'error': 'Evento não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )


class InscricaoCreateAPIView(APIView):
    """
    Endpoint para inscrição em eventos
    Rate Limit: 50 requisições por dia
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [InscricaoThrottle]
    
    def post(self, request):
        serializer = InscricaoCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        evento_id = serializer.validated_data['evento_id']
        usuario = request.user  # Usuário autenticado
        
        try:
            evento = Evento.objects.get(id=evento_id)
            
            # 1. BLOQUEIO DE ORGANIZADOR
            if usuario.perfil == 'organizador':
                LogAuditoria.objects.create(
                    usuario=usuario,
                    acao="Tentativa Inscrição API (Negada)",
                    detalhes="Organizador tentou se inscrever."
                )
                return Response(
                    {'error': 'Organizadores não podem se inscrever em eventos.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 2. VALIDAÇÃO DE VAGAS
            qtd_inscritos = Inscricao.objects.filter(evento=evento).count()
            if qtd_inscritos >= evento.qtd_participantes:
                LogAuditoria.objects.create(
                    usuario=usuario,
                    acao="Tentativa Inscrição API (Cheio)",
                    detalhes=f"Evento '{evento.tipo}' lotado."
                )
                return Response(
                    {'error': 'Não há mais vagas disponíveis para este evento.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 3. VALIDAÇÃO SE JÁ INSCRITO
            if Inscricao.objects.filter(usuario=usuario, evento=evento).exists():
                return Response(
                    {'error': 'Você já está inscrito neste evento.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 4. SALVAR INSCRIÇÃO
            inscricao = Inscricao.objects.create(
                usuario=usuario,
                evento=evento
            )
            
            # LOG
            LogAuditoria.objects.create(
                usuario=usuario,
                acao="Inscrição Evento API",
                detalhes=f"Inscrito com sucesso no evento ID {evento.id} ({evento.tipo})"
            )
            
            inscricao_serializer = InscricaoSerializer(inscricao)
            
            return Response({
                'message': f'Inscrição no evento "{evento.tipo}" realizada com sucesso!',
                'inscricao': inscricao_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Evento.DoesNotExist:
             return Response(
                {'error': 'Evento não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erro interno: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MinhasInscricoesAPIView(APIView):
    """
    Endpoint para listar inscrições do usuário autenticado
    GET /api/minhas-inscricoes/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Busca as inscrições do usuário autenticado
        inscricoes = Inscricao.objects.filter(
            usuario=request.user
        ).order_by('-data_inscricao')
        
        serializer = InscricaoSerializer(inscricoes, many=True)
        
        # LOG
        try:
            LogAuditoria.objects.create(
                usuario=request.user,
                acao="Consulta Minhas Inscrições API",
                detalhes="Listou suas próprias inscrições"
            )
        except:
            pass

        return Response({
            'count': inscricoes.count(),
            'inscricoes': serializer.data
        }, status=status.HTTP_200_OK)


class CancelarInscricaoAPIView(APIView):
    """
    Endpoint para cancelar uma inscrição
    DELETE /api/inscricoes/<evento_id>/
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [InscricaoThrottle]
    
    def delete(self, request, evento_id):
        """Cancela a inscrição do usuário em um evento"""
        usuario = request.user # Usuário autenticado
        
        try:
            inscricao = Inscricao.objects.get(
                usuario=usuario,
                evento_id=evento_id
            )
            
            # VALIDAÇÃO DE CERTIFICADO
            if Certificado.objects.filter(inscricao=inscricao).exists():
                LogAuditoria.objects.create(
                    usuario=usuario,
                    acao="Tentativa Cancelamento API (Negada)",
                    detalhes="Tentou cancelar evento com certificado emitido."
                )
                return Response(
                    {'error': 'Não é possível cancelar inscrição pois o certificado já foi emitido.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            evento_tipo = inscricao.evento.tipo
            inscricao.delete()
            
            # LOG
            LogAuditoria.objects.create(
                usuario=usuario,
                acao="Cancelamento Inscrição API",
                detalhes=f"Cancelou inscrição no evento ID {evento_id} ({evento_tipo})"
            )
            
            return Response({
                'message': f'Inscrição no evento "{evento_tipo}" cancelada com sucesso.'
            }, status=status.HTTP_200_OK)
            
        except Inscricao.DoesNotExist:
            return Response(
                {'error': 'Inscrição não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erro ao cancelar inscrição: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )