from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL CHECK(platform IN ('instagram','tiktok','youtube','other')),
    url TEXT NOT NULL UNIQUE,
    creator_name TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL DEFAULT '',
    caption TEXT NOT NULL DEFAULT '',
    views INTEGER NOT NULL DEFAULT 0 CHECK(views >= 0),
    likes INTEGER NOT NULL DEFAULT 0 CHECK(likes >= 0),
    comments INTEGER NOT NULL DEFAULT 0 CHECK(comments >= 0),
    topic TEXT NOT NULL DEFAULT '',
    hook TEXT NOT NULL DEFAULT '',
    format_type TEXT NOT NULL DEFAULT '',
    monetization_path TEXT NOT NULL DEFAULT '',
    source_notes TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'captured' CHECK(status IN ('captured','enriched','scored','selected','discarded')),
    hook_strength REAL NOT NULL DEFAULT 0 CHECK(hook_strength BETWEEN 0 AND 10),
    recreation_ease REAL NOT NULL DEFAULT 0 CHECK(recreation_ease BETWEEN 0 AND 10),
    monetization_potential REAL NOT NULL DEFAULT 0 CHECK(monetization_potential BETWEEN 0 AND 10),
    score REAL NOT NULL DEFAULT 0 CHECK(score BETWEEN 0 AND 100),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_references_status ON references(status);
CREATE INDEX IF NOT EXISTS idx_references_platform ON references(platform);
CREATE INDEX IF NOT EXISTS idx_references_score ON references(score DESC);
"""


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or settings.db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(db_path: Path | None = None) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


@contextmanager
def db_session(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    conn = connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
