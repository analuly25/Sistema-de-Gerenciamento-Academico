from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import os
import uuid
import re # Importante para a senha forte

# Importar modelos
from .models import Usuario, Evento, Inscricao, Certificado, LogAuditoria

# Create your views here.

def index(request):
    return render(request, 'aulaweb/index.html')

def registrar_log(usuario, acao, detalhes=""):
    try:
        LogAuditoria.objects.create(
            usuario=usuario,
            acao=acao,
            detalhes=detalhes
        )
    except Exception as e:
        print(f"Erro ao salvar log: {e}")

def login(request):
    # 1. Limpa qualquer sessão antiga ao entrar na página
    if 'usuario_id' in request.session:
        del request.session['usuario_id']

    # 2. Se o formulário foi enviado (clicou no botão Entrar)
    if request.method == 'POST':
        login_usuario = request.POST.get('usuario')
        senha_usuario = request.POST.get('senha')

        if not login_usuario or not senha_usuario:
            messages.error(request, 'Usuário e senha são obrigatórios.')
            return render(request, 'aulaweb/login.html')

        try:
            # Tenta encontrar o usuário no banco
            usuario_encontrado = Usuario.objects.get(login=login_usuario)

            # Verifica a senha
            if usuario_encontrado.senha == senha_usuario:
                
                # --- VERIFICAÇÃO SE A CONTA ESTÁ ATIVA ---
                if not usuario_encontrado.ativo:
                    messages.error(request, 'Esta conta ainda não foi ativada. Verifique o seu e-mail ou o terminal.')
                    return render(request, 'aulaweb/login.html')
                # -----------------------------------------

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
    if 'usuario_id' in request.session:
        del request.session['usuario_id']
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('index')


def signup(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        instituicao = request.POST.get('instituicao')
        login = request.POST.get('usuario')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        email = request.POST.get('email')
        perfil_selecionado = request.POST.get('perfil', 'aluno')
        data_nascimento_str = request.POST.get('data_nascimento')
        endereco = request.POST.get('endereco')
        curso = request.POST.get('curso')
        semestre_str = request.POST.get('semestre')

        if not all([nome, instituicao, login, senha, confirmar_senha, email]):
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return render(request, 'aulaweb/signup.html')

        # ======================================================
        # INÍCIO DA VALIDAÇÃO DE SENHA FORTE (ATUALIZADO)
        # ======================================================
        lista_erros = []

        if len(senha) < 8:
            lista_erros.append('A senha deve ter no mínimo 8 caracteres.')
        
        if not re.search(r'[A-Za-z]', senha):
            lista_erros.append('A senha deve conter pelo menos uma letra.')

        if not re.search(r'\d', senha):
            lista_erros.append('A senha deve conter pelo menos um número.')
        
        if not re.search(r'[^A-Za-z0-9]', senha):
            lista_erros.append('A senha deve conter pelo menos um caractere especial (ex: @, #, $).')

        if senha != confirmar_senha:
            lista_erros.append('As senhas não coincidem.')

        if lista_erros:
            for erro in lista_erros:
                messages.error(request, erro)
            return render(request, 'aulaweb/signup.html')

        if Usuario.objects.filter(login=login).exists():
            messages.error(request, 'Este nome de usuário já está em uso.')
            return render(request, 'aulaweb/signup.html')

        data_nascimento = data_nascimento_str if data_nascimento_str else None
        semestre = int(semestre_str) if semestre_str else None

        try:
            novo_usuario = Usuario(
                nome=nome,
                instituicao=instituicao,
                login=login,
                senha=senha,
                perfil=perfil_selecionado,
                email=email,
                data_nascimento=data_nascimento,
                endereco=endereco,
                curso=curso,
                semestre=semestre,
                ativo=False 
            )
            novo_usuario.save()

            registrar_log(novo_usuario, "Criação de Novo Usuário", f"Nome: {novo_usuario.nome}")

            # 6. Enviar E-mail de Ativação
            link_ativacao = request.build_absolute_uri(
                reverse('ativar_conta', args=[str(novo_usuario.token)])
            )

            assunto = 'Ative a sua conta no Eventify'
            mensagem = f"""
            Olá, {nome}!

            Bem-vindo ao Eventify. Seu perfil foi criado como: {perfil_selecionado.upper()}.
            Para ativar sua conta, clique no link abaixo:

            {link_ativacao}
            """
            
            send_mail(
                assunto,
                mensagem,
                'sistema@eventify.com',
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Cadastro realizado! Verifique seu e-mail (ou terminal) para ativar a conta.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {e}')
            return render(request, 'aulaweb/signup.html')

    return render(request, 'aulaweb/signup.html')


def eventos(request):
    todos_os_eventos = Evento.objects.all().order_by('data_inicio')
    usuario_logado = None
    inscricoes_ids = []

    if 'usuario_id' in request.session:
        try:
            usuario_logado = Usuario.objects.get(id=request.session['usuario_id'])
            inscricoes_ids = Inscricao.objects.filter(usuario=usuario_logado).values_list('evento_id', flat=True)
        except Usuario.DoesNotExist:
            pass 
    
    contexto = {
        'eventos_lista': todos_os_eventos,
        'usuario': usuario_logado,
        'inscricoes_ids': inscricoes_ids
    }
    return render(request, 'aulaweb/eventos.html', contexto)

def criar_evento(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    try:
        usuario_logado = Usuario.objects.get(id=request.session['usuario_id'])
    except Usuario.DoesNotExist:
        return redirect('login')

    if usuario_logado.perfil != 'organizador':
        messages.error(request, 'Acesso negado. Apenas organizadores podem criar eventos.')
        return redirect('eventos') 

    professores = Usuario.objects.filter(perfil='professor')

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        horario = request.POST.get('horario')
        local = request.POST.get('local')
        qtd_participantes_str = request.POST.get('qtd_participantes')
        banner_arquivo = request.FILES.get('banner') 
        responsavel_id = request.POST.get('responsavel')

        if not all([tipo, data_inicio, data_fim, horario, local, qtd_participantes_str]):
            messages.error(request, 'Todos os campos de texto são obrigatórios.')
            return render(request, 'aulaweb/criar_evento.html', {'professores': professores})

        if banner_arquivo:
            extensao = os.path.splitext(banner_arquivo.name)[1].lower()
            if extensao not in ['.jpg', '.jpeg', '.png', '.webp']:
                messages.error(request, 'O banner deve ser uma imagem (JPG, PNG ou WEBP).')
                return render(request, 'aulaweb/criar_evento.html', {'professores': professores})

        try:
            qtd_participantes = int(qtd_participantes_str)
            if qtd_participantes <= 0:
                 raise ValueError("A quantidade deve ser positiva.")

            data_inicio_dt = timezone.datetime.strptime(data_inicio, '%Y-%m-%d').date()
            if data_inicio_dt < timezone.now().date():
                 messages.error(request, 'A data de início não pode ser no passado.')
                 return render(request, 'aulaweb/criar_evento.html', {'professores': professores})

            novo_evento = Evento(
                tipo=tipo,
                data_inicio=data_inicio,
                data_fim=data_fim,
                horario=horario,
                local=local,
                qtd_participantes=qtd_participantes,
                organizador=usuario_logado,
                banner=banner_arquivo 
            )
            
            if responsavel_id:
                novo_evento.responsavel_id = responsavel_id

            novo_evento.save()

            registrar_log(usuario_logado, "Criação de Evento", f"Evento: {novo_evento.tipo}")

            messages.success(request, 'Evento criado com sucesso!')
            return redirect('eventos')

        except ValueError:
            messages.error(request, 'Quantidade de participantes inválida.')
        except Exception as e:
            messages.error(request, f'Erro ao salvar: {e}')

    return render(request, 'aulaweb/criar_evento.html', {'professores': professores})


def editar_evento(request, evento_id):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario_logado = Usuario.objects.get(id=request.session['usuario_id'])
    

    evento = get_object_or_404(Evento, id=evento_id)

    if usuario_logado.perfil != 'organizador' or evento.organizador.id != usuario_logado.id:
        messages.error(request, 'Você não tem permissão para editar este evento.')
        return redirect('eventos')

    professores = Usuario.objects.filter(perfil='professor')

    if request.method == 'POST':
        try:
            evento.tipo = request.POST.get('tipo')
            evento.local = request.POST.get('local')
            evento.qtd_participantes = int(request.POST.get('qtd_participantes'))
            evento.data_inicio = request.POST.get('data_inicio')
            evento.data_fim = request.POST.get('data_fim')
            evento.horario = request.POST.get('horario')

            resp_id = request.POST.get('responsavel')
            if resp_id:
                evento.responsavel_id = resp_id
            
            if 'banner' in request.FILES:
                banner_arquivo = request.FILES['banner']
                extensao = os.path.splitext(banner_arquivo.name)[1].lower()
                if extensao in ['.jpg', '.jpeg', '.png', '.webp']:
                    evento.banner = banner_arquivo
            
            evento.save()
            
            registrar_log(usuario_logado, "Edição de Evento", f"Evento ID {evento.id} editado.")
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('eventos')

        except Exception as e:
            messages.error(request, f'Erro ao atualizar evento: {e}')


    return render(request, 'aulaweb/editar_evento.html', {
        'evento': evento,
        'professores': professores
    })

def inscrever_evento(request, evento_id):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario_id = request.session.get('usuario_id')
    usuario_logado = get_object_or_404(Usuario, id=usuario_id)
    evento = get_object_or_404(Evento, id=evento_id)
    pagina_anterior = request.META.get('HTTP_REFERER', 'index')

    if usuario_logado.perfil == 'organizador':
        messages.error(request, 'Organizadores não podem se inscrever em eventos.')
        return redirect(pagina_anterior) 

    if Inscricao.objects.filter(usuario=usuario_logado, evento=evento).exists():
        messages.warning(request, 'Você já está inscrito neste evento!')
        return redirect(pagina_anterior)

    nova_inscricao = Inscricao(usuario=usuario_logado, evento=evento)
    nova_inscricao.save()

    registrar_log(usuario_logado, "Inscrição em Evento", f"Evento ID: {evento.id}")

    messages.success(request, 'Inscrição realizada com sucesso!')
    return redirect(pagina_anterior)

def cancelar_inscricao(request, evento_id):
    if 'usuario_id' not in request.session:
        return redirect('login')
        
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    evento = get_object_or_404(Evento, id=evento_id)
    
    inscricao = get_object_or_404(Inscricao, usuario=usuario, evento=evento)
    
    if Certificado.objects.filter(inscricao=inscricao).exists():
        messages.error(request, 'Não é possível cancelar um evento que já possui certificado emitido!')
        return redirect('meuseventos')

    inscricao.delete()
    messages.success(request, 'Inscrição cancelada com sucesso.')
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
            'usuario': usuario_logado
        }
        return render(request, 'aulaweb/certificados.html', contexto)
        
    except Usuario.DoesNotExist:
        if 'usuario_id' in request.session:
            del request.session['usuario_id']
        messages.error(request, 'Usuário não encontrado. Faça login novamente.')
        return redirect('login')

def meuseventos(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    try:
        usuario_logado = Usuario.objects.get(id=request.session['usuario_id'])
        
        inscricoes_brutas = Inscricao.objects.filter(
            usuario=usuario_logado
        ).select_related('evento').order_by('evento__data_inicio')
        
        lista_blindada = []
        for inscricao in inscricoes_brutas:
            tem_cert = Certificado.objects.filter(inscricao=inscricao).exists()
            item = {
                'dados': inscricao,
                'ja_emitiu': tem_cert
            }
            lista_blindada.append(item)
        
        contexto = {
            'lista_eventos': lista_blindada,
            'hoje': timezone.now().date(),
            'usuario': usuario_logado
        }
        return render(request, 'aulaweb/meuseventos.html', contexto)
        
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

        registrar_log(usuario_logado, "Geração de Certificado", f"Evento: {evento.tipo}")
        
        messages.success(request, f'Certificado do evento "{evento.tipo}" gerado com sucesso!')
        return redirect('meuseventos') 

    except (Usuario.DoesNotExist, Evento.DoesNotExist, Inscricao.DoesNotExist):
        messages.error(request, 'Ocorreu um erro: inscrição não encontrada.')
        return redirect('meuseventos')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado: {e}')
        return redirect('meuseventos')


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

def editar_perfil(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario_id = request.session['usuario_id']
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        try:
            usuario.nome = request.POST.get('nome')
            usuario.email = request.POST.get('email')
            usuario.telefone = request.POST.get('telefone')
            usuario.endereco = request.POST.get('endereco')
            usuario.curso = request.POST.get('curso')
            usuario.instituicao = request.POST.get('instituicao')
            data_nasc = request.POST.get('data_nascimento')
            if data_nasc:
                usuario.data_nascimento = data_nasc
            semestre = request.POST.get('semestre')
            if semestre:
                usuario.semestre = int(semestre)
            
            usuario.save()

            registrar_log(usuario, "Edição de Perfil", "Usuário atualizou seus dados cadastrais")

            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')

        except Exception as e:
            messages.error(request, f'Erro ao atualizar perfil: {e}')

    return render(request, 'aulaweb/editar_perfil.html', {'usuario': usuario})  

def ativar_conta(request, token):
    try:
        usuario = Usuario.objects.get(token=token)
        
        if usuario.ativo:
            messages.warning(request, 'Esta conta já foi ativada anteriormente.')
        else:
            usuario.ativo = True
            usuario.save()
            messages.success(request, 'Conta ativada com sucesso! Agora pode fazer login.')
            
    except Usuario.DoesNotExist:
        messages.error(request, 'Link de ativação inválido ou expirado.')
    except Exception as e:
        messages.error(request, 'Erro ao ativar conta.')
        
    return redirect('login')

def logs_auditoria(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    
    usuario_logado = Usuario.objects.get(id=request.session['usuario_id'])
    
    if usuario_logado.perfil != 'organizador':
        messages.error(request, 'Acesso restrito a organizadores.')
        return redirect('index')

    logs = LogAuditoria.objects.all().order_by('-data_hora')

    data_filtro = request.GET.get('data')
    usuario_filtro = request.GET.get('usuario')

    if data_filtro:
        logs = logs.filter(data_hora__date=data_filtro)
    
    if usuario_filtro:
        logs = logs.filter(usuario__nome__icontains=usuario_filtro) | logs.filter(usuario__email__icontains=usuario_filtro)

    return render(request, 'aulaweb/logs.html', {
        'logs': logs,
        'usuario': usuario_logado
    })