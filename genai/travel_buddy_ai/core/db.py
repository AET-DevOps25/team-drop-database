from qdrant_client import QdrantClient
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional

from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """数据库连接管理类"""
    
    def __init__(self):
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._qdrant_client: Optional[QdrantClient] = None
    
    @property
    def engine(self) -> Engine:
        """获取 SQLAlchemy 引擎"""
        if self._engine is None:
            database_url = (
                f"postgresql://{settings.attraction_db_user}:"
                f"{settings.attraction_db_password}@"
                f"{settings.attraction_db_host}:"
                f"{settings.attraction_db_port}/"
                f"{settings.attraction_db_name}"
            )
            self._engine = create_engine(database_url)
            logger.info("数据库引擎已创建")
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """获取会话工厂"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.engine)
        return self._session_factory
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.session_factory()


# 全局数据库连接实例
db_connection = DatabaseConnection()


def get_database_session() -> Session:
    """
    获取数据库会话（用于依赖注入）
    
    Returns:
        数据库会话对象
    """
    return db_connection.get_session()


def get_qdrant_connection() -> QdrantClient:
    """
    获取 Qdrant 客户端连接
    
    Returns:
        Qdrant 客户端实例
    """
    if db_connection._qdrant_client is None:
        if settings.qdrant_url:
            # 使用完整的 URL 连接
            db_connection._qdrant_client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key
            )
        else:
            # 使用主机和端口连接
            db_connection._qdrant_client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key
            )
        logger.info("Qdrant 客户端连接已创建")
    
    return db_connection._qdrant_client
