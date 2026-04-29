"""CRUD for evaluation.auto_results."""
from fastapi import APIRouter, HTTPException, Query, status

from app.models.evaluation_schemas import AutoResultCreate, AutoResultOut, AutoResultUpdate
from app.repositories.auto_results_repository import (
    delete_result as repo_delete,
    get_by_id,
    insert_result,
    list_results as repo_list,
    update_result as repo_update,
)

router = APIRouter(prefix="/api/evaluation", tags=["evaluation-results"])


@router.get("/results", response_model=list[AutoResultOut])
def list_results(
    run_id: int | None = Query(None, description="Filter by run_id"),
    test_case_id: int | None = Query(None, description="Filter by test_case_id"),
):
    rows = repo_list(run_id=run_id, test_case_id=test_case_id)
    return [AutoResultOut.model_validate(r) for r in rows]


@router.get("/results/{result_id}", response_model=AutoResultOut)
def get_result(result_id: int):
    row = get_by_id(result_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Result not found")
    return AutoResultOut.model_validate(row)


@router.post("/results", response_model=AutoResultOut, status_code=status.HTTP_201_CREATED)
def create_result(body: AutoResultCreate):
    row = insert_result(
        run_id=body.run_id,
        test_case_id=body.test_case_id,
        agent_answer=body.agent_answer,
        score_accuracy=body.score_accuracy,
        score_helpfulness=body.score_helpfulness,
        score_safety=body.score_safety,
        score_hallucination=body.score_hallucination,
        score_overall=body.score_overall,
        judge_rationale=body.judge_rationale,
    )
    return AutoResultOut.model_validate(row)


@router.put("/results/{result_id}", response_model=AutoResultOut)
def update_result(result_id: int, body: AutoResultUpdate):
    if get_by_id(result_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Result not found")
    patch = body.model_dump(exclude_unset=True)
    if not patch:
        row = get_by_id(result_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Result not found")
        return AutoResultOut.model_validate(row)
    row = repo_update(result_id, patch)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Result not found")
    return AutoResultOut.model_validate(row)


@router.delete("/results/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_result(result_id: int):
    if not repo_delete(result_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Result not found")
