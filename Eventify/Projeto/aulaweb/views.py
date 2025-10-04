from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'aulaweb/index.html')

def login(request):

    return render(request, 'aulaweb/login.html')

def criar_conta(request):
    return render(request, 'aulaweb/signup.html')

def eventos(request):
    return render(request, 'aulaweb/eventos.html')

def certificados(request):
    return render(request, 'aulaweb/certificados.html')

def meus_eventos(request):
    return render(request, 'aulaweb/meuseventos.html')

def perfil(request):
    return render(request, 'aulaweb/perfil.html')


