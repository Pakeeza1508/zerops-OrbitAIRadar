from datetime import datetime, timezone

from app.services.matching.engine import score_opportunity
from app.services.scrapper.extract import deterministic_extract
from app.services.scrapper.normalize import build_opportunity
from app.services.search import deterministic_query_filters
from app.utils.dates import extract_deadline, parse_date


def test_parse_date_requires_explicit_year():
    assert parse_date("September 14, 2026") is not None
    assert parse_date("September 14") is None


def test_deadline_extraction():
    dt, raw = extract_deadline("Application deadline: September 14, 2026")
    assert dt == datetime(2026, 9, 14, tzinfo=timezone.utc)
    assert raw == "September 14, 2026"


def test_deterministic_extraction_finds_apply_and_signals():
    html = """
    <html><head><title>AI Internship 2026</title>
    <meta name="description" content="Paid fully remote AI internship"></head>
    <body><h1>AI Internship 2026</h1>
    <p>Deadline: September 14, 2026</p>
    <a href="/apply">Apply now</a></body></html>
    """
    out = deterministic_extract("https://example.com/internship", html)
    assert out["category"] == "internship"
    assert out["applicationUrl"] == "https://example.com/apply"
    assert out["remote"] is True
    assert out["fundingType"] == "paid"
    assert out["deadline"].date().isoformat() == "2026-09-14"


def test_match_engine_profile_fit():
    result = score_opportunity(
        {
            "requiredSkills": ["Python", "React"],
            "countriesEligible": ["Global"],
            "category": "internship",
            "remote": True,
            "fundingType": "stipend",
        },
        {
            "skills": ["Python"],
            "country": "Pakistan",
            "preferredCategories": ["internship"],
            "locationPreference": ["remote"],
            "fundingPreference": "funded_only",
        },
    )
    assert result["matchScore"] >= 70
    assert result["eligibilityStatus"] == "eligible"
    assert "React" in result["missingSkills"]


def test_query_fallback():
    out = deterministic_query_filters(
        "Find fully funded remote AI internships closing within 60 days"
    )
    assert "internship" in out["categories"]
    assert out["remote"] is True
    assert out["fundingRequired"] is True
    assert out["deadlineBefore"] is not None


def test_normalizer_builds_valid_document():
    html = """
    <html><head><title>Open Source Fellowship 2026</title></head>
    <body><h1>Open Source Fellowship 2026</h1>
    <p>Applications are open worldwide. Deadline: December 1, 2026.</p>
    <a href="/apply">Apply</a></body></html>
    """
    deterministic = deterministic_extract("https://example.com/fellowship", html)
    opp = build_opportunity(
        "https://example.com/fellowship",
        deterministic,
        None,
        None,
        "listing",
    )
    assert opp is not None
    assert opp.canonicalUrl == "https://example.com/fellowship"
    assert opp.applicationUrl == "https://example.com/apply"


def test_generic_listing_is_not_concrete_opportunity():
    html = """
    <html><head><title>Scholarship Database</title></head>
    <body><h1>Scholarship Database</h1><p>Search scholarships and all opportunities.</p>
    <a href="/scholarship/a">Scholarship A</a></body></html>
    """
    out = deterministic_extract("https://example.com/scholarships", html, "scholarship")
    assert out["isLikelyOpportunity"] is False
