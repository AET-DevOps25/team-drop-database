import spacy
from travel_buddy_ai.pipelines.parser.base import InputParser
from travel_buddy_ai.pipelines.parser.schema import ParsedQuery

_NLP = spacy.load("en_core_web_sm")   # ⚠️ 需提前 `python -m spacy download en_core_web_sm`

class SpacyParser(InputParser):
    name = "spacy"

    def parse(self, text: str) -> ParsedQuery:
        doc = _NLP(text)
        cities = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
        numbers = [ent.text for ent in doc.ents if ent.label_ == "CARDINAL"]
        days = int(numbers[0]) if numbers else None

        return ParsedQuery(
            raw=text,
            days=days,
            start_city=cities[0] if cities else None,
            must_visit=[],
            preferences=[],
        )
