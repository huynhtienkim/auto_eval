"""CRUD for evaluation.auto_test_cases."""
from fastapi import APIRouter, HTTPException, Query, status

from app.models.evaluation_schemas import TestCaseCreate, TestCaseOut, TestCaseUpdate
from app.repositories.evaluation_cases_repository import (
    delete_case as repo_delete,
    get_by_id,
    insert_case,
    list_cases as repo_list,
    update_case as repo_update,
)

router = APIRouter(prefix="/api/evaluation", tags=["evaluation-cases"])


@router.get("/cases", response_model=list[TestCaseOut])
def list_cases(active_only: bool = Query(True, description="If false, include is_active = false rows")):
    rows = repo_list(active_only=active_only)
    return [TestCaseOut.model_validate(r) for r in rows]


@router.get("/cases/{case_id}", response_model=TestCaseOut)
def get_case(case_id: int):
    row = get_by_id(case_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found")
    return TestCaseOut.model_validate(row)


@router.post("/cases", response_model=TestCaseOut, status_code=status.HTTP_201_CREATED)
def create_case(body: TestCaseCreate):
    row = insert_case(
        question=body.question,
        gold_answer=body.gold_answer,
        intent=body.intent,
        category=body.category,
        difficulty=body.difficulty,
        notes=body.notes,
        is_active=body.is_active,
    )
    return TestCaseOut.model_validate(row)


@router.put("/cases/{case_id}", response_model=TestCaseOut)
def update_case(case_id: int, body: TestCaseUpdate):
    if get_by_id(case_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found")
    patch = body.model_dump(exclude_unset=True)
    if not patch:
        row = get_by_id(case_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found")
        return TestCaseOut.model_validate(row)
    row = repo_update(case_id, patch)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found")
    return TestCaseOut.model_validate(row)


@router.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(case_id: int):
    if not repo_delete(case_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found")
