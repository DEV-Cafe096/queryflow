from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


class Dialect(str, Enum):
    postgresql = "postgresql"
    mysql = "mysql"
    sqlite = "sqlite"
    mssql = "mssql"
    other = "other"


class ConnectionConfig(BaseModel):
    """Either fill (dialect, host, port, user, password, database) or set raw_url
    directly for a dialect not covered by the structured fields (e.g. Snowflake,
    BigQuery, Oracle) — anything SQLAlchemy has a dialect package for."""

    name: str
    dialect: Dialect
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    raw_url: Optional[str] = None
    allow_write: bool = False

    @model_validator(mode="after")
    def _check_fields(self):
        if self.raw_url:
            return self
        if self.dialect == Dialect.sqlite:
            if not self.database:
                raise ValueError("sqlite requer 'database' (caminho do arquivo)")
            return self
        if self.dialect == Dialect.other:
            raise ValueError("dialect 'other' exige raw_url")
        missing = [f for f in ("host", "user", "database") if not getattr(self, f)]
        if missing:
            raise ValueError(f"campos obrigatórios ausentes: {', '.join(missing)}")
        return self


class ConnectionCreateResponse(BaseModel):
    id: str
    name: str
    dialect: Dialect
    allow_write: bool


class ColumnInfo(BaseModel):
    name: str
    type: str
    primary_key: bool = False


class TableInfo(BaseModel):
    name: str
    columns: list[ColumnInfo]
    foreign_keys: list[dict[str, Any]] = Field(default_factory=list)


class SchemaResponse(BaseModel):
    connection_id: str
    dialect: Dialect
    tables: list[TableInfo]


class QueryRequest(BaseModel):
    connection_id: str
    question: str


class QueryGenerateResponse(BaseModel):
    history_id: str
    question: str
    sql: str
    error: Optional[str] = None


class QueryExecuteRequest(BaseModel):
    connection_id: str
    sql: str
    history_id: Optional[str] = None


class QueryExecuteResponse(BaseModel):
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    truncated: bool = False
    status_message: Optional[str] = None
    error: Optional[str] = None


class FeedbackRequest(BaseModel):
    feedback: str


class HistoryItem(BaseModel):
    id: str
    connection_id: str
    question: str
    sql: str
    row_count: Optional[int] = None
    feedback: Optional[str] = None
    error: Optional[str] = None
    created_at: str
