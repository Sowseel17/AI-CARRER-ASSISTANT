import json

from prompts import ANALYSIS_PROMPT


def _extract_json(text):
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json")

    cleaned = cleaned.replace("```", "").strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]

    return cleaned


def analyze_resume(model, resume_text, job_description):

    prompt = f"""
{ANALYSIS_PROMPT}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}
"""

    response = model.generate_content(prompt)

    return json.loads(_extract_json(response.text))