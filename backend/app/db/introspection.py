from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from app.models.schemas import ColumnInfo, TableInfo


def get_schema(engine: Engine) -> list[TableInfo]:
    inspector = inspect(engine)
    tables: list[TableInfo] = []
    for table_name in inspector.get_table_names():
        pk_columns = set(inspector.get_pk_constraint(table_name).get("constrained_columns") or [])
        columns = [
            ColumnInfo(
                name=col["name"],
                type=str(col["type"]),
                primary_key=col["name"] in pk_columns,
            )
            for col in inspector.get_columns(table_name)
        ]
        foreign_keys = [
            {
                "constrained_columns": fk["constrained_columns"],
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"],
            }
            for fk in inspector.get_foreign_keys(table_name)
        ]
        tables.append(TableInfo(name=table_name, columns=columns, foreign_keys=foreign_keys))
    return tables


def schema_as_prompt_dict(tables: list[TableInfo]) -> dict:
    """Compact {table: [col:type, ...]} shape, cheap to embed in an LLM prompt."""
    return {t.name: [f"{c.name}:{c.type}" for c in t.columns] for t in tables}
