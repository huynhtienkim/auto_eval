"""API shapes for evaluation.auto_test_cases."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TestCaseOut(BaseModel):
    id: int
    question: str
    gold_answer: Optional[str] = None
    intent: Optional[str] = None
    category: Optional[str] = None
    difficulty: int = 1
    is_active: bool = True
    created_at: datetime
    notes: Optional[str] = None


class TestCaseCreate(BaseModel):
    question: str = Field(..., min_length=1)
    gold_answer: Optional[str] = None
    intent: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=80)
    difficulty: int = Field(1, ge=0, le=32767)
    notes: Optional[str] = None
    is_active: bool = True


class TestCaseUpdate(BaseModel):
    question: Optional[str] = Field(None, min_length=1)
    gold_answer: Optional[str] = None
    intent: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=80)
    difficulty: Optional[int] = Field(None, ge=0, le=32767)
    notes: Optional[str] = None
    is_active: Optional[bool] = None
