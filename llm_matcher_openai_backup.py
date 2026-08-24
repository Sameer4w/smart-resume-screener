import json
from pathlib import Path
from typing import Dict

from openai import OpenAI


PROMPT_PATH = (
    Path(__file__).resolve().parent
    / "prompts"
    / "matching_prompt.txt"
)


def load_matching_prompt() -> str:
    """Load the matching prompt template."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def validate_match_result(result: Dict) -> Dict:
    """Validate and normalize the LLM matching result."""
    required_fields = [
        "match_score",
        "summary",
        "matching_skills",
        "missing_skills",
        "experience_match",
        "education_match",
        "justification",
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing required field: {field}")

    score = result["match_score"]

    if not isinstance(score, int) or not 1 <= score <= 10:
        raise ValueError("match_score must be an integer from 1 to 10")

    if not isinstance(result["matching_skills"], list):
        raise ValueError("matching_skills must be a list")

    if not isinstance(result["missing_skills"], list):
        raise ValueError("missing_skills must be a list")

    return result


def match_resume_to_job(
    resume_text: str,
    job_description: str,
    model: str = "gpt-5-mini",
) -> Dict:
    """Compare a resume with a job description using an LLM."""
    if not resume_text.strip():
        raise ValueError("Resume text cannot be empty")

    if not job_description.strip():
        raise ValueError("Job description cannot be empty")

    client = OpenAI()

    prompt_template = load_matching_prompt()

    prompt = prompt_template.format(
        resume=resume_text,
        job_description=job_description,
    )

    response = client.responses.create(
        model=model,
        input=prompt,
    )

    raw_output = response.output_text.strip()

    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned invalid JSON: {raw_output}"
        ) from exc

    return validate_match_result(result)
