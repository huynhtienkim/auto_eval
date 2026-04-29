"""Users table."""
from __future__ import annotations

from typing import Any, Optional

from app.db.connection import get_conn


def insert_user_returning_id(email: str, password_hash: str) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO app.users (email, password_hash) VALUES (%s, %s) RETURNING id",
                (email, password_hash),
            )
            row = cur.fetchone()
            uid = int(row[0])
            cur.execute(
                "INSERT INTO app.user_eval_state (user_id, state) VALUES (%s, %s::jsonb)",
                (uid, "{}"),
            )
    return uid


def fetch_credentials_by_email(email: str) -> Optional[tuple[int, str]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, password_hash FROM app.users WHERE email = %s",
                (email,),
            )
            row = cur.fetchone()
    if row is None:
        return None
    return int(row[0]), row[1]


def fetch_user_profile(user_id: int) -> Optional[tuple[Any, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT email, created_at FROM app.users WHERE id = %s", (user_id,))
            return cur.fetchone()
