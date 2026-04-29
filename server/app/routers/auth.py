"""Registration, login, current user."""
from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import errors as pg_errors

from app.dependencies.auth import get_user_id
from app.models.schemas import LoginBody, RegisterBody
from app.repositories.user_repository import fetch_user_profile
from app.services.auth_app import authenticate, register_new_user, token_response

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterBody):
    try:
        uid = register_new_user(body.email, body.password)
    except pg_errors.UniqueViolation:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    return token_response(uid, body.email)


@router.post("/login")
def login(body: LoginBody):
    uid = authenticate(body.email, body.password)
    if uid is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return token_response(uid, body.email)


@router.get("/me")
def me(user_id: int = Depends(get_user_id)):
    row = fetch_user_profile(user_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return {"id": user_id, "email": row[0], "created_at": row[1].isoformat() if row[1] else None}
