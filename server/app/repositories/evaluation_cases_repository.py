"""CRUD for evaluation.auto_test_cases (configurable schema/table)."""
from __future__ import annotations

from typing import Any, Optional

import psycopg
from psycopg import sql as pg_sql

from app.config import (
    EVALUATION_SCHEMA,
    EVALUATION_TABLE,
    PG_CONNECT_TIMEOUT,
)
from app.repositories.evaluation_repository import evaluation_dsn


def _fqn():
    return pg_sql.SQL("{}.{}").format(
        pg_sql.Identifier(EVALUATION_SCHEMA),
        pg_sql.Identifier(EVALUATION_TABLE),
    )


def _row_to_dict(row: tuple[Any, ...]) -> dict[str, Any]:
    (
        id_,
        question,
        gold_answer,
        intent,
        category,
        difficulty,
        is_active,
        created_at,
        notes,
    ) = row
    return {
        "id": int(id_),
        "question": question,
        "gold_answer": gold_answer,
        "intent": intent,
        "category": category,
        "difficulty": int(difficulty) if difficulty is not None else 1,
        "is_active": bool(is_active),
        "created_at": created_at,
        "notes": notes,
    }


def list_cases(*, active_only: bool = True) -> list[dict[str, Any]]:
    dsn = evaluation_dsn()
    base = pg_sql.SQL(
        "SELECT id, question, gold_answer, intent, category, difficulty, is_active, created_at, notes FROM {}"
    ).format(_fqn())
    q = (
        pg_sql.SQL("{} WHERE is_active = TRUE ORDER BY id ASC").format(base)
        if active_only
        else pg_sql.SQL("{} ORDER BY id ASC").format(base)
    )

    with psycopg.connect(dsn, connect_timeout=PG_CONNECT_TIMEOUT) as conn:
        with conn.cursor() as cur:
            cur.execute(q)
            rows = cur.fetchall()
    return [_row_to_dict(r) for r in rows]


def get_by_id(case_id: int) -> Optional[dict[str, Any]]:
    dsn = evaluation_dsn()
    q = pg_sql.SQL(
        """
        SELECT id, question, gold_answer, intent, category, difficulty, is_active, created_at, notes
        FROM {} WHERE id = %s
        """
    ).format(_fqn())
    with psycopg.connect(dsn, connect_timeout=PG_CONNECT_TIMEOUT) as conn:
        with conn.cursor() as cur:
            cur.execute(q, (case_id,))
            row = cur.fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def insert_case(
    *,
    question: str,
    gold_answer: Optional[str],
    intent: Optional[str],
    category: Optional[str],
    difficulty: int,
    notes: Optional[str],
    is_active: bool,
) -> dict[str, Any]:
    dsn = evaluation_dsn()
    q = pg_sql.SQL(
        """
        INSERT INTO {} (question, gold_answer, intent, category, difficulty, notes, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, question, gold_answer, intent, category, difficulty, is_active, created_at, notes
        """
    ).format(_fqn())
    with psycopg.connect(dsn, connect_timeout=PG_CONNECT_TIMEOUT) as conn:
        with conn.cursor() as cur:
            cur.execute(
                q,
                (question, gold_answer, intent, category, difficulty, notes, is_active),
            )
            row = cur.fetchone()
    return _row_to_dict(row)


def update_case(case_id: int, fields: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Update columns present in ``fields`` (value may be None for nullable columns)."""
    allowed = ("question", "gold_answer", "intent", "category", "difficulty", "notes", "is_active")
    cols: list[pg_sql.Identifier] = []
    vals: list[Any] = []
    for k in allowed:
        if k in fields:
            cols.append(pg_sql.Identifier(k))
            vals.append(fields[k])
    if not cols:
        return get_by_id(case_id)

    set_frag = pg_sql.SQL(", ").join(pg_sql.SQL("{} = %s").format(c) for c in cols)
    vals.append(case_id)
    q = pg_sql.SQL(
        """
        UPDATE {} SET {}
        WHERE id = %s
        RETURNING id, question, gold_answer, intent, category, difficulty, is_active, created_at, notes
        """
    ).format(_fqn(), set_frag)

    dsn = evaluation_dsn()
    with psycopg.connect(dsn, connect_timeout=PG_CONNECT_TIMEOUT) as conn:
        with conn.cursor() as cur:
            cur.execute(q, vals)
            row = cur.fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def delete_case(case_id: int) -> bool:
    dsn = evaluation_dsn()
    q = pg_sql.SQL("DELETE FROM {} WHERE id = %s").format(_fqn())
    with psycopg.connect(dsn, connect_timeout=PG_CONNECT_TIMEOUT) as conn:
        with conn.cursor() as cur:
            cur.execute(q, (case_id,))
            n = cur.rowcount
    return n > 0
