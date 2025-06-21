from typing import Dict, Any
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
)
from travel_buddy_ai.pipelines.parser.base import InputParser
from travel_buddy_ai.pipelines.parser.schema import ParsedQuery

_SYSTEM_PROMPT = (
    "You are a travel query parser. "
    "Extract the following JSON keys from the user message: "
    "days (int or null), start_city, end_city, must_visit (list), preferences (list). "
    "Return ONLY valid JSON."
)

class LLMParser(InputParser):
    name = "llm"

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model_name=model_name, temperature=0)

    def parse(self, text: str) -> ParsedQuery:
        resp = self.llm(
            [
                SystemMessage(content=_SYSTEM_PROMPT),
                HumanMessage(content=text),
            ]
        )
        data: Dict[str, Any] = resp.json()  # LangChain 会自动 .json() 成 dict
        return ParsedQuery(raw=text, **data)