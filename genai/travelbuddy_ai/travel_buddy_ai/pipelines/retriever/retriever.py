from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from langchain.schema import Document

from travel_buddy_ai.config import settings
from travel_buddy_ai.pipelines.parser.schema import ParsedQuery

# ---------- 1. 初始化向量库 ----------
_embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)

_qdrant_client = QdrantClient(
    url=settings.qdrant_url,  # e.g. "http://localhost:6333"
    prefer_grpc=False,
)

VECTOR_STORE = Qdrant(
    client=_qdrant_client,
    collection_name="attractions",
    embeddings=_embeddings,
)

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

    return VECTOR_STORE.similarity_search(
        query=question,
        k=top_k,
        filter=q_filter,           # None 则表示不加过滤
    )
