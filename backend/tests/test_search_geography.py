"""Regression tests for global search intent: python -m unittest discover -s tests -p 'test_search_geography.py'."""
import unittest

from app.services.search_geography import (
    applicant_eligibility,
    destination_matches,
    destination_eligibility,
    remote_eligibility,
    education_eligibility,
    geography_from_query,
)


class GeographyTests(unittest.TestCase):
    def test_foreign_study_india_to_germany(self):
        self.assertEqual(geography_from_query("Find scholarships in Germany for Indian students"), {
            "applicantCountries": ["India"], "destinationCountries": ["Germany"],
        })

    def test_domestic_pakistan(self):
        self.assertEqual(geography_from_query("AI internships in Pakistan for Pakistani students"), {
            "applicantCountries": ["Pakistan"], "destinationCountries": ["Pakistan"],
        })

    def test_foreign_study_pakistan_to_usa(self):
        self.assertEqual(geography_from_query("AI fellowships in USA for Pakistani students"), {
            "applicantCountries": ["Pakistan"], "destinationCountries": ["United States"],
        })

    def test_canadian_remote_no_destination(self):
        self.assertEqual(geography_from_query("Remote internships for Canadian students"), {
            "applicantCountries": ["Canada"], "destinationCountries": [],
        })

    def test_nigeria_worldwide(self):
        self.assertEqual(geography_from_query("Scholarships worldwide for Nigerian students"), {
            "applicantCountries": ["Nigeria"], "destinationCountries": [],
        })

    def test_usa_domestic(self):
        self.assertEqual(geography_from_query("Internships in USA for American students"), {
            "applicantCountries": ["United States"], "destinationCountries": ["United States"],
        })

    def test_third_country_asia(self):
        self.assertEqual(geography_from_query("Scholarships in Japan for students from Bangladesh"), {
            "applicantCountries": ["Bangladesh"], "destinationCountries": ["Japan"],
        })

    def test_no_country_unrestricted(self):
        self.assertEqual(geography_from_query("Remote Python internships worldwide"), {
            "applicantCountries": [], "destinationCountries": [],
        })

    def test_antarctica_not_assumed_eligible(self):
        self.assertEqual(geography_from_query("Internships in Antarctica closing tomorrow")["destinationCountries"], ["Antarctica"])

    def test_eligibility_explicit_exclusion(self):
        self.assertEqual(applicant_eligibility(["United States"], ["India"]), "ineligible")

    def test_eligibility_worldwide(self):
        self.assertEqual(applicant_eligibility(["Worldwide"], ["India"]), "eligible")

    def test_eligibility_unknown_is_unverified(self):
        self.assertEqual(applicant_eligibility([], ["India"]), "unverified")

    def test_destination_strict_not_nationality(self):
        self.assertTrue(destination_matches(["Berlin, Germany"], ["Germany"]))
        self.assertFalse(destination_matches(["Karachi, Pakistan"], ["Germany"]))
        self.assertTrue(destination_matches([], ["Germany"]))
        self.assertEqual(destination_eligibility([], ["Germany"]), "unverified")
        self.assertEqual(destination_eligibility(["Karachi, Pakistan"], ["Germany"]), "ineligible")
        self.assertEqual(destination_eligibility(["Berlin, Germany"], ["Germany"]), "eligible")


    def test_remote_unknown_not_rejected(self):
        self.assertEqual(remote_eligibility(None, True), "unverified")
        self.assertEqual(remote_eligibility(True, True), "eligible")
        self.assertEqual(remote_eligibility(False, True), "ineligible")
        self.assertEqual(remote_eligibility(None, None), "not_requested")

    def test_unverified_location_must_not_be_claimed_as_match(self):
        self.assertEqual(destination_eligibility(["Not specified"], ["United States"]), "unverified")
        self.assertEqual(destination_eligibility([], ["Japan"]), "unverified")
        self.assertEqual(destination_eligibility(["New York, USA"], ["United States"]), "eligible")
        self.assertEqual(destination_eligibility(["Berlin, Germany"], ["United States"]), "ineligible")

    def test_education_unknown_is_unverified(self):
        self.assertEqual(education_eligibility([], ["undergraduate"]), "unverified")
        self.assertEqual(education_eligibility(["PhD"], ["undergraduate"]), "ineligible")
        self.assertEqual(education_eligibility(["Bachelor's"], ["undergraduate"]), "eligible")


if __name__ == "__main__":
    unittest.main()
