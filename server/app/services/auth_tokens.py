"""JWT encode/decode."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

from app.config import JWT_ALG, JWT_EXP_HOURS, JWT_SECRET


def create_token(user_id: int, email: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=JWT_EXP_HOURS)
    return jwt.encode(
        {"sub": str(user_id), "email": email, "exp": exp},
        JWT_SECRET,
        algorithm=JWT_ALG,
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
