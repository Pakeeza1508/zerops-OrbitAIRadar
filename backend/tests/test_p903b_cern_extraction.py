"""P9-03B extraction regression; run with Python unittest, no database needed."""
import unittest
from datetime import datetime, timezone

from app.services.scrapper.extract import deterministic_extract, extract_fields
from app.utils.dates import extract_deadline

URL = "https://careers.cern/jobs/cern-summer-student-programme-2026-member-and-non-member-state/"

HTML = """
<html><head>
<title>CERN Summer Student Programme 2027 (Member and Non-Member State) – careers.cern</title>
</head><body>
<header class="entry-header">
<h1>CERN Summer Student Programme 2027 (Member and Non-Member State)</h1>
<div class="job-meta">Geneva, Switzerland <span class="ref">SUMM-2027</span></div>
<a href="https://jobs.smartrecruiters.com/oneclick-ui/company/CERN/publication/17fedbe8-c355-4ece-a8a1-866352de5a40?dcr_ci=CERN">Apply now</a>
<div class="before">Before 21/01/2027 at 23:59 (Geneva Time)</div>
</header>
<main>
<h2>What you'll do</h2><p>Join the summer student programme in Physics, Engineering or Computer Science.
You will be designing projects, not studying Design.</p>
<p>Ideal start date: 14/06/2027 Contract duration (in months): 2</p>
<p>Job flexibility: Fully Onsite</p>
<p>A 94 CHF per calendar day net subsistence allowance.</p>
<h2>Your eligibility</h2>
<ul><li>You are a Bachelor's or Master's student (not a PhD candidate), and have completed six semesters.</li>
<li>You remain enrolled as a full-time student throughout the stay.</li></ul>
</main></body></html>
"""


class CernExtractionTests(unittest.TestCase):
    def test_deadline_geneva_timezone(self):
        deadline, raw = extract_deadline("Before 21/01/2027 at 23:59 (Geneva Time)")
        self.assertEqual(deadline, datetime(2027, 1, 21, 22, 59, tzinfo=timezone.utc))
        self.assertIn("Geneva Time", raw)

    def test_no_deadline_from_2027_start_date(self):
        deadline, _ = extract_deadline("Ideal start date: 14/06/2027")
        self.assertIsNone(deadline)

    def test_title_year_is_2027_even_when_slug_says_2026(self):
        found = deterministic_extract(URL, HTML)
        self.assertIn("2027", found["title"])
        self.assertEqual(found["category"], "internship")

    def test_source_evidence_extraction(self):
        found = deterministic_extract(URL, HTML)
        self.assertEqual(found["locations"], ["Geneva, Switzerland"])
        self.assertEqual(found["countriesEligible"], ["Worldwide"])
        self.assertEqual(found["remote"], False)
        self.assertEqual(found["onsite"], True)
        self.assertEqual(found["educationLevels"], ["undergraduate", "masters"])
        self.assertEqual(found["fundingType"], "stipend")
        self.assertEqual(found["fundingAmount"], 94.0)
        self.assertEqual(found["currency"], "CHF")
        self.assertIn("smartrecruiters.com", found["applicationUrl"])
        self.assertEqual(found["deadline"], datetime(2027, 1, 21, 22, 59, tzinfo=timezone.utc))

    def test_designed_not_design_field(self):
        self.assertEqual(extract_fields("We designed several engineering projects"), ["Engineering"])
        self.assertNotIn("Design", extract_fields("The programme is designed for students"))


if __name__ == "__main__":
    unittest.main()
