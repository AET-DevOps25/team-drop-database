from pydantic import BaseModel
from typing import List, Optional


class VectorSearchRequest(BaseModel):
    """Vector search request model"""
    query: str
    limit: int = 10
    score_threshold: float = 0.7
    filters: Optional[dict] = None


class VectorSearchResult(BaseModel):
    """Vector search result model"""
    content: str
    metadata: dict
    score: float


class DocumentIndexRequest(BaseModel):
    """Document indexing request model"""
    documents: List[dict]
    force_reindex: bool = False


class DocumentModel(BaseModel):
    """Document model for indexing"""
    id: str
    content: str
    metadata: Optional[dict] = None
