"""evaluation.auto_test_cases (separate DSN optional)."""
from __future__ import annotations

import psycopg
from psycopg import sql as pg_sql

from app.config import (
    DATABASE_URL,
    EVALUATION_DATABASE_URL,
    EVALUATION_SCHEMA,
    EVALUATION_TABLE,
    PG_CONNECT_TIMEOUT,
)


def evaluation_dsn() -> str:
    return EVALUATION_DATABASE_URL or DATABASE_URL


def count_rows() -> tuple[bool, int | str]:
    """Returns (success, row_count or error message)."""
    dsn = evaluation_dsn()
    query = pg_sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
        pg_sql.Identifier(EVALUATION_SCHEMA),
        pg_sql.Identifier(EVALUATION_TABLE),
    )
    try:
        with psycopg.connect(dsn, connect_timeout=PG_CONNECT_TIMEOUT) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                row = cur.fetchone()
        n = int(row[0]) if row else 0
        return True, n
    except Exception as e:
        return False, str(e)
