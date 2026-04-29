"""CRUD for evaluation.auto_results (configurable schema/table)."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

import psycopg
from psycopg import sql as pg_sql
from psycopg.sql import Placeholder

from app.config import (
    EVALUATION_RESULTS_TABLE,
    EVALUATION_SCHEMA,
    PG_CONNECT_TIMEOUT,
)
from app.repositories.evaluation_repository import evaluation_dsn


def _fqn():
    return pg_sql.SQL("{}.{}").format(
        pg_sql.Identifier(EVALUATION_SCHEMA),
        pg_sql.Identifier(EVALUATION_RESULTS_TABLE),
    )


def _num(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    return float(v)


def _row_to_dict(row: tuple[Any, ...]) -> dict[str, Any]:
    (
        id_,
        run_id,
        test_case_id,
        agent_answer,
        score_accuracy,
        score_helpfulness,
        score_safety,
        score_hallucination,
        score_overall,
        judge_rationale,
    ) = row
    return {
        "id": int(id_),
        "run_id": int(run_id) if run_id is not None else None,
        "test_case_id": int(test_case_id) if test_case_id is not None else None,
        "agent_answer": agent_answer,
        "score_accuracy": _num(score_accuracy),
        "score_helpfulness": _num(score_helpfulness),
        "score_safety": _num(score_safety),
        "score_hallucination": _num(score_hallucination),
        "score_overall": _num(score_overall),
        "judge_rationale": judge_rationale,
    }


_SELECT = """
    SELECT id, run_id, test_case_id, agent_answer,
           score_accuracy, score_helpfulness, score_safety, score_hallucination, score_overall,
           judge_rationale
    FROM {}
"""


def list_results(
    *,
    run_id: Optional[int] = None,
    test_case_id: Optional[int] = None,
) -> list[dict[str, Any]]:
    dsn = evaluation_dsn()
    base = pg_sql.SQL(_SELECT).format(_fqn())
    wheres: list[pg_sql.Composed] = []
    params: list[Any] = []
    if run_id is not None:
        wheres.append(pg_sql.SQL("run_id = {}").format(Placeholder()))
        params.append(run_id)
    if test_case_id is not None:
        wheres.append(pg_sql.SQL("test_case_id = {}").format(Placeholder()))
        params.append(test_case_id)
    if wheres:
        q = pg_sql.SQL("{} WHERE {} ORDER BY id DESC").format(
            base,
            pg_sql.SQL(" AND ").join(wheres),
        )
    else:
        q = pg_sql.SQL("{} ORDER BY id DESC").format(base)

    with psycopg.connect(dsn, connect_timeout=PG_CONNECT_TIMEOUT) as conn:
        with conn.cursor() as cur:
            cur.execute(q, params)
            rows = cur.fetchall()
    return [_row_to_dict(r) for r in rows]


def get_by_id(result_id: int) -> Optional[dict[str, Any]]:
    dsn = evaluation_dsn()
    q = pg_sql.SQL(_SELECT + " WHERE id = %s").format(_fqn())
    with psycopg.connect(dsn, connect_timeout=PG_CONNECT_TIMEOUT) as conn:
        with conn.cursor() as cur:
            cur.execute(q, (result_id,))
            row = cur.fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def insert_result(
    *,
    run_id: Optional[int],
    test_case_id: Optional[int],
    agent_answer: Optional[str],
    score_accuracy: Optional[float],
    score_helpfulness: Optional[float],
    score_safety: Optional[float],
    score_hallucination: Optional[float],
    score_overall: Optional[float],
    judge_rationale: Optional[str],
) -> dict[str, Any]:
    dsn = evaluation_dsn()
    q = pg_sql.SQL(
        """
        INSERT INTO {} (
            run_id, test_case_id, agent_answer,
            score_accuracy, score_helpfulness, score_safety, score_hallucination, score_overall,
            judge_rationale
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, run_id, test_case_id, agent_answer,
                  score_accuracy, score_helpfulness, score_safety, score_hallucination, score_overall,
                  judge_rationale
        """
    ).format(_fqn())
    with psycopg.connect(dsn, connect_timeout=PG_CONNECT_TIMEOUT) as conn:
        with conn.cursor() as cur:
            cur.execute(
                q,
                (
                    run_id,
                    test_case_id,
                    agent_answer,
                    score_accuracy,
                    score_helpfulness,
                    score_safety,
                    score_hallucination,
                    score_overall,
                    judge_rationale,
                ),
            )
            row = cur.fetchone()
    return _row_to_dict(row)


def update_result(result_id: int, fields: dict[str, Any]) -> Optional[dict[str, Any]]:
    allowed = (
        "run_id",
        "test_case_id",
        "agent_answer",
        "score_accuracy",
        "score_helpfulness",
        "score_safety",
        "score_hallucination",
        "score_overall",
        "judge_rationale",
    )
    cols: list[pg_sql.Identifier] = []
    vals: list[Any] = []
    for k in allowed:
        if k in fields:
            cols.append(pg_sql.Identifier(k))
            vals.append(fields[k])
    if not cols:
        return get_by_id(result_id)

    set_frag = pg_sql.SQL(", ").join(pg_sql.SQL("{} = %s").format(c) for c in cols)
    vals.append(result_id)
    q = pg_sql.SQL(
        """
        UPDATE {} SET {}
        WHERE id = %s
        RETURNING id, run_id, test_case_id, agent_answer,
                  score_accuracy, score_helpfulness, score_safety, score_hallucination, score_overall,
                  judge_rationale
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


def delete_result(result_id: int) -> bool:
    dsn = evaluation_dsn()
    q = pg_sql.SQL("DELETE FROM {} WHERE id = %s").format(_fqn())
    with psycopg.connect(dsn, connect_timeout=PG_CONNECT_TIMEOUT) as conn:
        with conn.cursor() as cur:
            cur.execute(q, (result_id,))
            n = cur.rowcount
    return n > 0
