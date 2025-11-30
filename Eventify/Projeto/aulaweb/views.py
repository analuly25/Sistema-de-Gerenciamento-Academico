from django.shortcuts import render, redirect
from django.contrib import messages
# Importar todos os modelos necessários
from .models import Usuario, Evento, Inscricao, Certificado
from django.db import IntegrityError
from django.utils import timezone # Importar para verificar a data/hora
import os

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
        data_nascimento = data_nascimento_str if data_nascimento_str else None
        email = email if email else None
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
                email=email,
                data_nascimento=data_nascimento,
                endereco=endereco,
                curso=curso,
                semestre=semestre
            )
            novo_usuario.save() 

            messages.success(request, 'Cadastro realizado com sucesso! Faça o login.')
            return redirect('login') 

        except IntegrityError:
            messages.error(request, 'Ocorreu um erro ao criar a conta.')
            return render(request, 'aulaweb/signup.html')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro: {e}')
            return render(request, 'aulaweb/signup.html')

    return render(request, 'aulaweb/signup.html')


def eventos(request):
    # 1. Buscar todos os eventos
    todos_os_eventos = Evento.objects.all().order_by('data_inicio')
    
    usuario_logado = None
    inscricoes_ids = [] # Lista vazia por padrão

    if 'usuario_id' in request.session:
        try:
            usuario_logado = Usuario.objects.get(id=request.session['usuario_id'])
            
            # NOVO: Busca apenas os IDs dos eventos que o usuário já se inscreveu
            # values_list retorna uma lista simples como [1, 5, 8] em vez de objetos completos
            inscricoes_ids = Inscricao.objects.filter(usuario=usuario_logado).values_list('evento_id', flat=True)
            
        except Usuario.DoesNotExist:
            pass 
    
    contexto = {
        'eventos_lista': todos_os_eventos,
        'usuario': usuario_logado,
        'inscricoes_ids': inscricoes_ids # Enviamos essa lista para o HTML
    }
    
    return render(request, 'aulaweb/eventos.html', contexto)




def criar_evento(request):

    if request.method == 'POST':
        # Nota: Adicionar request.FILES para pegar a imagem
        tipo = request.POST.get('tipo')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        horario = request.POST.get('horario')
        local = request.POST.get('local')
        qtd_participantes_str = request.POST.get('qtd_participantes')
        banner_arquivo = request.FILES.get('banner') # Captura o arquivo

        # Validações Básicas
        if not all([tipo, data_inicio, data_fim, horario, local, qtd_participantes_str]):
            messages.error(request, 'Todos os campos de texto são obrigatórios.')
            return render(request, 'aulaweb/criar_evento.html')

        # Validação do Banner (Tipo de arquivo)
        if banner_arquivo:
            extensao = os.path.splitext(banner_arquivo.name)[1].lower()
            if extensao not in ['.jpg', '.jpeg', '.png', '.webp']:
                messages.error(request, 'O banner deve ser uma imagem (JPG, PNG ou WEBP).')
                return render(request, 'aulaweb/criar_evento.html')

        try:
            qtd_participantes = int(qtd_participantes_str)
            if qtd_participantes <= 0:
                 raise ValueError("A quantidade deve ser positiva.")

            # Validação de Datas (Não permitir datas passadas)
            data_inicio_dt = timezone.datetime.strptime(data_inicio, '%Y-%m-%d').date()
            if data_inicio_dt < timezone.now().date():
                 messages.error(request, 'A data de início não pode ser no passado.')
                 return render(request, 'aulaweb/criar_evento.html')

            novo_evento = Evento(
                tipo=tipo,
                data_inicio=data_inicio,
                data_fim=data_fim,
                horario=horario,
                local=local,
                qtd_participantes=qtd_participantes,
                organizador=usuario_logado,
                banner=banner_arquivo # Salva a imagem
            )
            novo_evento.save()

            messages.success(request, 'Evento criado com sucesso!')
            return redirect('eventos')

        except ValueError:
            messages.error(request, 'Quantidade de participantes inválida.')
        except Exception as e:
            messages.error(request, f'Erro ao salvar: {e}')

    return render(request, 'aulaweb/criar_evento.html')


def inscrever_evento(request, evento_id):
    if 'usuario_id' not in request.session:
        messages.error(request, 'Você precisa fazer login para se inscrever em um evento.')
        return redirect('login')

    try:
        usuario_logado = Usuario.objects.get(id=request.session['usuario_id'])
        evento_para_inscrever = Evento.objects.get(id=evento_id)
        
        nova_inscricao = Inscricao(
            usuario=usuario_logado,
            evento=evento_para_inscrever
        )
        nova_inscricao.save()
        
        messages.success(request, f'Inscrição no evento "{evento_para_inscrever.tipo}" realizada com sucesso!')

    except Evento.DoesNotExist:
        messages.error(request, 'O evento em que você tentou se inscrever não existe.')
    except Usuario.DoesNotExist:
        messages.error(request, 'Seu usuário não foi encontrado. Faça login novamente.')
    except IntegrityError:
        messages.warning(request, 'Você já está inscrito neste evento.')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado: {e}')

    return redirect('eventos')

# ===============================
# NOVA FUNÇÃO: Cancelar Inscrição
# ===============================
def cancelar_inscricao(request, evento_id):
    # 1. Verificar se o usuário está logado
    if 'usuario_id' not in request.session:
        messages.error(request, 'Você precisa fazer login para cancelar uma inscrição.')
        return redirect('login')

    try:
        # 2. Buscar o usuário e o evento
        usuario_logado = Usuario.objects.get(id=request.session['usuario_id'])
        evento = Evento.objects.get(id=evento_id)
        
        # 3. Encontrar a inscrição específica para apagar
        inscricao = Inscricao.objects.get(usuario=usuario_logado, evento=evento)
        
        # 4. Apagar a inscrição
        inscricao.delete()
        
        messages.success(request, f'Sua inscrição no evento "{evento.tipo}" foi cancelada.')

    except (Inscricao.DoesNotExist, Usuario.DoesNotExist, Evento.DoesNotExist):
        messages.error(request, 'Inscrição não encontrada.')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao cancelar: {e}')

    # 5. Redirecionar de volta para a página "Meus Eventos"
    return redirect('meuseventos')


def certificados(request):
    if 'usuario_id' not in request.session:
        messages.error(request, 'Você precisa fazer login para ver esta página.')
        return redirect('login')

    try:
        usuario_logado = Usuario.objects.get(id=request.session['usuario_id'])
        
        certificados_do_usuario = Certificado.objects.filter(
            inscricao__usuario=usuario_logado
        ).order_by('-data_emissao')
        
        contexto = {
            'certificados_lista': certificados_do_usuario,
            'usuario': usuario_logado # Passa o usuário para o template
        }
        return render(request, 'aulaweb/certificados.html', contexto)
        
    except Usuario.DoesNotExist:
        if 'usuario_id' in request.session:
            del request.session['usuario_id']
        messages.error(request, 'Usuário não encontrado. Faça login novamente.')
        return redirect('login')

def gerar_certificado(request, evento_id):
    if 'usuario_id' not in request.session:
        messages.error(request, 'Você precisa fazer login para gerar um certificado.')
        return redirect('login')
    
    try:
        usuario_logado = Usuario.objects.get(id=request.session['usuario_id'])
        evento = Evento.objects.get(id=evento_id)
        inscricao = Inscricao.objects.get(usuario=usuario_logado, evento=evento)
        
        if evento.data_fim > timezone.now().date():
            messages.error(request, 'Você só pode emitir o certificado após o término do evento.')
            return redirect('meuseventos') 

        if Certificado.objects.filter(inscricao=inscricao).exists():
            messages.warning(request, 'Este certificado já foi emitido.')
            return redirect('certificados') 
            
        novo_certificado = Certificado(
            inscricao=inscricao
        )
        novo_certificado.save()
        
        messages.success(request, f'Certificado do evento "{evento.tipo}" gerado com sucesso!')
        return redirect('certificados') 

    except (Usuario.DoesNotExist, Evento.DoesNotExist, Inscricao.DoesNotExist):
        messages.error(request, 'Ocorreu um erro: inscrição não encontrada.')
        return redirect('meuseventos')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado: {e}')
        return redirect('meuseventos')


# Em aulaweb/views.py

def meuseventos(request):
    # ... (código de verificação de login) ...

    try:
        usuario_logado = Usuario.objects.get(id=request.session['usuario_id'])
        
        eventos_inscritos = Evento.objects.filter(
            inscricoes__usuario=usuario_logado
        ).order_by('data_inicio')
        
        # O CONTEXTO TEM DE TER 'hoje'
        contexto = {
            'eventos_lista': eventos_inscritos,
            'hoje': timezone.now().date(), # <--- VERIFICA ESTA LINHA
            'usuario': usuario_logado
        }
        return render(request, 'aulaweb/meuseventos.html', contexto)
        
        
    except Usuario.DoesNotExist:
        if 'usuario_id' in request.session:
            del request.session['usuario_id']
        messages.error(request, 'Usuário não encontrado. Faça login novamente.')
        return redirect('login')


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