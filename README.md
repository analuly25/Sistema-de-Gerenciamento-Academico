# Eventify - Sistema de Gerenciamento Acadêmico

O **Eventify** é uma aplicação web desenvolvida em Django para a gestão completa de eventos acadêmicos. O sistema permite que organizadores criem e administrem eventos, enquanto alunos e professores podem se inscrever, acompanhar suas participações e emitir certificados automaticamente. O projeto também conta com uma API REST integrada.

---

## Integrantes 

Ana Luiza Gomes 
Bárbara Parente
Beatriz Espindola

---

## 📋 Índice

1. [Funcionalidades](#-funcionalidades)
2. [Regras de Negócio](#-regras-de-negócio)
3. [Tecnologias Utilizadas](#-tecnologias-utilizadas)
4. [Pré-requisitos](#-pré-requisitos)
5. [Instalação e Configuração](#-instalação-e-configuração)
6. [Como Rodar o Projeto](#-como-rodar-o-projeto)
7. [Documentação da API](#-documentação-da-api)
8. [Testes](#-testes)

---

## 🚀 Funcionalidades

* **Autenticação e Perfis:** Login e Cadastro de usuários com perfis distintos (Aluno, Professor, Organizador).
* **Gestão de Eventos:** Criação e edição de eventos (apenas Organizadores), incluindo upload de banners.
* **Inscrições:** Sistema de inscrição e cancelamento com controle automático de vagas.
* **Certificados:** Emissão de certificados após a conclusão do evento.
* **Auditoria:** Logs automáticos de ações críticas (login, criação de eventos, etc.) para segurança.
* **API REST:** Endpoints para integração externa (Login, Listagem, Inscrição).
* **Dashboard:** Visualização de "Meus Eventos" e calendário acadêmico.

---

## ⚖️ Regras de Negócio

O sistema implementa as seguintes regras para garantir a integridade dos dados:

### 1. Permissões de Usuário
* **Aluno/Professor:** Podem visualizar eventos, se inscrever, cancelar inscrições e gerar certificados.
* **Organizador:** Pode criar e editar eventos e visualizar logs de auditoria.
* **Restrição de Inscrição:** Organizadores **não** podem se inscrever em eventos (bloqueio via interface e API).

### 2. Eventos e Vagas
* A data de início do evento não pode ser anterior à data atual.
* A quantidade de participantes deve ser um número positivo.
* Inscrições são bloqueadas se o evento atingir a capacidade máxima (lotado).

### 3. Inscrições
* Um usuário não pode se inscrever duas vezes no mesmo evento.
* O cancelamento da inscrição é permitido, exceto se o certificado já tiver sido emitido.

### 4. Certificados
* O certificado só fica disponível para emissão se a data atual for posterior à `data_fim` do evento.
* O sistema impede a emissão duplicada de certificados para a mesma inscrição.

### 5. API e Segurança
* **Rate Limiting:**
    * Consultas de eventos: Limite de 20 requisições/dia por usuário.
    * Inscrições: Limite de 50 requisições/dia por usuário.

---

## 🛠 Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Framework Web:** Django 5.x
* **API:** Django REST Framework (DRF)
* **Banco de Dados:** SQLite (Padrão do projeto)
* **Autenticação:** Django Auth & Token Authentication
* **Frontend:** HTML5, CSS3, JavaScript (jQuery)

---

## ⚙️ Pré-requisitos

Certifique-se de ter instalado em sua máquina:
* [Python](https://www.python.org/downloads/) (versão 3.10 ou superior)
* [Git](https://git-scm.com/)

---

## 📥 Instalação e Configuração

Siga os passos abaixo para configurar o ambiente de desenvolvimento:

1.  **Clonar o repositório:**
    ```bash
    git clone [https://github.com/analuly25/sistema-de-gerenciamento-academico.git](https://github.com/analuly25/sistema-de-gerenciamento-academico.git)
    cd sistema-de-gerenciamento-academico/Projeto
    ```

2.  **Criar um Ambiente Virtual:**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar as Dependências:**
    O projeto utiliza pacotes adicionais como DRF e Pillow. Instale-os com:
    ```bash
    pip install django djangorestframework pillow requests
    ```

4.  **Aplicar as Migrações do Banco de Dados:**
    ```bash
    python manage.py migrate
    ```

5.  **Popular o Banco de Dados (Opcional - Recomendado):**
    O projeto possui um comando personalizado para criar dados de teste automaticamente.
    ```bash
    python manage.py seed
    ```
    Isso criará os seguintes usuários para teste:
    * **Organizador:** `organizador@sgea.com` / Senha: `Admin@123`
    * **Aluno:** `aluno@sgea.com` / Senha: `Aluno@123`
    * **Professor:** `professor@sgea.com` / Senha: `Professor@123`

---

## ▶️ Como Rodar o Projeto

1.  **Iniciar o Servidor:**
    Com o ambiente virtual ativo, execute:
    ```bash
    python manage.py runserver
    ```

2.  **Acessar a Aplicação:**
    Abra seu navegador e acesse:
    `http://127.0.0.1:8000/`

---

## 🔌 Documentação da API

O projeto expõe uma API RESTful acessível em `http://127.0.0.1:8000/api/`.

### Principais Endpoints:

| Método | Endpoint | Descrição | Autenticação |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/login/` | Realiza login e retorna o Token | Pública |
| `POST` | `/api/logout/` | Revoga o Token do usuário | Token |
| `GET` | `/api/eventos/` | Lista todos os eventos | Token |
| `GET` | `/api/eventos/<id>/` | Detalhes de um evento | Token |
| `POST` | `/api/inscricoes/` | Inscreve o usuário em um evento | Token |
| `GET` | `/api/minhas-inscricoes/` | Lista inscrições do usuário | Token |
| `DELETE`| `/api/inscricoes/<id>/` | Cancela uma inscrição | Token |

*Nota: Requisições autenticadas devem enviar o cabeçalho `Authorization: Token <seu_token>`.*

---

## 🧪 Testes

O projeto inclui um script automatizado para testar os endpoints da API.

Para rodar o teste da API:
```bash
python test_api.py
