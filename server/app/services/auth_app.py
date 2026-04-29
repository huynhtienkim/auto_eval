"""Register / login orchestration."""
from __future__ import annotations

from app.repositories import user_repository as users
from app.services.auth_tokens import create_token
from app.services.passwords import hash_password, verify_password


def register_new_user(email: str, plain_password: str) -> int:
    return users.insert_user_returning_id(email.lower(), hash_password(plain_password))


def authenticate(email: str, plain_password: str) -> int | None:
    row = users.fetch_credentials_by_email(email.lower())
    if row is None:
        return None
    uid, pw_hash = row
    if not verify_password(plain_password, pw_hash):
        return None
    return uid


def token_response(user_id: int, email: str) -> dict:
    token = create_token(user_id, email.lower())
    return {"access_token": token, "token_type": "bearer", "user_id": user_id}
