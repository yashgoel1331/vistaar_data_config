"""Thin psycopg2 data-access layer for the config_versions table."""

from __future__ import annotations

import json
import logging
import os
from contextlib import contextmanager
from typing import Any

import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool

logger = logging.getLogger(__name__)

_pool: SimpleConnectionPool | None = None

DATABASE_URL_DEFAULT = (
    "postgresql://postgres:efwzThw2KHTNx6tLko6uy9dLtBratJYuxOy2mgBgc4Q"
    "@localhost:5432/postgres"
)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS config_versions (
    config_type    TEXT    NOT NULL,
    version_number INTEGER NOT NULL,
    snapshot       JSONB   NOT NULL,
    triggered_by   TEXT,
    note           TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (config_type, version_number)
);
"""


def init_db(dsn: str | None = None) -> None:
    global _pool
    dsn = dsn or os.getenv("DATABASE_URL", DATABASE_URL_DEFAULT)
    _pool = SimpleConnectionPool(1, 10, dsn=dsn)
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
        conn.commit()
    logger.info("db: pool initialised, config_versions table ensured")


def close_db() -> None:
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


@contextmanager
def _connection():
    conn = _pool.getconn()
    try:
        yield conn
    finally:
        _pool.putconn(conn)


# ── Query helpers ────────────────────────────────────────────────────


def fetch_latest_row(config_type: str, columns: tuple[str, ...] = ("snapshot", "version_number")) -> dict[str, Any] | None:
    cols = ", ".join(columns)
    sql = f"SELECT {cols} FROM config_versions WHERE config_type = %s ORDER BY version_number DESC LIMIT 1"
    with _connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (config_type,))
            row = cur.fetchone()
    return dict(row) if row else None


def fetch_row_by_version(config_type: str, version: int, columns: tuple[str, ...] = ("snapshot", "version_number")) -> dict[str, Any] | None:
    cols = ", ".join(columns)
    sql = f"SELECT {cols} FROM config_versions WHERE config_type = %s AND version_number = %s LIMIT 1"
    with _connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (config_type, version))
            row = cur.fetchone()
    return dict(row) if row else None


def fetch_all_versions(config_type: str, columns: tuple[str, ...] = ("version_number", "triggered_by", "note")) -> list[dict[str, Any]]:
    cols = ", ".join(columns)
    sql = f"SELECT {cols} FROM config_versions WHERE config_type = %s ORDER BY version_number DESC"
    with _connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (config_type,))
            return [dict(r) for r in cur.fetchall()]


def insert_config_version(row: dict[str, Any]) -> dict[str, Any]:
    sql = """
        INSERT INTO config_versions (config_type, version_number, snapshot, triggered_by, note)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING config_type, version_number, snapshot, triggered_by, note
    """
    with _connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (
                row["config_type"],
                row["version_number"],
                json.dumps(row["snapshot"], ensure_ascii=False),
                row.get("triggered_by"),
                row.get("note"),
            ))
            inserted = dict(cur.fetchone())
        conn.commit()
    return inserted


def upsert_config_version(row: dict[str, Any]) -> dict[str, Any]:
    sql = """
        INSERT INTO config_versions (config_type, version_number, snapshot, triggered_by, note)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (config_type, version_number) DO UPDATE
            SET snapshot = EXCLUDED.snapshot,
                triggered_by = EXCLUDED.triggered_by,
                note = EXCLUDED.note
        RETURNING config_type, version_number, snapshot, triggered_by, note
    """
    with _connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (
                row["config_type"],
                row["version_number"],
                json.dumps(row["snapshot"], ensure_ascii=False),
                row.get("triggered_by"),
                row.get("note"),
            ))
            result = dict(cur.fetchone())
        conn.commit()
    return result


def delete_versions(config_type: str, version_numbers: list[int]) -> None:
    if not version_numbers:
        return
    sql = "DELETE FROM config_versions WHERE config_type = %s AND version_number = ANY(%s)"
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (config_type, version_numbers))
        conn.commit()
