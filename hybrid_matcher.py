
from typing import Dict, List

from llm_matcher import match_resume_to_job


def hybrid_match_resume(
    resume_text: str,
    job_description: str,
    resume_skills: List[str] = None,
    use_llm: bool = True,
) -> Dict:
    """
    Hybrid resume matching.

    Strategy:
    1. Try the LLM when enabled.
    2. If the LLM is unavailable or fails,
       automatically use the local matcher.
    """

    if not resume_text.strip():
        raise ValueError(
            "Resume text cannot be empty"
        )

    if not job_description.strip():
        raise ValueError(
            "Job description cannot be empty"
        )

    # ---------------------------------------------------------
    # 1. Try LLM
    # ---------------------------------------------------------

    if use_llm:
        try:
            from llm_service import llm_match_resume

            result = llm_match_resume(
                resume_text=resume_text,
                job_description=job_description,
            )

            result["matching_method"] = "LLM"

            return result

        except Exception as exc:
            print(
                f"⚠️ LLM unavailable: "
                f"{type(exc).__name__}: {exc}"
            )
            print(
                "🔄 Falling back to local matcher..."
            )

    # ---------------------------------------------------------
    # 2. Local fallback
    # ---------------------------------------------------------

    result = match_resume_to_job(
        resume_text=resume_text,
        job_description=job_description,
        resume_skills=resume_skills,
    )

    result["matching_method"] = "LOCAL"

    return result
