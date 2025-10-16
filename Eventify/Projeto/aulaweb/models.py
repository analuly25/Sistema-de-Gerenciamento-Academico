from django.db import models

# Create your models here.
# ===============================

# Usuário

# ===============================

class Usuario(models.Model):

    PERFIL_CHOICES = [

        ('aluno', 'Aluno'),

        ('professor', 'Professor'),

        ('organizador', 'Organizador'),

    ]

 

    nome = models.CharField(max_length=100, db_column='nome')
    
    # O campo 'telefone' foi removido daqui.

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

    data_inicio = models.DateField(db_column='data_inicio')

    data_fim = models.DateField(db_column='data_fim')

    horario = models.TimeField(db_column='horario')

    local = models.CharField(max_length=100, db_column='local')

    qtd_participantes = models.IntegerField(db_column='qtd_participantes')

    organizador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_organizador',
        related_name='eventos'
    )

 

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