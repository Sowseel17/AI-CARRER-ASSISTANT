ANALYSIS_PROMPT = """
You are an experienced ATS Expert, Senior Technical Recruiter, and Career Coach.

Analyze the provided resume against the Job Description.

Evaluate the resume professionally and provide detailed feedback.

Return ONLY VALID JSON in the following format:

{
    "ats_score": 0,
    "resume_summary": "",

    "matching_skills": [],

    "missing_skills": [],

    "strengths": [],

    "weaknesses": [],

    "suggestions": [],

    "resume_enhancement": [],

    "keyword_recommendations": [],

    "learning_roadmap": []
}

Instructions:

1. ATS Score should be between 0 and 100.

2. Resume Summary should summarize the candidate professionally.

3. Matching Skills should contain skills matching the Job Description.

4. Missing Skills should contain important skills absent from the resume.

5. Strengths should highlight the strongest aspects of the resume.

6. Weaknesses should mention sections that need improvement.

7. Suggestions should provide high-level recommendations.

8. Resume Enhancement should tell the candidate EXACTLY where improvements should be made.

Example:

- Add Docker under Technical Skills.
- Mention REST API development in Projects.
- Add measurable achievements in Experience.
- Include GitHub links for projects.
- Improve the Professional Summary.

9. Keyword Recommendations should contain ATS-friendly keywords from the Job Description that should be added naturally to the resume.

10. Learning Roadmap should recommend technologies and concepts to learn for this role.

Return ONLY JSON.
"""


COMPARISON_PROMPT = """
You are an ATS Expert and Senior Technical Recruiter.

Compare the OLD resume and UPDATED resume against the SAME Job Description.

First calculate an ATS score for BOTH resumes separately.

Then compare them.

Return ONLY VALID JSON.

{
    "old_ats_score": 0,
    "new_ats_score": 0,
    "improvement_score": 0,
    "new_skills_added": [],
    "removed_skills": [],
    "still_missing_skills": [],
    "improved_sections": [],
    "overall_feedback": ""
}

Rules:

1. Give ATS score out of 100 for BOTH resumes.
2. Improvement score = New ATS - Old ATS.
3. New skills must only contain skills present in the updated resume but not in the old resume.
4. Removed skills must contain skills removed from the updated resume.
5. still_missing_skills should contain skills from the JD that are still missing.
6. Return ONLY JSON.
Do not write explanations.
"""