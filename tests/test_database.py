import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import (
    get_all_resumes,
    get_connection,
    initialize_database,
    save_resume,
)


def test_database_initialization():
    initialize_database()

    connection = get_connection()

    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = 'resumes'
        """
    ).fetchall()

    connection.close()

    assert len(tables) == 1


def test_save_and_retrieve_resume():
    initialize_database()

    candidate = {
        "name": "Test Candidate",
        "email": "test@example.com",
        "phone": "+91 9999999999",
        "skills": ["Python", "SQL"],
        "education": ["B.Tech Computer Science"],
        "experience": ["Software Engineering Intern"],
    }

    resume_id = save_resume(
        candidate,
        "Test Candidate Python SQL"
    )

    assert resume_id is not None

    resumes = get_all_resumes()

    assert len(resumes) >= 1

    saved = next(
        resume for resume in resumes
        if resume["id"] == resume_id
    )

    assert saved["name"] == "Test Candidate"
    assert saved["email"] == "test@example.com"
    assert "Python" in saved["skills"]
    assert "SQL" in saved["skills"]
