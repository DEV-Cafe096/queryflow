<h1 align="center">
  <img src="https://img.shields.io/static/v1?label=Projeto&message=QueryFlow&color=1E90FF&style=flat-square&logo= iconography&logoColor=white"/>
  <img src="https://img.shields.io/static/v1?label=Desenvolvido%20por&message=Michel%20Correa&color=7159c1&style=flat-square&logo=ghost"/>
</h1>

<h3 align="center">QueryFlow: Seu Assistente Inteligente para Consultas SQL</h3>
<p align="center">Transforme linguagem natural em consultas SQL com o poder da IA!</p>
<p align="center">=================================</p>

## 🚀 Visão Geral do Projeto

O QueryFlow é uma aplicação web interativa que demonstra o poder dos agentes de Inteligência Artificial (IA) na tradução de perguntas em linguagem natural para consultas SQL. Utilizando a API do Google Gemini, o QueryFlow permite que usuários, mesmo sem conhecimento técnico em SQL, interajam com um banco de dados MySQL para obter informações valiosas.

Este projeto foi desenvolvido como uma evolução, explorando como modelos de linguagem avançados podem facilitar o acesso e a manipulação de dados.

## ✨ Funcionalidades

*   **Interface Web Intuitiva:** Desenvolvida com Streamlit para uma experiência de usuário amigável.
*   **Tradução de Linguagem Natural para SQL:** Utilize a API do Google Gemini para converter suas perguntas em queries SQL.
*   **Conexão com Banco de Dados MySQL:** Interaja diretamente com seu banco de dados MySQL local ou remoto.
*   **Visualização de Resultados:** Veja os resultados das suas consultas diretamente na aplicação.
*   **Configuração Segura:** Insira suas credenciais da API e do banco de dados através de uma interface segura.
*   **Histórico de Interações (Opcional):** Capacidade de salvar perguntas, queries geradas e feedback para futuras análises (requer configuração da tabela de histórico).

## 🏛️ Arquitetura Simplificada

A arquitetura do queryflow envolve:

1.  **Interface do Usuário (Streamlit):** O usuário interage com a aplicação web, inserindo perguntas e configurando conexões.
2.  **Agente de IA (Google Gemini):** A pergunta em linguagem natural, juntamente com o esquema do banco de dados, é enviada para a API do Gemini.
3.  **Geração de SQL:** O Gemini processa a entrada e retorna uma query SQL correspondente.
4.  **Banco de Dados (MySQL):** A query SQL gerada é executada no banco de dados MySQL configurado pelo usuário.
5.  **Exibição de Resultados:** Os dados retornados pelo banco são exibidos na interface Streamlit.

*(Você pode adicionar uma nova imagem de arquitetura aqui se desejar, mostrando o fluxo com Streamlit e Gemini)*
<!-- ![delta](img/nova_arquitetura_QueryFlow.png) -->

## 🛠️ Pré-requisitos e Configuração

Antes de começar, certifique-se de que você tem o seguinte:

1.  **Python 3.8+**
2.  **Servidor MySQL:** Instalado e rodando (localmente ou acessível remotamente).
3.  **Chave de API do Google Gemini:**
    *   Obtenha sua chave no [Google AI Studio](https://aistudio.google.com/).
4.  **Git** (para clonar o repositório, se aplicável).

### Passos para Instalação e Configuração:

1.  **Clone o Repositório (se você estiver obtendo o código de um repositório git):**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO_AQUI]
    cd QueryFlow # ou o nome da pasta do projeto
    ```

2.  **Crie e Ative um Ambiente Virtual Python (Recomendado):**
    ```bash
    python -m venv venv
    # No Windows:
    # venv\Scripts\activate
    # No macOS/Linux:
    # source venv/bin/activate
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Certifique-se de que seu `requirements.txt` está atualizado com `streamlit`, `google-generativeai`, `mysql-connector-python`, `python-dotenv`)*

4.  **Configure as Variáveis de Ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto e adicione suas credenciais:
    ```env
    GEMINI_API_KEY=SUA_CHAVE_API_GEMINI_AQUI
    MYSQL_HOST=localhost
    MYSQL_USER=seu_usuario_mysql
    MYSQL_PASSWORD=sua_senha_mysql
    MYSQL_DB=QueryFlow # Ou o nome do seu banco de dados
    GEMINI_MODEL_NAME=gemini-1.5-flash-latest # Modelo Gemini padrão
    ```