"""Regression tests: strict AI results cannot claim unknown destination/eligibility."""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.opportunities import list_opportunities


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
            "description": "AI career-break research",
            "countriesEligible": [], "locations": [], "educationLevels": [],
            "createdAt": None,
        }
        result = await self._search([cern], False)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["searchDestinationEligibility"], "unverified")


if __name__ == "__main__":
    unittest.main()
