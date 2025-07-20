"""
Unit tests for LLM Models
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from travel_buddy_ai.models.llm_models import BaseLLMModel, ModelType


class MockLLMModel(BaseLLMModel):
    """Mock implementation of BaseLLMModel for testing"""
    
    def __init__(self, model_name: str = "mock-model", available: bool = True):
        super().__init__(model_name)
        self._available = available
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        return f"Mock response for: {prompt[:30]}..."
    
    def is_available(self) -> bool:
        return self._available


class TestBaseLLMModel:
    """Test cases for BaseLLMModel"""
    
    def test_init(self):
        """Test model initialization"""
        model = MockLLMModel("test-model")
        assert model.model_name == "test-model"
    
    def test_generate(self):
        """Test text generation"""
        model = MockLLMModel()
        result = model.generate("Test prompt", max_tokens=500, temperature=0.5)
        assert "Mock response for: Test prompt" in result
    
    def test_is_available_true(self):
        """Test model availability check - available"""
        model = MockLLMModel(available=True)
        assert model.is_available() is True
    
    def test_is_available_false(self):
        """Test model availability check - not available"""
        model = MockLLMModel(available=False)
        assert model.is_available() is False


class TestModelType:
    """Test cases for ModelType enum"""
    
    def test_model_types(self):
        """Test model type enumeration"""
        assert ModelType.OPENAI.value == "openai"
        assert ModelType.LOCAL_OLLAMA.value == "local_ollama"


# Integration tests with actual model classes would go here
# For now, we'll test the mock implementations to ensure the interface works

@pytest.fixture
def mock_openai_model():
    """Fixture for mocked OpenAI model"""
    with patch('travel_buddy_ai.models.llm_models.settings') as mock_settings:
        mock_settings.openai_api_key = "test-key"
        # We would import and create actual OpenAI model here if needed
        return MockLLMModel("openai-mock", available=True)


@pytest.fixture
def mock_ollama_model():
    """Fixture for mocked Ollama model"""
    with patch('travel_buddy_ai.models.llm_models.settings') as mock_settings:
        mock_settings.local_ollama_url = "http://localhost:11434"
        # We would import and create actual Ollama model here if needed
        return MockLLMModel("ollama-mock", available=True)


class TestModelIntegration:
    """Integration tests for model functionality"""
    
    def test_openai_model_interface(self, mock_openai_model):
        """Test OpenAI model interface"""
        result = mock_openai_model.generate("Tell me about Munich")
        assert isinstance(result, str)
        assert len(result) > 0
        assert mock_openai_model.is_available()
    
    def test_ollama_model_interface(self, mock_ollama_model):
        """Test Ollama model interface"""
        result = mock_ollama_model.generate("What attractions are in Munich?")
        assert isinstance(result, str)
        assert len(result) > 0
        assert mock_ollama_model.is_available()
    
    def test_model_parameter_passing(self):
        """Test that model parameters are properly passed"""
        model = MockLLMModel()
        
        # Test with different parameters
        result1 = model.generate("Test", max_tokens=100, temperature=0.1)
        result2 = model.generate("Test", max_tokens=500, temperature=0.9)
        
        # Both should return strings (content may be same due to mock)
        assert isinstance(result1, str)
        assert isinstance(result2, str)
