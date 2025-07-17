"""
Simplified generic vector service
Removes attractions-specific logic, provides generic vector operations
"""

from typing import List, Optional, Dict, Any
import httpx
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.db import get_qdrant_connection
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)


class GenericVectorService:
    """Generic vector storage service class"""

    def __init__(self, collection_name: str = None):
        self._dense_embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large", 
            api_key=settings.openai_api_key
        )
        self._sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.collection_name = collection_name or settings.attraction_vectors_collection
        self._qdrant_client = None
        self.vector_store = None
    @retry(
        wait=wait_fixed(3),
        stop=stop_after_attempt(10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout)),
        reraise=True
    )
    def create_collection(self, collection_name: str) -> None:
        """Create Qdrant collection"""
        self._lazy_init()
        if not self._qdrant_client.collection_exists(collection_name):
            self._qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "dense": VectorParams(size=3072, distance=Distance.COSINE)
                },
                sparse_vectors_config={
                    "sparse": SparseVectorParams(
                        index=models.SparseIndexParams(on_disk=False)
                    )
                },
            )
            logger.info(f"Vector collection '{collection_name}' created")

    def add_documents(self, documents: List[Document], ids: List[str] = None) -> None:
        """Add documents to vector storage"""
        self._lazy_init()
        if ids:
            # Ensure IDs are in integer format (required by Qdrant)
            processed_ids = []
            for doc_id in ids:
                try:
                    # If it's a numeric string, convert to integer
                    processed_ids.append(int(doc_id))
                except ValueError:
                    # If not numeric, generate integer ID using hash
                    processed_ids.append(abs(hash(doc_id)) % (10**10))
            
            self.vector_store.add_documents(documents=documents, ids=processed_ids)
        else:
            self.vector_store.add_documents(documents=documents)
        
        logger.info(f"Added {len(documents)} documents to vector storage")

    def search(self, query: str, limit: int = 10, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Perform vector search"""
        self._lazy_init()
        docs_with_scores = self.vector_store.similarity_search_with_score(
            query, k=limit
        )
        
        results = []
        for doc, score in docs_with_scores:
            if score >= score_threshold:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                })
        
        return results

    def delete_by_id(self, doc_id: str) -> None:
        """Delete document by ID"""
        self._lazy_init()
        try:
            # Convert ID to integer format
            int_id = int(doc_id) if doc_id.isdigit() else abs(hash(doc_id)) % (10**10)
            self._qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=[int_id]
            )
            logger.info(f"Document ID {doc_id} deleted")
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information"""
        self._lazy_init()
        if not self._qdrant_client.collection_exists(self.collection_name):
            return {"exists": False}
        
        collection_info = self._qdrant_client.get_collection(self.collection_name)
        return {
            "exists": True,
            "vectors_count": collection_info.vectors_count,
            "points_count": collection_info.points_count,
            "indexed_vectors_count": collection_info.indexed_vectors_count
        }

    def get_list_of_collections(self) -> List[str]:
        """Get list of all collections"""
        self._lazy_init()
        collections = self._qdrant_client.get_collections()
        return [col.name for col in collections.collections]
    
    def _lazy_init(self):
        """Lazily initialize vector store and client if not already done"""
        if self._qdrant_client and self.vector_store:
            return

        self._qdrant_client = get_qdrant_connection()

        self.create_collection(self.collection_name)

        self.vector_store = QdrantVectorStore(
            client=self._qdrant_client,
            collection_name=self.collection_name,
            embedding=self._dense_embeddings,
            sparse_embedding=self._sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse",
        )

        logger.info("✅ Vector store initialized successfully")

