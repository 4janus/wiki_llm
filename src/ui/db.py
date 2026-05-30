"""SQLite persistence for tester tokens and download grants."""
from __future__ import annotations

import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "juraklar.db"

_TOKEN_CHARSET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # removes ambiguous 0/O/1/I/L
_TOKEN_TTL_DAYS = 14
_GRANT_TTL_MINUTES = 10


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tester_tokens (
                token      TEXT PRIMARY KEY,
                email      TEXT NOT NULL,
                advisor_id TEXT NOT NULL,
                rating     INTEGER NOT NULL,
                comment    TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS download_grants (
                grant_id   TEXT PRIMARY KEY,
                advisor_id TEXT NOT NULL,
                service_id INTEGER NOT NULL,
                fmt        TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used       INTEGER DEFAULT 0
            );
        """)


def create_token(email: str, advisor_id: str, rating: int, comment: str | None) -> str:
    token = "".join(secrets.choice(_TOKEN_CHARSET) for _ in range(8))
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=_TOKEN_TTL_DAYS)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO tester_tokens VALUES (?,?,?,?,?,?,?)",
            (token, email, advisor_id, rating, comment or "", now.isoformat(), expires.isoformat()),
        )
    return token


def validate_and_consume_token(raw: str) -> bool:
    """Normalise input, verify expiry, delete on success."""
    token = raw.upper().replace("-", "").replace(" ", "")
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT expires_at FROM tester_tokens WHERE token=?", (token,)
        ).fetchone()
        if not row or row[0] < now:
            return False
        conn.execute("DELETE FROM tester_tokens WHERE token=?", (token,))
    return True


def create_grant(advisor_id: str, service_id: int, fmt: str) -> str:
    grant_id = secrets.token_urlsafe(16)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=_GRANT_TTL_MINUTES)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO download_grants VALUES (?,?,?,?,?,?,0)",
            (grant_id, advisor_id, service_id, fmt, now.isoformat(), expires.isoformat()),
        )
    return grant_id


def consume_grant(grant_id: str) -> dict | None:
    """Returns {advisor_id, service_id, fmt} if grant is valid and unused; None otherwise."""
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT advisor_id, service_id, fmt FROM download_grants "
            "WHERE grant_id=? AND used=0 AND expires_at>?",
            (grant_id, now),
        ).fetchone()
        if not row:
            return None
        conn.execute("UPDATE download_grants SET used=1 WHERE grant_id=?", (grant_id,))
        return {"advisor_id": row[0], "service_id": row[1], "fmt": row[2]}
