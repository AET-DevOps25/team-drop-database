from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional

from travel_buddy_ai.models.attractions import (
    VectorSearchRequest, 
    VectorSearchResult, 
    AttractionIndexRequest
)
from travel_buddy_ai.services.vector_service import AttractionVectorService
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/vector", tags=["向量搜索"])

# 全局向量服务实例
vector_service = AttractionVectorService()


@router.post("/search", response_model=List[VectorSearchResult])
async def search_attractions(request: VectorSearchRequest) -> List[VectorSearchResult]:
    """
    基于语义相似度搜索旅游景点
    
    Args:
        request: 搜索请求参数
        
    Returns:
        匹配的景点列表
    """
    try:
        results = await vector_service.retrieve_by_similarity(
            query=request.query,
            score_threshold=request.score_threshold,
            limit=request.limit,
            city_filter=request.city_filter,
            country_filter=request.country_filter
        )
        
        logger.info(f"搜索查询 '{request.query}' 返回 {len(results)} 个结果")
        return results
        
    except Exception as e:
        logger.error(f"景点搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/index")
async def index_attractions(
    request: AttractionIndexRequest,
    background_tasks: BackgroundTasks
):
    """
    将指定景点索引到向量存储中
    
    Args:
        request: 索引请求参数
        background_tasks: 后台任务
        
    Returns:
        操作结果
    """
    try:
        if request.attraction_ids:
            # 索引指定的景点
            for attraction_id in request.attraction_ids:
                background_tasks.add_task(
                    vector_service.add_attraction, 
                    attraction_id
                )
            
            return {
                "message": f"已开始索引 {len(request.attraction_ids)} 个景点",
                "attraction_ids": request.attraction_ids,
                "status": "processing"
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail="必须提供要索引的景点 ID 列表"
            )
            
    except Exception as e:
        logger.error(f"景点索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"索引失败: {str(e)}")


@router.post("/index/batch")
async def batch_index_attractions(
    background_tasks: BackgroundTasks,
    page_size: int = 100,
    city_filter: Optional[str] = None
):
    """
    批量索引所有景点到向量存储中
    
    Args:
        background_tasks: 后台任务
        page_size: 每页处理的景点数量
        city_filter: 城市过滤器
        
    Returns:
        操作结果
    """
    try:
        background_tasks.add_task(
            vector_service.index_attractions_to_vector_store,
            page_size,
            city_filter
        )
        
        return {
            "message": "已开始批量索引景点",
            "page_size": page_size,
            "city_filter": city_filter,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"批量索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量索引失败: {str(e)}")


@router.delete("/attractions/{attraction_id}")
async def remove_attraction_from_index(attraction_id: int):
    """
    从向量存储中移除指定景点
    
    Args:
        attraction_id: 景点 ID
        
    Returns:
        操作结果
    """
    try:
        await vector_service.remove_attraction(attraction_id)
        
        return {
            "message": f"景点 ID {attraction_id} 已从向量存储中移除",
            "attraction_id": attraction_id,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"移除景点失败: {e}")
        raise HTTPException(status_code=500, detail=f"移除失败: {str(e)}")


@router.get("/collections")
async def get_collections():
    """
    获取所有向量集合列表
    
    Returns:
        集合列表
    """
    try:
        collections = vector_service.get_list_of_collections()
        return {
            "collections": collections,
            "count": len(collections)
        }
        
    except Exception as e:
        logger.error(f"获取集合列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取集合列表失败: {str(e)}")


@router.get("/collections/{collection_name}/info")
async def get_collection_info(collection_name: str):
    """
    获取指定集合的详细信息
    
    Args:
        collection_name: 集合名称
        
    Returns:
        集合信息
    """
    try:
        if collection_name != vector_service.collection_name:
            raise HTTPException(
                status_code=404, 
                detail=f"集合 '{collection_name}' 不存在"
            )
        
        info = await vector_service.get_collection_info()
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取集合信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取集合信息失败: {str(e)}")


@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """
    删除指定的向量集合
    
    Args:
        collection_name: 集合名称
        
    Returns:
        操作结果
    """
    try:
        vector_service.delete_collection(collection_name)
        
        return {
            "message": f"集合 '{collection_name}' 已删除",
            "collection_name": collection_name,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"删除集合失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除集合失败: {str(e)}")
