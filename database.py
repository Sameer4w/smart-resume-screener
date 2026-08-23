import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional


DATABASE_PATH = Path(__file__).resolve().parent / "data" / "resumes.db"


def get_connection() -> sqlite3.Connection:
    """Create a connection to the SQLite database."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    """Create the resumes table if it does not exist."""
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT,
                skills TEXT,
                education TEXT,
                experience TEXT,
                resume_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def save_resume(candidate: Dict, resume_text: str) -> int:
    """Save parsed resume information and return its database ID."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO resumes (
                name,
                email,
                phone,
                skills,
                education,
                experience,
                resume_text
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate.get("name", ""),
                candidate.get("email", ""),
                candidate.get("phone", ""),
                json.dumps(candidate.get("skills", [])),
                json.dumps(candidate.get("education", [])),
                json.dumps(candidate.get("experience", [])),
                resume_text,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def get_all_resumes() -> List[Dict]:
    """Return all stored resumes."""
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM resumes
            ORDER BY created_at DESC
            """
        ).fetchall()

        results = []

        for row in rows:
            item = dict(row)

            item["skills"] = json.loads(item["skills"] or "[]")
            item["education"] = json.loads(item["education"] or "[]")
            item["experience"] = json.loads(item["experience"] or "[]")

            results.append(item)

        return results

    finally:
        connection.close()


def get_resume(resume_id: int) -> Optional[Dict]:
    """Return one stored resume by ID."""
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM resumes
            WHERE id = ?
            """,
            (resume_id,),
        ).fetchone()

        if row is None:
            return None

        item = dict(row)

        item["skills"] = json.loads(item["skills"] or "[]")
        item["education"] = json.loads(item["education"] or "[]")
        item["experience"] = json.loads(item["experience"] or "[]")

        return item

    finally:
        connection.close()

def get_resume_count() -> int:
    """Return the total number of stored resumes."""
    connection = get_connection()

    try:
        row = connection.execute(
            "SELECT COUNT(*) AS count FROM resumes"
        ).fetchone()

        return int(row["count"])

    finally:
        connection.close()
