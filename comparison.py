import json

from prompts import COMPARISON_PROMPT


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


def compare_resumes(
    model,
    old_text,
    new_text,
    job_description
):

    prompt = f"""
{COMPARISON_PROMPT}

JOB DESCRIPTION:
{job_description}

OLD RESUME:
{old_text}

UPDATED RESUME:
{new_text}
"""

    response = model.generate_content(prompt)
    print(response.text)

    return json.loads(_extract_json(response.text))