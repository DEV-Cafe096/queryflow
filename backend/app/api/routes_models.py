from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.llm.gemini_client import GeminiError, list_models

router = APIRouter(prefix="/api/models", tags=["models"])


class ListModelsRequest(BaseModel):
    api_key: str | None = None


@router.post("/list")
def list_available_models(payload: ListModelsRequest):
    try:
        return {"models": list_models(payload.api_key)}
    except GeminiError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
