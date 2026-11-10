import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.deps import get_connection_or_404
from app.config import get_settings
from app.db import connection_manager
from app.db.executor import QueryRejected, execute
from app.db.introspection import get_schema, schema_as_prompt_dict
from app.llm.gemini_client import GeminiError, generate_sql
from app.models.schemas import (
    QueryExecuteRequest,
    QueryExecuteResponse,
    QueryGenerateResponse,
    QueryRequest,
)
from app.storage import app_store

router = APIRouter(prefix="/api/query", tags=["query"])


def _generate(connection_id: str, question: str) -> QueryGenerateResponse:
    config = get_connection_or_404(connection_id)
    engine = connection_manager.get_engine(connection_id, config)
    tables = get_schema(engine)
    schema_dict = schema_as_prompt_dict(tables)

    try:
        sql = generate_sql(question, schema_dict, config.dialect)
    except GeminiError as exc:
        history_id = app_store.save_history(connection_id, question, sql="", error=str(exc))
        return QueryGenerateResponse(history_id=history_id, question=question, sql="", error=str(exc))

    history_id = app_store.save_history(connection_id, question, sql=sql)
    return QueryGenerateResponse(history_id=history_id, question=question, sql=sql)


@router.post("", response_model=QueryGenerateResponse)
def generate(payload: QueryRequest):
    return _generate(payload.connection_id, payload.question)


@router.get("/stream")
def stream(connection_id: str, question: str):
    def event(event_name: str, data: dict) -> str:
        return f"event: {event_name}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    def gen():
        try:
            config = get_connection_or_404(connection_id)
            yield event("status", {"message": "Lendo esquema do banco..."})
            engine = connection_manager.get_engine(connection_id, config)
            tables = get_schema(engine)
            schema_dict = schema_as_prompt_dict(tables)

            yield event("status", {"message": "Gerando SQL com Gemini..."})
            try:
                sql = generate_sql(question, schema_dict, config.dialect)
            except GeminiError as exc:
                history_id = app_store.save_history(connection_id, question, sql="", error=str(exc))
                yield event("error", {"message": str(exc)})
                return

            history_id = app_store.save_history(connection_id, question, sql=sql)
            yield event("sql", {"history_id": history_id, "sql": sql})

            yield event("status", {"message": "Executando no banco de dados..."})
            settings = get_settings()
            try:
                columns, rows, truncated, status_message = execute(
                    engine,
                    sql,
                    config.dialect,
                    config.allow_write,
                    settings.max_result_rows,
                    settings.query_timeout_seconds,
                )
            except QueryRejected as exc:
                app_store.update_history_result(history_id, row_count=None, error=str(exc))
                yield event("error", {"message": str(exc)})
                return
            except Exception as exc:
                app_store.update_history_result(history_id, row_count=None, error=str(exc))
                yield event("error", {"message": f"Erro ao executar query: {exc}"})
                return

            app_store.update_history_result(history_id, row_count=len(rows), error=None)
            yield event(
                "result",
                {
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows),
                    "truncated": truncated,
                    "status_message": status_message,
                },
            )
        except HTTPException as exc:
            yield event("error", {"message": exc.detail})
        except Exception as exc:  # pragma: no cover - defensive
            yield event("error", {"message": str(exc)})

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.post("/execute", response_model=QueryExecuteResponse)
def execute_query(payload: QueryExecuteRequest):
    config = get_connection_or_404(payload.connection_id)
    engine = connection_manager.get_engine(payload.connection_id, config)
    settings = get_settings()
    try:
        columns, rows, truncated, status_message = execute(
            engine,
            payload.sql,
            config.dialect,
            config.allow_write,
            settings.max_result_rows,
            settings.query_timeout_seconds,
        )
    except QueryRejected as exc:
        if payload.history_id:
            app_store.update_history_result(payload.history_id, row_count=None, error=str(exc))
        return QueryExecuteResponse(error=str(exc))
    except Exception as exc:
        if payload.history_id:
            app_store.update_history_result(payload.history_id, row_count=None, error=str(exc))
        return QueryExecuteResponse(error=f"Erro ao executar query: {exc}")

    if payload.history_id:
        app_store.update_history_result(payload.history_id, row_count=len(rows), error=None)

    return QueryExecuteResponse(
        columns=columns,
        rows=rows,
        row_count=len(rows),
        truncated=truncated,
        status_message=status_message,
    )
