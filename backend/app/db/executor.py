import sqlglot
from sqlglot import exp
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from app.models.schemas import Dialect

_SQLGLOT_DIALECT = {
    Dialect.postgresql: "postgres",
    Dialect.mysql: "mysql",
    Dialect.sqlite: "sqlite",
    Dialect.mssql: "tsql",
}


class QueryRejected(Exception):
    """Raised when a generated/edited statement fails the safety guardrails."""


def _sqlglot_dialect(dialect: Dialect) -> str | None:
    return _SQLGLOT_DIALECT.get(dialect)


def prepare_statement(sql: str, dialect: Dialect, allow_write: bool, max_rows: int) -> str:
    """Parses the statement (dialect-aware), enforces the read-only/WHERE
    guardrails, and injects a row LIMIT on SELECTs that lack one."""
    sql = sql.strip().rstrip(";")
    if not sql:
        raise QueryRejected("SQL vazio.")

    gdialect = _sqlglot_dialect(dialect)
    try:
        statements = sqlglot.parse(sql, read=gdialect)
    except Exception as exc:
        raise QueryRejected(f"Não foi possível interpretar o SQL: {exc}") from exc

    statements = [s for s in statements if s is not None]
    if len(statements) != 1:
        raise QueryRejected("Apenas uma instrução SQL por execução é permitida.")
    parsed = statements[0]

    if isinstance(parsed, (exp.Select, exp.Union)):
        if not parsed.args.get("limit"):
            parsed = parsed.limit(max_rows)
        return parsed.sql(dialect=gdialect)

    if not allow_write:
        raise QueryRejected(
            "Esta conexão está em modo somente leitura. Apenas consultas SELECT são permitidas "
            "(ative 'permitir escrita' nas configurações da conexão para liberar INSERT/UPDATE/DELETE)."
        )

    if isinstance(parsed, (exp.Update, exp.Delete)) and not parsed.args.get("where"):
        raise QueryRejected("UPDATE/DELETE exigem uma cláusula WHERE explícita.")

    if isinstance(parsed, (exp.Insert, exp.Update, exp.Delete)):
        return parsed.sql(dialect=gdialect)

    raise QueryRejected(
        "Tipo de instrução não permitido (apenas SELECT sempre; INSERT/UPDATE/DELETE com "
        "'permitir escrita' habilitado)."
    )


def _apply_timeout(conn: Connection, dialect: Dialect, timeout_seconds: int) -> None:
    try:
        if dialect == Dialect.postgresql:
            conn.execute(text(f"SET statement_timeout = {timeout_seconds * 1000}"))
        elif dialect == Dialect.mysql:
            conn.execute(text(f"SET SESSION MAX_EXECUTION_TIME={timeout_seconds * 1000}"))
    except Exception:
        pass  # best-effort; not every server/user has permission to set this


def execute(
    engine: Engine,
    sql: str,
    dialect: Dialect,
    allow_write: bool,
    max_rows: int,
    timeout_seconds: int,
) -> tuple[list[str], list[dict], bool, str | None]:
    """Returns (columns, rows, truncated, status_message)."""
    safe_sql = prepare_statement(sql, dialect, allow_write, max_rows)
    with engine.connect() as conn:
        _apply_timeout(conn, dialect, timeout_seconds)
        result = conn.execute(text(safe_sql))
        if result.returns_rows:
            columns = list(result.keys())
            fetched = result.fetchmany(max_rows + 1)
            truncated = len(fetched) > max_rows
            rows = [dict(zip(columns, row)) for row in fetched[:max_rows]]
            conn.commit()
            return columns, rows, truncated, None
        row_count = result.rowcount
        conn.commit()
        return [], [], False, f"Comando executado com sucesso. {row_count} linha(s) afetada(s)."
