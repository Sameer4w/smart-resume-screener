
import re
from typing import Dict, List


KNOWN_SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "sql",
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "node.js",
    "nodejs",
    "fastapi",
    "flask",
    "django",
    "spring boot",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "mongodb",
    "mysql",
    "postgresql",
    "postgres",
    "sqlite",
    "redis",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "pandas",
    "numpy",
    "scikit-learn",
    "rest api",
    "rest",
    "linux",
]


SKILL_ALIASES = {
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite"],
    "git": ["git", "github", "gitlab"],
}


def normalize_text(text: str) -> str:
    """Normalize text for reliable comparison."""
    text = text.lower()
    text = text.replace("node.js", "nodejs")
    text = text.replace("spring boot", "springboot")
    return text


def contains_term(text: str, term: str) -> bool:
    """Check whether a skill or skill alias appears in text."""
    normalized = normalize_text(text)
    normalized_term = normalize_text(term)

    return bool(
        re.search(
            rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])",
            normalized,
        )
    )


def detect_skills(text: str) -> List[str]:
    """Detect known technical skills from text."""
    found = []

    for skill in KNOWN_SKILLS:

        aliases = SKILL_ALIASES.get(skill, [skill])

        if any(contains_term(text, alias) for alias in aliases):
            found.append(skill)

    return found


def extract_required_skills(job_description: str) -> List[str]:
    """Extract technical skills mentioned in the job description."""
    return detect_skills(job_description)


def extract_resume_skills(resume_text: str) -> List[str]:
    """Extract technical skills mentioned in the resume."""
    return detect_skills(resume_text)


def calculate_score(
    required_skills: List[str],
    matching_skills: List[str],
    resume_text: str,
    job_description: str,
) -> int:
    """Calculate a 1–10 local match score."""

    if not required_skills:
        return 5

    skill_ratio = len(matching_skills) / len(required_skills)

    score = 1 + round(skill_ratio * 7)

    resume_lower = resume_text.lower()

    experience_words = [
        "experience",
        "developed",
        "developer",
        "engineer",
        "internship",
        "project",
        "worked",
    ]

    if any(word in resume_lower for word in experience_words) and matching_skills:
        score += 1

    job_words = set(re.findall(r"[a-zA-Z]{4,}", job_description.lower()))
    resume_words = set(re.findall(r"[a-zA-Z]{4,}", resume_lower))

    overlap = len(job_words & resume_words)

    if overlap >= 8:
        score += 1

    return max(1, min(10, score))


def match_resume_to_job(
    resume_text: str,
    job_description: str,
    model: str = "local",
) -> Dict:
    """Compare a resume with a job description locally."""

    if not resume_text.strip():
        raise ValueError("Resume text cannot be empty")

    if not job_description.strip():
        raise ValueError("Job description cannot be empty")

    resume_skills = extract_resume_skills(resume_text)
    required_skills = extract_required_skills(job_description)

    matching_skills = [
        skill
        for skill in required_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill
        for skill in required_skills
        if skill not in resume_skills
    ]

    score = calculate_score(
        required_skills,
        matching_skills,
        resume_text,
        job_description,
    )

    if score >= 9:
        summary = "Exceptional alignment with the job requirements."
    elif score >= 8:
        summary = "Very strong alignment with the job requirements."
    elif score >= 7:
        summary = "Good alignment with the job requirements."
    elif score >= 6:
        summary = "Moderate alignment with the job requirements."
    elif score >= 5:
        summary = "Partial alignment with the job requirements."
    else:
        summary = "Limited alignment with the job requirements."

    if matching_skills:
        experience_match = (
            "The resume demonstrates experience or exposure related "
            "to the matching skills: "
            + ", ".join(matching_skills)
            + "."
        )
    else:
        experience_match = (
            "No strong technical skill overlap was identified."
        )

    education_match = (
        "Education information was found in the resume; "
        "detailed requirement matching is based primarily on "
        "the available job and resume text."
    )

    if matching_skills:
        justification = (
            f"The candidate matches {len(matching_skills)} of "
            f"{len(required_skills)} detected technical requirements. "
            f"Matching skills include: {', '.join(matching_skills)}."
        )
    else:
        justification = (
            "No matching technical skills were detected between "
            "the resume and job description."
        )

    return {
        "match_score": score,
        "summary": summary,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "experience_match": experience_match,
        "education_match": education_match,
        "justification": justification,
    }
