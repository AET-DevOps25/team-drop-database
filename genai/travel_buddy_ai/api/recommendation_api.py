from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from travel_buddy_ai.services.recommendation_service import TravelRecommendationService
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/recommendations", tags=["旅行推荐"])

# 全局推荐服务实例
recommendation_service = TravelRecommendationService()


class TravelRecommendationRequest(BaseModel):
    """旅行推荐请求模型"""
    query: str
    limit: int = 5
    score_threshold: float = 0.7
    city_filter: Optional[str] = None
    country_filter: Optional[str] = None


class CityRecommendationRequest(BaseModel):
    """城市推荐请求模型"""
    city_name: str
    interest_keywords: Optional[str] = None
    limit: int = 10


class ThemedRecommendationRequest(BaseModel):
    """主题推荐请求模型"""
    theme: str
    location: Optional[str] = None
    limit: int = 8


class RecommendationResponse(BaseModel):
    """推荐响应模型"""
    recommendation: str
    query: str
    status: str = "success"


@router.post("/general", response_model=RecommendationResponse)
async def get_general_recommendations(request: TravelRecommendationRequest) -> RecommendationResponse:
    """
    获取基于查询的通用旅行推荐
    
    Args:
        request: 推荐请求参数
        
    Returns:
        旅行推荐
    """
    try:
        recommendation = await recommendation_service.get_travel_recommendations(
            query=request.query,
            limit=request.limit,
            score_threshold=request.score_threshold,
            city_filter=request.city_filter,
            country_filter=request.country_filter
        )
        
        logger.info(f"成功生成通用推荐，查询: '{request.query}'")
        
        return RecommendationResponse(
            recommendation=recommendation,
            query=request.query
        )
        
    except Exception as e:
        logger.error(f"生成通用推荐失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成推荐失败: {str(e)}")


@router.post("/city", response_model=RecommendationResponse)
async def get_city_recommendations(request: CityRecommendationRequest) -> RecommendationResponse:
    """
    获取基于城市的旅行推荐
    
    Args:
        request: 城市推荐请求参数
        
    Returns:
        城市旅行推荐
    """
    try:
        recommendation = await recommendation_service.get_city_recommendations(
            city_name=request.city_name,
            interest_keywords=request.interest_keywords,
            limit=request.limit
        )
        
        query = f"城市推荐: {request.city_name}"
        if request.interest_keywords:
            query += f" (兴趣: {request.interest_keywords})"
        
        logger.info(f"成功生成城市推荐，城市: '{request.city_name}'")
        
        return RecommendationResponse(
            recommendation=recommendation,
            query=query
        )
        
    except Exception as e:
        logger.error(f"生成城市推荐失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成城市推荐失败: {str(e)}")


@router.post("/themed", response_model=RecommendationResponse)
async def get_themed_recommendations(request: ThemedRecommendationRequest) -> RecommendationResponse:
    """
    获取基于主题的旅行推荐
    
    Args:
        request: 主题推荐请求参数
        
    Returns:
        主题旅行推荐
    """
    try:
        recommendation = await recommendation_service.get_themed_recommendations(
            theme=request.theme,
            location=request.location,
            limit=request.limit
        )
        
        query = f"主题推荐: {request.theme}"
        if request.location:
            query += f" (地点: {request.location})"
        
        logger.info(f"成功生成主题推荐，主题: '{request.theme}'")
        
        return RecommendationResponse(
            recommendation=recommendation,
            query=query
        )
        
    except Exception as e:
        logger.error(f"生成主题推荐失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成主题推荐失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    推荐服务健康检查
    
    Returns:
        服务状态
    """
    try:
        # 简单的健康检查
        return {
            "status": "healthy",
            "service": "recommendation_service",
            "message": "推荐服务运行正常"
        }
    except Exception as e:
        logger.error(f"推荐服务健康检查失败: {e}")
        raise HTTPException(status_code=503, detail=f"服务不可用: {str(e)}")
