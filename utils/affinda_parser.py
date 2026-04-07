import requests
import os
import time

API_KEY      = os.getenv("AFFINDA_API_KEY")
WORKSPACE_ID = os.getenv("AFFINDA_WORKSPACE")
V3_URL       = "https://api.affinda.com/v3/documents"


def _parse_with_affinda(file_path: str) -> dict:
    """Try Affinda v3 API. Returns dict with 'error' key on failure."""
    headers = {"Authorization": f"Bearer {API_KEY}"}

    for attempt in range(3):
        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    V3_URL,
                    headers=headers,
                    files={"file": f},
                    data={"workspace": WORKSPACE_ID},
                    timeout=60,
                )

            if response.status_code in (200, 201):
                body   = response.json()
                parsed = body.get("data") or {}

                name_obj = parsed.get("name") or {}
                name = name_obj.get("raw", "") if isinstance(name_obj, dict) else str(name_obj)

                skills = [
                    s.get("name", "")
                    for s in (parsed.get("skills") or [])
                    if isinstance(s, dict)
                ]
                education = [
                    (e.get("accreditation") or {}).get("education", "")
                    for e in (parsed.get("education") or [])
                    if isinstance(e, dict)
                ]
                experience = [
                    w.get("jobTitle", "")
                    for w in (parsed.get("workExperience") or [])
                    if isinstance(w, dict)
                ]

                return {
                    "name":       name,
                    "skills":     [s for s in skills     if s],
                    "education":  [e for e in education  if e],
                    "experience": [x for x in experience if x],
                    "source":     "affinda",
                }

            elif response.status_code == 429:
                wait = int(response.headers.get("Retry-After", 5))
                print(f"[Affinda] Rate limited. Waiting {wait}s (attempt {attempt + 1}/3)...")
                time.sleep(wait)
                continue

            elif response.status_code in (401, 403):
                return {"error": f"Affinda auth failed ({response.status_code}). Check your AFFINDA_API_KEY."}

            elif response.status_code == 404:
                return {"error": "Affinda 404 — Check your AFFINDA_WORKSPACE value in .env"}

            else:
                return {"error": f"Affinda API error {response.status_code}: {response.text}"}

        except requests.exceptions.Timeout:
            print(f"[Affinda] Timeout on attempt {attempt + 1}/3...")
            time.sleep(2)

        except FileNotFoundError:
            return {"error": f"Resume file not found: {file_path}"}

        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    return {"error": "Affinda API timed out after 3 attempts"}


def _parse_with_pypdf(file_path: str) -> dict:
    """
    Fallback parser using pypdf + regex extraction.
    Works 100% offline — no API key needed.
    """
    try:
        from pypdf import PdfReader
        import re

        reader = PdfReader(file_path)
        full_text = "\n".join(
            page.extract_text() for page in reader.pages
            if page.extract_text()
        )

        lines = [l.strip() for l in full_text.split("\n") if l.strip()]
        name = lines[0] if lines else ""

        # Skills section
        skills = []
        skill_match = re.search(
            r'SKILLS?\s*[:\-]?\s*(.*?)(?=\n[A-Z]{3,}|\Z)',
            full_text, re.IGNORECASE | re.DOTALL
        )
        if skill_match:
            raw_skills = skill_match.group(1)
            skills = [
                s.strip().strip("•·–-")
                for s in re.split(r'[,\n•·|]', raw_skills)
                if 2 < len(s.strip()) < 60
            ][:20]

        # Education section
        degree_keywords = r'(B\.?Tech|B\.?E|M\.?Tech|MBA|B\.?Sc|M\.?Sc|Bachelor|Master|Ph\.?D|CGPA|Score)'
        education = [
            line.strip() for line in full_text.split("\n")
            if re.search(degree_keywords, line, re.IGNORECASE)
            and len(line.strip()) > 5
        ][:5]

        # Experience section
        experience = []
        exp_match = re.search(
            r'(?:EXPERIENCE|INTERNSHIP|WORK)\s*[:\-]?\s*(.*?)(?=\n[A-Z]{3,}|\Z)',
            full_text, re.IGNORECASE | re.DOTALL
        )
        if exp_match:
            for line in exp_match.group(1).split("\n"):
                line = line.strip()
                if 5 < len(line) < 80 and not line.startswith("•"):
                    experience.append(line)
            experience = experience[:5]

        return {
            "name":       name,
            "skills":     skills,
            "education":  education,
            "experience": experience,
            "source":     "pypdf_fallback",
        }

    except Exception as e:
        return {"error": f"pypdf fallback failed: {str(e)}"}


def parse_resume(file_path: str) -> dict:
    """
    Smart parser with automatic fallback:
      1. Try Affinda v3 (if API_KEY + WORKSPACE_ID are set)
      2. Fall back to pypdf local extraction
    """
    if API_KEY and WORKSPACE_ID:
        result = _parse_with_affinda(file_path)
        if "error" not in result:
            return result
        print(f"[Parser] Affinda failed: {result['error']} — falling back to pypdf")
    else:
        missing = []
        if not API_KEY:      missing.append("AFFINDA_API_KEY")
        if not WORKSPACE_ID: missing.append("AFFINDA_WORKSPACE")
        print(f"[Parser] Missing env vars: {', '.join(missing)} — using pypdf fallback")

    return _parse_with_pypdf(file_path)