"""Builds a demo.db SQLite file from the sample CSVs in banco_de_dados/datasets/.

Lets the app be exercised end-to-end without needing a real MySQL/Postgres
server, and doubles as a live example that the same backend works against
any SQLAlchemy-supported dialect without code changes.
"""

import csv
import sqlite3
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BACKEND_DIR.parent / "banco_de_dados" / "datasets"
DB_PATH = BACKEND_DIR / "demo.db"

SCHEMA = """
CREATE TABLE clientes (
    cliente_id INTEGER PRIMARY KEY,
    nome TEXT,
    cpf TEXT,
    email TEXT
);

CREATE TABLE enderecos (
    endereco_id INTEGER PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(cliente_id),
    rua TEXT,
    cidade TEXT,
    estado TEXT,
    cep TEXT
);

CREATE TABLE movimentacoes (
    movimentacao_id INTEGER PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(cliente_id),
    tipo_movimentacao TEXT,
    valor REAL,
    data_movimentacao TEXT
);

CREATE TABLE pagamentos (
    pagamento_id INTEGER PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(cliente_id),
    valor REAL,
    data_pagamento TEXT
);
"""

TABLES = {
    "clientes": "clientes.csv",
    "enderecos": "enderecos.csv",
    "movimentacoes": "movimentacoes.csv",
    "pagamentos": "pagamentos.csv",
}


def load_csv(conn: sqlite3.Connection, table: str, csv_path: Path) -> None:
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        placeholders = ", ".join("?" for _ in header)
        conn.executemany(
            f"INSERT INTO {table} ({', '.join(header)}) VALUES ({placeholders})",
            reader,
        )


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        for table, filename in TABLES.items():
            csv_path = DATASETS_DIR / filename
            if not csv_path.exists():
                print(f"Aviso: {csv_path} não encontrado, pulando '{table}'.")
                continue
            load_csv(conn, table, csv_path)
            print(f"Carregado: {table} <- {filename}")
        conn.commit()
    finally:
        conn.close()

    print(f"\nBanco de demonstração criado em: {DB_PATH}")


if __name__ == "__main__":
    main()
