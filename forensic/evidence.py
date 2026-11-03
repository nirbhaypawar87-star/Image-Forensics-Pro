
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "forensic.db"
)


def create_evidence_table():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evidence_id TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def save_evidence(filename, sha256, file_size):
    create_evidence_table()

    evidence_id = "EVD-" + uuid.uuid4().hex[:12].upper()
    created_at = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO evidence_records
            (evidence_id, filename, sha256, file_size, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            evidence_id,
            filename,
            sha256,
            file_size,
            created_at
        ))

    return {
        "evidence_id": evidence_id,
        "filename": filename,
        "sha256": sha256,
        "file_size": file_size,
        "created_at": created_at
    }


def get_evidence_records(limit=100):
    create_evidence_table()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT evidence_id, filename, sha256,
                   file_size, created_at
            FROM evidence_records
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]
