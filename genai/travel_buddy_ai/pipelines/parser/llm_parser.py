import json
import os
from typing import Any, Dict
from pydantic import ValidationError
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from travel_buddy_ai.pipelines.parser.base import InputParser
from travel_buddy_ai.pipelines.parser.schema import ParsedQuery
from travel_buddy_ai.core.config import settings

_SYSTEM_PROMPT = """You are a travel query parser.

Your task is to extract structured information from the user's natural language travel query.

You must respond in **valid JSON** with the following fields:
{
  "days": int or null,
  "visited_cities": list of strings,       // e.g. ["Berlin", "Munich"]
  "must_visit": list of strings,           // e.g. ["Brandenburg Gate"]
  "preferences": list of strings           // e.g. ["nature", "food"]
}

If any field is not mentioned, set it to null or [] as appropriate.
Respond with **JSON only**. No explanations or extra text.

Example:
User: I want to visit Berlin, Hamburg, and Dresden for 5 days. I love architecture and museums.
→
{
  "days": 5,
  "visited_cities": ["Berlin", "Hamburg", "Dresden"],
  "must_visit": [],
  "preferences": ["architecture", "museums"]
}
"""

class LLMParser(InputParser):
    name = "llm"

    def __init__(self, model_name: str = "gpt-4o"):
        a = settings
        if not settings.openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY. Please set it in .env or your environment.")

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=SecretStr(settings.openai_api_key)
        )

    def parse(self, text: str) -> ParsedQuery:
        try:
            resp = self.llm(
                [
                    SystemMessage(content=_SYSTEM_PROMPT),
                    HumanMessage(content=text),
                ]
            )
            data: Dict[str, Any] = resp.model_dump()

            json_str = resp.content.strip()
            parsed_dict: Dict[str, Any] = json.loads(json_str)
            return ParsedQuery(raw=text, **parsed_dict)
        except (ValidationError, KeyError, TypeError, ValueError) as e:
            print(f"[LLMParser] Invalid response: {e}")
            return ParsedQuery(raw=text)

