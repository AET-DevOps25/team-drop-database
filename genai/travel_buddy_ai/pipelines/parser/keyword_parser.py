import re
from travel_buddy_ai.pipelines.parser.base import InputParser
from travel_buddy_ai.pipelines.parser.schema import ParsedQuery

CITY_PATTERN = r"(Berlin|Munich|Hamburg|Paris|Rome)"
DAYS_PATTERN = r"(\d+)\s*(?:days?|天)"

class KeywordParser(InputParser):
    name = "keyword"

    def parse(self, text: str) -> ParsedQuery:
        days_match = re.search(DAYS_PATTERN, text, re.I)
        city_match = re.search(CITY_PATTERN, text, re.I)

        days = int(days_match.group(1)) if days_match else None
        city = city_match.group(1) if city_match else None

        must_visit = []
        # TODO: Add some testing pattern
        if "Neuschwanstein" in text:
            must_visit.append("Neuschwanstein Castle")

        # TODO: Add some testing pattern
        prefs = []
        if "budget" in text.lower() or "money saving" in text:
            prefs.append("budget")
        if "art" in text.lower() or "culture" in text:
            prefs.append("culture")

        return ParsedQuery(
            raw=text, days=days, start_city=city, must_visit=must_visit, preferences=prefs
        )

# TESTING USAGE ONLY