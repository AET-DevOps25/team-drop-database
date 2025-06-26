from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from travel_buddy_ai.pipelines.parser import get_parser
# from travel_buddy_ai.pipelines.retriever import semantic_search

router = APIRouter()

class RecommendRequest(BaseModel):
    query: str
    user_id: Optional[int] = None


class RecommendResponse(BaseModel):
    itinerary: str


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    if not req.query.strip():
        raise HTTPException(400, "query cannot be empty")

    parser = get_parser("llm")
    parsed = parser.parse(req.query)
    print("解析结果 ->", parsed)

    # docs = semantic_search(req.query, parsed, top_k=6)

    # TODO: 调用 MCP Pipeline
    return RecommendResponse(
        itinerary="Day 1: Berlin → Neuschwanstein Castle\nDay 2: ..."
    )
