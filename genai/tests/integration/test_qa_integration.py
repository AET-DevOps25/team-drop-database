"""
Integration tests for the complete Q&A system
These tests require actual external services (Qdrant, OpenAI) to be available
"""
import pytest
import os
from typing import Dict, Any

from travel_buddy_ai.services.qa_system_fixed import AttractionQASystem


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def qa_system():
    """Create a real Q&A system for integration testing"""
    # Skip if required environment variables are not set
    required_env_vars = ["OPENAI_API_KEY", "QDRANT_URL"]
    for var in required_env_vars:
        if not os.getenv(var):
            pytest.skip(f"Integration test skipped: {var} environment variable not set")
    
    return AttractionQASystem(model_type="openai")


class TestQASystemIntegration:
    """Integration tests for the complete Q&A system"""
    
    def test_system_initialization(self, qa_system):
        """Test that the system initializes correctly with real services"""
        assert qa_system is not None
        assert qa_system.collection_name == "attractions_collection"
        
        # Test model info
        model_info = qa_system.get_current_model_info()
        assert model_info["model_name"] is not None
        assert model_info["model_type"] is not None
    
    def test_list_available_models(self, qa_system):
        """Test listing available models"""
        models = qa_system.list_available_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert "openai" in models
    
    def test_search_attractions_real(self, qa_system):
        """Test real attraction search"""
        results = qa_system.search_attractions("Munich attractions", limit=5)
        
        # We may or may not get results depending on data in Qdrant
        assert isinstance(results, list)
        
        # If we have results, validate their structure
        if results:
            for result in results:
                assert "content" in result
                assert "metadata" in result
                assert "score" in result
                assert isinstance(result["score"], (int, float))
    
    def test_query_preprocessing(self, qa_system):
        """Test query preprocessing functionality"""
        test_cases = [
            ("Plan a 5-day itinerary", "Munich attractions recommended attractions tourist attractions"),
            ("Tell me about museums", "Munich museum art culture history attractions"),
            ("Where can I eat?", "Munich restaurant food dining attractions"),
            ("Random question", "Random question")  # Should remain unchanged
        ]
        
        for input_query, expected in test_cases:
            result = qa_system.preprocess_query(input_query)
            assert result == expected
    
    @pytest.mark.slow
    def test_complete_qa_workflow(self, qa_system):
        """Test the complete Q&A workflow end-to-end"""
        questions = [
            "What are the top attractions in Munich?",
            "Tell me about free things to do",
            "Recommend some museums"
        ]
        
        for question in questions:
            result = qa_system.ask(question)
            
            # Validate response structure
            assert isinstance(result, dict)
            assert "question" in result
            assert "search_results" in result
            assert "answer" in result
            assert "results_count" in result
            
            # Validate content
            assert result["question"] == question
            assert isinstance(result["search_results"], list)
            assert isinstance(result["answer"], str)
            assert isinstance(result["results_count"], int)
            assert len(result["answer"]) > 0
    
    def test_model_switching(self, qa_system):
        """Test switching between available models"""
        available_models = qa_system.list_available_models()
        original_model = qa_system.get_current_model_info()["model_name"]
        
        for model in available_models:
            if model != original_model:
                # Try to switch to different model
                success = qa_system.switch_model(model)
                if success:
                    current_model = qa_system.get_current_model_info()["model_name"]
                    assert current_model != original_model
                    
                    # Switch back
                    qa_system.switch_model(original_model)
                    break
    
    @pytest.mark.slow
    def test_error_handling_with_invalid_query(self, qa_system):
        """Test error handling with potentially problematic queries"""
        problematic_queries = [
            "",  # Empty query
            "a" * 1000,  # Very long query
            "🎭🎨🎪🎫🎬",  # Only emojis
            "AAAAAAAAAA" * 50,  # Repetitive text
        ]
        
        for query in problematic_queries:
            try:
                result = qa_system.ask(query)
                # Should not raise exception, should return valid structure
                assert isinstance(result, dict)
                assert "answer" in result
            except Exception as e:
                pytest.fail(f"System should handle problematic query gracefully: {query}. Error: {e}")


class TestQASystemPerformance:
    """Performance tests for the Q&A system"""
    
    @pytest.mark.slow
    def test_response_time(self, qa_system):
        """Test that responses are generated within reasonable time"""
        import time
        
        question = "What are the best attractions in Munich?"
        
        start_time = time.time()
        result = qa_system.ask(question)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Response should be within 30 seconds
        assert response_time < 30, f"Response took too long: {response_time:.2f} seconds"
        assert len(result["answer"]) > 0
    
    @pytest.mark.slow
    def test_concurrent_requests_simulation(self, qa_system):
        """Test handling multiple requests (simulated sequentially)"""
        questions = [
            "What can I do in Munich?",
            "Tell me about parks",
            "Recommend restaurants",
            "Where are the museums?",
            "What's free to visit?"
        ]
        
        results = []
        for question in questions:
            result = qa_system.ask(question)
            results.append(result)
        
        # All requests should succeed
        assert len(results) == len(questions)
        for result in results:
            assert isinstance(result["answer"], str)
            assert len(result["answer"]) > 0


# Fixtures for testing with different configurations
@pytest.fixture(scope="module")
def qa_system_with_local_model():
    """Create Q&A system with local model if available"""
    if not os.getenv("LOCAL_OLLAMA_URL"):
        pytest.skip("Local Ollama not configured")
    
    try:
        qa_system = AttractionQASystem(model_type="local_ollama")
        return qa_system
    except Exception:
        pytest.skip("Local Ollama model not available")


class TestLocalModelIntegration:
    """Integration tests specifically for local models"""
    
    def test_local_model_qa(self, qa_system_with_local_model):
        """Test Q&A with local model"""
        result = qa_system_with_local_model.ask("What attractions are in Munich?")
        
        assert isinstance(result, dict)
        assert "answer" in result
        assert len(result["answer"]) > 0
    
    def test_local_model_fallback(self, qa_system):
        """Test fallback to local model when OpenAI fails"""
        # This would require mocking OpenAI to fail
        # For now, we just test that the mechanism exists
        assert hasattr(qa_system, '_handle_model_fallback')
        assert hasattr(qa_system, '_restore_original_model')
