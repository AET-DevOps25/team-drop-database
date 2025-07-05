from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document

from travel_buddy_ai.core.config import settings
from travel_buddy_ai.pipelines.parser.schema import ParsedQuery

# ---------- 1. 初始化向量库 ----------
_embeddings = None
_qdrant_client = None
VECTOR_STORE = None

def get_vector_store():
    """延迟初始化向量存储，避免在模块导入时连接"""
    global _embeddings, _qdrant_client, VECTOR_STORE
    
    if VECTOR_STORE is None:
        _embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
        _qdrant_client = QdrantClient(
            url=settings.qdrant_url,  # e.g. "http://localhost:6333"
            prefer_grpc=False,
            check_compatibility=False,
        )
        VECTOR_STORE = QdrantVectorStore(
            client=_qdrant_client,
            collection_name="attractions",
            embedding=_embeddings,
        )
    
    return VECTOR_STORE

# ---------- 2. 构造过滤器 ----------
def _build_filter(parsed: ParsedQuery) -> Optional[qm.Filter]:
    """
    将 ParsedQuery 中的 must_visit / preferences
    转成 Qdrant Filter 语法
    """
    conditions = []

    if parsed.must_visit:
        # name in [...]
        conditions.append(
            qm.FieldCondition(
                key="name",
                match=qm.MatchAny(any=parsed.must_visit),
            )
        )

    if parsed.preferences:
        # tags contains any [...]
        conditions.append(
            qm.FieldCondition(
                key="tags",
                match=qm.MatchAny(any=parsed.preferences),
            )
        )

    if not conditions:
        return None

    return qm.Filter(must=conditions)  # 相当于 AND 关系


# ---------- 3. 对外检索函数 ----------
def semantic_search(
    question: str,
    parsed: ParsedQuery,
    top_k: int = 8,
) -> List[Document]:
    """
    常规语义检索 + 元数据过滤
    返回 langchain.schema.Document 列表
    """
    q_filter = _build_filter(parsed)
    vector_store = get_vector_store()

    return vector_store.similarity_search(
        query=question,
        k=top_k,
        filter=q_filter,           # None 则表示不加过滤
    )
