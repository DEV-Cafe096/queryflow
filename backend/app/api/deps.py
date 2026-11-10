from fastapi import HTTPException

from app.models.schemas import ConnectionConfig
from app.storage import app_store


def get_connection_or_404(connection_id: str) -> ConnectionConfig:
    config = app_store.get_connection(connection_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Conexão não encontrada.")
    return config
