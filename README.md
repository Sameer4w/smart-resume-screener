# 📄 Smart Resume Screener

AI-powered resume analysis and candidate screening system.

## 🎯 Objective

Intelligently parse resumes, extract candidate information and skills, and compare candidates against a job description.

## ✨ Features

- PDF and TXT resume upload
- Resume text extraction
- Candidate information extraction
- Skill extraction
- Education and experience extraction
- Job description matching
- Hybrid resume matching
- Candidate scoring from 1–10
- Candidate ranking
- Shortlisted candidate identification
- Skill-gap analysis
- ATS-style resume analysis
- Resume improvement recommendations
- Explainable AI analysis
- SQLite database storage
- Streamlit dashboard

## 🏗️ Project Structure

```text
smart-resume-screener/
│
├── app.py
├── config.py
├── database.py
├── hybrid_matcher.py
├── llm_matcher.py
├── llm_matcher_openai_backup.py
├── llm_service.py
├── requirements.txt
├── resume_extractor.py
├── resume_parser.py
│
├── tests/
│   ├── test_database.py
│   ├── test_extractor.py
│   ├── test_llm_matcher.py
│   └── test_parser.py
│
├── prompts/
│   └── matching_prompt.txt
│
└── data/
    └── .gitkeep
