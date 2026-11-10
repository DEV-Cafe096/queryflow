from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL

from app.models.schemas import ConnectionConfig, Dialect

_DRIVER_BY_DIALECT = {
    Dialect.postgresql: "postgresql+psycopg2",
    Dialect.mysql: "mysql+pymysql",
    Dialect.mssql: "mssql+pyodbc",
}

# In-memory engine cache keyed by connection_id. Engines pool their own
# connections, so we build one per saved connection and reuse it.
_engine_cache: dict[str, Engine] = {}


def build_url(config: ConnectionConfig) -> str:
    if config.raw_url:
        return config.raw_url
    if config.dialect == Dialect.sqlite:
        return f"sqlite:///{config.database}"
    drivername = _DRIVER_BY_DIALECT[config.dialect]
    return str(
        URL.create(
            drivername=drivername,
            username=config.user,
            password=config.password,
            host=config.host,
            port=config.port,
            database=config.database,
        )
    )


def build_engine(config: ConnectionConfig) -> Engine:
    url = build_url(config)
    connect_args = {}
    if config.dialect == Dialect.mysql:
        connect_args["connect_timeout"] = 5
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


def get_engine(connection_id: str, config: ConnectionConfig) -> Engine:
    engine = _engine_cache.get(connection_id)
    if engine is None:
        engine = build_engine(config)
        _engine_cache[connection_id] = engine
    return engine


def test_connection(config: ConnectionConfig) -> None:
    """Raises if the connection cannot be established."""
    engine = build_engine(config)
    try:
        with engine.connect():
            pass
    finally:
        engine.dispose()


def drop_engine(connection_id: str) -> None:
    engine = _engine_cache.pop(connection_id, None)
    if engine is not None:
        engine.dispose()
