from __future__ import annotations

import io
import re
from typing import Any

from docx import Document
from pypdf import PdfReader

from app.services.ai.groq_client import groq_client


MAX_RESUME_TEXT_CHARS = 14_000

RESUME_SYSTEM = """You extract factual student/candidate profile information from a resume/CV.

STRICT RULES:
- Use ONLY information explicitly present in the resume text.
- NEVER invent, guess, or infer personal facts that are not supported.
- If a value is not present, return null or [].
- Keep skills concise and deduplicated.
- Do not create opportunity preferences unless the resume explicitly states them.
- educationLevel must be one of:
  ["high_school", "undergraduate", "graduate", "postgraduate", "recent_graduate"] or null.
- experienceLevel must be one of:
  ["student", "beginner", "entry", "junior", "mid", "senior"] or null.
- graduationYear must be a 4-digit integer or null.
- Reply ONLY with a valid JSON object matching exactly this shape:

{
  "fullName": string|null,
  "country": string|null,
  "educationLevel": string|null,
  "fieldOfStudy": string|null,
  "institution": string|null,
  "graduationYear": integer|null,
  "experienceLevel": string|null,
  "skills": string[],
  "interests": string[]
}
"""


def _clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    parts: list[str] = []

    for page in reader.pages:
        try:
            value = page.extract_text() or ""
        except Exception:
            value = ""
        if value.strip():
            parts.append(value)

    return _clean_text("\n".join(parts))


def _extract_docx(data: bytes) -> str:
    document = Document(io.BytesIO(data))
    parts: list[str] = []

    for paragraph in document.paragraphs:
        value = paragraph.text.strip()
        if value:
            parts.append(value)

    # CVs often contain skills/education inside tables.
    for table in document.tables:
        for row in table.rows:
            values = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if values:
                parts.append(" | ".join(values))

    return _clean_text("\n".join(parts))


def extract_resume_text(filename: str, data: bytes) -> str:
    """
    Extract text from a PDF or DOCX resume entirely in memory.
    The uploaded file is not written to disk or stored in MongoDB.
    """
    if not data:
        raise ValueError("The uploaded CV is empty.")

    suffix = (filename or "").lower().strip()

    if suffix.endswith(".pdf"):
        text = _extract_pdf(data)
    elif suffix.endswith(".docx"):
        text = _extract_docx(data)
    else:
        raise ValueError("Only PDF and DOCX CV files are supported.")

    if not text:
        raise ValueError(
            "No readable text was found in this CV. "
            "If it is a scanned/image-only PDF, upload a text-based PDF or DOCX."
        )

    return text[:MAX_RESUME_TEXT_CHARS]


def _clean_list(values: Any, limit: int) -> list[str]:
    if not isinstance(values, list):
        return []

    out: list[str] = []
    seen: set[str] = set()

    for raw in values:
        if not isinstance(raw, str):
            continue

        value = raw.strip()[:80]
        key = value.lower()

        if value and key not in seen:
            seen.add(key)
            out.append(value)

        if len(out) >= limit:
            break

    return out


def _clean_nullable_string(value: Any, max_length: int) -> str | None:
    if not isinstance(value, str):
        return None

    value = value.strip()
    return value[:max_length] if value else None


def _clean_year(value: Any) -> int | None:
    try:
        year = int(value)
    except (TypeError, ValueError):
        return None

    return year if 1950 <= year <= 2100 else None


def sanitize_resume_profile(raw: dict[str, Any] | None) -> dict[str, Any]:
    raw = raw if isinstance(raw, dict) else {}

    allowed_education = {
        "high_school",
        "undergraduate",
        "graduate",
        "postgraduate",
        "recent_graduate",
    }
    allowed_experience = {
        "student",
        "beginner",
        "entry",
        "junior",
        "mid",
        "senior",
    }

    education = _clean_nullable_string(raw.get("educationLevel"), 60)
    experience = _clean_nullable_string(raw.get("experienceLevel"), 40)

    if education not in allowed_education:
        education = None

    if experience not in allowed_experience:
        experience = None

    return {
        "fullName": _clean_nullable_string(raw.get("fullName"), 120),
        "country": _clean_nullable_string(raw.get("country"), 80),
        "educationLevel": education,
        "fieldOfStudy": _clean_nullable_string(raw.get("fieldOfStudy"), 120),
        "institution": _clean_nullable_string(raw.get("institution"), 160),
        "graduationYear": _clean_year(raw.get("graduationYear")),
        "experienceLevel": experience,
        "skills": _clean_list(raw.get("skills"), 60),
        "interests": _clean_list(raw.get("interests"), 40),
    }


def deterministic_resume_fallback(text: str) -> dict[str, Any]:
    """
    Minimal safe fallback when Groq is unavailable.
    It intentionally extracts very little rather than guessing.
    """
    year_match = re.search(r"\b(19|20)\d{2}\b", text)

    known_skills = [
        "Python",
        "JavaScript",
        "TypeScript",
        "React",
        "Node.js",
        "FastAPI",
        "Django",
        "Flask",
        "MongoDB",
        "PostgreSQL",
        "SQL",
        "Git",
        "Docker",
        "AWS",
        "Azure",
        "GCP",
        "Machine Learning",
        "Artificial Intelligence",
        "Data Science",
        "C++",
        "C#",
        "Java",
        "Go",
        "Rust",
        "Flutter",
        "React Native",
        "Figma",
    ]

    lower = text.lower()
    skills = [skill for skill in known_skills if skill.lower() in lower]

    return {
        "fullName": None,
        "country": None,
        "educationLevel": None,
        "fieldOfStudy": None,
        "institution": None,
        "graduationYear": int(year_match.group(0)) if year_match else None,
        "experienceLevel": None,
        "skills": skills,
        "interests": [],
    }


async def parse_resume_profile(text: str) -> dict[str, Any]:
    """
    Convert extracted resume text into Orbit ProfileRequest-compatible fields.
    Uses Groq when configured and gracefully falls back when unavailable.
    """
    clean = _clean_text(text)[:MAX_RESUME_TEXT_CHARS]

    if not clean:
        raise ValueError("Resume text is empty.")

    if groq_client.enabled:
        result = await groq_client.json_completion(
            RESUME_SYSTEM,
            f"RESUME TEXT:\n{clean}",
            max_tokens=900,
            temperature=0.0,
        )

        if isinstance(result, dict):
            profile = sanitize_resume_profile(result)
            return {
                "profile": profile,
                "parsedBy": "groq",
                "aiConfigured": True,
            }

    fallback = sanitize_resume_profile(deterministic_resume_fallback(clean))

    return {
        "profile": fallback,
        "parsedBy": "deterministic",
        "aiConfigured": groq_client.enabled,
    }
