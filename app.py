import os
import tempfile

import streamlit as st

from database import (
    initialize_database,
    save_resume,
    get_all_resumes,
    get_resume_count,
    get_ranked_resumes,
    save_match_result,
)
from llm_matcher import match_resume_to_job
from resume_extractor import extract_candidate_data
from resume_parser import extract_resume_text


st.set_page_config(
    page_title="Smart Resume Screener",
    page_icon="📄",
    layout="wide",
)


initialize_database()


st.title("📄 Smart Resume Screener")

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

st.subheader("🏆 Candidate Ranking")

ranked_candidates = get_ranked_resumes()

if not ranked_candidates:
    st.info("No candidates have been scored yet.")
else:
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

st.subheader("Job Description")

job_description = st.text_area(
    "Enter the job description",
    height=250,
    placeholder="Paste the job description here...",
)

st.subheader("Resume Upload")

uploaded_files = st.file_uploader(
    "Upload resume files",
    type=["pdf", "txt"],
    accept_multiple_files=True,
)


if uploaded_files:
    st.success(f"{len(uploaded_files)} resume(s) uploaded.")


if job_description.strip() and uploaded_files:

    st.divider()

    st.subheader("Resume Analysis")

    if st.button("Process Resumes", type="primary"):

        processed_count = 0

        for uploaded_file in uploaded_files:

            suffix = os.path.splitext(uploaded_file.name)[1].lower()

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as temporary_file:

                temporary_file.write(uploaded_file.getvalue())
                temporary_path = temporary_file.name

            try:
                resume_text = extract_resume_text(temporary_path)

                if not resume_text.strip():
                    st.warning(
                        f"Could not extract text from {uploaded_file.name}."
                    )
                    continue

                candidate = extract_candidate_data(resume_text)

                candidate["name"] = os.path.splitext(
                    uploaded_file.name
                )[0]

                resume_id = save_resume(
                    candidate,
                    resume_text,
                )

                processed_count += 1

                st.success(
                    f"{uploaded_file.name} processed successfully "
                    f"(ID: {resume_id})."
                )

                with st.expander(
                    f"Extracted data — {uploaded_file.name}"
                ):
                    st.write("**Email:**", candidate["email"])
                    st.write("**Phone:**", candidate["phone"])
                    st.write("**Skills:**", candidate["skills"])
                    st.write("**Education:**", candidate["education"])
                    st.write("**Experience:**", candidate["experience"])

                st.markdown("### 🤖 Job Match")

                try:
                    match_result = match_resume_to_job(
                        resume_text=resume_text,
                        job_description=job_description,
                    )

                    save_match_result(
                        resume_id=resume_id,
                        job_description=job_description,
                        match_result=match_result,
                    )

                    st.metric(
                        "Match Score",
                        f"{match_result['match_score']}/10",
                    )

                    st.write(
                        "**Summary:**",
                        match_result["summary"],
                    )

                    st.write(
                        "**Matching Skills:**",
                        ", ".join(match_result["matching_skills"])
                        or "None identified",
                    )

                    st.write(
                        "**Missing Skills:**",
                        ", ".join(match_result["missing_skills"])
                        or "None identified",
                    )

                    st.write(
                        "**Experience Match:**",
                        match_result["experience_match"],
                    )

                    st.write(
                        "**Education Match:**",
                        match_result["education_match"],
                    )

                    st.write(
                        "**Justification:**",
                        match_result["justification"],
                    )

                except Exception as match_error:
                    st.warning(
                        "AI matching is temporarily unavailable. "
                        "Please configure a valid LLM API key."
                    )

            except Exception as exc:
                st.error(
                    f"Error processing {uploaded_file.name}: {exc}"
                )

            finally:
                try:
                    os.remove(temporary_path)
                except OSError:
                    pass

        if processed_count:
            st.info(
                f"{processed_count} resume(s) processed and stored."
            )
