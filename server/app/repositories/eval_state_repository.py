"""Per-user JSON eval UI state."""
from __future__ import annotations

from typing import Any, Optional

from app.db.connection import get_conn


def get_raw_state(user_id: int) -> Optional[Any]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT state FROM app.user_eval_state WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
    if row is None:
        return None
    return row[0]


def upsert_state(user_id: int, payload_json: str) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO app.user_eval_state (user_id, state, updated_at)
                VALUES (%s, %s::jsonb, now())
                ON CONFLICT (user_id) DO UPDATE SET state = EXCLUDED.state, updated_at = now()
                """,
                (user_id, payload_json),
            )
