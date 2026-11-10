from fastapi import APIRouter, HTTPException

from app.models.schemas import FeedbackRequest, HistoryItem
from app.storage import app_store

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[HistoryItem])
def list_history(limit: int = 200):
    return app_store.list_history(limit=limit)


@router.post("/{history_id}/feedback")
def send_feedback(history_id: str, payload: FeedbackRequest):
    ok = app_store.save_feedback(history_id, payload.feedback)
    if not ok:
        raise HTTPException(status_code=404, detail="Registro de histórico não encontrado.")
    return {"ok": True}
