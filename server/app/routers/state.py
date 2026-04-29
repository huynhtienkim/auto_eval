"""Synchronized eval UI state per user."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_user_id
from app.models.schemas import EvalState
from app.services.eval_state_service import load_merged_state, persist_state

router = APIRouter(prefix="/api", tags=["state"])


@router.get("/state")
def get_state(user_id: int = Depends(get_user_id)):
    return load_merged_state(user_id)


@router.put("/state")
def put_state(body: EvalState, user_id: int = Depends(get_user_id)):
    persist_state(user_id, body)
    return {"ok": True, "updated_at": datetime.now(timezone.utc).isoformat()}
