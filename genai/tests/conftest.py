"""
Test configuration and shared fixtures
"""
import os
import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, List, Any


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    mock_settings = Mock()
    mock_settings.openai_api_key = "test-api-key"
    mock_settings.qdrant_url = "http://localhost:6333"
    mock_settings.llm_model_type = "openai"
    mock_settings.local_ollama_url = "http://localhost:11434"
    return mock_settings


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for testing"""
    mock_client = Mock()
    
    # Mock search results
    mock_result = Mock()
    mock_result.payload = {
        "page_content": "Test attraction content",
        "metadata": {"name": "Test Attraction", "location": "Munich"}
    }
    mock_result.score = 0.85
    
    mock_client.search.return_value = [mock_result]
    return mock_client


@pytest.fixture
def mock_openai_embeddings():
    """Mock OpenAI embeddings for testing"""
    mock_embeddings = Mock()
    mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dim vector
    return mock_embeddings


@pytest.fixture
def sample_search_results():
    """Sample search results for testing"""
    return [
        {
            "content": "Munich is the capital of Bavaria and offers many attractions including Marienplatz.",
            "metadata": {"name": "Marienplatz", "location": "Munich", "type": "square"},
            "score": 0.9
        },
        {
            "content": "The English Garden is one of the largest urban parks in the world.",
            "metadata": {"name": "English Garden", "location": "Munich", "type": "park"},
            "score": 0.8
        }
    ]


@pytest.fixture
def sample_questions():
    """Sample questions for testing"""
    return [
        "What are the best attractions in Munich?",
        "Tell me about museums in Munich",
        "Plan a 3-day itinerary for Munich",
        "Are there any free attractions?",
        "What outdoor activities can I do?"
    ]


class MockLLMModel:
    """Mock LLM model for testing"""
    
    def __init__(self, model_name: str = "test-model"):
        self.model_name = model_name
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        return f"This is a test response for prompt: {prompt[:50]}..."
    
    def is_available(self) -> bool:
        return True


@pytest.fixture
def mock_llm_model():
    """Mock LLM model for testing"""
    return MockLLMModel()


@pytest.fixture
def mock_model_manager():
    """Mock model manager for testing"""
    mock_manager = Mock()
    mock_manager.get_current_model.return_value = MockLLMModel()
    mock_manager.set_model.return_value = True
    mock_manager.list_available_models.return_value = ["openai", "local_ollama"]
    mock_manager.generate.return_value = "Test generated response"
    return mock_manager


# Test data
TEST_ATTRACTIONS_DATA = [
    {
        "name": "Marienplatz",
        "description": "The central square in Munich with the famous Glockenspiel",
        "location": "Munich City Center",
        "type": "square",
        "rating": 4.5,
        "price": "free"
    },
    {
        "name": "English Garden",
        "description": "Large urban park with beer gardens and surfing",
        "location": "Munich",
        "type": "park",
        "rating": 4.6,
        "price": "free"
    },
    {
        "name": "Neuschwanstein Castle",
        "description": "Fairy-tale castle that inspired Disney",
        "location": "Near Munich",
        "type": "castle",
        "rating": 4.7,
        "price": "€15"
    }
]
