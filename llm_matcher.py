
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
    "linux",
]


SKILL_ALIASES = {
    "sql": ["sql"],
    "git": ["git"],
    "rest api": ["rest api", "restful api", "restful", "rest"],
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("node.js", "nodejs")
    text = text.replace("spring boot", "springboot")
    return text


def contains_term(text: str, term: str) -> bool:
    normalized = normalize_text(text)
    normalized_term = normalize_text(term)

    return bool(
        re.search(
            rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])",
            normalized,
        )
    )


def detect_skills(text: str) -> List[str]:
    found = []

    for skill in KNOWN_SKILLS:
        aliases = SKILL_ALIASES.get(skill, [skill])

        if any(contains_term(text, alias) for alias in aliases):
            found.append(skill)

    return found


def extract_required_skills(job_description: str) -> List[str]:
    return detect_skills(job_description)


def extract_resume_skills(resume_text: str) -> List[str]:
    return detect_skills(resume_text)


def extract_education_match(
    resume_text: str,
    job_description: str,
) -> str:

    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    degree_terms = [
        "b.tech",
        "btech",
        "b.e",
        "be ",
        "bachelor",
        "b.sc",
        "bsc",
        "m.tech",
        "mtech",
        "m.e",
        "master",
        "m.sc",
        "msc",
        "computer science",
        "information technology",
        "software engineering",
    ]

    resume_education = [
        term for term in degree_terms
        if term in resume_lower
    ]

    job_education = [
        term for term in degree_terms
        if term in job_lower
    ]

    if not job_education:
        if resume_education:
            return (
                "The resume contains relevant education information, "
                "including "
                + ", ".join(resume_education[:3])
                + ". The job description does not state a specific "
                "education requirement."
            )

        return (
            "No specific education requirement is stated in the "
            "job description, and no clear education information "
            "was detected in the resume."
        )

    matched = [
        term for term in job_education
        if term in resume_lower
    ]

    if matched:
        return (
            "The candidate's education includes "
            + ", ".join(resume_education[:3])
            + ", which aligns with the education requirement "
            "stated in the job description."
        )

    return (
        "The job description specifies "
        + ", ".join(job_education[:3])
        + ", but the resume does not clearly show the same "
        "education requirement."
    )


def extract_experience_match(
    resume_text: str,
    job_description: str,
    matching_skills: List[str],
) -> str:

    resume_lower = resume_text.lower()

    project_indicators = [
        "project",
        "developed",
        "built",
        "implemented",
        "created",
        "application",
        "system",
        "internship",
        "experience",
        "developer",
        "engineer",
    ]

    has_experience = any(
        indicator in resume_lower
        for indicator in project_indicators
    )

    if not has_experience:
        return (
            "No clear professional or project experience relevant "
            "to the job requirements was detected in the resume."
        )

    if matching_skills:
        return (
            "The resume contains relevant project or development "
            "experience involving "
            + ", ".join(matching_skills[:6])
            + ", which supports the technical requirements of the role."
        )

    return (
        "The resume contains project or development experience, "
        "but no strong technical overlap with the job requirements "
        "was detected."
    )


def calculate_score(
    required_skills: List[str],
    matching_skills: List[str],
    resume_text: str,
    job_description: str,
) -> Dict:
    """Calculate weighted score and return its breakdown."""

    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    # ---------------------------------------------------------
    # 1. Technical skill match - 60%
    # ---------------------------------------------------------
    if required_skills:
        skill_ratio = len(matching_skills) / len(required_skills)
    else:
        skill_ratio = 0.0

    skill_score = skill_ratio * 6.0

    # ---------------------------------------------------------
    # 2. Relevant experience / project evidence - 20%
    # ---------------------------------------------------------
    experience_keywords = [
        "experience",
        "developed",
        "develop",
        "built",
        "implemented",
        "project",
        "internship",
        "application",
        "system",
    ]

    experience_evidence = sum(
        1
        for word in experience_keywords
        if word in resume_lower
    )

    experience_score = min(
        experience_evidence / 5.0,
        1.0
    ) * 2.0

    if matching_skills:
        matching_skill_evidence = sum(
            1
            for skill in matching_skills
            if skill.lower() in resume_lower
        )

        if matching_skill_evidence > 0:
            experience_score = min(
                2.0,
                experience_score + 0.5
            )

    # ---------------------------------------------------------
    # 3. Education relevance - 10%
    # ---------------------------------------------------------
    education_terms = [
        "b.tech",
        "btech",
        "bachelor",
        "computer science",
        "information technology",
        "software engineering",
        "m.tech",
        "mtech",
        "master",
    ]

    job_education_terms = [
        term
        for term in education_terms
        if term in job_lower
    ]

    if not job_education_terms:
        education_score = 1.0
    elif any(
        term in resume_lower
        for term in job_education_terms
    ):
        education_score = 1.0
    else:
        education_score = 0.5

    # ---------------------------------------------------------
    # 4. Overall relevance - 10%
    # ---------------------------------------------------------
    job_words = set(
        re.findall(r"[a-zA-Z]{4,}", job_lower)
    )

    resume_words = set(
        re.findall(r"[a-zA-Z]{4,}", resume_lower)
    )

    if job_words:
        overlap_ratio = len(
            job_words & resume_words
        ) / len(job_words)
    else:
        overlap_ratio = 0.0

    relevance_score = min(
        overlap_ratio,
        1.0
    ) * 1.0

    # ---------------------------------------------------------
    # Final weighted score
    # ---------------------------------------------------------
    total_score = (
        skill_score
        + experience_score
        + education_score
        + relevance_score
    )

    score = round(total_score)

    score = max(1, min(10, score))

    return {
        "score": score,
        "technical_skills": round(skill_score, 2),
        "experience": round(experience_score, 2),
        "education": round(education_score, 2),
        "relevance": round(relevance_score, 2),
    }

def match_resume_to_job(
    resume_text: str,
    job_description: str,
    model: str = "local",
    resume_skills: List[str] = None,
) -> Dict:

    if not resume_text.strip():
        raise ValueError("Resume text cannot be empty")

    if not job_description.strip():
        raise ValueError("Job description cannot be empty")

    if resume_skills is None:
        resume_skills = extract_resume_skills(resume_text)

    resume_skills = [
        skill.lower()
        for skill in resume_skills
    ]

    required_skills = extract_required_skills(
        job_description
    )

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

    score_breakdown = calculate_score(
        required_skills,
        matching_skills,
        resume_text,
        job_description,
    )

    score = score_breakdown["score"]

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

    experience_match = extract_experience_match(
        resume_text,
        job_description,
        matching_skills,
    )

    education_match = extract_education_match(
        resume_text,
        job_description,
    )

    if matching_skills:
        justification = (
            f"The candidate received {score}/10 based on technical "
            f"skill alignment, relevant project or development "
            f"experience, education relevance, and overall resume-job "
            f"alignment. Strong matches include "
            f"{', '.join(matching_skills)}."
        )

        if missing_skills:
            justification += (
                f" Important gaps include "
                f"{', '.join(missing_skills)}."
            )
    else:
        justification = (
            f"The candidate received {score}/10 because no strong "
            "technical skill overlap was detected between the "
            "resume and job description."
        )

    return {
        "match_score": score,
        "score_breakdown": {
            "technical_skills": score_breakdown["technical_skills"],
            "experience": score_breakdown["experience"],
            "education": score_breakdown["education"],
            "relevance": score_breakdown["relevance"],
        },
        "summary": summary,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "experience_match": experience_match,
        "education_match": education_match,
        "justification": justification,
    }
