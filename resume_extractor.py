import re
from typing import Dict, List


def extract_email(text: str) -> str:
    """Extract the first email address from resume text."""
    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """Extract a likely phone number from resume text."""
    match = re.search(
        r"(?:\+?\d{1,3}[\s.-]?)?"
        r"(?:\(?\d{3}\)?[\s.-]?)?"
        r"\d{3}[\s.-]?\d{4}",
        text
    )

    return match.group(0) if match else ""


def extract_skills(text: str) -> List[str]:
    """Extract commonly listed technical skills."""
    skill_keywords = [
        "Python",
        "Java",
        "JavaScript",
        "C",
        "C++",
        "C#",
        "SQL",
        "HTML",
        "CSS",
        "React",
        "Node.js",
        "FastAPI",
        "Django",
        "Flask",
        "Spring Boot",
        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
        "Scikit-learn",
        "Pandas",
        "NumPy",
        "Git",
        "Docker",
        "AWS",
        "Azure",
        "GCP",
        "MongoDB",
        "PostgreSQL",
        "MySQL",
    ]

    text_lower = text.lower()

    found = []

    for skill in skill_keywords:
        if skill.lower() in text_lower:
            found.append(skill)

    return found


def extract_education(text: str) -> List[str]:
    """Extract lines that appear to describe education."""
    education_keywords = [
        "b.tech",
        "btech",
        "b.e.",
        "bachelor",
        "m.tech",
        "mtech",
        "m.e.",
        "master",
        "mba",
        "phd",
        "ph.d",
        "university",
        "college",
        "degree",
    ]

    lines = []

    for line in text.splitlines():
        cleaned = line.strip()

        if cleaned and any(
            keyword in cleaned.lower()
            for keyword in education_keywords
        ):
            lines.append(cleaned)

    return lines


def extract_experience(text: str) -> List[str]:
    """Extract lines that appear to describe professional experience."""
    experience_keywords = [
        "experience",
        "intern",
        "internship",
        "developer",
        "engineer",
        "software",
        "worked",
        "employment",
        "company",
    ]

    lines = []

    for line in text.splitlines():
        cleaned = line.strip()

        if cleaned and any(
            keyword in cleaned.lower()
            for keyword in experience_keywords
        ):
            lines.append(cleaned)

    return lines


def extract_candidate_data(text: str) -> Dict:
    """Extract structured candidate information from resume text."""
    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
    }
