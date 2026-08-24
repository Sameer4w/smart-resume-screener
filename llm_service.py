
import json
import os
from pathlib import Path
from typing import Dict

PROMPT_PATH = (
    Path(__file__).resolve().parent
    / "prompts"
    / "matching_prompt.txt"
)


def load_prompt() -> str:
    """Load the LLM matching prompt."""
    return PROMPT_PATH.read_text(
        encoding="utf-8"
    )


def validate_result(result: Dict) -> Dict:
    """Validate the LLM response structure."""

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
            raise ValueError(
                f"LLM response missing field: {field}"
            )

    score = result["match_score"]

    if not isinstance(score, int):
        raise ValueError(
            "match_score must be an integer"
        )

    if not 1 <= score <= 10:
        raise ValueError(
            "match_score must be between 1 and 10"
        )

    if not isinstance(
        result["matching_skills"], list
    ):
        raise ValueError(
            "matching_skills must be a list"
        )

    if not isinstance(
        result["missing_skills"], list
    ):
        raise ValueError(
            "missing_skills must be a list"
        )

    return result


def llm_match_resume(
    resume_text: str,
    job_description: str,
    model: str = "gpt-5-mini",
) -> Dict:
    """
    Compare a resume with a job description
    using an OpenAI-compatible LLM.
    """

    if not resume_text.strip():
        raise ValueError(
            "Resume text cannot be empty"
        )

    if not job_description.strip():
        raise ValueError(
            "Job description cannot be empty"
        )

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not configured"
        )

    from openai import OpenAI

    client = OpenAI()

    prompt_template = load_prompt()

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
            "LLM returned invalid JSON"
        ) from exc

    return validate_result(result)
