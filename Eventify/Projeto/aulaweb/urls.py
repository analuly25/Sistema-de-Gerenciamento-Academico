# inicio/urls.p

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('criar_conta', views.criar_conta, name='criar_conta'),
    path('eventos', views.eventos, name='eventos'),
    path('certificados', views.certificados, name='certificados'),
    path('meus_eventos', views.meus_eventos, name='meus_eventos'),
    path('perfil', views.perfil, name='perfil')
]