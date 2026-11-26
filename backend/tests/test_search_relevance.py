"""Regression tests: strict AI results cannot claim unknown destination/eligibility."""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.opportunities import list_opportunities, skill_query_matches, clearly_historical_program


class _Cursor:
    def __init__(self, docs):
        self.docs = docs
    def sort(self, *_):
        return self
    def limit(self, *_):
        return self
    async def to_list(self, *_):
        return self.docs


class SearchRelevanceTests(unittest.IsolatedAsyncioTestCase):
    async def _search(self, docs, strict):
        db = MagicMock()
        db.opportunities.find.return_value = _Cursor(docs)
        with (
            patch("app.services.opportunities.get_db", return_value=db),
            patch("app.services.opportunities.get_profile", new=AsyncMock(return_value={"country": "Pakistan"})),
            patch("app.services.opportunities.enrich_opportunity", side_effect=lambda doc, profile: {
                **doc, "matchScore": 61, "matchedCountry": profile.get("country"),
            }),
        ):
            return await list_opportunities(
                "user1", categories=["fellowship"], skills=["AI"],
                applicant_countries=["Pakistan"],
                destination_countries=["United States"],
                require_verified_constraints=strict,
            )

    async def test_cern_career_break_unverified_us_not_ai_result(self):
        cern = {
            "title": "Post-Career Break Fellowship",
            "category": "fellowship", "status": "active",
            "description": "Research using AI in a scientific career-break program",
            "countriesEligible": [], "locations": [], "educationLevels": [],
            "createdAt": None,
        }
        result = await self._search([cern], True)
        self.assertEqual(result["total"], 0)

    async def test_confirmed_applicant_and_destination_still_works(self):
        record = {
            "title": "AI Fellowship in New York",
            "category": "fellowship", "status": "active",
            "description": "Artificial intelligence research fellowship",
            "countriesEligible": ["Pakistan"], "locations": ["New York, USA"],
            "educationLevels": [], "createdAt": None,
        }
        result = await self._search([record], True)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["matchedCountry"], "Pakistan")

    async def test_uncertain_record_remains_in_general_search(self):
        cern = {
            "title": "Post-Career Break Fellowship",
            "category": "fellowship", "status": "active",
            "description": "Artificial intelligence career-break research",
            "countriesEligible": [], "locations": [], "educationLevels": [],
            "createdAt": None,
        }
        result = await self._search([cern], False)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["searchDestinationEligibility"], "unverified")

    def test_terrestrial_fluxes_does_not_count_as_ai(self):
        record = {
            "title": "SARP East 2025 Terrestrial Fluxes Group",
            "shortDescription": "Summer research on terrestrial fluxes and atmospheric observations",
            "description": "Students study field measurements. AI tools are sometimes used by NASA across its projects.",
            "requiredSkills": [], "preferredSkills": [], "fieldsOfStudy": ["Earth Science"],
        }
        self.assertFalse(skill_query_matches(record, ["AI"]))
        self.assertTrue(clearly_historical_program(record))

    def test_real_ai_program_keeps_relevance(self):
        record = {
            "title": "AI Research Internship",
            "shortDescription": "Machine learning for climate prediction",
            "description": "Interns train models",
            "requiredSkills": ["Python"], "preferredSkills": [],
        }
        self.assertTrue(skill_query_matches(record, ["AI"]))
        self.assertFalse(clearly_historical_program(record))

    def test_past_check_date_alone_not_expired(self):
        record = {"title": "AI Research Internship", "lastCheckedAt": "2026-08-26"}
        self.assertFalse(clearly_historical_program(record))

    def test_historical_title_without_future_deadline(self):
        record = {"title": "2025 Summer Internship", "deadline": None}
        self.assertTrue(clearly_historical_program(record))


if __name__ == "__main__":
    unittest.main()
