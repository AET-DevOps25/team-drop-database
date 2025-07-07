from pydantic import BaseModel
from typing import List, Optional


class VectorSearchRequest(BaseModel):
    """向量搜索请求模型"""
    query: str
    limit: int = 10
    score_threshold: float = 0.7
    filters: Optional[dict] = None  # 通用过滤器


class VectorSearchResult(BaseModel):
    """向量搜索结果模型"""
    content: str
    metadata: dict
    score: float


class DocumentIndexRequest(BaseModel):
    """文档索引请求模型"""
    documents: List[dict]  # 通用文档格式
    force_reindex: bool = False


class DocumentModel(BaseModel):
    """通用文档模型"""
    id: str
    content: str
    metadata: Optional[dict] = None
