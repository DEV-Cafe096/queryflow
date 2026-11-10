<h1 align="center">
  <img src="https://img.shields.io/static/v1?label=Projeto&message=QueryFlow&color=1E90FF&style=flat-square&logo= iconography&logoColor=white"/>
  <img src="https://img.shields.io/static/v1?label=Desenvolvido%20por&message=Michel%20Correa&color=7159c1&style=flat-square&logo=ghost"/>
</h1>

<h3 align="center">QueryFlow: Seu Assistente Inteligente para Consultas SQL</h3>
<p align="center">Transforme linguagem natural em consultas SQL, em qualquer banco de dados, com o poder da IA!</p>

## 🚀 Visão Geral

QueryFlow é uma aplicação web que traduz perguntas em português para SQL usando o Gemini, e executa a consulta no banco de dados conectado. A partir desta versão, o projeto foi reescrito como uma aplicação web moderna (Next.js + FastAPI) com suporte a **qualquer banco de dados compatível com SQLAlchemy** — não apenas MySQL.

## ✨ Funcionalidades

- **Interface web em Next.js**, com chat de perguntas, SQL gerado editável (com realce de sintaxe), tabela de resultados paginável e exportação em CSV.
- **Qualquer banco de dados**: PostgreSQL, MySQL, SQLite, SQL Server ou qualquer outro dialeto suportado pelo SQLAlchemy (via URL de conexão bruta), tudo pela mesma interface — basta cadastrar a conexão.
- **Geração de SQL com Gemini**, com o dialeto de destino informado ao modelo (a sintaxe muda entre bancos, ex. `LIMIT` vs `TOP`).
- **Guardrails de segurança** aplicados no backend (não apenas pedidos por prompt): por padrão, apenas `SELECT` é permitido; `INSERT`/`UPDATE`/`DELETE` só funcionam se a conexão tiver "permitir escrita" habilitado, e `UPDATE`/`DELETE` sempre exigem `WHERE`. Resultados têm limite de linhas e timeout de execução.
- **Histórico e feedback** de perguntas/consultas, armazenados localmente (não na base de dados do cliente).
- **Credenciais cifradas** localmente quando uma conexão é salva.

## 🏛️ Arquitetura

```
frontend/   Next.js (App Router) + TypeScript + Tailwind + shadcn/ui
backend/    FastAPI + SQLAlchemy (multi-dialeto) + Gemini
banco_de_dados/  Gerador de dados fictícios (CSV) para popular um banco de demonstração
```

1. O usuário faz uma pergunta em português na interface web.
2. O backend lê o schema do banco conectado via `sqlalchemy.inspect()` (funciona com qualquer dialeto).
3. Pergunta + schema + dialeto de destino são enviados ao Gemini, que retorna o SQL.
4. O SQL passa pelos guardrails de segurança antes de ser executado.
5. Resultado é exibido na interface, com opção de editar o SQL manualmente antes de rodar novamente.

## 🛠️ Como rodar localmente

### Pré-requisitos

- Python 3.11+
- Node.js 20+
- Uma chave de API do [Google AI Studio](https://aistudio.google.com/) (Gemini)

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate   # ou: uv venv && source venv/bin/activate
pip install -r requirements.txt                    # ou: uv pip install -r requirements.txt --python venv/bin/python

cp .env.example .env
# edite .env e preencha GEMINI_API_KEY e APP_SECRET_KEY
# gere uma APP_SECRET_KEY com: python -c "import secrets; print(secrets.token_urlsafe(32))"

# opcional: cria um banco SQLite de demonstração a partir dos CSVs em banco_de_dados/datasets/
python scripts/seed_sqlite_demo.py

uvicorn app.main:app --reload --port 8000
```

A API sobe em `http://localhost:8000` (docs interativas em `/docs`).

### Frontend

```bash
cd frontend
cp .env.example .env.local   # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm install
npm run dev
```

Acesse `http://localhost:3000`, vá em **Conexões** e cadastre seu banco (ou aponte para `./demo.db` com dialeto SQLite, se você rodou o seed acima).

### Populando um MySQL real (opcional)

`banco_de_dados/scripts/create_table.py` continua disponível para quem quiser popular um MySQL com o mesmo conjunto de dados fictícios (usa as variáveis `MYSQL_*` do `.env` daquele diretório).

## 🔒 Notas de segurança

- Conexões novas nascem **somente leitura**; escrita precisa ser habilitada explicitamente por conexão.
- A senha do banco nunca é enviada ao Gemini — apenas nomes/tipos de tabelas e colunas.
- Histórico e credenciais salvas ficam num SQLite local do próprio app (`backend/app_store.db`), nunca dentro do banco de dados do cliente.
