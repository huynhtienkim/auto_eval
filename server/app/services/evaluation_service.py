"""Evaluation DB summary & connectivity checks."""
from __future__ import annotations

from urllib.parse import urlparse

from app.config import EVALUATION_DATABASE_URL, EVALUATION_SCHEMA, EVALUATION_TABLE
from app.repositories.evaluation_repository import count_rows, evaluation_dsn


def mask_database_url(url: str) -> str:
    try:
        u = urlparse(url)
        if not u.hostname:
            return url
        auth = f"{u.username}:***@" if u.username else ""
        port = f":{u.port}" if u.port else ""
        path = u.path or ""
        return f"{u.scheme}://{auth}{u.hostname}{port}{path}"
    except Exception:
        return "(could not parse DATABASE_URL)"


def evaluation_qualified_name() -> str:
    return f'"{EVALUATION_SCHEMA}".{EVALUATION_TABLE}'


def build_config_view() -> dict:
    return {
        "schema": EVALUATION_SCHEMA,
        "table": EVALUATION_TABLE,
        "qualified_name": evaluation_qualified_name(),
        "dsn_summary": mask_database_url(evaluation_dsn()),
        "uses_dedicated_eval_url": bool(EVALUATION_DATABASE_URL),
    }


def run_connection_test() -> dict:
    ok, payload = count_rows()
    base = {
        "schema": EVALUATION_SCHEMA,
        "table": EVALUATION_TABLE,
        "qualified_name": evaluation_qualified_name(),
    }
    if ok:
        return {"ok": True, "row_count": int(payload), **base}
    return {"ok": False, "error": str(payload), **base}
