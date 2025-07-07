from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document

from travel_buddy_ai.models.common import (
    VectorSearchRequest, 
    VectorSearchResult, 
    DocumentIndexRequest,
    DocumentModel
)
from travel_buddy_ai.services.generic_vector_service import GenericVectorService
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/vector", tags=["向量搜索"])

# 全局向量服务实例
vector_service = GenericVectorService()


@router.post("/search", response_model=List[VectorSearchResult])
async def search_documents(request: VectorSearchRequest) -> List[VectorSearchResult]:
    """
    基于语义相似度搜索文档
    
    Args:
        request: 搜索请求参数
        
    Returns:
        匹配的文档列表
    """
    try:
        results = vector_service.search(
            query=request.query,
            limit=request.limit,
            score_threshold=request.score_threshold
        )
        
        # 转换为响应格式
        search_results = [
            VectorSearchResult(
                content=result["content"],
                metadata=result["metadata"],
                score=result["score"]
            )
            for result in results
        ]
        
        logger.info(f"搜索查询 '{request.query}' 返回 {len(search_results)} 个结果")
        return search_results
        
    except Exception as e:
        logger.error(f"文档搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/index")
async def index_documents(request: DocumentIndexRequest):
    """
    将文档索引到向量存储中
    
    Args:
        request: 索引请求参数
        
    Returns:
        操作结果
    """
    try:
        documents = []
        ids = []
        
        for doc_data in request.documents:
            # 创建Document对象
            doc = Document(
                page_content=doc_data.get("content", ""),
                metadata=doc_data.get("metadata", {})
            )
            documents.append(doc)
            
            # 使用ID或生成UUID
            doc_id = doc_data.get("id") or doc_data.get("metadata", {}).get("id")
            if doc_id:
                ids.append(str(doc_id))
        
        # 如果没有提供ID，使用None让向量服务自动生成
        vector_service.add_documents(documents, ids if ids else None)
        
        return {
            "message": f"已成功索引 {len(documents)} 个文档",
            "count": len(documents),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"文档索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"索引失败: {str(e)}")


@router.delete("/documents/{doc_id}")
async def remove_document_from_index(doc_id: str):
    """
    从向量存储中移除指定文档
    
    Args:
        doc_id: 文档 ID
        
    Returns:
        操作结果
    """
    try:
        vector_service.delete_by_id(doc_id)
        
        return {
            "message": f"文档 ID {doc_id} 已从向量存储中移除",
            "doc_id": doc_id,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"移除文档失败: {e}")
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
        集合详细信息
    """
    try:
        # 创建指定集合的服务实例
        collection_service = GenericVectorService(collection_name)
        info = collection_service.get_collection_info()
        
        return {
            "collection_name": collection_name,
            **info
        }
        
    except Exception as e:
        logger.error(f"获取集合信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取集合信息失败: {str(e)}")


@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """
    删除指定的向量集合
    
    Args:
        collection_name: 要删除的集合名称
        
    Returns:
        操作结果
    """
    try:
        vector_service._qdrant_client.delete_collection(collection_name)
        
        return {
            "message": f"集合 '{collection_name}' 已删除",
            "collection_name": collection_name,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"删除集合失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除集合失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    向量服务健康检查
    
    Returns:
        服务状态
    """
    try:
        collections = vector_service.get_list_of_collections()
        collection_info = vector_service.get_collection_info()
        
        return {
            "status": "healthy",
            "service": "Vector Search Service",
            "collections_count": len(collections),
            "default_collection": vector_service.collection_name,
            "default_collection_info": collection_info
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
