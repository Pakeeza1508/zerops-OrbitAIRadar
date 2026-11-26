"""Phase 9: positive match and Groq fallback reliability regression tests."""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.search_reconcile import reconcile_ai_filters
from app.services.opportunities import list_opportunities


class _Cursor:
    def __init__(self, rows):
        self.rows = rows
    def sort(self, *args):
        return self
    def limit(self, *args):
        return self
    async def to_list(self, *args):
        return self.rows


class FilterReliabilityTests(unittest.TestCase):
    def test_fallback_when_groq_unavailable(self):
        raw, used, why = reconcile_ai_filters(
            "Find AI internships in Japan for Indian students", None
        )
        self.assertFalse(used)
        self.assertEqual(why, "ai_unavailable_or_invalid")
        self.assertEqual(raw["applicantCountries"], ["India"])
        self.assertEqual(raw["destinationCountries"], ["Japan"])
        self.assertIn("internship", raw["categories"])

    def test_reject_incomplete_groq_result(self):
        raw, used, why = reconcile_ai_filters(
            "Remote internships for Canadian students", {"categories": ["internship"]}
        )
        self.assertFalse(used)
        self.assertEqual(why, "ai_incomplete")
        self.assertEqual(raw["remote"], True)

    def test_ai_cannot_overwrite_explicit_geo_or_skills(self):
        groq = {
            "categories": ["scholarship"], "skills": ["Cooking"],
            "remote": None, "fundingRequired": None,
            "educationLevels": [], "applicantCountries": ["Pakistan"],
            "destinationCountries": ["Germany"], "queryText": "cooking",
        }
        raw, used, why = reconcile_ai_filters(
            "Find remote AI internships in Japan for Canadian students", groq
        )
        self.assertTrue(used)
        self.assertEqual(why, "ai_validated")
        self.assertEqual(raw["categories"], ["internship"])
        self.assertIn("AI", raw["skills"])
        self.assertEqual(raw["applicantCountries"], ["Canada"])
        self.assertEqual(raw["destinationCountries"], ["Japan"])
        self.assertEqual(raw["remote"], True)
        self.assertIsNone(raw["queryText"])

    def test_worldwide_has_no_destination(self):
        groq = {
            "categories": ["scholarship"], "skills": [],
            "remote": None, "fundingRequired": True,
            "educationLevels": [], "applicantCountries": ["Nigeria"],
            "destinationCountries": ["Nigeria"],
        }
        raw, used, _ = reconcile_ai_filters(
            "Fully funded scholarships worldwide for Nigerian students", groq
        )
        self.assertTrue(used)
        self.assertEqual(raw["destinationCountries"], [])


class PositiveMatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_genuine_matching_opportunity_is_not_lost(self):
        positive = {
            "title": "AI Research Internship 2027",
            "category": "internship",
            "status": "active",
            "description": "Machine learning research and artificial intelligence",
            "shortDescription": "Remote AI internship for 2027",
            "requiredSkills": ["AI", "Python"],
            "countriesEligible": ["Worldwide"],
            "locations": [],
            "remote": True,
            "educationLevels": ["undergraduate"],
            "createdAt": None,
        }
        unrelated = {
            **positive,
            "title": "SARP East 2025 Terrestrial Fluxes Group",
            "shortDescription": "Earth science terrestrial fluxes",
            "description": "NASA earth science remote field observations",
            "requiredSkills": ["Earth Science"],
        }
        db = MagicMock()
        db.opportunities.find.return_value = _Cursor([positive, unrelated])
        with (
            patch("app.services.opportunities.get_db", return_value=db),
            patch("app.services.opportunities.get_profile", new=AsyncMock(return_value={"country": "Pakistan"})),
            patch("app.services.opportunities.enrich_opportunity", side_effect=lambda doc, profile: {
                **doc, "matchScore": 82, "matchedCountry": profile.get("country")
            }),
        ):
            result = await list_opportunities(
                "test-user", categories=["internship"], skills=["AI"],
                remote=True, applicant_countries=["Canada"],
                education_levels=["undergraduate"], require_verified_constraints=True
            )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["title"], "AI Research Internship 2027")
        self.assertEqual(result["items"][0]["matchedCountry"], "Canada")
        self.assertEqual(result["items"][0]["searchEligibility"], "eligible")


if __name__ == "__main__":
    unittest.main()
