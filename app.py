import os

import google.generativeai as genai
import streamlit as st
from pypdf import PdfReader

from analyzer import analyze_resume
from comparison import compare_resumes

# ==========================
# GEMINI CONFIG
# ==========================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Career Assistant")
st.write(
    "Upload your resume and compare it with a Job Description to get ATS insights, skill-gap analysis, and a learning roadmap."
)


# ==========================
# HELPERS
# ==========================

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def render_string_list(items, success=False, warn=False, empty_message=None):
    if items:
        for item in items:
            if success:
                st.success(item)
            elif warn:
                st.warning(item)
            else:
                st.write(f"• {item}")
    elif empty_message:
        st.info(empty_message)


# ==========================
# FILE UPLOAD
# ==========================

uploaded_file = st.file_uploader(
    "Upload Resume PDF",
    type=["pdf"]
)

old_resume = st.file_uploader(
    "Upload Previous Resume",
    type=["pdf"],
    key="old_resume"
)

new_resume = st.file_uploader(
    "Upload Updated Resume",
    type=["pdf"],
    key="new_resume"
)

# ==========================
# JOB DESCRIPTION
# ==========================

st.subheader("📋 Job Description")
job_description = st.text_area(
    "Paste Job Description Here",
    height=250
)

# ==========================
# RESUME ANALYSIS
# ==========================

if uploaded_file is not None:
    resume_text = extract_text_from_pdf(uploaded_file)

    if len(resume_text.strip()) < 50:
        st.error("Unable to extract enough text from PDF.")
    else:
        st.success("Resume uploaded successfully!")

        with st.expander("View Resume Text"):
            st.text_area(
                "Resume Content",
                resume_text,
                height=250
            )

        if st.button("🚀 Analyze Resume"):
            if not job_description.strip():
                st.warning("Please paste a Job Description.")
            else:
                with st.spinner("Analyzing Resume..."):
                    try:
                        result = analyze_resume(
                            model,
                            resume_text,
                            job_description
                        )

                        ats_score = int(result.get("ats_score", 0))
                        ats_score = min(max(ats_score, 0), 100)

                        st.header("📊 ATS Dashboard")
                        st.metric("ATS Score", f"{ats_score}/100")
                        st.progress(ats_score)

                        tab1, tab2, tab3, tab4 = st.tabs(
                            ["Skills", "Analysis", "Suggestions", "Roadmap"]
                        )

                        with tab1:
                            col1, col2 = st.columns(2)

                            with col1:
                                st.subheader("✅ Matching Skills")
                                render_string_list(
                                    result.get("matching_skills", []),
                                    success=True,
                                    empty_message="No matching skills identified."
                                )

                            with col2:
                                st.subheader("❌ Missing Skills")
                                render_string_list(
                                    result.get("missing_skills", []),
                                    warn=True,
                                    empty_message="No missing skills identified."
                                )

                        with tab2:
                            st.subheader("Resume Summary")
                            st.write(result.get("resume_summary", ""))

                            st.subheader("💪 Strengths")
                            render_string_list(
                                result.get("strengths", []),
                                empty_message="No strengths returned by the model."
                            )

                            st.subheader("⚠ Weaknesses")
                            render_string_list(
                                result.get("weaknesses", []),
                                empty_message="No weaknesses returned by the model."
                            )

                        with tab3:
                            st.subheader("🚀 Suggestions")
                            render_string_list(
                                result.get("suggestions", []),
                                empty_message="No suggestions returned by the model."
                            )

                        with tab4:
                            st.subheader("📚 Learning Roadmap")
                            render_string_list(
                                result.get("learning_roadmap", []),
                                empty_message="No roadmap returned by the model."
                            )

                        st.balloons()
                    except Exception as e:
                        st.error(f"Analysis Error: {e}")

# ==========================
# RESUME COMPARISON SECTION
# ==========================

st.markdown("---")
st.header("📈 Resume Progress Tracker")

if old_resume is not None and new_resume is not None:
    if st.button("📊 Compare Resumes"):
        try:
            old_resume_text = extract_text_from_pdf(old_resume)
            new_resume_text = extract_text_from_pdf(new_resume)

            with st.spinner("Comparing resumes..."):
                comparison = compare_resumes(
                    model,
                    old_resume_text,
                    new_resume_text
                )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Old ATS Score",
                    comparison.get("old_ats_score", 0)
                )

            with col2:
                st.metric(
                    "New ATS Score",
                    comparison.get("new_ats_score", 0)
                )

            with col3:
                st.metric(
                    "Improvement",
                    f"+{comparison.get('improvement_score', 0)}"
                )

            st.subheader("✅ New Skills Added")
            render_string_list(
                comparison.get("new_skills_added", []),
                success=True,
                empty_message="No new skills detected."
            )

            st.subheader("❌ Removed Skills")
            render_string_list(
                comparison.get("removed_skills", []),
                warn=True,
                empty_message="No removed skills."
            )

            st.subheader("🚀 Improved Sections")
            render_string_list(
                comparison.get("improved_sections", []),
                empty_message="No improved sections returned by the model."
            )

            st.subheader("⚠ Sections Still Weak")
            render_string_list(
                comparison.get("weak_sections", []),
                empty_message="No weak sections returned by the model."
            )

            st.subheader("📋 Overall Feedback")
            st.info(comparison.get("overall_feedback", "No feedback available."))

        except Exception as e:
            st.error(f"Comparison Error: {e}")
else:
    st.info("Upload both the previous resume and the updated resume to compare them.")
