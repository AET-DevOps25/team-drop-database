from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from travel_buddy_ai.pipelines.parser import get_parser
from travel_buddy_ai.pipelines.retriever import semantic_search
from travel_buddy_ai.api.vector_api import router as vector_router
from travel_buddy_ai.services.qa_system_fixed import AttractionQASystem

router = APIRouter()
router.include_router(vector_router)

class RecommendRequest(BaseModel):
    query: str
    user_id: Optional[int] = None


class RecommendResponse(BaseModel):
    itinerary: str

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    success: bool
    question: str
    answer: str
    results_count: int


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    if not req.query.strip():
        raise HTTPException(400, "query cannot be empty")

    parser = get_parser("llm")
    parsed = parser.parse(req.query)
    print("Parse result ->", parsed)

    docs = semantic_search(req.query, parsed, top_k=6)

    # TODO: Call MCP Pipeline
    return RecommendResponse(
        itinerary="Day 1: Berlin → Neuschwanstein Castle\nDay 2: ..."
    )

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(req: QuestionRequest, request: Request):
    if not hasattr(request.app.state, "qa_system") or request.app.state.qa_system is None:
        try:
            request.app.state.qa_system = AttractionQASystem()
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"QA system initialization failed: {str(e)}"
            )

    qa_system = request.app.state.qa_system

    if qa_system is None:
        raise HTTPException(
            status_code=503,
            detail="QA system not initialized or initialization failed, please try again later"
        )

    if not req.question.strip():
        raise HTTPException(400, "question cannot be empty")

    try:
        result = qa_system.ask(req.question.strip())

        return QuestionResponse(
            success=True,
            question=result["question"],
            answer=result["answer"],
            results_count=result["results_count"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {str(e)}"
        )