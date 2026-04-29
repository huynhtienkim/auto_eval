"""Postgres connections — uses DATABASE_URL from config (PG_* / DATABASE_URL in .env)."""
from __future__ import annotations

from contextlib import contextmanager

import psycopg

from app.config import DATABASE_URL, PG_CONNECT_TIMEOUT


@contextmanager
def get_conn():
    conn = psycopg.connect(DATABASE_URL, connect_timeout=PG_CONNECT_TIMEOUT)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
