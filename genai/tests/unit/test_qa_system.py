"""
Unit tests for AttractionQASystem
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from travel_buddy_ai.services.qa_system_fixed import AttractionQASystem


class TestAttractionQASystem:
    """Test cases for AttractionQASystem"""
    
    @patch('travel_buddy_ai.services.qa_system_fixed.model_manager')
    @patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings')
    @patch('travel_buddy_ai.services.qa_system_fixed.settings')
    def test_init_success(self, mock_settings, mock_embeddings_class, mock_model_manager):
        """Test successful initialization"""
        # Arrange
        mock_settings.openai_api_key = "test-key"
        mock_embeddings = Mock()
        mock_embeddings_class.return_value = mock_embeddings
        mock_model_manager.set_model.return_value = True
        mock_model_manager.get_current_model.return_value = Mock(model_name="test-model")
        mock_model_manager.list_available_models.return_value = ["openai", "local"]
        
        # Act
        qa_system = AttractionQASystem(model_type="openai")
        
        # Assert
        assert qa_system.collection_name == "attractions_collection"
        assert qa_system.original_model_type == "openai"
        mock_model_manager.set_model.assert_called_once_with("openai")
    
    @patch('travel_buddy_ai.services.qa_system_fixed.model_manager')
    @patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings')
    @patch('travel_buddy_ai.services.qa_system_fixed.settings')
    def test_init_model_fallback(self, mock_settings, mock_embeddings_class, mock_model_manager):
        """Test initialization with model fallback"""
        # Arrange
        mock_settings.openai_api_key = "test-key"
        mock_embeddings = Mock()
        mock_embeddings_class.return_value = mock_embeddings
        mock_model_manager.set_model.return_value = False  # First model fails
        mock_model_manager.get_current_model.return_value = Mock(model_name="fallback-model")
        mock_model_manager.list_available_models.return_value = ["openai", "local"]
        
        # Act
        qa_system = AttractionQASystem(model_type="unavailable-model")
        
        # Assert
        assert qa_system.original_model_type == "unavailable-model"
        mock_model_manager.set_model.assert_called_once_with("unavailable-model")
    
    @patch('travel_buddy_ai.services.qa_system_fixed.model_manager')
    @patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings')
    @patch('travel_buddy_ai.services.qa_system_fixed.settings')
    def test_init_no_available_model(self, mock_settings, mock_embeddings_class, mock_model_manager):
        """Test initialization fails when no model is available"""
        # Arrange
        mock_settings.openai_api_key = "test-key"
        mock_embeddings = Mock()
        mock_embeddings_class.return_value = mock_embeddings
        mock_model_manager.set_model.return_value = False
        mock_model_manager.get_current_model.return_value = None
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="No available LLM model"):
            AttractionQASystem()
    
    def test_preprocess_query_itinerary(self):
        """Test query preprocessing for itinerary planning"""
        with patch('travel_buddy_ai.services.qa_system_fixed.model_manager'), \
             patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings'), \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'):
            
            qa_system = AttractionQASystem()
            
            # Test itinerary keywords
            queries = [
                "Plan a 5-day itinerary for Munich",
                "Create a trip schedule",
                "What to do for 3 days?"
            ]
            
            for query in queries:
                result = qa_system.preprocess_query(query)
                assert "Munich attractions recommended attractions tourist attractions" == result
    
    def test_preprocess_query_museum(self):
        """Test query preprocessing for museums"""
        with patch('travel_buddy_ai.services.qa_system_fixed.model_manager'), \
             patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings'), \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'):
            
            qa_system = AttractionQASystem()
            
            # Test queries that should be transformed
            museum_queries = [
                "Tell me about museums",
                "Art galleries in Munich",
                "Historical places to visit"
            ]
            
            for query in museum_queries:
                result = qa_system.preprocess_query(query)
                assert "Munich museum art culture history attractions" == result
    
    def test_preprocess_query_no_match(self):
        """Test query preprocessing when no keywords match"""
        with patch('travel_buddy_ai.services.qa_system_fixed.model_manager'), \
             patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings'), \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'):
            
            qa_system = AttractionQASystem()
            
            # Use a query that doesn't contain any keywords
            original_query = "How is the wifi signal?"
            result = qa_system.preprocess_query(original_query)
            assert result == original_query
    
    @patch('travel_buddy_ai.services.qa_system_fixed.get_qdrant_connection')
    def test_search_attractions_success(self, mock_get_qdrant, mock_openai_embeddings, sample_search_results):
        """Test successful attraction search"""
        with patch('travel_buddy_ai.services.qa_system_fixed.model_manager'), \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'):
            
            # Arrange
            mock_qdrant_client = Mock()
            mock_search_result = Mock()
            mock_search_result.payload = {
                "page_content": "Test content",
                "metadata": {"name": "Test Attraction"}
            }
            mock_search_result.score = 0.85
            mock_qdrant_client.search.return_value = [mock_search_result]
            mock_get_qdrant.return_value = mock_qdrant_client
            
            with patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings') as mock_embeddings_class:
                mock_embeddings_class.return_value = mock_openai_embeddings
                qa_system = AttractionQASystem()
                
                # Act
                results = qa_system.search_attractions("Munich attractions")
                
                # Assert
                assert len(results) == 1
                assert results[0]["content"] == "Test content"
                assert results[0]["metadata"]["name"] == "Test Attraction"
                assert results[0]["score"] == 0.85
    
    @patch('travel_buddy_ai.services.qa_system_fixed.get_qdrant_connection')
    def test_search_attractions_failure(self, mock_get_qdrant, mock_openai_embeddings):
        """Test attraction search failure"""
        with patch('travel_buddy_ai.services.qa_system_fixed.model_manager'), \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'):
            
            # Arrange
            mock_qdrant_client = Mock()
            mock_qdrant_client.search.side_effect = Exception("Connection failed")
            mock_get_qdrant.return_value = mock_qdrant_client
            
            with patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings') as mock_embeddings_class:
                mock_embeddings_class.return_value = mock_openai_embeddings
                qa_system = AttractionQASystem()
                
                # Act
                results = qa_system.search_attractions("Munich attractions")
                
                # Assert
                assert results == []
    
    def test_create_prompt_with_results(self, sample_search_results):
        """Test prompt creation with search results"""
        with patch('travel_buddy_ai.services.qa_system_fixed.model_manager'), \
             patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings'), \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'):
            
            qa_system = AttractionQASystem()
            
            question = "What are the best attractions?"
            prompt = qa_system._create_prompt(question, sample_search_results)
            
            assert question in prompt
            assert "Munich is the capital of Bavaria" in prompt
            assert "English Garden" in prompt
            assert "Guidelines:" in prompt
    
    def test_create_prompt_no_results(self):
        """Test prompt creation without search results"""
        with patch('travel_buddy_ai.services.qa_system_fixed.model_manager'), \
             patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings'), \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'):
            
            qa_system = AttractionQASystem()
            
            question = "What are the best attractions?"
            prompt = qa_system._create_prompt(question, [])
            
            assert question in prompt
            assert "don't have specific attraction information" in prompt
            assert "general response about Munich travel" in prompt
    
    @patch('travel_buddy_ai.services.qa_system_fixed.model_manager')
    def test_generate_with_timeout_success(self, mock_model_manager, mock_openai_embeddings):
        """Test successful answer generation"""
        with patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings') as mock_embeddings_class, \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'):
            
            # Arrange
            mock_embeddings_class.return_value = mock_openai_embeddings
            mock_model = Mock()
            mock_model.model_name = "gpt-3.5-turbo"
            mock_model_manager.get_current_model.return_value = mock_model
            mock_model_manager.generate.return_value = "Generated answer"
            
            qa_system = AttractionQASystem()
            
            # Act
            result = qa_system._generate_with_timeout("Test prompt")
            
            # Assert
            assert result == "Generated answer"
            mock_model_manager.generate.assert_called_once()
    
    @patch('travel_buddy_ai.services.qa_system_fixed.model_manager')
    def test_generate_with_timeout_failure(self, mock_model_manager, mock_openai_embeddings):
        """Test answer generation failure"""
        with patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings') as mock_embeddings_class, \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'):
            
            # Arrange
            mock_embeddings_class.return_value = mock_openai_embeddings
            mock_model = Mock()
            mock_model.model_name = "gpt-3.5-turbo"
            mock_model_manager.get_current_model.return_value = mock_model
            mock_model_manager.generate.side_effect = Exception("API Error")
            
            qa_system = AttractionQASystem()
            
            # Act
            result = qa_system._generate_with_timeout("Test prompt")
            
            # Assert
            assert "I encountered an error" in result
    
    @patch('travel_buddy_ai.services.qa_system_fixed.model_manager')
    def test_switch_model_success(self, mock_model_manager, mock_openai_embeddings):
        """Test successful model switching"""
        with patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings') as mock_embeddings_class, \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'):
            
            # Arrange
            mock_embeddings_class.return_value = mock_openai_embeddings
            mock_model_manager.set_model.return_value = True
            mock_model_manager.get_current_model.return_value = Mock(model_name="new-model")
            
            qa_system = AttractionQASystem()
            
            # Act
            result = qa_system.switch_model("new-model")
            
            # Assert
            assert result is True
            mock_model_manager.set_model.assert_called_with("new-model")
    
    def test_list_available_models(self, mock_model_manager, mock_openai_embeddings):
        """Test listing available models"""
        with patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings') as mock_embeddings_class, \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'), \
             patch('travel_buddy_ai.services.qa_system_fixed.model_manager', mock_model_manager):
            
            # Arrange
            mock_embeddings_class.return_value = mock_openai_embeddings
            mock_model_manager.list_available_models.return_value = ["openai", "local_ollama"]
            
            qa_system = AttractionQASystem()
            
            # Act
            models = qa_system.list_available_models()
            
            # Assert
            assert models == ["openai", "local_ollama"]
    
    def test_get_current_model_info(self, mock_model_manager, mock_openai_embeddings):
        """Test getting current model info"""
        with patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings') as mock_embeddings_class, \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'), \
             patch('travel_buddy_ai.services.qa_system_fixed.model_manager', mock_model_manager):
            
            # Arrange
            mock_embeddings_class.return_value = mock_openai_embeddings
            mock_model = Mock()
            mock_model.model_name = "test-model"
            mock_model_manager.get_current_model.return_value = mock_model
            
            qa_system = AttractionQASystem()
            
            # Act
            info = qa_system.get_current_model_info()
            
            # Assert
            assert info["model_name"] == "test-model"
            assert "model_type" in info
    
    @patch('travel_buddy_ai.services.qa_system_fixed.get_qdrant_connection')
    def test_ask_integration(self, mock_get_qdrant, mock_openai_embeddings, mock_model_manager):
        """Test complete ask workflow"""
        with patch('travel_buddy_ai.services.qa_system_fixed.OpenAIEmbeddings') as mock_embeddings_class, \
             patch('travel_buddy_ai.services.qa_system_fixed.settings'), \
             patch('travel_buddy_ai.services.qa_system_fixed.model_manager', mock_model_manager):
            
            # Arrange
            mock_embeddings_class.return_value = mock_openai_embeddings
            
            # Mock Qdrant search results
            mock_qdrant_client = Mock()
            mock_search_result = Mock()
            mock_search_result.payload = {
                "page_content": "Munich is beautiful",
                "metadata": {"name": "Munich"}
            }
            mock_search_result.score = 0.9
            mock_qdrant_client.search.return_value = [mock_search_result]
            mock_get_qdrant.return_value = mock_qdrant_client
            
            # Mock model generation
            mock_model = Mock()
            mock_model.model_name = "test-model"
            mock_model_manager.get_current_model.return_value = mock_model
            mock_model_manager.generate.return_value = "Munich has many attractions"
            
            qa_system = AttractionQASystem()
            
            # Act
            result = qa_system.ask("What can I do in Munich?")
            
            # Assert
            assert result["question"] == "What can I do in Munich?"
            assert result["results_count"] == 1
            assert "Munich has many attractions" in result["answer"]
            assert len(result["search_results"]) == 1
