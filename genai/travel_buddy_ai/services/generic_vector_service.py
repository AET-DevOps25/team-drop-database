"""
简化的通用向量服务
移除attractions特定逻辑，提供通用向量操作
"""

from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams

from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.db import get_qdrant_connection
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)


class GenericVectorService:
    """通用向量存储服务类"""

    def __init__(self, collection_name: str = None):
        self._dense_embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large", 
            api_key=settings.openai_api_key
        )
        self._sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.collection_name = collection_name or settings.attraction_vectors_collection
        self._qdrant_client = get_qdrant_connection()
        self.create_collection(self.collection_name)
        
        self.vector_store: QdrantVectorStore = QdrantVectorStore(
            client=self._qdrant_client,
            collection_name=self.collection_name,
            embedding=self._dense_embeddings,
            sparse_embedding=self._sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse",
        )

    def create_collection(self, collection_name: str) -> None:
        """创建 Qdrant 集合"""
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
            logger.info(f"向量集合 '{collection_name}' 已创建")

    def add_documents(self, documents: List[Document], ids: List[str] = None) -> None:
        """添加文档到向量存储"""
        if ids:
            # 确保ID是整数格式（Qdrant要求）
            processed_ids = []
            for doc_id in ids:
                try:
                    # 如果是数字字符串，转换为整数
                    processed_ids.append(int(doc_id))
                except ValueError:
                    # 如果不是数字，使用hash生成整数ID
                    processed_ids.append(abs(hash(doc_id)) % (10**10))
            
            self.vector_store.add_documents(documents=documents, ids=processed_ids)
        else:
            self.vector_store.add_documents(documents=documents)
        
        logger.info(f"已添加 {len(documents)} 个文档到向量存储中")

    def search(self, query: str, limit: int = 10, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """执行向量搜索"""
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
        """根据ID删除文档"""
        try:
            # 转换ID为整数格式
            int_id = int(doc_id) if doc_id.isdigit() else abs(hash(doc_id)) % (10**10)
            self._qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=[int_id]
            )
            logger.info(f"文档 ID {doc_id} 已删除")
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
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
        """获取所有集合列表"""
        collections = self._qdrant_client.get_collections()
        return [col.name for col in collections.collections]
