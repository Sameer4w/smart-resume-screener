# 📄 Smart Resume Screener

AI-powered resume analysis and candidate screening system.

## 🎯 Objective

The objective of Smart Resume Screener is to intelligently parse PDF/TXT resumes, extract structured candidate information and skills, compare candidates with a given job description, calculate match scores, identify skill gaps, and provide recruiter-oriented recommendations.

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

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │   Streamlit UI       │
                    │     app.py           │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   Resume Processing  │
                    │ resume_parser.py     │
                    │ resume_extractor.py  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   Hybrid Matcher     │
                    │ hybrid_matcher.py    │
                    └──────────┬───────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
     ┌────────▼─────────┐             ┌────────▼─────────┐
     │ Rule/Feature     │             │ LLM Matching     │
     │ Based Matching   │             │ llm_matcher.py   │
     └────────┬─────────┘             └────────┬─────────┘
              │                                 │
              └────────────────┬────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │   Score & Analysis   │
                    │ Ranking / Skill Gap  │
                    │ ATS / Explanation    │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ SQLite Database      │
                    │ database.py          │
                    └──────────────────────┘
```

## 🔄 Processing Workflow

```text
Resume Upload
      ↓
Extract Resume Text
      ↓
Extract Candidate Information
      ↓
Extract Skills / Education / Experience
      ↓
Store Candidate in SQLite
      ↓
Enter Job Description
      ↓
Hybrid Resume Matching
      ↓
Calculate Match Score
      ↓
Rank Candidates
      ↓
Identify Skill Gaps
      ↓
ATS Analysis
      ↓
Explainable Recommendation
      ↓
Recruiter Dashboard
```

## 🤖 LLM Usage

The system uses LLM-based semantic matching as part of the resume evaluation process.

The LLM is used to:

- Compare resume information with the job description
- Understand semantic relevance
- Support candidate scoring
- Provide justification for candidate alignment
- Identify relevant strengths and gaps

### Example Matching Prompt

```text
Compare the following resume with the following job description.

Resume:
{resume_text}

Job Description:
{job_description}

Evaluate the candidate's suitability on a scale from 1 to 10.

Consider:
- Technical skills
- Relevant experience
- Education
- Job-description relevance

Return a clear score and justification.
```

The project also contains the matching prompt in:

`prompts/matching_prompt.txt`

## 🧠 Hybrid Matching

The application combines structured resume analysis with semantic matching.

The matching process considers:

- Technical skill alignment
- Experience
- Education
- Job-description relevance
- Semantic similarity

The final result is used for candidate ranking and recruiter decision support.

## 📊 Dashboard Outputs

- Total candidates
- Average match score
- Highest match score
- Shortlisted candidates
- Match distribution
- Candidate ranking
- Skill-gap analytics
- Candidate comparison
- Score comparison
- ATS compatibility analysis
- Resume improvement recommendations
- Explainable AI analysis
- Recruiter recommendation

## 🛠️ Technologies Used

- Python
- Streamlit
- SQLite
- PDF/TXT processing
- LLM-based semantic matching
- Hybrid matching
- Pytest

## 📂 Project Structure

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
```

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone https://github.com/Sameer4w/smart-resume-screener.git
cd smart-resume-screener
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

## 🧪 Testing

Run the test suite using:

```bash
pytest
```

Tests cover:

- Database operations
- Resume extraction
- Resume parsing
- LLM matching

## 📌 Assignment Deliverables

This repository contains:

- Application source code
- Resume processing modules
- Hybrid matching implementation
- LLM matching implementation
- Database implementation
- Matching prompt
- Automated tests
- Project documentation

A 2–3 minute demonstration video can be used to demonstrate the complete application workflow.

## 👨‍💻 Project

**Smart Resume Screener**

AI-powered recruitment analytics and candidate decision-support system.
