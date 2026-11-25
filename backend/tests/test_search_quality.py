import ast
import re
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
from app.services.search_geography import geography_from_query

ROOT = Path(__file__).resolve().parents[1] / "app/services"
def isolated(filename, names, env):
    tree = ast.parse((ROOT / filename).read_text())
    nodes = [x for x in tree.body if (isinstance(x, ast.FunctionDef) and x.name in names)
             or (isinstance(x, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "NON_OPPORTUNITY_TITLES" for t in x.targets))]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),filename,"exec"),env)
    return env

class RelevanceTests(unittest.TestCase):
    def test_t3_t5_parsing(self):
        env=isolated("search.py",{"deterministic_query_filters"},
            dict(re=re,datetime=datetime,timedelta=timedelta,timezone=timezone,
                 geography_from_query=geography_from_query,SKILL_VOCAB=["AI","Python"]))
        parse=env["deterministic_query_filters"]
        a=parse("Find software engineering internships in USA for American students.")
        b=parse("Find remote AI internships for Canadian students.")
        self.assertEqual(a["categories"],["internship"])
        self.assertIn("Software Engineering",a["skills"])
        self.assertEqual(b["categories"],["internship"])
        self.assertEqual(b["skills"],["AI"])
        self.assertTrue(b["remote"])
    def test_news_and_skill_evidence(self):
        env=isolated("opportunities.py",{"skill_query_matches","is_generic_content_page"},dict(re=re))
        match=env["skill_query_matches"]
        self.assertTrue(env["is_generic_content_page"]({"title":"NASA Watches Earth's Weight, Finds Center of Mass"}))
        self.assertFalse(match({"title":"SARP East 2025 Terrestrial Fluxes Group","description":"Earth science"} ,["AI"]))
        self.assertFalse(match({"title":"Short-Term Internship","description":"General research"},["Software Engineering"]))
        self.assertTrue(match({"title":"Software Engineering Intern"},["Software Engineering"]))
        self.assertTrue(match({"title":"AI Internship"},["AI"]))
