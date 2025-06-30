import uuid
from typing import List, Optional, Dict, Any

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import models
from qdrant_client.http.models import (
    Distance,
    SparseVectorParams,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue
)

from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.db import get_qdrant_connection
from travel_buddy_ai.core.logger import get_logger
from travel_buddy_ai.models.attractions import AttractionModel, VectorSearchResult
from travel_buddy_ai.repositories.attraction_repository import AttractionRepository

logger = get_logger(__name__)


class AttractionVectorService:
    """旅游景点向量存储服务类"""

    def __init__(self):
        self._dense_embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large", 
            api_key=settings.openai_api_key
        )
        self._sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.collection_name = settings.attraction_vectors_collection
        self._qdrant_client = get_qdrant_connection()
        self.create_collection(self.collection_name)
        self.vector_store: QdrantVectorStore = QdrantVectorStore(
            client=self._qdrant_client,
            collection_name=self.collection_name,
            embedding=self._dense_embeddings,
            sparse_embedding=self._sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            # 使用密集和稀疏向量进行混合检索，提高召回率和精确度
            vector_name="dense",
            # Qdrant 中存储密集向量的字段名
            sparse_vector_name="sparse",
            # Qdrant 中存储稀疏向量的字段名
        )

    def create_collection(self, collection_name: str) -> None:
        """
        创建 Qdrant 集合用于存储向量
        """
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

    def delete_collection(self, collection_name: str) -> None:
        """
        删除 Qdrant 集合
        """
        if self._qdrant_client.collection_exists(collection_name):
            self._qdrant_client.delete_collection(
                collection_name=collection_name
            )
            logger.info(f"向量集合 '{collection_name}' 已删除")

    def get_list_of_collections(self) -> List[str]:
        """
        获取所有 Qdrant 集合列表
        """
        collections = self._qdrant_client.get_collections()
        return [col.name for col in collections.collections]

    def add_attractions(self, attractions: List[AttractionModel]) -> None:
        """
        将景点列表添加到向量存储中
        
        Args:
            attractions: 要索引的景点列表
        """
        documents = []
        uuids = []

        for attraction in attractions:
            # 创建文档，使用景点的向量化内容
            documents.append(
                Document(
                    page_content=attraction.content_for_vector,
                    metadata={
                        "id": str(attraction.id),
                        "name": attraction.name,
                        "city_name": attraction.city.name,
                        "city_country": attraction.city.country,
                        "country": attraction.location.country,
                        "latitude": attraction.location.latitude,
                        "longitude": attraction.location.longitude,
                    },
                )
            )
            uuids.append(str(attraction.id))

        self.vector_store.add_documents(documents=documents, ids=uuids)
        logger.info(f"已添加 {len(attractions)} 个景点到向量存储中")

    async def retrieve_by_similarity(
        self, 
        query: str, 
        score_threshold: float = 0.7,
        limit: int = 10,
        city_filter: Optional[str] = None,
        country_filter: Optional[str] = None
    ) -> List[VectorSearchResult]:
        """
        基于相似度检索相关景点
        
        Args:
            query: 查询字符串
            score_threshold: 最小分数阈值
            limit: 返回结果数量限制
            city_filter: 城市过滤器
            country_filter: 国家过滤器

        Returns:
            匹配的景点列表
        """
        try:
            # 构建过滤器
            filter_conditions = []
            
            if city_filter:
                filter_conditions.append(
                    FieldCondition(
                        key="metadata.city_name",
                        match=MatchValue(value=city_filter)
                    )
                )
            
            if country_filter:
                filter_conditions.append(
                    FieldCondition(
                        key="metadata.country",
                        match=MatchValue(value=country_filter)
                    )
                )
            
            # 执行向量搜索
            search_kwargs = {
                "k": limit,
                "score_threshold": score_threshold
            }
            
            if filter_conditions:
                search_kwargs["filter"] = Filter(must=filter_conditions)
            
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query=query, **search_kwargs
            )
            
            # 转换为结果模型
            results = []
            attraction_ids = []
            
            for doc, score in docs_with_scores:
                attraction_id = int(doc.metadata.get("id"))
                attraction_ids.append(attraction_id)
            
            # 从数据库获取完整的景点信息
            if attraction_ids:
                repository = AttractionRepository()
                attractions = await repository.get_attractions_by_ids(attraction_ids)
                
                # 创建 ID 到景点的映射
                attraction_map = {attr.id: attr for attr in attractions}
                
                # 按照搜索结果的顺序构建结果
                for doc, score in docs_with_scores:
                    attraction_id = int(doc.metadata.get("id"))
                    if attraction_id in attraction_map:
                        results.append(VectorSearchResult(
                            attraction=attraction_map[attraction_id],
                            score=score
                        ))
            
            logger.info(f"相似度搜索返回 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"相似度搜索失败: {e}")
            return []

    async def index_attractions_to_vector_store(
        self, 
        page_size: int = 100,
        city_filter: Optional[str] = None
    ) -> None:
        """
        批量将景点数据从数据库索引到向量存储中
        
        Args:
            page_size: 每页处理的景点数量
            city_filter: 城市过滤器，只索引指定城市的景点
        """
        page: int = 0
        offset: int = page * page_size
        total_indexed = 0

        repository = AttractionRepository()
        attractions: List[AttractionModel] = (
            await repository.list_attractions_with_summary(
                limit=page_size, offset=offset, city_name=city_filter
            )
        )

        while len(attractions) > 0:
            # 添加景点到向量存储
            self.add_attractions(attractions)
            total_indexed += len(attractions)

            page += 1
            offset = page * page_size

            # 获取下一页
            attractions = await repository.list_attractions_with_summary(
                limit=page_size, offset=offset, city_name=city_filter
            )

        logger.info(f"总共索引了 {total_indexed} 个景点到向量存储中")

    async def add_attraction(self, attraction_id: int) -> None:
        """
        根据 ID 将单个景点添加到向量存储中
        
        Args:
            attraction_id: 要添加的景点 ID
        """
        repository = AttractionRepository()
        attraction: Optional[AttractionModel] = await repository.get_attraction_by_id(
            attraction_id
        )

        if not attraction or not attraction.description or not attraction.description.strip():
            logger.error(
                f"景点 ID {attraction_id} 未找到或没有描述信息"
            )
            return

        # 创建文档
        document = Document(
            page_content=attraction.content_for_vector,
            metadata={
                "id": str(attraction.id),
                "name": attraction.name,
                "city_name": attraction.city.name,
                "city_country": attraction.city.country,
                "country": attraction.location.country,
                "latitude": attraction.location.latitude,
                "longitude": attraction.location.longitude,
            },
        )

        # 添加到向量存储
        self.vector_store.add_documents(
            documents=[document], ids=[str(attraction.id)]
        )
        
        logger.info(f"景点 '{attraction.name}' (ID: {attraction_id}) 已添加到向量存储中")

    async def remove_attraction(self, attraction_id: int) -> None:
        """
        从向量存储中移除指定景点
        
        Args:
            attraction_id: 要移除的景点 ID
        """
        try:
            self._qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=[str(attraction_id)]
            )
            logger.info(f"景点 ID {attraction_id} 已从向量存储中移除")
        except Exception as e:
            logger.error(f"移除景点 ID {attraction_id} 失败: {e}")

    async def get_collection_info(self) -> Dict[str, Any]:
        """
        获取向量集合信息
        
        Returns:
            集合信息字典
        """
        try:
            collection_info = self._qdrant_client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.params.collection_name,
                "vectors_count": collection_info.vectors_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            return {}
