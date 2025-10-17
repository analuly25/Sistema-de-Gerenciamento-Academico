# Eventify - Sistema de Gerenciamento Acadêmico

## 1. Descrição do Projeto

O **Eventify** é um sistema de gerenciamento acadêmico e de eventos, desenvolvido com a framework Python Django. A plataforma permite que utilizadores se registem, visualizem eventos disponíveis, se inscrevam e, após a conclusão, gerem os seus próprios certificados.

O sistema possui diferentes tipos de perfis de utilizador, nomeadamente `aluno` (o perfil padrão de registo), `professor` e `organizador`. Utilizadores com o perfil de `organizador` têm privilégios especiais, como a capacidade de criar e publicar novos eventos na plataforma.

## 2. Funcionalidades Principais

O sistema oferece um conjunto completo de funcionalidades para a gestão de eventos e participação dos utilizadores:

### Autenticação e Perfis
* **Registo (Sign up):** Permite que novos utilizadores (alunos) criem uma conta fornecendo dados como nome, login, senha, instituição e outros detalhes académicos (curso, semestre, etc.).
* **Login:** Sistema de autenticação para acesso à plataforma.
* **Logout:** Permite ao utilizador sair da sua sessão de forma segura.
* **Gestão de Perfil:** Uma página dedicada onde o utilizador pode visualizar os seus dados pessoais e académicos registados.

### Gestão de Eventos
* **Visualização de Eventos:** Uma página pública que lista todos os eventos futuros disponíveis, com detalhes como tipo, local e data.
* **Detalhes do Evento:** Funcionalidade na lista de eventos que permite expandir um cartão para ver mais detalhes (organizador, horário, vagas, etc.).
* **Criação de Eventos (Organizador):** Utilizadores com o perfil `organizador` têm acesso a um formulário para criar e publicar novos eventos no sistema.

### Inscrições e Certificados
* **Inscrição em Eventos:** Utilizadores logados podem inscrever-se nos eventos de seu interesse com um único clique.
* **Meus Eventos:** Uma página pessoal que lista todos os eventos em que o utilizador está atualmente inscrito.
* **Cancelamento de Inscrição:** O utilizador pode cancelar a sua inscrição num evento (desde que este ainda não tenha ocorrido).
* **Geração de Certificados:** Após a data de término de um evento, o utilizador pode gerar um certificado de participação.
* **Meus Certificados:** Uma galeria pessoal onde o utilizador pode visualizar todos os certificados que já emitiu.

## 3. Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias:

* **Backend:** Python 3 e Django Framework.
* **Base de Dados:** SQLite 3 (a base de dados padrão do Django, configurada em `settings.py`).
* **Frontend:**
    * HTML5 (para a estrutura das páginas).
    * CSS3 (para estilização, através do ficheiro `style.css`).
    * JavaScript (para interatividade, como o menu "hambúrguer" e a caixa de detalhes dos eventos).

## 4. Como Executar o Projeto

Para executar este projeto localmente, segue estes passos básicos (assumindo que tens o Python e o `pip` instalados):

1.  **Clonar o Repositório (ou descarregar os ficheiros)**
    ```bash
    # Se estiveres a usar o Git
    git clone [URL_DO_TEU_REPOSITORIO]
    cd [NOME_DA_PASTA_DO_PROJETO]
    ```

2.  **Criar um Ambiente Virtual (Recomendado)**
    ```bash
    python -m venv venv
    # No Windows
    .\venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instalar as Dependências**
    (É uma boa prática criar um ficheiro `requirements.txt` com as dependências, como o Django)
    ```bash
    pip install Django
    # Se tiveres um requirements.txt:
    # pip install -r requirements.txt
    ```

4.  **Aplicar as Migrações da Base de Dados**
    Isto irá criar o ficheiro `db.sqlite3` e definir as tabelas (`Usuario`, `Evento`, etc.).
    ```bash
    # Navega para a pasta que contém o manage.py
    cd Eventify/Projeto
    python manage.py migrate
    ```

5.  **Executar o Servidor de Desenvolvimento**
    ```bash
    python manage.py runserver
    ```

6.  **Aceder ao Projeto**
    Abre o teu navegador e visita [http://127.0.0.1:8000/](http://127.0.0.1:8000/) para ver a aplicação a funcionar.
