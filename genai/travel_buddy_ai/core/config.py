from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    host: str = "0.0.0.0"
    port: int = 8000
    
    # OpenAI API 配置
    openai_api_key: Optional[str] = None
    
    # Qdrant 向量数据库配置
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    qdrant_url: Optional[str] = None
    
    # 向量存储集合名称
    attraction_vectors_collection: str = "attraction_vectors"
    
    # 数据库配置 (连接到旅游景点数据库)
    attraction_db_host: str = "localhost"
    attraction_db_port: int = 5432
    attraction_db_name: str = "attractions_db"
    attraction_db_user: str = "postgres"
    attraction_db_password: str = "password"
    
    # RAG 配置
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_search_results: int = 10
    similarity_threshold: float = 0.7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
