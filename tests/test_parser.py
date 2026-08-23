import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resume_parser import extract_resume_text


def test_txt_resume_extraction():
    test_resume = Path("/tmp/test_resume.txt")

    test_resume.write_text(
        "John Doe\n"
        "Python Developer\n"
        "Skills: Python, SQL, FastAPI",
        encoding="utf-8"
    )

    result = extract_resume_text(str(test_resume))

    assert "John Doe" in result
    assert "Python" in result
    assert "SQL" in result


def test_unsupported_file_type():
    test_file = Path("/tmp/test_resume.docx")
    test_file.write_text("sample", encoding="utf-8")

    with pytest.raises(ValueError):
        extract_resume_text(str(test_file))


def test_pdf_resume_extraction():
    test_pdf = Path("/tmp/test_resume.pdf")

    result = extract_resume_text(str(test_pdf))

    assert "John Doe" in result
    assert "Python Developer" in result
    assert "Python" in result
