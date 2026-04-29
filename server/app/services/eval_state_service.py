"""Merge persisted JSON with defaults for /api/state."""
from __future__ import annotations

import json
from typing import Any

from app.models.schemas import EvalState
from app.repositories import eval_state_repository


def load_merged_state(user_id: int) -> dict[str, Any]:
    raw = eval_state_repository.get_raw_state(user_id)
    if raw is None:
        return EvalState().model_dump()
    data = raw
    if isinstance(data, str):
        data = json.loads(data)
    if not isinstance(data, dict):
        return EvalState().model_dump()
    return EvalState.model_validate({**EvalState().model_dump(), **data}).model_dump()


def persist_state(user_id: int, body: EvalState) -> None:
    eval_state_repository.upsert_state(user_id, json.dumps(body.model_dump()))
