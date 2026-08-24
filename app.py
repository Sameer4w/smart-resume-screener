import os
import tempfile

import streamlit as st


# ============================================================
# PROFESSIONAL SMART RESUME SCREENER UI
# ============================================================

st.markdown("""
<style>

/* ============================================================
   CURRENT JOB DESCRIPTION — READABLE TEXT
   ============================================================ */

[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #d0d0d0 !important;
    border-radius: 12px !important;
}

/* Expander title */
[data-testid="stExpander"] summary {
    color: #000000 !important;
    font-weight: 600 !important;
}

/* ALL text inside expanded Job Description */
[data-testid="stExpander"] p,
[data-testid="stExpander"] li,
[data-testid="stExpander"] span,
[data-testid="stExpander"] div,
[data-testid="stExpander"] label {
    color: #000000 !important;
}

/* Markdown content inside expander */
[data-testid="stExpander"] [data-testid="stMarkdownContainer"],
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] li,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] span {
    color: #000000 !important;
}

/* Headings */
[data-testid="stExpander"] h1,
[data-testid="stExpander"] h2,
[data-testid="stExpander"] h3,
[data-testid="stExpander"] h4,
[data-testid="stExpander"] strong {
    color: #000000 !important;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
.hero-title {
    color: #4da3ff !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    visibility: visible !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO HEADER
# ============================================================

st.markdown("""
<div class="hero">
<div class="hero-title">📄 Smart Resume Screener</div>
<div class="hero-subtitle">
AI-powered resume analysis, candidate ranking,
skill-gap detection and recruiter decision support.
</div>
</div>
""", unsafe_allow_html=True)



from database import (
    find_existing_resume,
    initialize_database,
    save_resume,
    get_all_resumes,
    get_resume_count,
    get_ranked_resumes,
    save_match_result,
)
from hybrid_matcher import hybrid_match_resume
from resume_extractor import extract_candidate_data
from resume_parser import extract_resume_text





st.set_page_config(
    page_title="Smart Resume Screener",
    page_icon="📄",
    layout="wide",
)

st.markdown("""
<style>

/* Make expanded Current Job Description clearly readable */
[data-testid="stExpander"] {
    background: rgba(20, 25, 35, 0.95) !important;
    border: 1px solid rgba(255, 255, 255, 0.20) !important;
    border-radius: 12px !important;
}

/* Expander title */
[data-testid="stExpander"] summary {
    color: #ffffff !important;
    font-weight: 600 !important;
}

</style>
""", unsafe_allow_html=True)



initialize_database()




st.write(
    "Upload resumes and compare candidates against a job description "
    "using intelligent resume analysis."
)

st.divider()

st.subheader("📊 Candidate Database")

candidate_count = get_resume_count()

st.metric(
    "Stored Candidates",
    candidate_count,
)

with st.expander("View Stored Candidates"):
    stored_candidates = get_all_resumes()

    if not stored_candidates:
        st.info("No candidates have been stored yet.")
    else:
        for candidate in stored_candidates:
            st.markdown(
                f"**{candidate["id"]}. {candidate["name"]}**"
            )
            st.write(
                f"Email: {candidate["email"] or "Not available"}"
            )
            st.write(
                f"Phone: {candidate["phone"] or "Not available"}"
            )
            st.write(
                "Skills: "
                + (
                    ", ".join(candidate["skills"])
                    if candidate["skills"]
                    else "Not available"
                )
            )
            st.divider()

st.subheader("Job Description")

with st.form("job_description_form"):

    job_description_input = st.text_area(
        "Enter the job description",
        height=250,
        placeholder="Paste the job description here...",
    )

    apply_job_description = st.form_submit_button(
        "✅ Apply Job Description",
        type="primary",
    )

if "job_description" not in st.session_state:
    st.session_state.job_description = ""

if apply_job_description:
    st.session_state.job_description = job_description_input.strip()

job_description = st.session_state.job_description

if job_description:
    with st.expander(
        "📋 Current Job Description",
        expanded=False,
    ):
        st.write(job_description)

st.subheader("Resume Upload")

uploaded_files = st.file_uploader(
    "Upload resume files",
    type=["pdf", "txt"],
    accept_multiple_files=True,
)


if uploaded_files:

    st.success(f"{len(uploaded_files)} resume(s) uploaded.")

    # ---------------------------------------------------------
    # Process uploaded resumes
    # ---------------------------------------------------------

    if not job_description.strip():

        st.warning(
            "⚠️ Please apply a job description before processing resumes."
        )

    else:

        import tempfile
        from pathlib import Path

        for uploaded_file in uploaded_files:

            try:

                # -------------------------------------------------
                # 1. Save uploaded file temporarily
                # -------------------------------------------------

                suffix = Path(uploaded_file.name).suffix

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as temp_file:

                    temp_file.write(uploaded_file.getbuffer())
                    temp_path = temp_file.name

                # -------------------------------------------------
                # 2. Extract resume text
                # -------------------------------------------------

                resume_text = extract_resume_text(temp_path)

                if not resume_text.strip():

                    st.error(
                        f"❌ Could not extract text from "
                        f"{uploaded_file.name}"
                    )

                    continue

                # -------------------------------------------------
                # 3. Check duplicate resume
                # -------------------------------------------------

                existing_resume = find_existing_resume(resume_text)

                if existing_resume:

                    st.info(
                        f"ℹ️ {uploaded_file.name} is already "
                        f"stored in the database."
                    )

                    continue

                # -------------------------------------------------
                # 4. Extract candidate information
                # -------------------------------------------------

                candidate = extract_candidate_data(resume_text)

                # Candidate name is not currently extracted
                # from the resume, so use the filename.
                candidate["name"] = Path(
                    uploaded_file.name
                ).stem

                # -------------------------------------------------
                # 5. Save candidate
                # -------------------------------------------------

                resume_id = save_resume(
                    candidate=candidate,
                    resume_text=resume_text,
                )

                # -------------------------------------------------
                # 6. Run Hybrid Matcher
                # -------------------------------------------------

                match_result = hybrid_match_resume(
                    resume_text=resume_text,
                    job_description=job_description,
                    resume_skills=candidate.get("skills", []),
                )

                # -------------------------------------------------
                # 7. Save match result
                # -------------------------------------------------

                save_match_result(
                    resume_id=resume_id,
                    job_description=job_description,
                    match_result=match_result,
                )

                # -------------------------------------------------
                # 8. Show result
                # -------------------------------------------------

                score = match_result.get("match_score", 0)

                st.success(
                    f"✅ {uploaded_file.name} processed successfully!"
                )

                st.write(
                    f"📊 Match Score: **{score}/10**"
                )

                st.write(
                    f"🟢 Matching Skills: "
                    f"{match_result.get('matching_skills', [])}"
                )

                st.write(
                    f"🔴 Missing Skills: "
                    f"{match_result.get('missing_skills', [])}"
                )

            except Exception as exc:

                st.error(
                    f"❌ Could not process "
                    f"{uploaded_file.name}: {exc}"
                )


# ---------------------------------------------------------
# Recalculate existing candidates
# ---------------------------------------------------------

st.markdown("### 🔄 Recalculate Existing Candidates")

st.write(
    "Use the current job description to re-evaluate "
    "all candidates already stored in the database."
)

recalculate_clicked = st.button(
    "🔄 Recalculate All Candidates",
    type="secondary",
    disabled=not job_description.strip(),
)

if recalculate_clicked:

    stored_candidates = get_all_resumes()

    if not stored_candidates:
        st.warning(
            "No stored candidates are available."
        )

    else:
        recalculated_count = 0

        for candidate in stored_candidates:

            try:
                match_result = hybrid_match_resume(
                    resume_text=candidate["resume_text"],
                    job_description=job_description,
                    resume_skills=candidate["skills"],
                )

                save_match_result(
                    resume_id=candidate["id"],
                    job_description=job_description,
                    match_result=match_result,
                )

                recalculated_count += 1

            except Exception as exc:
                st.error(
                    f"Could not recalculate "
                    f"{candidate['name']}: {exc}"
                )

        if recalculated_count:
            st.success(
                f"✅ {recalculated_count} candidate(s) "
                "recalculated successfully."
            )

            st.rerun()


st.subheader("🏆 Candidate Ranking")

ranked_candidates = get_ranked_resumes()

SHORTLIST_THRESHOLD = 7.0

if ranked_candidates:
    min_score = st.slider(
        "Minimum Match Score",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.5,
    )

    ranked_candidates = [
        candidate
        for candidate in ranked_candidates
        if candidate["match_score"] >= min_score
    ]

if not ranked_candidates:
    st.info("No candidates have been scored yet.")
else:
    shortlisted_candidates = [
        candidate
        for candidate in ranked_candidates
        if candidate["match_score"] >= SHORTLIST_THRESHOLD
    ]

    # ---------------------------------------------------------
    # Recruiter Analytics Dashboard
    # ---------------------------------------------------------

    st.markdown("### 📊 Recruiter Analytics Dashboard")

    total_candidates = len(ranked_candidates)

    average_score = sum(
        candidate["match_score"]
        for candidate in ranked_candidates
    ) / total_candidates

    highest_score = max(
        candidate["match_score"]
        for candidate in ranked_candidates
    )

    shortlisted_percentage = (
        len(shortlisted_candidates)
        / total_candidates
        * 100
    )

    average_technical = sum(
        candidate.get("technical_skills_score", 0) or 0
        for candidate in ranked_candidates
    ) / total_candidates

    average_experience = sum(
        candidate.get("experience_score", 0) or 0
        for candidate in ranked_candidates
    ) / total_candidates

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "👥 Total Candidates",
            total_candidates,
        )

    with col2:
        st.metric(
            "📊 Average Score",
            f"{average_score:.2f}/10",
        )

    with col3:
        st.metric(
            "🏆 Highest Score",
            f"{highest_score:.1f}/10",
        )

    with col4:
        st.metric(
            "⭐ Shortlisted",
            f"{shortlisted_percentage:.0f}%",
        )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "💻 Avg Technical Skills",
            f"{average_technical:.2f}/6",
        )

    with col2:
        st.metric(
            "💼 Avg Experience",
            f"{average_experience:.2f}/2",
        )

    st.divider()

    st.metric(
        "Shortlisted Candidates",
        len(shortlisted_candidates),
    )

    if shortlisted_candidates:
        st.markdown("### ⭐ Shortlisted Candidates")

        for candidate in shortlisted_candidates:
            st.success(
                f"{candidate["name"]} — "
                f"{candidate["match_score"]}/10"
            )
    else:
        st.info(
            f"No candidates reached the "
            f"{SHORTLIST_THRESHOLD}/10 shortlist threshold."
        )

    if ranked_candidates:
        excellent_count = sum(
            1 for candidate in ranked_candidates
            if candidate["match_score"] >= 8
        )

        good_count = sum(
            1 for candidate in ranked_candidates
            if 6 <= candidate["match_score"] < 8
        )

        low_count = sum(
            1 for candidate in ranked_candidates
            if candidate["match_score"] < 6
        )

        st.markdown("### 📈 Match Distribution")

        col1, col2, col3 = st.columns(3)

        col1.metric("Excellent (8–10)", excellent_count)
        col2.metric("Good (6–7.9)", good_count)
        col3.metric("Low (<6)", low_count)

        top_candidate = ranked_candidates[0]

        st.markdown("### 🥇 Top Candidate")

        st.info(
            f"**{top_candidate["name"]}** — "
            f"{top_candidate["match_score"]}/10"
        )

    # Candidate Recommendation
    st.markdown("### 🥇 Candidate Recommendation")

    if ranked_candidates:
        best_candidate = ranked_candidates[0]

        st.success(
            f"Recommended Candidate: "
            f"{best_candidate["name"]} — "
            f"{best_candidate["match_score"]}/10"
        )

        st.write(
            "**Why this candidate?**"
        )

        st.write(
            "This candidate achieved the highest match score "
            "among the evaluated candidates."
        )

        if best_candidate["matching_skills"]:
            st.write(
                "**Strong Matching Skills:** "
                + ", ".join(
                    best_candidate["matching_skills"]
                )
            )

        if best_candidate["missing_skills"]:
            st.write(
                "**Skills to Improve:** "
                + ", ".join(
                    best_candidate["missing_skills"]
                )
            )
        else:
            st.write(
                "**Skills to Improve:** None identified"
            )

        breakdown = {
            "Technical Skills": best_candidate.get(
                "technical_skills_score", 0
            ),
            "Experience": best_candidate.get(
                "experience_score", 0
            ),
            "Education": best_candidate.get(
                "education_score", 0
            ),
            "Relevance": best_candidate.get(
                "relevance_score", 0
            ),
        }

        st.write("**Score Breakdown:**")

        for component, value in breakdown.items():
            st.write(
                f"- {component}: {value}"
            )

        if len(ranked_candidates) >= 2:
            second_candidate = ranked_candidates[1]

            score_difference = (
                best_candidate["match_score"]
                - second_candidate["match_score"]
            )

            st.info(
                f"Score advantage over the next candidate: "
                f"{score_difference:.1f} points"
            )

        # Recruiter Decision
        st.markdown("### 🧑‍💼 Recruiter Decision")

        best_score = best_candidate["match_score"]
        missing_count = len(
            best_candidate["missing_skills"]
        )

        if best_score >= 8 and missing_count == 0:
            decision = "🥇 Strongly Recommended"
            explanation = (
                "The candidate has excellent alignment with the "
                "job requirements and no identified skill gaps."
            )
        elif best_score >= 7:
            decision = "✅ Recommended with Reservations"
            explanation = (
                "The candidate has good overall alignment, but "
                "some skill or experience gaps may need attention."
            )
        elif best_score >= 5:
            decision = "⚠️ Consider for Further Review"
            explanation = (
                "The candidate has partial alignment with the role. "
                "Additional evaluation is recommended."
            )
        else:
            decision = "❌ Not Recommended"
            explanation = (
                "The candidate has limited alignment with the "
                "current job requirements."
            )

        st.info(
            f"**{decision}**"
        )

        st.write(
            f"**Overall Score:** {best_score}/10"
        )

        st.write(
            f"**Decision Reason:** {explanation}"
        )

        if missing_count:
            st.write(
                "**Key Skill Gaps:** "
                + ", ".join(
                    best_candidate["missing_skills"]
                )
            )
        else:
            st.write(
                "**Key Skill Gaps:** None identified"
            )

    st.markdown("### 📋 All Ranked Candidates")

    ranking_table = []

    for rank, candidate in enumerate(ranked_candidates, start=1):
        ranking_table.append(
            {
                "Rank": rank,
                "Candidate": candidate["name"],
                "Email": candidate["email"] or "Not available",
                "Score": candidate["match_score"],
                "Status": (
                    "Shortlisted"
                    if candidate["match_score"] >= SHORTLIST_THRESHOLD
                    else "Not Shortlisted"
                ),
                "Matching Skills": ", ".join(
                    candidate["matching_skills"]
                ),
                "Missing Skills": ", ".join(
                    candidate["missing_skills"]
                ),
            }
        )

    st.dataframe(
        ranking_table,
        width="stretch",
        hide_index=True,
    )

    # Export ranked candidates
    import pandas as pd

    export_data = []

    for candidate in ranked_candidates:
        export_data.append(
            {
                "Rank": ranked_candidates.index(candidate) + 1,
                "Candidate": candidate["name"],
                "Email": candidate["email"] or "Not available",
                "Score": candidate["match_score"],
                "Technical Skills Score": candidate.get(
                    "technical_skills_score", 0
                ),
                "Experience Score": candidate.get(
                    "experience_score", 0
                ),
                "Education Score": candidate.get(
                    "education_score", 0
                ),
                "Relevance Score": candidate.get(
                    "relevance_score", 0
                ),
                "Matching Skills": ", ".join(
                    candidate["matching_skills"]
                ),
                "Missing Skills": ", ".join(
                    candidate["missing_skills"]
                ),
                "Status": (
                    "Shortlisted"
                    if candidate["match_score"]
                    >= SHORTLIST_THRESHOLD
                    else "Not Shortlisted"
                ),
            }
        )

    export_df = pd.DataFrame(export_data)

    csv_data = export_df.to_csv(index=False)

    st.download_button(
        label="📥 Download Ranked Candidates CSV",
        data=csv_data,
        file_name="ranked_candidates.csv",
        mime="text/csv",
    )


    st.divider()

    
# ============================================================
# Skill Gap Analytics
# ============================================================

st.markdown("### 🧠 Skill Gap Analytics")

if ranked_candidates:

    all_missing_skills = []

    for candidate in ranked_candidates:
        all_missing_skills.extend(
            candidate.get("missing_skills", [])
        )

    if all_missing_skills:

        from collections import Counter

        skill_counts = Counter(
            skill.lower()
            for skill in all_missing_skills
        )

        skill_gap_data = [
            {
                "Skill": skill,
                "Candidates Missing": count,
            }
            for skill, count in skill_counts.most_common()
        ]

        st.dataframe(
            skill_gap_data,
            width="stretch",
            hide_index=True,
        )

        st.markdown("#### 🔴 Most Common Skill Gaps")

        for skill, count in skill_counts.most_common(5):
            st.write(
                f"**{skill}** — missing in "
                f"{count} candidate(s)"
            )

    else:
        st.success(
            "No major skill gaps identified among the "
            "evaluated candidates."
        )

else:
    st.info(
        "Skill gap analytics will appear after "
        "candidates are scored."
    )


st.markdown("### 🔍 Candidate Comparison")

if len(ranked_candidates) >= 2:

    candidate_names = [
        candidate["name"]
        for candidate in ranked_candidates
    ]

    selected_candidates = st.multiselect(
        "Select candidates to compare",
        candidate_names,
        default=candidate_names[:2],
    )

    if len(selected_candidates) >= 2:

        comparison_candidates = [
            candidate
            for candidate in ranked_candidates
            if candidate["name"] in selected_candidates
        ]

        comparison_table = []

        for candidate in comparison_candidates:
            comparison_table.append(
                {
                    "Candidate": candidate["name"],
                    "Score": f'{candidate["match_score"]}/10',
                    "Technical Skills": (
                        f'{candidate.get("technical_skills_score", 0):.2f}/6'
                    ),
                    "Experience": (
                        f'{candidate.get("experience_score", 0):.2f}/2'
                    ),
                    "Education": (
                        f'{candidate.get("education_score", 0):.2f}/1'
                    ),
                    "Relevance": (
                        f'{candidate.get("relevance_score", 0):.2f}/1'
                    ),
                    "Matching Skills": (
                        ", ".join(candidate["matching_skills"]) or "None"
                    ),
                    "Missing Skills": (
                        ", ".join(candidate["missing_skills"]) or "None"
                    ),
                    "Status": (
                        "Shortlisted"
                        if candidate["match_score"] >= SHORTLIST_THRESHOLD
                        else "Not Shortlisted"
                    ),
                }
            )

        st.dataframe(
            comparison_table,
            width="stretch",
            hide_index=True,
        )

        # Visual Score Comparison

        st.markdown("### 📊 Score Comparison")

        chart_data = []

        for candidate in comparison_candidates:
            chart_data.append(
                {
                    "Candidate": candidate["name"],
                    "Technical Skills": candidate.get(
                        "technical_skills_score", 0
                    ),
                    "Experience": candidate.get(
                        "experience_score", 0
                    ),
                    "Education": candidate.get(
                        "education_score", 0
                    ),
                    "Relevance": candidate.get(
                        "relevance_score", 0
                    ),
                }
            )

        import pandas as pd

        chart_df = pd.DataFrame(chart_data)

        st.bar_chart(
            chart_df.set_index("Candidate"),
            stack=False,
        )

    else:
        st.info(
            "Select at least two candidates to compare."
        )

else:
    st.info(
        "At least two scored candidates are required for comparison."
    )

    for rank, candidate in enumerate(ranked_candidates, start=1):
        score = candidate["match_score"]

        st.markdown(
            f"**#{rank} — {candidate["name"]}**"
        )

        st.write(
            f"Match Score: **{score}/10**"
        )

        st.write(
            f"Email: {candidate["email"] or "Not available"}"
        )

        if candidate["matching_skills"]:
            st.write(
                "Matching Skills: "
                + ", ".join(candidate["matching_skills"])
            )

        if candidate["missing_skills"]:
            st.write(
                "Missing Skills: "
                + ", ".join(candidate["missing_skills"])
            )

        if candidate["justification"]:
            st.write(
                "Justification:",
                candidate["justification"]
            )

        st.divider()


# ============================================================
# 📄 Resume Quality / ATS Analysis
# ============================================================

st.divider()

st.markdown("### 📄 Resume Quality / ATS Analysis")

if ranked_candidates:

    st.write(
        "Analyze each candidate's ATS compatibility "
        "based on job match and required skill coverage."
    )

    for candidate in ranked_candidates:

        matching_count = len(
            candidate.get("matching_skills", [])
        )

        missing_count = len(
            candidate.get("missing_skills", [])
        )

        total_skills = matching_count + missing_count

        if total_skills > 0:
            skill_coverage = (
                matching_count / total_skills
            ) * 100
        else:
            skill_coverage = 0

        match_score = candidate.get(
            "match_score", 0
        )

        ats_score = (
            (match_score / 10) * 70
            + (skill_coverage / 100) * 30
        )

        ats_score = min(
            100,
            round(ats_score, 2)
        )

        st.markdown(
            f"#### 👤 {candidate['name']}"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "ATS Score",
            f"{ats_score}/100"
        )

        col2.metric(
            "Skill Coverage",
            f"{skill_coverage:.1f}%"
        )

        col3.metric(
            "Job Match",
            f"{match_score}/10"
        )

        if ats_score >= 80:

            st.success(
                "🟢 Strong ATS compatibility"
            )

        elif ats_score >= 60:

            st.warning(
                "🟡 Moderate ATS compatibility"
            )

        else:

            st.error(
                "🔴 Low ATS compatibility"
            )

        if candidate.get("missing_skills"):

            st.write(
                "**Recommended Improvements:**"
            )

            for skill in candidate["missing_skills"]:

                st.write(
                    f"- Strengthen **{skill}** "
                    "if you have this skill."
                )

        else:

            st.write(
                "✅ No major skill gaps identified."
            )


# ============================================================
# 📝 Resume Improvement Recommendations
# ============================================================

st.divider()

st.markdown("### 📝 Resume Improvement Recommendations")

if ranked_candidates:

    st.write(
        "Get actionable recommendations for improving each "
        "candidate's resume based on the current job description."
    )

    for candidate in ranked_candidates:

        st.markdown(
            f"#### 👤 {candidate['name']}"
        )

        matching_skills = candidate.get(
            "matching_skills", []
        )

        missing_skills = candidate.get(
            "missing_skills", []
        )

        recommendations = []

        # Skill recommendations
        if missing_skills:

            for skill in missing_skills:
                recommendations.append(
                    f"Strengthen or add **{skill}** "
                    "if you have relevant experience."
                )

        # Experience recommendation
        experience_score = candidate.get(
            "experience_score", 0
        )

        if experience_score < 2:

            recommendations.append(
                "Add more relevant backend development "
                "experience, internships, or academic projects."
            )

        # Technical skills recommendation
        technical_score = candidate.get(
            "technical_skills_score", 0
        )

        if technical_score < 4:

            recommendations.append(
                "Improve the Technical Skills section by "
                "highlighting technologies directly related "
                "to the job description."
            )

        # Project recommendation
        if candidate.get("relevance_score", 0) < 0.5:

            recommendations.append(
                "Improve project descriptions by clearly "
                "mentioning your role, technologies used, "
                "and contribution."
            )

        # General ATS recommendation
        recommendations.append(
            "Use clear section headings and include relevant "
            "job-description keywords naturally throughout "
            "the resume."
        )

        if recommendations:

            for number, recommendation in enumerate(
                recommendations,
                start=1
            ):

                st.write(
                    f"**{number}.** {recommendation}"
                )

        else:

            st.success(
                "✅ No major improvements identified."
            )

        st.caption(
            f"Current Match Score: "
            f"{candidate.get('match_score', 0)}/10"
        )

else:

    st.info(
        "Resume improvement recommendations will appear "
        "after candidates are scored."
    )



# ============================================================
# RESUME IMPROVEMENT RECOMMENDATIONS
# ============================================================

st.markdown("### 📌 Resume Improvement Recommendations")

if ranked_candidates:

    recommendation_candidate = ranked_candidates[0]

    st.write(
        f"**Candidate:** {recommendation_candidate['name']}"
    )

    missing_skills = recommendation_candidate.get(
        "missing_skills", []
    )

    matching_skills = recommendation_candidate.get(
        "matching_skills", []
    )

    st.write(
        f"**Current Match Score:** "
        f"{recommendation_candidate['match_score']}/10"
    )

    if missing_skills:

        st.info(
            "The recommendations below focus on improving "
            "the candidate's alignment with the current job description."
        )

        st.markdown("#### 🛠️ Recommended Improvements")

        # ----------------------------------------------------
        # Skills Section
        # ----------------------------------------------------

        st.markdown("**1. Skills Section**")

        st.write(
            "Review the job description and add missing skills "
            "that the candidate genuinely possesses or has relevant "
            "experience with."
        )

        st.write(
            "**Missing skills:** "
            + ", ".join(missing_skills)
        )

        # ----------------------------------------------------
        # Technical Skills
        # ----------------------------------------------------

        st.markdown("**2. Technical Skills**")

        st.write(
            "Highlight relevant programming languages, frameworks, "
            "databases, APIs, development tools, and technologies "
            "that match the target role."
        )

        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        st.markdown("**3. Experience**")

        st.write(
            "Add measurable achievements and clearly describe "
            "backend development responsibilities, technologies "
            "used, and the candidate's contribution."
        )

        # ----------------------------------------------------
        # Projects
        # ----------------------------------------------------

        st.markdown("**4. Projects**")

        st.write(
            "Strengthen relevant projects by mentioning the "
            "technologies used, backend functionality implemented, "
            "APIs developed, databases used, and the candidate's "
            "specific contribution."
        )

        # ----------------------------------------------------
        # Job Alignment
        # ----------------------------------------------------

        st.markdown("**5. Job Alignment**")

        st.write(
            "Prioritize skills and experience that directly appear "
            "in the job description. Use clear and relevant "
            "terminology so recruiters can quickly identify "
            "the candidate's suitability."
        )

    else:

        st.success(
            "No major skill gaps were identified. "
            "The resume already has strong alignment with "
            "the current job description."
        )

        st.markdown("#### ⭐ Maintain Strong Alignment")

        st.write(
            "Continue emphasizing the candidate's strongest "
            "matching skills and relevant experience."
        )

        if matching_skills:
            st.write(
                "**Strong matching skills:** "
                + ", ".join(matching_skills)
            )

else:

    st.info(
        "Resume improvement recommendations will appear "
        "after candidates are scored."
    )





# ============================================================
# ADVANCED NLP / SEMANTIC SKILL MATCHING
# ============================================================



# ============================================================
# EXPLAINABLE AI
# ============================================================

def generate_candidate_explanation(candidate):
    """
    Generates a transparent explanation of the candidate score.
    Uses the existing scoring components rather than replacing
    the scoring system.
    """

    score = candidate.get("match_score", 0)

    technical = candidate.get(
        "technical_skills_score", 0
    )

    experience = candidate.get(
        "experience_score", 0
    )

    education = candidate.get(
        "education_score", 0
    )

    relevance = candidate.get(
        "relevance_score", 0
    )

    matching_skills = candidate.get(
        "matching_skills", []
    )

    missing_skills = candidate.get(
        "missing_skills", []
    )

    strengths = []
    weaknesses = []

    # --------------------------------------------------------
    # Technical Skills
    # --------------------------------------------------------

    if technical >= 5:
        strengths.append(
            "Strong technical skill alignment"
        )
    elif technical >= 3:
        strengths.append(
            "Moderate technical skill alignment"
        )
    else:
        weaknesses.append(
            "Limited technical skill alignment"
        )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    if experience >= 1.5:
        strengths.append(
            "Relevant experience"
        )
    elif experience >= 1:
        strengths.append(
            "Some relevant experience"
        )
    else:
        weaknesses.append(
            "Limited relevant experience"
        )

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    if education >= 0.75:
        strengths.append(
            "Education matches the expected qualification"
        )
    else:
        weaknesses.append(
            "Education alignment could be stronger"
        )

    # --------------------------------------------------------
    # Relevance
    # --------------------------------------------------------

    if relevance >= 0.7:
        strengths.append(
            "High overall job-description relevance"
        )
    elif relevance >= 0.4:
        strengths.append(
            "Reasonable job-description relevance"
        )
    else:
        weaknesses.append(
            "Low overall job-description relevance"
        )

    # --------------------------------------------------------
    # Missing Skills
    # --------------------------------------------------------

    if missing_skills:
        weaknesses.append(
            "Missing required skills: "
            + ", ".join(missing_skills)
        )

    # --------------------------------------------------------
    # Overall explanation
    # --------------------------------------------------------

    if score >= 8:
        decision = "Strong candidate alignment"
    elif score >= 7:
        decision = "Good candidate alignment"
    elif score >= 5:
        decision = "Partial candidate alignment"
    else:
        decision = "Low candidate alignment"

    return {
        "decision": decision,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "score_components": {
            "Technical Skills": technical,
            "Experience": experience,
            "Education": education,
            "Relevance": relevance,
        },
    }



def semantic_skill_match(resume_text, job_description):
    """
    Detect related technical terms using lightweight
    semantic keyword groups.

    This supplements exact skill matching and does not
    replace the existing scoring system.
    """

    text = (
        (resume_text or "") + " " +
        (job_description or "")
    ).lower()

    semantic_groups = {
        "rest api": [
            "rest api",
            "restful api",
            "restful services",
            "rest services",
            "web api",
            "http api",
            "api development",
        ],

        "sql": [
            "sql",
            "mysql",
            "postgresql",
            "postgres",
            "database queries",
            "relational database",
            "relational databases",
        ],

        "git": [
            "git",
            "github",
            "gitlab",
            "version control",
            "source control",
        ],

        "backend development": [
            "backend",
            "back-end",
            "server-side",
            "server side",
            "backend development",
            "backend applications",
            "web services",
        ],

        "python": [
            "python",
            "python programming",
            "python development",
        ],

        "java": [
            "java",
            "java programming",
            "java development",
        ],

        "spring boot": [
            "spring boot",
            "springboot",
            "spring framework",
        ],

        "fastapi": [
            "fastapi",
            "fast api",
            "python web framework",
        ],

        "docker": [
            "docker",
            "containerization",
            "containers",
            "docker containers",
        ],

        "postgresql": [
            "postgresql",
            "postgres",
            "postgres database",
        ],
    }

    detected = []

    for canonical_skill, variants in semantic_groups.items():

        found = False

        for variant in variants:
            if variant in text:
                found = True
                break

        if found:
            detected.append(canonical_skill)

    return detected


def calculate_semantic_bonus(
    resume_text,
    job_description,
    existing_matching_skills=None
):
    """
    Calculates a small semantic alignment bonus.

    Exact matching remains the primary scoring mechanism.
    Semantic matching provides additional evidence when
    equivalent terminology is used.
    """

    existing_matching_skills = (
        existing_matching_skills or []
    )

    semantic_matches = semantic_skill_match(
        resume_text,
        job_description
    )

    new_matches = [
        skill
        for skill in semantic_matches
        if skill.lower()
        not in [
            str(existing).lower()
            for existing in existing_matching_skills
        ]
    ]

    bonus = min(
        len(new_matches) * 0.15,
        0.75
    )

    return round(bonus, 2), new_matches



# ============================================================
# EXPLAINABLE AI RESULTS
# ============================================================

st.markdown("### 🧠 Explainable AI Analysis")

if ranked_candidates:

    explain_candidate = ranked_candidates[0]

    explanation = generate_candidate_explanation(
        explain_candidate
    )

    st.write(
        f"**Candidate:** "
        f"{explain_candidate['name']}"
    )

    st.write(
        f"**AI Assessment:** "
        f"{explanation['decision']}"
    )

    st.markdown("#### ✅ Why This Candidate Scored This Way")

    for strength in explanation["strengths"]:
        st.success(strength)

    if explanation["matching_skills"]:

        st.markdown("#### 💻 Matching Skills")

        st.write(
            ", ".join(
                explanation["matching_skills"]
            )
        )

    if explanation["weaknesses"]:

        st.markdown("#### ⚠️ Areas Requiring Attention")

        for weakness in explanation["weaknesses"]:
            st.warning(weakness)

    st.markdown("#### 📊 Transparent Score Contribution")

    score_components = explanation["score_components"]

    for component, value in score_components.items():

        st.write(
            f"**{component}:** {value}"
        )

else:

    st.info(
        "Explainable AI analysis will appear "
        "after candidates are scored."
    )


# ============================================================
# APPLICATION FOOTER
# ============================================================

st.markdown(
    """
    <div class="final-footer">
        Smart Resume Screener · AI-powered recruitment analytics
    </div>
    """,
    unsafe_allow_html=True,
)



# ============================================================
# FINAL UI POLISH
# ============================================================

st.markdown("""
<style>

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
}

/* Main buttons */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    min-height: 45px;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
}

/* Download button */
.stDownloadButton > button {
    width: 100%;
    border-radius: 12px;
    min-height: 45px;
    font-weight: 700;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: white;
    border-radius: 16px;
    padding: 10px;
}

/* Metrics */
[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 14px rgba(15,23,42,0.06);
}

/* Expanders */
[data-testid="stExpander"] {
    background: white;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
}

/* Tables */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    border: 1px solid #e2e8f0;
}

/* Text inputs */
textarea,
input {
    border-radius: 12px !important;
}

/* Section spacing */
h2, h3 {
    margin-top: 25px;
}

/* Success / info boxes */
[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Footer */
.final-footer {
    margin-top: 50px;
    padding: 25px;
    text-align: center;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
}



/* ============================================================
   FINAL UI READABILITY FIX
   ============================================================ */

/* Streamlit metric cards */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border-radius: 16px !important;
    border: 1px solid #e2e8f0 !important;
    padding: 18px !important;
    box-shadow: 0 4px 14px rgba(15,23,42,0.06) !important;
}

[data-testid="stMetric"] label {
    color: #64748b !important;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #0f172a !important;
}

/* Streamlit expandable sections */
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {
    color: #0f172a !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background: #ffffff !important;
    border-radius: 14px !important;
}

/* Text inside white containers */
.stMarkdown,
.stMarkdown p,
.stMarkdown li {
    color: inherit;
}

/* Candidate cards */
.candidate-card {
    background: #ffffff !important;
    color: #0f172a !important;
}

.candidate-card * {
    color: #0f172a !important;
}

/* Metric labels and values */
.metric-card {
    background: #ffffff !important;
    color: #0f172a !important;
}

.metric-card .metric-label {
    color: #64748b !important;
}

.metric-card .metric-value {
    color: #0f172a !important;
}

/* Inputs */
textarea,
input {
    color: #0f172a !important;
    background: #ffffff !important;
}

/* Select boxes */
[data-baseweb="select"] {
    background: #ffffff !important;
}

[data-baseweb="select"] * {
    color: #0f172a !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    color: #0f172a !important;
    border-radius: 16px !important;
}

/* File uploader drop zone */
[data-testid="stFileUploader"] section {
    background: #ffffff !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 14px !important;
    padding: 16px !important;
}

/* Upload button */
[data-testid="stFileUploader"] button {
    background: #4f46e5 !important;
    color: #ffffff !important;
    border: 1px solid #4338ca !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}

/* Upload button text */
[data-testid="stFileUploader"] button span {
    color: #ffffff !important;
}

/* Upload button icon */
[data-testid="stFileUploader"] button svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}

/* Hover */
[data-testid="stFileUploader"] button:hover {
    background: #4338ca !important;
    color: #ffffff !important;
}

/* Drag and drop text */
[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section span {
    color: #334155 !important;
}

/* Uploaded file name */
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
    background: #f8fafc !important;
    color: #0f172a !important;
}

/* Slider labels */
[data-testid="stSlider"] label {
    color: #f8fafc !important;
}

/* General headings */
h1, h2, h3, h4, h5, h6 {
    color: #f8fafc !important;
}

/* Horizontal lines */
hr {
    border-color: #334155 !important;
}

</style>
""", unsafe_allow_html=True)



    
# ============================================================
# FINAL UI CONTRAST FIX
# ============================================================

st.markdown("""
<style>

/* Fix metric visibility */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 18px !important;
}

[data-testid="stMetricLabel"] {
    color: #475569 !important;
}

[data-testid="stMetricValue"] {
    color: #0f172a !important;
}

[data-testid="stMetricDelta"] {
    color: #475569 !important;
}

/* Improve text visibility */
[data-testid="stMetric"] p,
[data-testid="stMetric"] div {
    color: #0f172a !important;
}

</style>
""", unsafe_allow_html=True)




