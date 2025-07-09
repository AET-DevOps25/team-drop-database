from typing import List, Optional
from pydantic import BaseModel

class ParsedQuery(BaseModel):
    raw: str
    days: Optional[int] = None
    visited_cities: List[str] = []
    must_visit: List[str] = []
    preferences: List[str] = []
