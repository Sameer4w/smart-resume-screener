import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resume_extractor import (
    extract_candidate_data,
    extract_email,
    extract_phone,
    extract_skills,
)


SAMPLE_RESUME = """
John Doe
Email: john.doe@gmail.com
Phone: +91 9876543210

EDUCATION
B.Tech in Computer Science
VIT University, 2026

SKILLS
Python, Java, SQL, FastAPI, Machine Learning, Git, Docker

EXPERIENCE
Software Engineering Intern at ABC Technologies
Worked on Python backend development and REST APIs.
"""


def test_email_extraction():
    assert extract_email(SAMPLE_RESUME) == "john.doe@gmail.com"


def test_phone_extraction():
    assert "9876543210" in extract_phone(SAMPLE_RESUME)


def test_skill_extraction():
    skills = extract_skills(SAMPLE_RESUME)

    assert "Python" in skills
    assert "Java" in skills
    assert "SQL" in skills
    assert "FastAPI" in skills


def test_candidate_data_structure():
    candidate = extract_candidate_data(SAMPLE_RESUME)

    assert "email" in candidate
    assert "phone" in candidate
    assert "skills" in candidate
    assert "education" in candidate
    assert "experience" in candidate
