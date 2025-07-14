from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration class"""
    host: str = "0.0.0.0"
    port: int = 8000
    
    # OpenAI API configuration
    openai_api_key: Optional[str] = None
    
    # LLM model configuration
    llm_model_type: str = "openai"  # openai, gpt4all, llamacpp, ollama
    llm_model_name: str = "gpt-3.5-turbo"  # specific model name
    llm_model_path: Optional[str] = None  # local model path (for llamacpp etc.)
    
    # Qdrant vector database configuration
    qdrant_host: str = "localhost"
    qdrant_port: int = 6334
    qdrant_api_key: Optional[str] = None
    qdrant_url: Optional[str] = None
    
    # Vector storage collection name
    attraction_vectors_collection: str = "attraction_vectors"
    
    # Database configuration (connect to tourism attraction database)
    attraction_db_host: str = "localhost"
    attraction_db_port: int = 5443
    attraction_db_name: str = "team-drop-database"
    attraction_db_user: str = "user"
    attraction_db_password: str = "password"
    
    # RAG configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_search_results: int = 10
    similarity_threshold: float = 0.7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
