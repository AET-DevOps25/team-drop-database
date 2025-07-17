from typing import Dict
from travel_buddy_ai.pipelines.parser.base import InputParser
from travel_buddy_ai.pipelines.parser.keyword_parser import KeywordParser
from travel_buddy_ai.pipelines.parser.llm_parser import LLMParser

_PARSERS: Dict[str, InputParser] = {
    KeywordParser.name: KeywordParser(),
    LLMParser.name: LLMParser(),
}

def get_parser(name: str = "keyword") -> InputParser:
    if name not in _PARSERS:
        raise ValueError(f"parser '{name}' not registered")
    return _PARSERS[name]