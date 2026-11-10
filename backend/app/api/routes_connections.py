from fastapi import APIRouter, HTTPException

from app.db import connection_manager
from app.models.schemas import ConnectionConfig, ConnectionCreateResponse
from app.storage import app_store

router = APIRouter(prefix="/api/connections", tags=["connections"])


@router.post("/test")
def test_connection(config: ConnectionConfig):
    try:
        connection_manager.test_connection(config)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Falha ao conectar: {exc}") from exc
    return {"ok": True}


@router.post("", response_model=ConnectionCreateResponse)
def create_connection(config: ConnectionConfig):
    try:
        connection_manager.test_connection(config)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Falha ao conectar: {exc}") from exc
    conn_id = app_store.save_connection(config)
    return ConnectionCreateResponse(
        id=conn_id, name=config.name, dialect=config.dialect, allow_write=config.allow_write
    )


@router.get("", response_model=list[ConnectionCreateResponse])
def list_connections():
    return [
        ConnectionCreateResponse(
            id=conn_id, name=cfg.name, dialect=cfg.dialect, allow_write=cfg.allow_write
        )
        for conn_id, cfg in app_store.list_connections()
    ]


@router.delete("/{connection_id}")
def delete_connection(connection_id: str):
    connection_manager.drop_engine(connection_id)
    app_store.delete_connection(connection_id)
    return {"ok": True}
