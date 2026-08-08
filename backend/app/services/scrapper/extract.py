
"""Deterministic extraction, cheapest strategy first.

Priority: JSON-LD/schema.org -> meta tags -> CSS heuristics -> regex/date parsing.
Groq is only invoked by the pipeline when this module cannot produce enough data.
"""

import json
import re

from bs4 import BeautifulSoup

from app.utils.dates import extract_deadline, has_closed_marker, parse_date
from app.utils.text import sanitize_display, strip_html, truncate

CATEGORY_KEYWORDS = {
    "scholarship": ("scholarship", "bursary", "tuition award", "studentship"),
    "internship": ("internship", "intern programme", "intern program", "summer intern"),
    "fellowship": ("fellowship", "fellow programme", "fellow program"),
    "hackathon": ("hackathon", "hack day", "codefest", "datathon"),
    "grant": ("grant", "funding call", "seed fund", "micro-grant"),
    "competition": ("competition", "contest", "challenge", "olympiad", "award"),
    "research": ("research programme", "research program", "reu", "research assistant", "phd position"),
    "open_source": ("open source", "gsoc", "google summer of code", "outreachy", "hacktoberfest"),
    "developer_program": ("developer program", "developer programme", "student ambassador", "dev program"),
    "mentorship": ("mentorship", "mentoring programme", "mentoring program", "mentee"),
}

SKILL_VOCAB = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Django", "Flask", "FastAPI",
    "Java", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "SQL", "NoSQL",
    "MongoDB", "PostgreSQL", "AI", "Machine Learning", "Deep Learning", "Data Science",
    "Data Analysis", "NLP", "Computer Vision", "Cybersecurity", "Blockchain", "Cloud",
    "AWS", "Azure", "DevOps", "Docker", "Kubernetes", "Linux", "Git", "Open Source",
    "UI/UX", "Figma", "Product Design", "Mobile Development", "Android", "iOS", "Robotics",
    "Embedded Systems", "Quantum Computing", "Statistics", "Mathematics", "Research",
]

EDUCATION_VOCAB = {
    "high school": ["high school", "secondary school", "pre-university"],
    "undergraduate": ["undergraduate", "bachelor", "bsc", "b.tech", "college student"],
    "masters": ["master", "msc", "m.tech", "graduate student", "postgraduate"],
    "phd": ["phd", "doctoral", "doctorate"],
    "postdoc": ["postdoc", "post-doctoral"],
    "bootcamp": ["bootcamp", "self-taught"],
}

FIELD_VOCAB = [
    "Computer Science", "Software Engineering", "Data Science", "Artificial Intelligence",
    "Engineering", "Mathematics", "Physics", "Biology", "Chemistry", "Medicine",
    "Economics", "Business", "Law", "Design", "Social Sciences", "Environmental Science",
    "Information Technology", "Cybersecurity", "Electrical Engineering", "Mechanical Engineering",
]

FUNDING_PATTERNS = [
    (r"fully[- ]funded", "fully_funded"),
    (r"full scholarship", "fully_funded"),
    (r"partial(?:ly)?[- ]funded", "partially_funded"),
    (r"stipend", "stipend"),
    (r"travel grant", "travel_grant"),
    (r"prize pool", "prize"),
    (r"cash prize", "prize"),
    (r"unpaid", "unpaid"),
    (r"paid internship", "paid"),
]

AMOUNT_RE = re.compile(
    r"(?:(US\$|\$|€|£|₹|PKR|USD|EUR|GBP|INR)\s?([\d][\d,\.]{2,12})|([\d][\d,\.]{2,12})\s?(USD|EUR|GBP|INR|PKR))",
    re.IGNORECASE,
)
CURRENCY_MAP = {"$": "USD", "us$": "USD", "€": "EUR", "£": "GBP", "₹": "INR"}

REMOTE_RE = re.compile(r"\b(fully remote|remote[- ]first|work from home|remote)\b", re.IGNORECASE)
HYBRID_RE = re.compile(r"\bhybrid\b", re.IGNORECASE)
ONSITE_RE = re.compile(r"\b(on[- ]site|onsite|in[- ]person)\b", re.IGNORECASE)

COUNTRY_LIST = [
    "Pakistan", "India", "Bangladesh", "Nigeria", "Kenya", "Ghana", "South Africa", "Egypt",
    "United States", "USA", "Canada", "United Kingdom", "UK", "Germany", "France", "Italy",
    "Spain", "Netherlands", "Sweden", "Norway", "Denmark", "Finland", "Switzerland", "Ireland",
    "Australia", "New Zealand", "Japan", "China", "South Korea", "Singapore", "Malaysia",
    "Indonesia", "Philippines", "Vietnam", "Turkey", "Brazil", "Mexico", "Argentina", "Chile",
    "Nepal", "Sri Lanka", "Morocco", "Tunisia", "Jordan", "UAE", "Saudi Arabia", "Qatar",
]
GLOBAL_RE = re.compile(
    r"\b(open to (?:all|applicants from all|students from all)|worldwide|all nationalities|any country|international students|globally)\b",
    re.IGNORECASE,
)

BULLET_LIMIT = 12


def _soup(html: str) -> BeautifulSoup:
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")


def page_text(html: str) -> tuple[str, BeautifulSoup]:
    soup = _soup(html)
    for tag in soup(["script", "style", "nav", "footer", "header", "form", "noscript", "svg"]):
        tag.decompose()
    main = soup.find("article") or soup.find("main") or soup.body or soup
    return strip_html(main.get_text(" ")), soup


def extract_jsonld(soup: BeautifulSoup) -> dict:
    """Parse schema.org JSON-LD blocks for the most useful opportunity types."""
    out: dict = {}
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = script.string or script.get_text() or ""
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue
        nodes = data if isinstance(data, list) else [data]
        if isinstance(data, dict) and isinstance(data.get("@graph"), list):
            nodes = data["@graph"]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            types = node.get("@type")
            types = [types] if isinstance(types, str) else (types or [])
            types = [t.lower() for t in types if isinstance(t, str)]
            if any(t in ("jobposting", "event", "educationaloccupationalprogram", "course", "article", "newsarticle", "blogposting", "webpage") for t in types):
                out.setdefault("title", node.get("title") or node.get("name") or node.get("headline"))
                desc = node.get("description")
                if desc:
                    out.setdefault("description", strip_html(desc))
                org = node.get("hiringOrganization") or node.get("organizer") or node.get("provider") or node.get("publisher")
                if isinstance(org, dict):
                    out.setdefault("organization", org.get("name"))
                elif isinstance(org, str):
                    out.setdefault("organization", org)
                deadline = (
                    node.get("applicationDeadline")
                    or node.get("validThrough")
                    or node.get("endDate")
                )
                if deadline:
                    out.setdefault("deadlineRaw", str(deadline))
                start = node.get("datePosted") or node.get("startDate")
                if start:
                    out.setdefault("applicationOpenRaw", str(start))
                loc = node.get("jobLocation") or node.get("location")
                if isinstance(loc, dict):
                    addr = loc.get("address")
                    if isinstance(addr, dict):
                        parts = [addr.get("addressLocality"), addr.get("addressCountry")]
                        text = ", ".join([p for p in parts if isinstance(p, str)])
                        if text:
                            out.setdefault("locations", [text])
                    elif isinstance(loc.get("name"), str):
                        out.setdefault("locations", [loc["name"]])
                if node.get("jobLocationType") == "TELECOMMUTE":
                    out.setdefault("remote", True)
    return {k: v for k, v in out.items() if v}


def extract_meta(soup: BeautifulSoup) -> dict:
    out: dict = {}

    def meta(*names: str) -> str | None:
        for name in names:
            tag = soup.find("meta", attrs={"property": name}) or soup.find(
                "meta", attrs={"name": name}
            )
            if tag and tag.get("content"):
                return tag["content"].strip()
        return None

    out["title"] = meta("og:title", "twitter:title") or (
        soup.title.get_text().strip() if soup.title else None
    )
    out["description"] = meta("og:description", "description", "twitter:description")
    out["organization"] = meta("og:site_name", "author")
    canonical = soup.find("link", attrs={"rel": "canonical"})
    if canonical and canonical.get("href"):
        out["canonical"] = canonical["href"].strip()
    return {k: v for k, v in out.items() if v}


def guess_category(text: str, hint: str | None = None) -> str:
    lowered = text.lower()[:6000]
    best, best_hits = hint or "other", 0
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = sum(lowered.count(k) for k in keywords)
        if hits > best_hits:
            best, best_hits = category, hits
    if best_hits == 0 and hint:
        return hint
    return best


def extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = []
    for skill in SKILL_VOCAB:
        token = skill.lower()
        pattern = r"(?<![a-z0-9])" + re.escape(token) + r"(?![a-z0-9])"
        if re.search(pattern, lowered):
            found.append(skill)
    return found[:15]


def extract_education_levels(text: str) -> list[str]:
    lowered = text.lower()
    return [level for level, terms in EDUCATION_VOCAB.items() if any(t in lowered for t in terms)]


def extract_fields(text: str) -> list[str]:
    lowered = text.lower()
    return [f for f in FIELD_VOCAB if f.lower() in lowered][:8]


def extract_countries(text: str) -> list[str]:
    if GLOBAL_RE.search(text):
        return ["Global"]
    lowered = text.lower()
    found = []
    for country in COUNTRY_LIST:
        if re.search(r"(?<![a-z])" + re.escape(country.lower()) + r"(?![a-z])", lowered):
            found.append(country)
    return found[:15]


def extract_funding(text: str) -> tuple[str | None, float | None, str | None]:
    lowered = text.lower()
    funding_type = None
    for pattern, label in FUNDING_PATTERNS:
        if re.search(pattern, lowered):
            funding_type = label
            break
    amount, currency = None, None
    match = AMOUNT_RE.search(text)
    if match:
        symbol = (match.group(1) or match.group(4) or "").lower()
        raw = match.group(2) or match.group(3) or ""
        try:
            amount = float(raw.replace(",", ""))
        except ValueError:
            amount = None
        currency = CURRENCY_MAP.get(symbol, symbol.upper() or None)
        if amount is not None and amount < 100:
            amount, currency = None, None
    return funding_type, amount, currency


def extract_bullets(soup: BeautifulSoup, keywords: tuple[str, ...]) -> list[str]:
    """Find list items under headings matching the given keywords."""
    out: list[str] = []
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "strong", "b"]):
        label = heading.get_text(" ").strip().lower()
        if not label or len(label) > 90:
            continue
        if not any(k in label for k in keywords):
            continue
        node = heading.find_next(["ul", "ol", "p"])
        if not node:
            continue
        if node.name in ("ul", "ol"):
            for li in node.find_all("li", limit=BULLET_LIMIT):
                value = strip_html(li.get_text(" "))
                if 8 < len(value) < 300:
                    out.append(value)
        else:
            value = strip_html(node.get_text(" "))
            if 15 < len(value) < 400:
                out.append(value)
        if len(out) >= BULLET_LIMIT:
            break
    seen, unique = set(), []
    for item in out:
        if item.lower() not in seen:
            seen.add(item.lower())
            unique.append(item)
    return unique[:BULLET_LIMIT]



def extract_application_url(soup: BeautifulSoup, base_url: str) -> str | None:
    """Find the most likely public application/registration URL on the page."""
    from urllib.parse import urljoin

    best: tuple[int, str] | None = None
    for anchor in soup.find_all("a", href=True):
        href = (anchor.get("href") or "").strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        label = strip_html(anchor.get_text(" ")).lower()
        target = urljoin(base_url, href)
        blob = f"{label} {target}".lower()
        score = 0
        if "apply" in label:
            score += 6
        if "application" in label:
            score += 5
        if "register" in label or "registration" in label:
            score += 4
        if any(x in blob for x in ("apply", "application", "register", "submission")):
            score += 2
        if "login" in blob or "sign in" in label:
            score -= 3
        if score > 0 and (best is None or score > best[0]):
            best = (score, target)
    return best[1] if best else None


GENERIC_LISTING_TITLE_TERMS = (
    "opportunities for individuals",
    "scholarship database",
    "search scholarships",
    "all internships",
    "all opportunities",
    "events calendar",
    "programmes and opportunities",
    "programs and opportunities",
)


def concrete_opportunity_score(result: dict) -> int:
    """Score whether deterministic extraction resembles one concrete apply-able item.

    This intentionally favours precision over recall. Ambiguous pages may still be
    accepted later when Groq explicitly classifies them as an opportunity.
    """
    title = (result.get("title") or "").strip().lower()
    if any(term in title for term in GENERIC_LISTING_TITLE_TERMS):
        return -3

    score = 0
    if result.get("applicationUrl"):
        score += 3
    if result.get("deadline"):
        score += 3
    if result.get("requirements") or result.get("eligibilityText"):
        score += 2
    if result.get("fundingType"):
        score += 1
    if result.get("countriesEligible") or result.get("educationLevels"):
        score += 1
    if result.get("usedJsonLd"):
        score += 1
    category = result.get("category")
    if category and category != "other":
        score += 1
    if result.get("closedMarker"):
        score += 1
    return score


def is_likely_concrete_opportunity(result: dict) -> bool:
    return concrete_opportunity_score(result) >= 3


def deterministic_extract(url: str, html: str, category_hint: str | None = None) -> dict:
    """Run the whole deterministic chain and report extraction confidence."""
    text, raw_soup = page_text(html)
    soup = _soup(html)

    jsonld = extract_jsonld(soup)
    meta = extract_meta(soup)

    title = jsonld.get("title") or meta.get("title")
    if title:
        title = re.split(r"\s+[|\u2013\u2014-]\s+", title)[0].strip()[:220]

    h1 = soup.find("h1")
    if (not title or len(title) < 8) and h1:
        title = strip_html(h1.get_text(" "))[:220]

    description = sanitize_display(jsonld.get("description") or meta.get("description")) or truncate(
        text, 900
    )
    signal_text = f"{title or ''} {description or ''} {text}"

    deadline = parse_date(jsonld.get("deadlineRaw")) if jsonld.get("deadlineRaw") else None
    deadline_text = jsonld.get("deadlineRaw") if deadline else None
    if not deadline:
        deadline, deadline_text = extract_deadline(signal_text)

    funding_type, funding_amount, currency = extract_funding(signal_text)
    countries = extract_countries(signal_text)
    remote = True if jsonld.get("remote") or REMOTE_RE.search(signal_text) else None
    hybrid = True if HYBRID_RE.search(signal_text) else None
    onsite = True if ONSITE_RE.search(signal_text) else None

    requirements = extract_bullets(
        soup, ("requirement", "eligib", "who can apply", "criteria", "qualification")
    )
    benefits = extract_bullets(soup, ("benefit", "what you get", "award", "perks", "offer"))

    eligibility_text = None
    for heading in soup.find_all(["h2", "h3", "h4"]):
        if "eligib" in heading.get_text(" ").lower():
            node = heading.find_next(["p", "ul"])
            if node:
                eligibility_text = truncate(strip_html(node.get_text(" ")), 700)
            break

    result = {
        "title": title,
        "organization": jsonld.get("organization") or meta.get("organization"),
        "description": description,
        "shortDescription": truncate(description, 200),
        "category": guess_category(signal_text, category_hint),
        "canonical": meta.get("canonical"),
        "applicationUrl": extract_application_url(soup, url),
        "deadline": deadline,
        "deadlineText": deadline_text,
        "applicationOpenDate": parse_date(jsonld.get("applicationOpenRaw"))
        if jsonld.get("applicationOpenRaw")
        else None,
        "countriesEligible": countries,
        "locations": jsonld.get("locations") or [],
        "remote": remote,
        "hybrid": hybrid,
        "onsite": onsite,
        "educationLevels": extract_education_levels(signal_text),
        "fieldsOfStudy": extract_fields(signal_text),
        "requiredSkills": extract_skills(signal_text[:6000]),
        "fundingType": funding_type,
        "fundingAmount": funding_amount,
        "currency": currency,
        "requirements": requirements,
        "benefits": benefits,
        "eligibilityText": eligibility_text,
        "closedMarker": has_closed_marker(text),
        "text": text,
        "usedJsonLd": bool(jsonld),
    }

    filled = sum(
        1
        for key in (
            "title",
            "organization",
            "description",
            "deadline",
            "countriesEligible",
            "requiredSkills",
            "fundingType",
            "requirements",
        )
        if result.get(key)
    )
    result["completeness"] = filled / 8
    result["concreteScore"] = concrete_opportunity_score(result)
    result["isLikelyOpportunity"] = is_likely_concrete_opportunity(result)
    del raw_soup
    return result

