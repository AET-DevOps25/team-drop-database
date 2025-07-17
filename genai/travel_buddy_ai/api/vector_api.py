from fastapi import APIRouter, HTTPException, Request
from typing import List
from langchain_core.documents import Document

from travel_buddy_ai.models.common import (
    VectorSearchRequest, 
    VectorSearchResult, 
    DocumentIndexRequest
)
from travel_buddy_ai.services.generic_vector_service import GenericVectorService
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/vector", tags=["Vector Search"])


@router.post("/search", response_model=List[VectorSearchResult])
async def search_documents(request: Request, body: VectorSearchRequest) -> List[VectorSearchResult]:
    vector_service: GenericVectorService = request.app.state.vector_service
    if not vector_service:
        raise HTTPException(status_code=500, detail="Vector service not initialized")

    try:
        results = vector_service.search(
            query=body.query,
            limit=body.limit,
            score_threshold=body.score_threshold
        )

        search_results = [
            VectorSearchResult(
                content=result["content"],
                metadata=result["metadata"],
                score=result["score"]
            )
            for result in results
        ]

        logger.info(f"Search query '{body.query}' returned {len(search_results)} results")
        return search_results

    except Exception as e:
        logger.error(f"Document search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/index")
async def index_documents(request: Request, body: DocumentIndexRequest):
    vector_service: GenericVectorService = request.app.state.vector_service
    if not vector_service:
        raise HTTPException(status_code=500, detail="Vector service not initialized")

    try:
        documents = []
        ids = []

        for doc_data in body.documents:
            doc = Document(
                page_content=doc_data.get("content", ""),
                metadata=doc_data.get("metadata", {})
            )
            documents.append(doc)
            doc_id = doc_data.get("id") or doc_data.get("metadata", {}).get("id")
            if doc_id:
                ids.append(str(doc_id))

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
async def remove_document_from_index(request: Request, doc_id: str):
    vector_service: GenericVectorService = request.app.state.vector_service
    if not vector_service:
        raise HTTPException(status_code=500, detail="Vector service not initialized")

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
async def get_collections(request: Request):
    vector_service: GenericVectorService = request.app.state.vector_service
    if not vector_service:
        raise HTTPException(status_code=500, detail="Vector service not initialized")

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
async def get_collection_info(request: Request, collection_name: str):
    try:
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
async def delete_collection(request: Request, collection_name: str):
    vector_service: GenericVectorService = request.app.state.vector_service
    if not vector_service:
        raise HTTPException(status_code=500, detail="Vector service not initialized")

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
async def health_check(request: Request):
    vector_service: GenericVectorService = request.app.state.vector_service
    if not vector_service:
        return {
            "status": "unhealthy",
            "error": "Vector service not initialized"
        }

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
