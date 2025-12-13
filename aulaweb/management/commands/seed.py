from django.core.management.base import BaseCommand
from aulaweb.models import Usuario

class Command(BaseCommand):
    help = 'Carga inicial de dados (Seeding) para testes e demonstração'

    def handle(self, *args, **kwargs):
        # Lista de usuários para criar
        usuarios_para_criar = [
            {
                'nome': 'Organizador Demo',
                'login': 'organizador@sgea.com',
                'senha': 'Admin@123',
                'perfil': 'organizador',
                'instituicao': 'SGEA Oficial',
                'email': 'organizador@sgea.com'
            },
            {
                'nome': 'Aluno Demo',
                'login': 'aluno@sgea.com',
                'senha': 'Aluno@123',
                'perfil': 'aluno',
                'instituicao': 'Universidade Exemplo',
                'email': 'aluno@sgea.com'
            },
            {
                'nome': 'Professor Demo',
                'login': 'professor@sgea.com',
                'senha': 'Professor@123',
                'perfil': 'professor',
                'instituicao': 'Instituto Federal',
                'email': 'professor@sgea.com'
            },
        ]

        self.stdout.write('Iniciando o seeding de dados...')

        for dados in usuarios_para_criar:
            # Verifica se o login já existe para evitar erro de duplicidade
            if not Usuario.objects.filter(login=dados['login']).exists():
                Usuario.objects.create(
                    nome=dados['nome'],
                    login=dados['login'],
                    senha=dados['senha'],
                    perfil=dados['perfil'],
                    instituicao=dados['instituicao'],
                    email=dados['email'],
                    ativo=True  # Cria o usuário já ativo para logar direto
                )
                self.stdout.write(self.style.SUCCESS(f"Usuário criado: {dados['login']} ({dados['perfil']})"))
            else:
                self.stdout.write(self.style.WARNING(f"Usuário já existe: {dados['login']}"))

        self.stdout.write(self.style.SUCCESS('Carga de dados concluída com sucesso!'))