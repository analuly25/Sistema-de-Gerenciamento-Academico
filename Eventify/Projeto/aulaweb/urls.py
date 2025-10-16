# inicio/urls.p

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login.html', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'), 
    path('signup.html', views.signup, name='signup'),
    path('eventos.html', views.eventos, name='eventos'),
    path('certificados.html', views.certificados, name='certificados'),
    path('meuseventos.html', views.meuseventos, name='meuseventos'),
    path('perfil.html', views.perfil, name='perfil')
]