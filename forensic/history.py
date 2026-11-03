
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "forensic_history.db"
)


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                image_format TEXT,
                width INTEGER,
                height INTEGER,
                analysis_type TEXT NOT NULL,
                result_summary TEXT,
                created_at TEXT NOT NULL
            )
        """)


def save_analysis(
    filename,
    sha256,
    file_size,
    analysis_type,
    result_summary,
    image_format=None,
    width=None,
    height=None
):
    initialize_database()

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO analysis_history (
                filename, sha256, file_size,
                image_format, width, height,
                analysis_type, result_summary, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename,
            sha256,
            file_size,
            image_format,
            width,
            height,
            analysis_type,
            result_summary,
            datetime.now(timezone.utc).isoformat()
        ))


def get_history(limit=100):
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM analysis_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]
