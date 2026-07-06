import os
import html
import re

import google.generativeai as genai
import streamlit as st
from pypdf import PdfReader

from analyzer import analyze_resume
from comparison import compare_resumes

# ==========================
# GEMINI CONFIG
# ==========================



genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(34, 197, 94, 0.12), transparent 24%),
                radial-gradient(circle at top right, rgba(59, 130, 246, 0.12), transparent 22%),
                linear-gradient(180deg, #0a1020 0%, #111b2e 100%);
        }

        .main .block-container {
            max-width: 1180px;
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            color: #e5eefc;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #08101e 0%, #0d1729 100%);
        }

        section[data-testid="stSidebar"] * {
            color: #dbe7f7;
        }

        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown li,
        section[data-testid="stSidebar"] .stCaption {
            color: rgba(248, 250, 252, 0.8) !important;
        }

        .hero-card {
            background: linear-gradient(135deg, #0d1727 0%, #13233d 100%);
            color: #f8fafc;
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 28px;
            padding: 1.6rem 1.8rem 1.45rem 1.8rem;
            box-shadow: 0 24px 52px rgba(3, 8, 20, 0.38);
        }

        .hero-eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.72rem;
            font-weight: 700;
            color: #fbbf24;
            margin-bottom: 0.55rem;
        }

        .hero-card h1 {
            margin: 0;
            font-size: 2.4rem;
            line-height: 1.05;
        }

        .hero-card p {
            margin-top: 0.85rem;
            margin-bottom: 0;
            color: rgba(248, 250, 252, 0.82);
            font-size: 1rem;
            max-width: 70ch;
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }

        .feature-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.45rem 0.75rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            background: rgba(248, 250, 252, 0.08);
            color: #f8fafc;
            border: 1px solid rgba(248, 250, 252, 0.1);
        }

        .section-title {
            font-size: 1.18rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
            color: #eef4ff;
        }

        .section-subtitle {
            color: #9fb0c7;
            margin-bottom: 0.85rem;
        }

        .panel-card {
            background: rgba(10, 17, 32, 0.96);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 22px;
            padding: 1.15rem 1.2rem;
            box-shadow: 0 16px 34px rgba(2, 6, 16, 0.28);
        }

        .panel-card .stButton button {
            border-radius: 999px;
            padding: 0.65rem 1.2rem;
            font-weight: 700;
        }

        .bullet-wrap {
            margin-top: 0.25rem;
        }

        .bullet-line {
            display: flex;
            gap: 0.55rem;
            align-items: flex-start;
            margin-bottom: 0.55rem;
            padding: 0.1rem 0;
            font-size: 0.96rem;
            line-height: 1.45;
            color: #e5eefc;
        }

        .bullet-line::before {
            content: "";
            display: inline-block;
            width: 0.55rem;
            height: 0.55rem;
            margin-top: 0.38rem;
            border-radius: 999px;
            flex: 0 0 auto;
        }

        .bullet-line.success::before {
            background: #22c55e;
        }

        .bullet-line.warning::before {
            background: #f59e0b;
        }

        .bullet-line.neutral::before {
            background: #94a3b8;
        }

        .callout-row {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.8rem;
            margin-top: 0.75rem;
        }

        .callout-card {
            background: linear-gradient(180deg, #111b2f 0%, #0d1626 100%);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 16px;
            padding: 0.85rem 0.95rem;
            box-shadow: 0 14px 30px rgba(2, 6, 16, 0.22);
        }

        .notice-card {
            border-radius: 16px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            padding: 0.85rem 0.95rem;
            margin: 0.35rem 0 0.8rem 0;
            color: #e5eefc;
            line-height: 1.45;
            box-shadow: 0 14px 30px rgba(2, 6, 16, 0.2);
        }

        .notice-card.info {
            background: #0f1a2d;
            border-color: rgba(59, 130, 246, 0.22);
        }

        .notice-card.success {
            background: #10241b;
            border-color: rgba(34, 197, 94, 0.22);
        }

        .notice-card.warning {
            background: #2a1d10;
            border-color: rgba(245, 158, 11, 0.24);
        }

        .notice-card.error {
            background: #2c1114;
            border-color: rgba(248, 113, 113, 0.24);
        }

        .callout-label {
            font-size: 0.77rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-weight: 700;
            color: #90a4c1;
            margin-bottom: 0.35rem;
        }

        .callout-value {
            color: #f8fbff;
            font-weight: 600;
            line-height: 1.45;
        }

        div[data-testid="stTextArea"] textarea,
        textarea {
            background: linear-gradient(180deg, #0d1727 0%, #0a1220 100%) !important;
            color: #f8fbff !important;
            border: 1px solid rgba(148, 163, 184, 0.22) !important;
            border-radius: 16px !important;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
        }

        div[data-testid="stFileUploader"] {
            background: linear-gradient(180deg, #0d1727 0%, #0a1220 100%);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 16px;
            padding: 0.6rem 0.75rem;
        }

        div[data-testid="stFileUploader"] section {
            background: transparent !important;
        }

        div[data-testid="stFileUploader"] button {
            background: #10b981;
            color: #04111b;
            border: 0;
            font-weight: 700;
        }

        div[data-baseweb="select"],
        div[data-baseweb="input"] {
            background: #0d1727 !important;
            color: #f8fbff !important;
        }

        div[data-testid="stExpander"] {
            background: rgba(10, 17, 32, 0.94);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
        }

        div[data-testid="stButton"] button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: #04111b !important;
            border: 0 !important;
            border-radius: 999px !important;
            font-weight: 800 !important;
            box-shadow: 0 12px 26px rgba(16, 185, 129, 0.24);
        }

        div[data-testid="stButton"] button:hover {
            background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
            color: #04111b !important;
        }

        div[data-testid="stTabs"] button {
            color: #cbd8ea !important;
            font-weight: 700;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #10b981 !important;
        }

        @media (max-width: 900px) {
            .callout-row {
                grid-template-columns: 1fr;
            }
        }

        div[data-testid="stMetric"] {
            background: rgba(10, 17, 32, 0.95);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            box-shadow: 0 14px 30px rgba(2, 6, 16, 0.2);
        }

        div[data-testid="stTabs"] button {
            font-weight: 600;
        }

        hr {
            border-color: rgba(148, 163, 184, 0.25) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-eyebrow">AI-powered career review</div>
        <h1>AI Career Assistant</h1>
        <p>
            Upload your resume and compare it with a job description to get ATS insights,
            skill-gap analysis, and a learning roadmap in a cleaner, more guided experience.
        </p>
        <div class="chip-row">
            <span class="feature-chip">ATS scoring</span>
            <span class="feature-chip">Skill match review</span>
            <span class="feature-chip">Resume comparison</span>
            <span class="feature-chip">Learning roadmap</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


def select_feature(feature_name):
    st.session_state["active_feature"] = feature_name
    st.rerun()


with st.sidebar:
    st.markdown("## Career Workspace")
    st.markdown(
        "Review the resume, compare an updated version, and keep the most recent analysis in session."
    )
    st.markdown("### Tips")
    st.markdown(
        "- Use a JD with responsibilities and required skills.\n"
        "- Keep the resume PDF text-based for best extraction.\n"
        "- Analyze once before using the comparison section."
    )
    if "previous_resume" in st.session_state:
        st.markdown(
            "<div class='notice-card success'>Comparison data is ready.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='notice-card info'>Run an analysis first to unlock the progress tracker.</div>",
            unsafe_allow_html=True,
        )

    st.markdown("### Features")
    if "active_feature" not in st.session_state:
        st.session_state["active_feature"] = "analyzer"

    st.button("Resume Analyzer", use_container_width=True, on_click=select_feature, args=("analyzer",))
    st.button("Resume Comparison", use_container_width=True, on_click=select_feature, args=("comparison",))
    st.button("Best Resume Finder", use_container_width=True, on_click=select_feature, args=("best_finder",))


active_feature = st.session_state.get("active_feature", "analyzer")

page_titles = {
    "analyzer": "Resume Analyzer",
    "comparison": "Resume Comparison",
    "best_finder": "Best Resume Finder",
}

st.markdown(
    f"<div class='section-title' style='margin-top:0.35rem;'>{page_titles.get(active_feature, 'Resume Analyzer')}</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='section-subtitle'>Use the sidebar buttons to switch between pages instantly.</div>",
    unsafe_allow_html=True,
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


def render_string_list(items, success=False, warn=False, empty_message=None, columns_count=None):
    if not items:
        if empty_message:
            st.caption(empty_message)
        return

    tone = "success" if success else "warning" if warn else "neutral"
    column_count = columns_count if columns_count else (2 if len(items) > 3 else 1)
    columns = st.columns(column_count, gap="large")
    grouped_items = [items[index::column_count] for index in range(column_count)]

    for column, group in zip(columns, grouped_items):
        with column:
            for item in group:
                st.markdown(
                    f'<div class="bullet-line {tone}">{html.escape(str(item))}</div>',
                    unsafe_allow_html=True,
                )


def render_callout_grid(items, labels=None, empty_message=None):
    if not items:
        if empty_message:
            st.caption(empty_message)
        return

    callout_labels = labels or [f"Item {index + 1}" for index in range(len(items))]
    columns = st.columns(min(3, len(items)), gap="medium")

    for index, (label, value) in enumerate(zip(callout_labels, items)):
        with columns[index % len(columns)]:
            st.markdown(
                f'''
                <div class="callout-card">
                    <div class="callout-label">{html.escape(str(label))}</div>
                    <div class="callout-value">{html.escape(str(value))}</div>
                </div>
                ''',
                unsafe_allow_html=True,
            )


def render_notice(message, tone="info"):
    st.markdown(
        f'<div class="notice-card {tone}">{html.escape(str(message))}</div>',
        unsafe_allow_html=True,
    )


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def clamp_score(value):
    return min(max(safe_int(value, 0), 0), 100)


def normalize_skill_terms(items):
    if not items:
        return []

    generic_terms = {
        "skill",
        "skills",
        "ability",
        "abilities",
        "experience",
        "knowledge",
        "familiarity",
        "understanding",
        "proficiency",
        "excellent communication",
        "communication",
        "teamwork",
        "problem solving",
        "problem-solving",
        "good communication",
        "strong communication",
        "attention to detail",
        "detail oriented",
        "detail-oriented",
        "adaptability",
        "leadership",
        "collaboration",
        "collaborative",
        "professionalism",
        "self motivated",
        "self-motivated",
        "responsible",
        "organized",
        "quick learner",
        "fast learner",
        "critical thinking",
    }

    value_terms = []
    seen = set()

    for raw_item in items:
        if raw_item is None:
            continue

        text = str(raw_item).strip()
        if not text:
            continue

        text = re.sub(r"^[\-•*\d\.\)\(\s]+", "", text)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(
            r"^(experience with|knowledge of|familiarity with|proficiency in|strong experience in|hands-on experience with)\s+",
            "",
            text,
            flags=re.IGNORECASE,
        )

        split_parts = [part.strip() for part in re.split(r"[;,/|]", text) if part.strip()]
        for part in split_parts:
            part = re.sub(r"\s+(and|or)\s+", ",", part, flags=re.IGNORECASE)
            subparts = [segment.strip() for segment in part.split(",") if segment.strip()]
            for candidate in subparts:
                candidate = re.sub(r"\s+", " ", candidate).strip(" .:")
                candidate_lower = candidate.lower()
                if len(candidate) < 2:
                    continue
                if candidate_lower in generic_terms:
                    continue
                if candidate_lower in seen:
                    continue
                if len(candidate.split()) > 6:
                    candidate = " ".join(candidate.split()[:4])
                seen.add(candidate_lower)
                value_terms.append(candidate)

    return value_terms


def normalize_person_name(value):
    if not value:
        return ""

    tokens = re.findall(r"[A-Za-z]+", str(value))
    tokens = [token.casefold() for token in tokens if len(token) > 1]
    return " ".join(tokens).strip()


def person_names_match(first_name, second_name):
    return normalize_person_name(first_name) == normalize_person_name(second_name)


def normalize_resume_signature(resume_text):
    return re.sub(r"\s+", " ", str(resume_text)).casefold().strip()


def extract_name_from_filename(filename):
    stem = os.path.splitext(filename)[0]
    stem = re.sub(r"(?i)\b(resume|cv|curriculum vitae|updated|final|draft|version|v\d+)\b", " ", stem)
    stem = re.sub(r"[_\-]+", " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip(" ._-|")

    if not stem:
        return ""

    words = [word for word in stem.split() if word.lower() not in {"resume", "cv", "final", "draft"}]
    if 2 <= len(words) <= 4:
        return " ".join(words).title()

    return ""


def extract_candidate_name(uploaded_file, resume_text):
    lines = [line.strip() for line in resume_text.splitlines()[:20] if line.strip()]
    excluded_words = {
        "resume",
        "curriculum",
        "vitae",
        "profile",
        "summary",
        "objective",
        "experience",
        "education",
        "skills",
        "projects",
        "contact",
        "email",
        "phone",
        "linkedin",
        "github",
        "portfolio",
    }

    candidate_lines = []
    for line in lines:
        clean_line = re.sub(r"\s+", " ", line).strip(" •-|:")
        lower_line = clean_line.lower()

        if "@" in clean_line or any(character.isdigit() for character in clean_line):
            continue

        if any(word in lower_line for word in excluded_words):
            continue

        words = re.findall(r"[A-Za-z][A-Za-z'.-]*", clean_line)
        if 2 <= len(words) <= 4:
            score = sum(1 for word in words if word[:1].isupper()) + sum(1 for word in words if len(word) > 1)
            if len(clean_line) <= 40:
                score += 1
            candidate_lines.append((score, clean_line))

    if candidate_lines:
        candidate_lines.sort(key=lambda item: (item[0], -len(item[1])), reverse=True)
        return candidate_lines[0][1].title()

    return extract_name_from_filename(uploaded_file.name)


# ==========================
# FILE UPLOAD
# ==========================

uploaded_file = None
job_description = ""
analyze_clicked = False

if active_feature == "analyzer":
    st.markdown("<div class='section-title'>Resume Upload</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-subtitle'>Upload your current resume first, then we’ll evaluate it against the job description.</div>",
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )

    st.markdown("<div class='section-title' style='margin-top:1.1rem;'>Job Description</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-subtitle'>Paste the target role description, responsibilities, and required skills.</div>",
        unsafe_allow_html=True,
    )
    job_description = st.text_area(
        "Paste Job Description Here",
        height=250,
        placeholder="Paste the full job description here...",
        label_visibility="collapsed",
    )

    button_col_left, button_col_mid, button_col_right = st.columns([1, 1.2, 1])
    with button_col_mid:
        analyze_clicked = st.button("Analyze Resume")

# ==========================
# RESUME ANALYSIS
# ==========================

if uploaded_file is not None:
    resume_text = extract_text_from_pdf(uploaded_file)

    if len(resume_text.strip()) < 50:
        render_notice("Unable to extract enough text from the PDF.", tone="error")
    else:
        render_notice("Resume uploaded successfully.", tone="success")

        with st.expander("View Resume Text"):
            st.text_area(
                "Resume Content",
                resume_text,
                height=250
            )

        if analyze_clicked:
            if not job_description.strip():
                render_notice("Please paste a job description before analyzing.", tone="warning")
            else:
                with st.spinner("Analyzing resume..."):
                    try:
                        result = analyze_resume(
                            model,
                            resume_text,
                            job_description,
                        )

                        ats_score = safe_int(result.get("ats_score", 0))
                        ats_score = min(max(ats_score, 0), 100)
                        result["ats_score"] = ats_score

                        candidate_name = extract_candidate_name(uploaded_file, resume_text)
                        result["candidate_name"] = candidate_name
                        result["candidate_name_key"] = normalize_person_name(candidate_name)
                        result["resume_signature"] = normalize_resume_signature(resume_text)

                        st.session_state["previous_resume"] = resume_text
                        st.session_state["previous_resume_signature"] = result["resume_signature"]
                        st.session_state["job_description"] = job_description
                        st.session_state["previous_analysis"] = result
                        st.session_state["previous_candidate_name"] = candidate_name
                        st.session_state["previous_candidate_name_key"] = normalize_person_name(candidate_name)

                        st.markdown("<div class='section-title'>ATS Dashboard</div>", unsafe_allow_html=True)
                        st.markdown(
                            "<div class='section-subtitle'>The score below summarizes how well the resume matches the selected role.</div>",
                            unsafe_allow_html=True,
                        )

                        render_callout_grid(
                            [
                                f"{ats_score}/100 ATS score",
                                f"{len(result.get('matching_skills', []))} matching skills",
                                f"{len(result.get('missing_skills', []))} missing skills",
                            ],
                            labels=["Overall", "Matches", "Gaps"],
                        )

                        st.progress(ats_score)

                        render_notice(
                            result.get(
                                "resume_summary",
                                "A concise summary was not returned by the model."
                            ),
                            tone="info",
                        )

                        tab1, tab2, tab3, tab4 = st.tabs(
                            ["Skills", "Analysis", "Suggestions", "Roadmap"]
                        )

                        with tab1:
                            skill_col_1, skill_col_2 = st.columns(2, gap="large")

                            with skill_col_1:
                                st.markdown("### Matching Skills")
                                render_string_list(
                                    result.get("matching_skills", []),
                                    success=True,
                                    empty_message="No matching skills identified."
                                )

                            with skill_col_2:
                                st.markdown("### Missing Skills")
                                render_string_list(
                                    result.get("missing_skills", []),
                                    warn=True,
                                    empty_message="No missing skills identified."
                                )

                        with tab2:
                            analysis_col_1, analysis_col_2 = st.columns(2, gap="large")

                            with analysis_col_1:
                                st.markdown("### Strengths")
                                render_string_list(
                                    result.get("strengths", []),
                                    empty_message="No strengths returned by the model."
                                )

                            with analysis_col_2:
                                st.markdown("### Weaknesses")
                                render_string_list(
                                    result.get("weaknesses", []),
                                    empty_message="No weaknesses returned by the model."
                                )

                        with tab3:
                            st.markdown("### Resume Optimization Recommendations")

                            suggestions = result.get("suggestions", [])

                            if suggestions:
                                render_string_list(suggestions)
                            else:
                                render_notice("No optimization recommendations available.", tone="info")

                            st.markdown("---")

                            st.markdown("### Resume Enhancement Suggestions")

                            enhancements = result.get("resume_enhancement", [])

                            if enhancements:
                                render_string_list(enhancements, success=True)
                            else:
                                render_notice(
                                    "Your resume structure looks good. No major enhancement suggestions were identified.",
                                    tone="success",
                                )

                            st.markdown("---")

                            st.markdown("### ATS Keyword Recommendations")

                            keywords = result.get("keyword_recommendations", [])

                            if keywords:
                                render_string_list(keywords)
                            else:
                                render_notice(
                                    "Your resume already includes most important keywords from the job description.",
                                    tone="success",
                                )

                        with tab4:
                            st.markdown("### Learning Roadmap")
                            render_string_list(
                                result.get("learning_roadmap", []),
                                empty_message="No roadmap returned by the model."
                            )

                        st.balloons()
                    except Exception as e:
                        render_notice(f"Analysis Error: {e}", tone="error")

# ==========================
# RESUME COMPARISON SECTION
# ==========================

if active_feature == "comparison":
    st.markdown("---")
    st.markdown("<div class='section-title'>Resume Progress Tracker</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-subtitle'>Compare an updated resume against the most recent analyzed version.</div>",
        unsafe_allow_html=True,
    )

    # Check whether the user has already analyzed a resume
    if "previous_resume" not in st.session_state:

        render_notice("Please analyze a resume first using the Resume ATS Analyzer.", tone="info")

    else:

        render_notice("Previous resume and job description loaded.", tone="success")

        st.markdown("<div class='section-title' style='margin-top:1.1rem;'>Updated Resume</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>After the first review, upload the improved version here to compare results.</div>",
            unsafe_allow_html=True,
        )
        new_resume = st.file_uploader(
            "Upload Updated Resume",
            type=["pdf"],
            key="new_resume"
        )

        if new_resume is not None:

            if st.button("Compare Updated Resume"):

                try:

                    old_resume_text = st.session_state["previous_resume"]
                    new_resume_text = extract_text_from_pdf(new_resume)
                    old_resume_signature = st.session_state.get("previous_resume_signature", normalize_resume_signature(old_resume_text))
                    new_resume_signature = normalize_resume_signature(new_resume_text)
                    same_resume_uploaded = False

                    new_candidate_name = extract_candidate_name(new_resume, new_resume_text)
                    new_candidate_name_key = normalize_person_name(new_candidate_name)
                    previous_candidate_name = st.session_state.get("previous_candidate_name", "")
                    previous_candidate_name_key = st.session_state.get(
                        "previous_candidate_name_key",
                        normalize_person_name(previous_candidate_name),
                    )

                    if previous_candidate_name_key and new_candidate_name_key and not person_names_match(previous_candidate_name, new_candidate_name):
                        render_notice(
                            f"Different candidate names were detected. Previous resume belongs to {previous_candidate_name or 'Unknown Candidate'} and the updated resume belongs to {new_candidate_name or 'Unknown Candidate'}. Please upload resumes for the same person only.",
                            tone="error",
                        )
                        raise ValueError("Different person resumes cannot be compared.")

                    if old_resume_signature == new_resume_signature:
                        old_ats_score = clamp_score(
                            st.session_state.get("previous_analysis", {}).get("ats_score", 0)
                        )
                        render_notice(
                            "You have uploaded the same resume again. Showing the same ATS score as the older resume.",
                            tone="error",
                        )

                        render_callout_grid(
                            [
                                f"{old_ats_score}/100",
                                f"{old_ats_score}/100",
                                "+0",
                            ],
                            labels=["Old ATS Score", "New ATS Score", "Improvement"],
                        )

                        st.markdown("### New Skills Added")
                        render_string_list(
                            [],
                            success=True,
                            empty_message="No new skills detected because the same resume was uploaded again.",
                            columns_count=3,
                        )

                        st.markdown("### Removed Skills")
                        render_string_list(
                            [],
                            warn=True,
                            empty_message="No removed skills detected because the same resume was uploaded again.",
                            columns_count=3,
                        )

                        st.markdown("### Overall Feedback")
                        render_notice(
                            "The old and updated resumes are identical, so no comparison was performed.",
                            tone="info",
                        )
                        same_resume_uploaded = True

                    if not same_resume_uploaded:
                        with st.spinner("Comparing resumes..."):

                            comparison = compare_resumes(
                                model,
                                old_resume_text,
                                new_resume_text,
                                st.session_state["job_description"]
                            )

                        previous_analysis = st.session_state.get("previous_analysis", {})
                        old_ats_score = clamp_score(previous_analysis.get("ats_score", comparison.get("old_ats_score", 0)))
                        new_ats_score = clamp_score(comparison.get("new_ats_score", 0))
                        improvement_score = new_ats_score - old_ats_score
                        comparison["old_ats_score"] = old_ats_score
                        comparison["new_ats_score"] = new_ats_score
                        comparison["improvement_score"] = improvement_score
                        comparison["new_skills_added"] = normalize_skill_terms(
                            comparison.get("new_skills_added", [])
                        )
                        comparison["removed_skills"] = normalize_skill_terms(
                            comparison.get("removed_skills", [])
                        )

                        render_callout_grid(
                            [
                                f"{old_ats_score}/100",
                                f"{new_ats_score}/100",
                                f"{improvement_score:+d}",
                            ],
                            labels=["Old ATS Score", "New ATS Score", "Improvement"],
                        )

                        st.markdown("### New Skills Added")
                        render_string_list(
                            comparison.get("new_skills_added", []),
                            success=True,
                            empty_message="No new skills detected.",
                            columns_count=3,
                        )

                        removed = comparison.get("removed_skills", [])

                        if removed:

                            st.markdown("### Removed Skills")

                            render_string_list(
                                removed,
                                warn=True,
                                columns_count=3,
                            )

                        else:

                            render_notice(
                                "No important skills were removed from the updated resume.",
                                tone="success",
                            )

                        st.markdown("### Improved Sections")
                        render_string_list(
                            comparison.get("improved_sections", []),
                            empty_message="No improved sections returned by the model."
                        )

                        weak_sections = comparison.get("weak_sections", [])

                        if weak_sections:

                            st.markdown("### Sections Still Weak")

                            render_string_list(
                                weak_sections
                            )

                        else:

                            render_notice(
                                "No significant weak sections identified based on the provided job description.",
                                tone="success",
                            )

                        st.markdown("### Overall Feedback")
                        render_notice(
                            comparison.get(
                                "overall_feedback",
                                "No feedback available."
                            ),
                            tone="info",
                        )

                except Exception as e:

                    render_notice(f"Comparison Error: {e}", tone="error")


# ==========================
# BEST RESUME FINDER
# ==========================

if active_feature == "best_finder":
    st.markdown("<div class='section-title' style='margin-top:1.1rem;'>Best Resume Finder</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-subtitle'>Upload multiple versions of the same person's resume, and the app will pick the strongest match for the current job description. Mixed names are rejected.</div>",
        unsafe_allow_html=True,
    )

    best_finder_job_description = st.text_area(
        "Best Resume Finder Job Description",
        height=220,
        placeholder="Paste the job description you want to compare all resume versions against...",
        label_visibility="collapsed",
    )

    best_resume_files = st.file_uploader(
        "Upload Resume Versions",
        type=["pdf"],
        accept_multiple_files=True,
        key="best_resume_files",
    )

    if best_resume_files:
        run_best_resume_check = st.button("Find Best Resume For JD", key="find_best_resume_btn")

        if run_best_resume_check:
            if not best_finder_job_description.strip():
                render_notice("Please paste a job description before comparing multiple resumes.", tone="warning")
            elif len(best_resume_files) < 2:
                render_notice("Upload at least two resume versions to find the best match.", tone="warning")
            else:
                try:
                    extracted_resumes = []

                    for uploaded_resume in best_resume_files:
                        resume_text = extract_text_from_pdf(uploaded_resume)

                        if len(resume_text.strip()) < 50:
                            render_notice(
                                f"Unable to extract enough text from {uploaded_resume.name}.",
                                tone="error",
                            )
                            raise ValueError("One or more uploaded resumes could not be read.")

                        candidate_name = extract_candidate_name(uploaded_resume, resume_text)
                        extracted_resumes.append(
                            {
                                "file_name": uploaded_resume.name,
                                "candidate_name": candidate_name,
                                "candidate_name_key": normalize_person_name(candidate_name),
                                "resume_text": resume_text,
                            }
                        )

                    with st.spinner("Scoring resume versions against the job description..."):
                        scored_resumes = []

                        for item in extracted_resumes:
                            analysis_result = analyze_resume(
                                model,
                                item["resume_text"],
                                best_finder_job_description,
                            )

                            ats_score = clamp_score(analysis_result.get("ats_score", 0))
                            scored_resumes.append(
                                {
                                    "file_name": item["file_name"],
                                    "candidate_name": item["candidate_name"] or "Unknown Candidate",
                                    "ats_score": ats_score,
                                    "analysis": analysis_result,
                                }
                            )

                        scored_resumes.sort(key=lambda item: item["ats_score"], reverse=True)
                        best_resume = scored_resumes[0]

                        render_notice(
                            f"Best resume for the current job description: {best_resume['candidate_name']} ({best_resume['file_name']}) with an ATS score of {best_resume['ats_score']}/100.",
                            tone="success",
                        )

                        render_callout_grid(
                            [
                                best_resume["candidate_name"],
                                best_resume["file_name"],
                                f"{best_resume['ats_score']}/100",
                            ],
                            labels=["Candidate", "Best File", "Best Score"],
                        )

                        st.markdown("### Ranked Resume Versions")
                        ranked_cols = st.columns(3, gap="medium")
                        for index, item in enumerate(scored_resumes[:3]):
                            with ranked_cols[index % 3]:
                                render_notice(
                                    f"{index + 1}. {item['candidate_name']} - {item['file_name']} - {item['ats_score']}/100",
                                    tone="info",
                                )

                        st.markdown("### Best Resume Match Summary")
                        render_string_list(
                            best_resume["analysis"].get("matching_skills", []),
                            success=True,
                            empty_message="No matching skills were returned for the best resume.",
                            columns_count=3,
                        )

                        st.markdown("### Best Resume Gaps")
                        render_string_list(
                            best_resume["analysis"].get("missing_skills", []),
                            warn=True,
                            empty_message="No missing skills were returned for the best resume.",
                            columns_count=3,
                        )
                except Exception as e:
                    render_notice(f"Best Resume Finder Error: {e}", tone="error")

