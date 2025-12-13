# inicio/urls.p

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login.html', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'), 
    path('signup.html', views.signup, name='signup'),
    
    # Rota de Eventos
    path('eventos.html', views.eventos, name='eventos'),
    path('criar_evento/', views.criar_evento, name='criar_evento'),
    path('editar_evento/<int:evento_id>/', views.editar_evento, name='editar_evento'),
    
    # Rota de Inscrição
    path('inscrever/<int:evento_id>/', views.inscrever_evento, name='inscrever_evento'),
    
    # ===============================
    # NOVA ROTA ADICIONADA
    # ===============================
    path('cancelar_inscricao/<int:evento_id>/', views.cancelar_inscricao, name='cancelar_inscricao'),
    
    # Rota de Certificado
    path('gerar_certificado/<int:evento_id>/', views.gerar_certificado, name='gerar_certificado'),
    path('certificados.html', views.certificados, name='certificados'),
    
    # Outras rotas
    path('meuseventos.html', views.meuseventos, name='meuseventos'),
    path('ativar/<uuid:token>/', views.ativar_conta, name='ativar_conta'),
    path('perfil.html', views.perfil, name='perfil'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('logs/', views.logs_auditoria, name='logs_auditoria')

]