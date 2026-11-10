import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from app.config import get_settings
from app.db.crypto import decrypt, encrypt
from app.models.schemas import ConnectionConfig, Dialect, HistoryItem

_SCHEMA = """
CREATE TABLE IF NOT EXISTS connections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dialect TEXT NOT NULL,
    host TEXT,
    port INTEGER,
    user TEXT,
    password_enc TEXT,
    database TEXT,
    raw_url_enc TEXT,
    allow_write INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS history (
    id TEXT PRIMARY KEY,
    connection_id TEXT NOT NULL,
    question TEXT NOT NULL,
    sql TEXT NOT NULL,
    row_count INTEGER,
    feedback TEXT,
    error TEXT,
    created_at TEXT NOT NULL
);
"""


@contextmanager
def _conn():
    conn = sqlite3.connect(get_settings().app_store_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _conn() as conn:
        conn.executescript(_SCHEMA)


def save_connection(config: ConnectionConfig) -> str:
    conn_id = str(uuid.uuid4())
    with _conn() as conn:
        conn.execute(
            """INSERT INTO connections
               (id, name, dialect, host, port, user, password_enc, database, raw_url_enc, allow_write, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                conn_id,
                config.name,
                config.dialect.value,
                config.host,
                config.port,
                config.user,
                encrypt(config.password) if config.password else "",
                config.database,
                encrypt(config.raw_url) if config.raw_url else "",
                int(config.allow_write),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
    return conn_id


def _row_to_config(row: sqlite3.Row) -> ConnectionConfig:
    return ConnectionConfig(
        name=row["name"],
        dialect=Dialect(row["dialect"]),
        host=row["host"],
        port=row["port"],
        user=row["user"],
        password=decrypt(row["password_enc"]) if row["password_enc"] else None,
        database=row["database"],
        raw_url=decrypt(row["raw_url_enc"]) if row["raw_url_enc"] else None,
        allow_write=bool(row["allow_write"]),
    )


def get_connection(connection_id: str) -> ConnectionConfig | None:
    with _conn() as conn:
        row = conn.execute("SELECT * FROM connections WHERE id = ?", (connection_id,)).fetchone()
    return _row_to_config(row) if row else None


def list_connections() -> list[tuple[str, ConnectionConfig]]:
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM connections ORDER BY created_at DESC").fetchall()
    return [(row["id"], _row_to_config(row)) for row in rows]


def delete_connection(connection_id: str) -> None:
    with _conn() as conn:
        conn.execute("DELETE FROM connections WHERE id = ?", (connection_id,))


def save_history(
    connection_id: str,
    question: str,
    sql: str,
    row_count: int | None = None,
    error: str | None = None,
) -> str:
    history_id = str(uuid.uuid4())
    with _conn() as conn:
        conn.execute(
            """INSERT INTO history (id, connection_id, question, sql, row_count, feedback, error, created_at)
               VALUES (?, ?, ?, ?, ?, NULL, ?, ?)""",
            (history_id, connection_id, question, sql, row_count, error, datetime.now(timezone.utc).isoformat()),
        )
    return history_id


def update_history_result(history_id: str, row_count: int | None, error: str | None) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE history SET row_count = ?, error = ? WHERE id = ?",
            (row_count, error, history_id),
        )


def save_feedback(history_id: str, feedback: str) -> bool:
    with _conn() as conn:
        cur = conn.execute("UPDATE history SET feedback = ? WHERE id = ?", (feedback, history_id))
    return cur.rowcount > 0


def list_history(limit: int = 200) -> list[HistoryItem]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [
        HistoryItem(
            id=row["id"],
            connection_id=row["connection_id"],
            question=row["question"],
            sql=row["sql"],
            row_count=row["row_count"],
            feedback=row["feedback"],
            error=row["error"],
            created_at=row["created_at"],
        )
        for row in rows
    ]
