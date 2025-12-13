# Eventify/Projeto/test_api.py
"""
Script de teste para a API REST do Eventify
Execute: python test_api.py
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000/api"
COLORS = {
    'GREEN': '\033[92m',
    'RED': '\033[91m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'END': '\033[0m'
}

def print_success(message):
    print(f"{COLORS['GREEN']}✓ {message}{COLORS['END']}")

def print_error(message):
    print(f"{COLORS['RED']}✗ {message}{COLORS['END']}")

def print_info(message):
    print(f"{COLORS['BLUE']}ℹ {message}{COLORS['END']}")

def print_warning(message):
    print(f"{COLORS['YELLOW']}⚠ {message}{COLORS['END']}")

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

class EventifyAPITester:
    def __init__(self):
        self.token = None
        self.user_info = None
        
    def test_login(self, login, senha):
        """Testa o endpoint de login"""
        print("\n" + "="*60)
        print_info("Testando Login...")
        print("="*60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/login/",
                json={"login": login, "senha": senha}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['token']
                self.user_info = data
                print_success(f"Login realizado com sucesso!")
                print_info(f"Usuário: {data['nome']} ({data['perfil']})")
                print_info(f"Token: {self.token[:20]}...")
                return True
            else:
                print_error(f"Falha no login: {response.status_code}")
                print_json(response.json())
                return False
                
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False
    
    def test_listar_eventos(self):
        """Testa a listagem de eventos"""
        print("\n" + "="*60)
        print_info("Testando Listagem de Eventos...")
        print("="*60)
        
        if not self.token:
            print_error("Você precisa fazer login primeiro!")
            return None
        
        try:
            headers = {"Authorization": f"Token {self.token}"}
            response = requests.get(f"{BASE_URL}/eventos/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Encontrados {data['count']} evento(s)")
                
                for i, evento in enumerate(data['eventos'], 1):
                    print(f"\n{i}. {evento['tipo']}")
                    print(f"   📍 Local: {evento['local']}")
                    print(f"   📅 Data: {evento['data_inicio']} a {evento['data_fim']}")
                    print(f"   ⏰ Horário: {evento['horario']}")
                    print(f"   👥 Vagas: {evento['qtd_participantes']}")
                    print(f"   👤 Organizador: {evento['organizador_nome']}")
                
                return data['eventos']
            else:
                print_error(f"Erro: {response.status_code}")
                print_json(response.json())
                return None
                
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return None
    
    def test_detalhe_evento(self, evento_id):
        """Testa os detalhes de um evento específico"""
        print("\n" + "="*60)
        print_info(f"Testando Detalhes do Evento ID {evento_id}...")
        print("="*60)
        
        if not self.token:
            print_error("Você precisa fazer login primeiro!")
            return None
        
        try:
            headers = {"Authorization": f"Token {self.token}"}
            response = requests.get(
                f"{BASE_URL}/eventos/{evento_id}/",
                headers=headers
            )
            
            if response.status_code == 200:
                evento = response.json()
                print_success("Detalhes obtidos com sucesso!")
                print(f"\n📌 {evento['tipo']}")
                print(f"   📍 Local: {evento['local']}")
                print(f"   📅 Período: {evento['data_inicio']} a {evento['data_fim']}")
                print(f"   ⏰ Horário: {evento['horario']}")
                print(f"   👥 Vagas: {evento['qtd_participantes']}")
                print(f"   👤 Organizador: {evento['organizador_nome']}")
                print(f"   🏢 Instituição: {evento['organizador_instituicao']}")
                
                if evento.get('usuario_inscrito'):
                    print_success("   ✓ Você está inscrito neste evento")
                else:
                    print_info("   ○ Você ainda não está inscrito")
                
                return evento
            else:
                print_error(f"Erro: {response.status_code}")
                print_json(response.json())
                return None
                
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return None
    
    def test_inscrever_evento(self, evento_id):
        """Testa a inscrição em um evento"""
        print("\n" + "="*60)
        print_info(f"Testando Inscrição no Evento ID {evento_id}...")
        print("="*60)
        
        if not self.token:
            print_error("Você precisa fazer login primeiro!")
            return False
        
        try:
            headers = {"Authorization": f"Token {self.token}"}
            response = requests.post(
                f"{BASE_URL}/inscricoes/",
                headers=headers,
                json={"evento_id": evento_id}
            )
            
            if response.status_code == 201:
                data = response.json()
                print_success(data['message'])
                print_info(f"ID da Inscrição: {data['inscricao']['id']}")
                print_info(f"Data: {data['inscricao']['data_inscricao']}")
                return True
            elif response.status_code == 400:
                print_warning(response.json()['error'])
                return False
            else:
                print_error(f"Erro: {response.status_code}")
                print_json(response.json())
                return False
                
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False
    
    def test_minhas_inscricoes(self):
        """Testa a listagem de inscrições do usuário"""
        print("\n" + "="*60)
        print_info("Testando Minhas Inscrições...")
        print("="*60)
        
        if not self.token:
            print_error("Você precisa fazer login primeiro!")
            return None
        
        try:
            headers = {"Authorization": f"Token {self.token}"}
            response = requests.get(
                f"{BASE_URL}/minhas-inscricoes/",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Você possui {data['count']} inscrição(ões)")
                
                if data['count'] > 0:
                    for i, inscricao in enumerate(data['inscricoes'], 1):
                        print(f"\n{i}. {inscricao['evento_tipo']}")
                        print(f"   📍 Local: {inscricao['evento_local']}")
                        print(f"   📅 Inscrito em: {inscricao['data_inscricao']}")
                        print(f"   🔖 ID: {inscricao['id']}")
                else:
                    print_info("Você ainda não possui inscrições")
                
                return data['inscricoes']
            else:
                print_error(f"Erro: {response.status_code}")
                print_json(response.json())
                return None
                
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return None
    
    def test_cancelar_inscricao(self, evento_id):
        """Testa o cancelamento de uma inscrição"""
        print("\n" + "="*60)
        print_info(f"Testando Cancelamento da Inscrição no Evento ID {evento_id}...")
        print("="*60)
        
        if not self.token:
            print_error("Você precisa fazer login primeiro!")
            return False
        
        try:
            headers = {"Authorization": f"Token {self.token}"}
            response = requests.delete(
                f"{BASE_URL}/inscricoes/{evento_id}/",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(data['message'])
                return True
            elif response.status_code == 404:
                print_warning(response.json()['error'])
                return False
            else:
                print_error(f"Erro: {response.status_code}")
                print_json(response.json())
                return False
                
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False
    
    def test_logout(self):
        """Testa o logout"""
        print("\n" + "="*60)
        print_info("Testando Logout...")
        print("="*60)
        
        if not self.token:
            print_error("Você não está logado!")
            return False
        
        try:
            headers = {"Authorization": f"Token {self.token}"}
            response = requests.post(f"{BASE_URL}/logout/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print_success(data['message'])
                self.token = None
                self.user_info = None
                return True
            else:
                print_error(f"Erro: {response.status_code}")
                print_json(response.json())
                return False
                
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False


def main():
    """Função principal de testes"""
    print("\n" + "="*60)
    print(f"{COLORS['BLUE']}🚀 EVENTIFY API - TESTE AUTOMATIZADO{COLORS['END']}")
    print("="*60)
    
    # Inicializar o testador
    tester = EventifyAPITester()
    
    # Solicitar credenciais
    print_info("\nDigite suas credenciais de teste:")
    login = input("Login: ")
    senha = input("Senha: ")
    
    # 1. Teste de Login
    if not tester.test_login(login, senha):
        print_error("\n❌ Falha no login. Encerrando testes.")
        return
    
    # 2. Teste de Listagem de Eventos
    eventos = tester.test_listar_eventos()
    
    # 3. Teste de Detalhes de Evento
    if eventos and len(eventos) > 0:
        primeiro_evento = eventos[0]
        tester.test_detalhe_evento(primeiro_evento['id'])
        
        # 4. Teste de Inscrição
        tester.test_inscrever_evento(primeiro_evento['id'])
        
        # 5. Teste de Minhas Inscrições
        tester.test_minhas_inscricoes()
        
        # 6. Teste de Cancelamento (opcional)
        print_info("\nDeseja testar o cancelamento de inscrição? (s/n)")
        if input().lower() == 's':
            tester.test_cancelar_inscricao(primeiro_evento['id'])
            tester.test_minhas_inscricoes()
    
    # 7. Teste de Logout
    tester.test_logout()
    
    print("\n" + "="*60)
    print_success("✅ Testes concluídos!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()