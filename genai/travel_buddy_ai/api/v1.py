from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from travel_buddy_ai.pipelines.parser import get_parser
from travel_buddy_ai.pipelines.retriever import semantic_search
from travel_buddy_ai.api.vector_api import router as vector_router
from travel_buddy_ai.core.state import app_state  # 导入状态管理

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
    print("解析结果 ->", parsed)

    docs = semantic_search(req.query, parsed, top_k=6)

    # TODO: 调用 MCP Pipeline
    return RecommendResponse(
        itinerary="Day 1: Berlin → Neuschwanstein Castle\nDay 2: ..."
    )

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(req: QuestionRequest):
    # 从全局状态获取QA系统
    qa_system = app_state.get_qa_system()
    
    if qa_system is None:
        raise HTTPException(
            status_code=503, 
            detail="QA系统未初始化或初始化失败，请稍后再试"
        )

    if not req.question.strip():
        raise HTTPException(400, "question cannot be empty")

    try:
        # 调用QA系统，使用正确的方法名
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
            detail=f"问答处理失败: {str(e)}"
        )