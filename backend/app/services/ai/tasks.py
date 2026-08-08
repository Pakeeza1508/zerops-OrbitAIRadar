
"""AI tasks built on Groq. Every task degrades gracefully when AI is disabled."""

import logging

from app.services.ai.groq_client import groq_client

logger = logging.getLogger("orbit.ai.tasks")

EXTRACTION_SYSTEM = """You extract structured opportunity data from web page text.
You are a strict extractor: NEVER invent information. If a field is not explicitly
stated in the provided text, return null (or an empty array).
Do not infer deadlines, funding, organizations, eligible countries or URLs.
Reply ONLY with a JSON object matching exactly this shape:
{
  "isOpportunity": boolean,
  "confidence": number between 0 and 1,
  "title": string|null,
  "organization": string|null,
  "category": one of ["scholarship","internship","fellowship","hackathon","grant","competition","research","open_source","developer_program","mentorship","other"]|null,
  "description": string|null,
  "deadline": string|null (ISO-8601 date if explicitly stated),
  "countriesEligible": string[],
  "educationLevels": string[],
  "fieldsOfStudy": string[],
  "requiredSkills": string[],
  "fundingType": string|null,
  "fundingAmount": number|null,
  "currency": string|null,
  "remote": boolean|null,
  "applicationUrl": string|null,
  "requirements": string[],
  "benefits": string[],
  "evidence": object mapping field names to short verbatim quotes from the text
}"""

CLASSIFY_SYSTEM = """You decide whether a web page describes a single, concrete opportunity
(scholarship, internship, fellowship, hackathon, grant, competition, research program,
open-source program, developer program or mentorship program) that a student could apply to.
Listing/index/news/blog pages are NOT opportunities.
Reply ONLY with JSON: {"isOpportunity": boolean, "confidence": number, "category": string|null, "reason": string}"""

EXPLAIN_SYSTEM = """You write one short, factual sentence explaining why an opportunity matches a
student, using ONLY the deterministic matching facts provided. Never add new facts, never invent
eligibility or deadlines. Max 40 words.
Reply ONLY with JSON: {"explanation": string}"""

QUERY_SYSTEM = """You convert a natural-language opportunity search into structured filters.
Reply ONLY with JSON using exactly these keys (omit nothing, use null/[] when unknown):
{
 "categories": string[] (subset of ["scholarship","internship","fellowship","hackathon","grant","competition","research","open_source","developer_program","mentorship"]),
 "countries": string[],
 "skills": string[],
 "remote": boolean|null,
 "fundingRequired": boolean|null,
 "deadlineBefore": string|null (ISO-8601 date),
 "deadlineAfter": string|null (ISO-8601 date),
 "educationLevels": string[],
 "queryText": string|null (free-text keywords),
 "answer": string (one sentence describing what you searched for)
}
Never output database operators or field names other than the keys above."""


async def classify_page(title: str, text: str) -> dict | None:
    if not groq_client.enabled:
        return None
    return await groq_client.json_completion(
        CLASSIFY_SYSTEM, f"TITLE: {title}\n\nTEXT:\n{text[:6000]}", max_tokens=300
    )


async def extract_opportunity(url: str, title: str, text: str) -> dict | None:
    if not groq_client.enabled:
        return None
    return await groq_client.json_completion(
        EXTRACTION_SYSTEM,
        f"URL: {url}\nTITLE: {title}\n\nPAGE TEXT (truncated):\n{text[:9000]}",
        max_tokens=1600,
    )


async def explain_match(opportunity: dict, profile: dict, match: dict) -> str | None:
    if not groq_client.enabled:
        return None
    facts = {
        "title": opportunity.get("title"),
        "organization": opportunity.get("organization"),
        "category": opportunity.get("category"),
        "deadline": str(opportunity.get("deadline")) if opportunity.get("deadline") else None,
        "countriesEligible": opportunity.get("countriesEligible"),
        "fundingType": opportunity.get("fundingType"),
        "remote": opportunity.get("remote"),
        "studentCountry": profile.get("country"),
        "studentField": profile.get("fieldOfStudy"),
        "studentEducation": profile.get("educationLevel"),
        "matchScore": match.get("matchScore"),
        "matchedSkills": match.get("matchedSkills"),
        "missingSkills": match.get("missingSkills"),
        "eligibilityStatus": match.get("eligibilityStatus"),
        "matchingReasons": match.get("matchingReasons"),
    }
    result = await groq_client.json_completion(
        EXPLAIN_SYSTEM, f"FACTS:\n{facts}", max_tokens=200, temperature=0.3
    )
    if isinstance(result, dict):
        value = result.get("explanation")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


async def query_to_filters(query: str) -> dict | None:
    if not groq_client.enabled:
        return None
    return await groq_client.json_completion(QUERY_SYSTEM, f"QUERY: {query}", max_tokens=600)

