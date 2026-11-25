"""Country recognition and search-specific eligibility, independent from user profile."""
from __future__ import annotations

import re

from app.services.iso_countries import ISO_COUNTRY_NAMES

# Accepted spelling variations; the ISO country registry supplies all other countries.
ALIASES = {
    "United States": ["usa", "u.s.a.", "us", "u.s.", "united states of america", "america", "american"],
    "United Kingdom": ["uk", "u.k.", "great britain", "britain", "england", "scotland", "welsh", "british"],
    "United Arab Emirates": ["uae", "u.a.e.", "emirati"],
    "South Korea": ["republic of korea", "korean"],
    "North Korea": ["democratic people's republic of korea"],
    "Russia": ["russian federation", "russian"],
    "Türkiye": ["turkey", "turkish", "turkiye"],
    "Czechia": ["czech republic", "czech"],
    "Ivory Coast": ["cote d'ivoire", "côte d'ivoire"],
    "Pakistan": ["pakistani"],
    "India": ["indian"],
    "Germany": ["german"],
    "France": ["french"],
    "Canada": ["canadian"],
    "Nigeria": ["nigerian"],
    "Australia": ["australian"],
    "China": ["chinese"],
    "Japan": ["japanese"],
    "Italy": ["italian"],
    "Spain": ["spanish"],
    "Brazil": ["brazilian"],
    "Bangladesh": ["bangladeshi"],
    "Nepal": ["nepali", "nepalese"],
    "Sri Lanka": ["sri lankan"],
    "Saudi Arabia": ["saudi"],
    "Netherlands": ["dutch"],
    "New Zealand": ["new zealander"],
    "South Africa": ["south african"],
    "Sweden": ["swedish"],
    "Norway": ["norwegian"],
    "Switzerland": ["swiss"],
    "Ireland": ["irish"],
    "Egypt": ["egyptian"],
    "Kenya": ["kenyan"],
    "Indonesia": ["indonesian"],
    "Malaysia": ["malaysian"],
    "Singapore": ["singaporean"],
    "Philippines": ["filipino", "philippine"],
    "Vietnam": ["vietnamese"],
    "Argentina": ["argentinian", "argentine"],
}

_CANONICAL = {}
for name in ISO_COUNTRY_NAMES:
    canonical = {
        "Russian Federation": "Russia",
        "Korea, Republic of": "South Korea",
        "Korea, Democratic People's Republic of": "North Korea",
        "Côte d'Ivoire": "Ivory Coast",
    }.get(name, name)
    if len(name) >= 4:
        _CANONICAL[name.lower()] = canonical
# Common ISO alpha-3 codes; full country and territory names are above.
_CANONICAL.update({
    "usa": "United States", "gbr": "United Kingdom", "deu": "Germany",
    "pak": "Pakistan", "ind": "India", "can": "Canada",
    "aus": "Australia", "nga": "Nigeria", "jpn": "Japan",
    "fra": "France", "chn": "China", "bra": "Brazil",
})
for canonical, aliases in ALIASES.items():
    _CANONICAL[canonical.lower()] = canonical
    for alias in aliases:
        _CANONICAL[alias.lower()] = canonical

# Prefer longest country labels; prevents "Korea" being taken from "South Korea".
_NAMES = sorted(_CANONICAL, key=len, reverse=True)
_COUNTRY_PATTERN = re.compile(
    r"(?<![a-z])(?:" + "|".join(re.escape(n) for n in _NAMES) + r")(?![a-z])",
    re.IGNORECASE,
)
_GLOBAL_MARKERS = {"global", "worldwide", "all countries", "any country", "open worldwide", "international"}
_EDUCATION_SYNONYMS = {
    "undergraduate": {"undergraduate", "bachelor", "bachelors", "bachelor's", "bsc", "college"},
    "masters": {"masters", "master", "master's", "postgraduate", "msc"},
    "phd": {"phd", "doctoral", "doctorate", "doctor of philosophy"},
}


def normalize_country(label: str) -> str:
    return _CANONICAL.get(str(label or "").strip().lower(), str(label or "").strip())


def countries_in_text(text: str) -> list[tuple[str, int, int]]:
    result = []
    occupied = []
    for match in _COUNTRY_PATTERN.finditer(text or ""):
        if any(match.start() < end and start < match.end() for start, end in occupied):
            continue
        country = normalize_country(match.group())
        result.append((country, match.start(), match.end()))
        occupied.append((match.start(), match.end()))
    return sorted(result, key=lambda entry: entry[1])


def geography_from_query(query: str) -> dict:
    """Return explicit student nationality and destination without assuming one means the other."""
    text = str(query or "")
    matches = countries_in_text(text)
    applicants, destinations = [], []
    lower = text.lower()
    for name, start, end in matches:
        pre = lower[max(0, start - 55):start]
        post = lower[end:end + 40]
        # "Indian students", "from Pakistan", "for students in Nigeria"
        nationality = bool(re.search(
            r"(?:\bfrom\s+|\bbased\s+in\s+|\bresident(?:s)?\s+(?:of|in)\s+|"
            r"\bcitizens?\s+(?:of|from)\s+|\bnationals?\s+(?:of|from)\s+|"
            r"\bfor\s+(?:students|applicants|graduates)\s+(?:from|in)\s+)$", pre
        )) or bool(re.match(r"\s+(?:students?|applicants?|citizens?|undergraduates?|graduates?)\b", post))
        # "scholarships in Germany", "internships at USA", "to Canada", "located in UK"
        destination = bool(re.search(r"(?:\bin\s+|\bto\s+|\bat\s+|\blocated\s+in\s+|\bbased\s+in\s+)$", pre))
        # Plain "from X" is nationality only if contextualized by student, applicant or first person.
        if re.search(r"\bfrom\s+$", pre) and not re.search(
            r"\b(?:students?|applicants?|graduates?|residents?|citizens?|i am|i'm|im|people|candidates?)\b", pre
        ):
            nationality = False
        if nationality:
            if name not in applicants:
                applicants.append(name)
        elif destination:
            if name not in destinations:
                destinations.append(name)
        else:
            # An unqualified country is ambiguous: do not invent eligibility or location.
            pass
    if re.search(r"\b(?:worldwide|anywhere in the world|across the world|globally)\b", lower):
        destinations = []
    return {"applicantCountries": applicants, "destinationCountries": destinations}


def applicant_eligibility(eligible_countries: list[str] | None, applicants: list[str]) -> str:
    """eligible, unverified or ineligible; missing eligibility is never proof of eligibility."""
    if not applicants:
        return "not_requested"
    listed = [str(x).strip() for x in (eligible_countries or []) if x]
    if not listed:
        return "unverified"
    normalized = {normalize_country(x) for x in listed}
    if any(x.lower() in _GLOBAL_MARKERS for x in listed):
        return "eligible"
    if any(normalize_country(x) in normalized for x in applicants):
        return "eligible"
    return "ineligible"


def destination_matches(locations: list[str] | None, destinations: list[str]) -> bool:
    if not destinations:
        return True
    # An unknown location cannot satisfy a country-specific search.
    for location in locations or []:
        recognized = {name for name, _, _ in countries_in_text(str(location))}
        if recognized.intersection(destinations):
            return True
    return False


def education_eligibility(levels: list[str] | None, requested: list[str]) -> str:
    if not requested:
        return "not_requested"
    if not levels:
        return "unverified"
    known = set()
    for level in levels:
        normalized = str(level).lower().replace("_", " ").strip()
        found = False
        for key, aliases in _EDUCATION_SYNONYMS.items():
            if normalized in aliases:
                known.add(key)
                found = True
        if not found:
            known.add(normalized)
    requested_normalized = set()
    for level in requested:
        value = str(level).lower().replace("_", " ").strip()
        matched = False
        for key, aliases in _EDUCATION_SYNONYMS.items():
            if value in aliases:
                requested_normalized.add(key)
                matched = True
        if not matched:
            requested_normalized.add(value)
    return "eligible" if known.intersection(requested_normalized) else "ineligible"
