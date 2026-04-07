from google import genai
from google.genai import types
import os

# Use gemini-2.5-flash — fast, free-tier friendly, current stable model
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def analyze_resume(parsed_data: dict, job_desc: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    # New SDK: create a client (replaces the old genai.configure() pattern)
    client = genai.Client(api_key=api_key)

    candidate_block = (
        f"Name       : {parsed_data.get('name', 'N/A')}\n"
        f"Skills     : {', '.join(parsed_data.get('skills', [])) or 'N/A'}\n"
        f"Education  : {', '.join(parsed_data.get('education', [])) or 'N/A'}\n"
        f"Experience : {', '.join(parsed_data.get('experience', [])) or 'N/A'}"
    )

    prompt = f"""You are an expert AI recruiter. Evaluate the candidate against the job description.

Candidate Profile:
{candidate_block}

Job Description:
{job_desc}

Rules:
- Be realistic and honest
- Do not exaggerate match scores
- Base the score strictly on skills and experience overlap

Respond ONLY in this exact format (no extra text):

Match Score: <number 0-100>

Missing Skills:
- <skill>

Strengths:
- <strength>

Suggestions:
- <suggestion>
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=800,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response (possibly blocked by safety filters)")

    return response.text