from django.db import models
import uuid

# ===============================

# Usuário

# ===============================

class Usuario(models.Model):
    ativo = models.BooleanField(default=False, db_column='ativo')
    token = models.UUIDField(default=uuid.uuid4, editable=False, db_column='token')
    
    PERFIL_CHOICES = [

        ('aluno', 'Aluno'),

        ('professor', 'Professor'),

        ('organizador', 'Organizador'),

    ]


    nome = models.CharField(max_length=100, db_column='nome')
    
    telefone = models.CharField(max_length=20, db_column='telefone', null=True, blank=True)

    instituicao = models.CharField(max_length=100, blank=True, null=True, db_column='instituicao')

    login = models.CharField(max_length=50, unique=True, db_column='login')

    senha = models.CharField(max_length=255, db_column='senha')

    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES, db_column='perfil')

    # ===============================
    # NOVOS CAMPOS ADICIONADOS
    # ===============================
    data_nascimento = models.DateField(
        db_column='data_nascimento', 
        null=True,  # O campo pode ser nulo no banco de dados
        blank=True  # O campo pode ser deixado em branco em formulários
    )
    
    endereco = models.CharField(
        max_length=255, 
        db_column='endereco', 
        null=True, 
        blank=True
    )
    
    email = models.EmailField(
        max_length=255, 
        db_column='email', 
        null=True, 
        blank=True
    )
    
    curso = models.CharField(
        max_length=100, 
        db_column='curso', 
        null=True, 
        blank=True
    )
    
    semestre = models.IntegerField(
        db_column='semestre', 
        null=True, 
        blank=True
    )

    @property
    def is_authenticated(self):
        """Retorna True para indicar ao Django que este utilizador está logado."""
        return True

    @property
    def is_anonymous(self):
        """Retorna False, pois usuários da base de dados não são anónimos."""
        return False

    class Meta:

        db_table = 'usuario'

        ordering = ['nome']

        verbose_name = 'Usuário'

        verbose_name_plural = 'Usuários'

 

    def __str__(self):

        return f"{self.nome} ({self.perfil})"

 

 

# ===============================

# Evento

# ===============================

class Evento(models.Model):

    tipo = models.CharField(max_length=50, db_column='tipo')

    banner = models.ImageField(upload_to='eventos_banners/', null=True, blank=True, db_column='banner')

    data_inicio = models.DateField(db_column='data_inicio')

    data_fim = models.DateField(db_column='data_fim')

    horario = models.TimeField(db_column='horario')

    local = models.CharField(max_length=100, db_column='local')

    qtd_participantes = models.IntegerField(db_column='qtd_participantes')

    responsavel = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos_responsavel')

    organizador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_organizador',
        related_name='eventos'
    )

    @property
    def vagas_restantes(self):
        return self.qtd_participantes - self.inscricoes.count()

    class Meta:

        db_table = 'evento'

        ordering = ['data_inicio']

        verbose_name = 'Evento'

        verbose_name_plural = 'Eventos'

 

    def __str__(self):

        return f"{self.tipo} - {self.local}"

 

# ===============================

# Inscrição

# ===============================

class Inscricao(models.Model):

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='inscricoes'
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        db_column='id_evento',
        related_name='inscricoes'
    )
    data_inscricao = models.DateTimeField(auto_now_add=True, db_column='data_inscricao')
    certificado_emitido = models.BooleanField(default=False)

 

    class Meta:

        db_table = 'inscricao'

        unique_together = ('usuario', 'evento')

        ordering = ['-data_inscricao']

        verbose_name = 'Inscrição'

        verbose_name_plural = 'Inscrições'

 

    def __str__(self):

        return f"{self.usuario.nome} → {self.evento.tipo}"

 

 

# ===============================

# Certificado

# ===============================

class Certificado(models.Model):

    inscricao = models.ForeignKey(
        Inscricao,
        on_delete=models.CASCADE,
        db_column='id_inscricao',
        related_name='certificados'
    )
    data_emissao = models.DateTimeField(auto_now_add=True, db_column='data_emissao')

 

    class Meta:

        db_table = 'certificado'

        ordering = ['-data_emissao']

        verbose_name = 'Certificado'

        verbose_name_plural = 'Certificados'

 

    def __str__(self):

        return f"Certificado de {self.inscricao.usuario.nome} - {self.inscricao.evento.tipo}"
    
class LogAuditoria(models.Model):
    # Quem fez a ação? (Pode ser null se for um erro de login, mas geralmente tem usuário)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Qual foi a ação? (Ex: "Criou Evento", "Gerou Certificado")
    acao = models.CharField(max_length=255)
    
    # Detalhes extras (Ex: "Nome do evento: Python Day")
    detalhes = models.TextField(blank=True, null=True)
    
    # Quando aconteceu?
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log: {self.acao} - {self.data_hora}"