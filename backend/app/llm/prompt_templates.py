import json

from app.models.schemas import Dialect

_DIALECT_LABEL = {
    Dialect.postgresql: "PostgreSQL",
    Dialect.mysql: "MySQL",
    Dialect.sqlite: "SQLite",
    Dialect.mssql: "SQL Server (T-SQL)",
    Dialect.other: "SQL padrão ANSI",
}

MODEL_ROLE = (
    "Você é um assistente que converte perguntas em linguagem natural (português) em "
    "consultas SQL. Gere APENAS a query SQL, sem explicações, sem markdown (nada de ```sql)."
)

RESTRICOES = [
    "Nunca gere DROP DATABASE, CREATE DATABASE, DROP TABLE ou TRUNCATE.",
    "Prefira sempre SELECT; só gere INSERT/UPDATE/DELETE se a pergunta pedir explicitamente uma alteração de dados.",
    "UPDATE e DELETE exigem sempre uma cláusula WHERE bem definida.",
    "Evite `SELECT *`; liste as colunas relevantes para a pergunta.",
    "Gere apenas uma única instrução SQL por resposta.",
]


def build_prompt(question: str, dialect: Dialect, schema: dict) -> str:
    dialect_label = _DIALECT_LABEL.get(dialect, "SQL padrão ANSI")
    return f"""{MODEL_ROLE}
Dialeto SQL de destino: {dialect_label}. A sintaxe gerada deve ser compatível com este dialeto
(ex.: LIMIT em PostgreSQL/MySQL/SQLite, TOP em SQL Server, aspas/quoting específicas do dialeto).

Esquema do banco de dados (tabela: [coluna:tipo, ...]):
{json.dumps(schema, indent=2, ensure_ascii=False)}

Restrições:
{chr(10).join(f"- {r}" for r in RESTRICOES)}

Pergunta do usuário: {question}
Query SQL:"""
