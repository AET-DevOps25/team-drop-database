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

router = APIRouter(prefix="/vector", tags=["Vector Search"])

# Global vector service instance
vector_service = GenericVectorService()


@router.post("/search", response_model=List[VectorSearchResult])
async def search_documents(request: VectorSearchRequest) -> List[VectorSearchResult]:
    """
    Search documents based on semantic similarity
    
    Args:
        request: Search request parameters
        
    Returns:
        List of matching documents
    """
    try:
        results = vector_service.search(
            query=request.query,
            limit=request.limit,
            score_threshold=request.score_threshold
        )
        
        # Convert to response format
        search_results = [
            VectorSearchResult(
                content=result["content"],
                metadata=result["metadata"],
                score=result["score"]
            )
            for result in results
        ]
        
        logger.info(f"Search query '{request.query}' returned {len(search_results)} results")
        return search_results
        
    except Exception as e:
        logger.error(f"Document search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/index")
async def index_documents(request: DocumentIndexRequest):
    """
    Index documents into vector storage
    
    Args:
        request: Index request parameters
        
    Returns:
        Operation result
    """
    try:
        documents = []
        ids = []
        
        for doc_data in request.documents:
            # Create Document object
            doc = Document(
                page_content=doc_data.get("content", ""),
                metadata=doc_data.get("metadata", {})
            )
            documents.append(doc)
            
            # Use ID or generate UUID
            doc_id = doc_data.get("id") or doc_data.get("metadata", {}).get("id")
            if doc_id:
                ids.append(str(doc_id))
        
        # If no ID provided, use None to let vector service generate automatically
        vector_service.add_documents(documents, ids if ids else None)
        
        return {
            "message": f"Successfully indexed {len(documents)} documents",
            "count": len(documents),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Document indexing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.delete("/documents/{doc_id}")
async def remove_document_from_index(doc_id: str):
    """
    Remove specified document from vector storage
    
    Args:
        doc_id: Document ID
        
    Returns:
        Operation result
    """
    try:
        vector_service.delete_by_id(doc_id)
        
        return {
            "message": f"Document ID {doc_id} has been removed from vector storage",
            "doc_id": doc_id,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Document removal failed: {e}")
        raise HTTPException(status_code=500, detail=f"Removal failed: {str(e)}")


@router.get("/collections")
async def get_collections():
    """
    Get list of all vector collections
    
    Returns:
        List of collections
    """
    try:
        collections = vector_service.get_list_of_collections()
        return {
            "collections": collections,
            "count": len(collections)
        }
        
    except Exception as e:
        logger.error(f"Failed to get collection list: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get collection list: {str(e)}")


@router.get("/collections/{collection_name}/info")
async def get_collection_info(collection_name: str):
    """
    Get detailed information of specified collection
    
    Args:
        collection_name: Collection name
        
    Returns:
        Detailed collection information
    """
    try:
        # Create service instance for specified collection
        collection_service = GenericVectorService(collection_name)
        info = collection_service.get_collection_info()
        
        return {
            "collection_name": collection_name,
            **info
        }
        
    except Exception as e:
        logger.error(f"Failed to get collection info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get collection info: {str(e)}")


@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """
    Delete specified vector collection
    
    Args:
        collection_name: Name of collection to delete
        
    Returns:
        Operation result
    """
    try:
        vector_service._qdrant_client.delete_collection(collection_name)
        
        return {
            "message": f"Collection '{collection_name}' has been deleted",
            "collection_name": collection_name,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Collection deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Collection deletion failed: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Vector service health check
    
    Returns:
        Service status
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
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
