"""Request/response bodies (Pydantic) — view-layer contracts."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class EvalState(BaseModel):
    model_config = ConfigDict(extra="ignore")

    cases: list[Any] = Field(default_factory=list)
    runs: list[Any] = Field(default_factory=list)
    results: list[Any] = Field(default_factory=list)
    nextCaseId: int = 1
    settings: dict[str, Any] = Field(default_factory=dict)
