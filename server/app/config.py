"""Environment-driven settings (loaded before other app imports use them)."""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent


def _database_url_from_env() -> str:
    """
    Prefer DATABASE_URL if set.
    Otherwise build from PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, PG_DATABASE (password URL-encoded).
    """
    explicit = (os.environ.get("DATABASE_URL") or "").strip()
    if explicit:
        return explicit

    user = (os.environ.get("PG_USER") or "").strip()
    password = os.environ.get("PG_PASSWORD", "")
    host = (os.environ.get("PG_HOST") or "").strip()
    port = (os.environ.get("PG_PORT") or "5432").strip()
    database = (os.environ.get("PG_DATABASE") or os.environ.get("PG_DB") or "").strip()

    if user and host and database:
        u = quote_plus(user, safe="")
        p = quote_plus(password, safe="")
        base = f"postgresql://{u}:{p}@{host}:{port}/{database}"
        sslmode = (os.environ.get("PG_SSLMODE") or "").strip()
        if sslmode:
            base += f"?sslmode={quote_plus(sslmode, safe='')}"
        return base

    return "postgresql://postgres:postgres@127.0.0.1:5432/bvab"


DATABASE_URL = _database_url_from_env()
EVALUATION_DATABASE_URL = (os.environ.get("EVALUATION_DATABASE_URL") or "").strip()
EVALUATION_SCHEMA = (os.environ.get("EVALUATION_SCHEMA") or "evaluation").strip()
EVALUATION_TABLE = (os.environ.get("EVALUATION_TABLE") or "auto_test_cases").strip()
EVALUATION_RESULTS_TABLE = (os.environ.get("EVALUATION_RESULTS_TABLE") or "auto_results").strip()

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-change-in-production")
JWT_ALG = "HS256"
JWT_EXP_HOURS = int(os.environ.get("JWT_EXP_HOURS", "168"))

N8N_UPSTREAM = os.environ.get("N8N_UPSTREAM_URL", "").rstrip("/")

CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

# Seconds — avoids hanging forever if Postgres host is wrong or server is down.
PG_CONNECT_TIMEOUT = int(os.environ.get("PG_CONNECT_TIMEOUT", "15"))
