"""evaluation.auto_test_cases diagnostics."""
from fastapi import APIRouter

from app.services.evaluation_service import build_config_view, run_connection_test

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.get("/config")
def evaluation_config():
    """Non-secret summary for the Test cases UI (password masked)."""
    return build_config_view()


@router.get("/test")
def evaluation_test():
    """Try SELECT COUNT(*) from configured schema.table."""
    return run_connection_test()
