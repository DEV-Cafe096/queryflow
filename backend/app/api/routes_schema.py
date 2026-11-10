from fastapi import APIRouter, HTTPException

from app.api.deps import get_connection_or_404
from app.db import connection_manager
from app.db.introspection import get_schema
from app.models.schemas import SchemaResponse

router = APIRouter(prefix="/api/connections", tags=["schema"])


@router.get("/{connection_id}/schema", response_model=SchemaResponse)
def schema_for_connection(connection_id: str):
    config = get_connection_or_404(connection_id)
    engine = connection_manager.get_engine(connection_id, config)
    try:
        tables = get_schema(engine)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Falha ao ler esquema: {exc}") from exc
    return SchemaResponse(connection_id=connection_id, dialect=config.dialect, tables=tables)
