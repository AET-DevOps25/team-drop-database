from qdrant_client import QdrantClient
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """Database connection management class"""
    
    def __init__(self):
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._qdrant_client: Optional[QdrantClient] = None
    
    @property
    def engine(self) -> Engine:
        """Get SQLAlchemy engine"""
        if self._engine is None:
            database_url = (
                f"postgresql://{settings.attraction_db_user}:"
                f"{settings.attraction_db_password}@"
                f"{settings.attraction_db_host}:"
                f"{settings.attraction_db_port}/"
                f"{settings.attraction_db_name}"
            )
            self._engine = create_engine(database_url)
            logger.info("Database engine created")
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Get session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.engine)
        return self._session_factory
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.session_factory()


# Global database connection instance
db_connection = DatabaseConnection()


def get_database_session() -> Session:
    """
    Get database session (for dependency injection)
    
    Returns:
        Database session object
    """
    return db_connection.get_session()

@retry(
    stop=stop_after_attempt(5),         # Maximum 5 retries
    wait=wait_fixed(2),                 # Wait 2 seconds between retries
    retry=retry_if_exception_type(Exception)  # Catch all connection type errors
)
def get_qdrant_connection() -> QdrantClient:
    """
    Get Qdrant client connection
    
    Returns:
        Qdrant client instance
    """
    if db_connection._qdrant_client is None:
        # For local development environment, force HTTP connection
        if settings.qdrant_host == "localhost" or settings.qdrant_host == "127.0.0.1":
            # Local development environment: use HTTP, no API key
            db_connection._qdrant_client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                https=False,
                api_key=None
            )
            logger.info("Qdrant local client connection created (HTTP mode)")
        elif settings.qdrant_url:
            # Use full URL connection (production environment)
            db_connection._qdrant_client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key
            )
            logger.info("Qdrant remote client connection created (URL mode)")
        else:
            # Use host and port connection (remote environment)
            db_connection._qdrant_client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key
            )
            logger.info("Qdrant remote client connection created (host-port mode)")
    db_connection._qdrant_client.get_collections()
    
    return db_connection._qdrant_client
