import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from llm_matcher import validate_match_result


def test_valid_llm_result():
    result = {
        "match_score": 8,
        "summary": "Strong candidate for the role.",
        "matching_skills": ["Python", "SQL", "FastAPI"],
        "missing_skills": ["AWS"],
        "experience_match": "Relevant backend development experience.",
        "education_match": "Relevant Computer Science degree.",
        "justification": "The candidate matches most of the required skills and experience."
    }

    validated = validate_match_result(result)

    assert validated["match_score"] == 8
    assert "Python" in validated["matching_skills"]
    assert "AWS" in validated["missing_skills"]


def test_invalid_score_is_rejected():
    result = {
        "match_score": 11,
        "summary": "Test",
        "matching_skills": [],
        "missing_skills": [],
        "experience_match": "Test",
        "education_match": "Test",
        "justification": "Test"
    }

    try:
        validate_match_result(result)
        assert False, "Invalid score should have been rejected"
    except ValueError as exc:
        assert "1 to 10" in str(exc)


def test_missing_field_is_rejected():
    result = {
        "match_score": 7,
        "summary": "Test",
        "matching_skills": [],
        "missing_skills": [],
        "experience_match": "Test",
        "education_match": "Test"
    }

    try:
        validate_match_result(result)
        assert False, "Missing field should have been rejected"
    except ValueError as exc:
        assert "justification" in str(exc)
