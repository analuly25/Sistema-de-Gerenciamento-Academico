from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario
from django.db import IntegrityError

# Create your views here.

def index(request):
    return render(request, 'aulaweb/index.html')

def login(request):
    # Limpa qualquer sessão antiga
    if 'usuario_id' in request.session:
        del request.session['usuario_id']

    if request.method == 'POST':
        login_usuario = request.POST.get('usuario')
        senha_usuario = request.POST.get('senha')

        if not login_usuario or not senha_usuario:
            messages.error(request, 'Usuário e senha são obrigatórios.')
            return render(request, 'aulaweb/login.html')

        try:
            usuario_encontrado = Usuario.objects.get(login=login_usuario)

            if usuario_encontrado.senha == senha_usuario:
                request.session['usuario_id'] = usuario_encontrado.id
                messages.success(request, 'Login realizado com sucesso!')
                return redirect('perfil') 
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
                return render(request, 'aulaweb/login.html')

        except Usuario.DoesNotExist:
            messages.error(request, 'Usuário ou senha inválidos.')
            return render(request, 'aulaweb/login.html')

    return render(request, 'aulaweb/login.html')

def logout_view(request):
    # Função de logout
    if 'usuario_id' in request.session:
        del request.session['usuario_id']
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('index') # Redireciona para a página inicial


def signup(request):
    if request.method == 'POST':
        # 1. Obter os dados obrigatórios
        nome = request.POST.get('nome')
        instituicao = request.POST.get('instituicao')
        login = request.POST.get('usuario')
        senha = request.POST.get('senha')

        # 2. Obter os NOVOS dados (opcionais)
        email = request.POST.get('email')
        data_nascimento_str = request.POST.get('data_nascimento')
        endereco = request.POST.get('endereco')
        curso = request.POST.get('curso')
        semestre_str = request.POST.get('semestre')


        # 3. Validar campos obrigatórios
        if not nome or not instituicao or not login or not senha:
            messages.error(request, 'Os campos Nome, Usuário, Senha e Instituição são obrigatórios.')
            return render(request, 'aulaweb/signup.html')

        # 4. Verificar se o usuário (login) já existe
        if Usuario.objects.filter(login=login).exists():
            messages.error(request, 'Este nome de usuário já está em uso. Tente outro.')
            return render(request, 'aulaweb/signup.html')

        # 5. Tratar os campos opcionais (que podem vir vazios)
        
        # Tratar data (só guardar se não for vazia)
        data_nascimento = data_nascimento_str if data_nascimento_str else None
        
        # Tratar email (só guardar se não for vazio)
        email = email if email else None

        # Tratar semestre (converter para int ou ser None)
        semestre = None
        if semestre_str:
            try:
                semestre = int(semestre_str)
            except ValueError:
                messages.error(request, 'O semestre deve ser um número válido.')
                return render(request, 'aulaweb/signup.html')


        # 6. Se tudo estiver OK, criar o novo usuário
        try:
            novo_usuario = Usuario(
                nome=nome,
                instituicao=instituicao,
                login=login,
                senha=senha,
                perfil='aluno',
                
                # Campos novos
                email=email,
                data_nascimento=data_nascimento,
                endereco=endereco,
                curso=curso,
                semestre=semestre
            )
            novo_usuario.save() # Salva o novo usuário no banco de dados

            messages.success(request, 'Cadastro realizado com sucesso! Faça o login.')
            return redirect('login') # Redireciona para a página de login

        except IntegrityError:
            messages.error(request, 'Ocorreu um erro ao criar a conta.')
            return render(request, 'aulaweb/signup.html')
        except Exception as e:
            # Apanha outros erros (ex: formato de data inválido)
            messages.error(request, f'Ocorreu um erro: {e}')
            return render(request, 'aulaweb/signup.html')


    # Se o método for GET, apenas mostra a página de cadastro
    return render(request, 'aulaweb/signup.html')

def eventos(request):
    return render(request, 'aulaweb/eventos.html')

def certificados(request):
    return render(request, 'aulaweb/certificados.html')

def meuseventos(request):
    return render(request, 'aulaweb/meuseventos.html')

def perfil(request):
    if 'usuario_id' not in request.session:
        messages.error(request, 'Você precisa fazer login para ver seu perfil.')
        return redirect('login')

    try:
        usuario_logado = Usuario.objects.get(id=request.session['usuario_id'])
        
        contexto = {
            'usuario': usuario_logado
        }
        
        return render(request, 'aulaweb/perfil.html', contexto)
        
    except Usuario.DoesNotExist:
        if 'usuario_id' in request.session:
            del request.session['usuario_id']
        messages.error(request, 'Usuário não encontrado. Faça login novamente.')
        return redirect('login')