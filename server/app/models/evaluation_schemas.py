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


class AutoResultOut(BaseModel):
    """evaluation.auto_results row."""

    id: int
    run_id: Optional[int] = None
    test_case_id: Optional[int] = None
    agent_answer: Optional[str] = None
    score_accuracy: Optional[float] = None
    score_helpfulness: Optional[float] = None
    score_safety: Optional[float] = None
    score_hallucination: Optional[float] = None
    score_overall: Optional[float] = None
    judge_rationale: Optional[str] = None


class AutoResultCreate(BaseModel):
    run_id: Optional[int] = None
    test_case_id: Optional[int] = None
    agent_answer: Optional[str] = None
    score_accuracy: Optional[float] = Field(None, ge=0, le=99.9)
    score_helpfulness: Optional[float] = Field(None, ge=0, le=99.9)
    score_safety: Optional[float] = Field(None, ge=0, le=99.9)
    score_hallucination: Optional[float] = Field(None, ge=0, le=99.9)
    score_overall: Optional[float] = Field(None, ge=0, le=99.9)
    judge_rationale: Optional[str] = None


class AutoResultUpdate(BaseModel):
    run_id: Optional[int] = None
    test_case_id: Optional[int] = None
    agent_answer: Optional[str] = None
    score_accuracy: Optional[float] = Field(None, ge=0, le=99.9)
    score_helpfulness: Optional[float] = Field(None, ge=0, le=99.9)
    score_safety: Optional[float] = Field(None, ge=0, le=99.9)
    score_hallucination: Optional[float] = Field(None, ge=0, le=99.9)
    score_overall: Optional[float] = Field(None, ge=0, le=99.9)
    judge_rationale: Optional[str] = None
