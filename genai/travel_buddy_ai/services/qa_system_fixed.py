#!/usr/bin/env python3
"""
Attraction Q&A System (Fixed Version)
Directly adapts to existing attractions_collection data format
Supports multiple LLM models (OpenAI, GPT4All, LLaMA, etc.)
"""

import time
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings

from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.db import get_qdrant_connection
from travel_buddy_ai.core.logger import get_logger
from travel_buddy_ai.models.llm_models import model_manager, ModelType

logger = get_logger(__name__)


class AttractionQASystem:
    """Attraction Q&A System"""
    
    def __init__(self, model_type: str = None):
        self.collection_name = "attractions_collection"
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            api_key=settings.openai_api_key
        )
        self.openai_timeout = 40
        self.original_model_type = model_type or "openai"
        
        self._initialize_model(model_type)
    
    def _initialize_model(self, model_type: str):
        """Initialize and validate LLM model"""
        if model_type and not model_manager.set_model(model_type):
            logger.warning(f"Model {model_type} not available, using default model")
        
        if not model_manager.get_current_model():
            raise RuntimeError("No available LLM model, please check configuration")
        
        current_model = model_manager.get_current_model()
        logger.info(f"Using LLM model: {current_model.model_name}")
        logger.info(f"Available models: {', '.join(model_manager.list_available_models())}")
    
    def _handle_model_fallback(self) -> bool:
        """Handle fallback to local model and restoration"""
        available_models = model_manager.list_available_models()
        local_models = [m for m in available_models if 'local' in m.lower() or 'ollama' in m.lower()]
        
        if not local_models:
            logger.warning("No local models available for fallback")
            return False
        
        for local_model in local_models:
            if model_manager.set_model(local_model):
                logger.info(f"Successfully fell back to local model: {local_model}")
                return True
        
        logger.error("Failed to fallback to any local model")
        return False
    
    def _restore_original_model(self):
        """Restore to original model after fallback"""
        if model_manager.set_model(self.original_model_type):
            logger.info(f"Restored to original model: {self.original_model_type}")
    
    def switch_model(self, model_type: str) -> bool:
        """Switch LLM model"""
        if model_manager.set_model(model_type):
            logger.info(f"Switched to model: {model_manager.get_current_model().model_name}")
            return True
        return False
    
    def list_available_models(self) -> List[str]:
        """Get list of available models"""
        return model_manager.list_available_models()
    
    def get_current_model_info(self) -> Dict[str, str]:
        """Get current model information"""
        current_model = model_manager.get_current_model()
        return {
            "model_name": current_model.model_name if current_model else "None",
            "model_type": type(current_model).__name__ if current_model else "None"
        }
    
    def preprocess_query(self, query: str) -> str:
        """Preprocess query for better search results"""
        query_lower = query.lower()
        
        query_mappings = {
            frozenset(['itinerary', 'plan', 'days', 'schedule', 'trip']): "Munich attractions recommended attractions tourist attractions",
            frozenset(['food', 'restaurant', 'eat', 'dining']): "Munich restaurant food dining attractions",
            frozenset(['shopping', 'shop', 'buy', 'market']): "Munich shopping market attractions",
            frozenset(['museum', 'art', 'culture', 'history', 'historical']): "Munich museum art culture history attractions",
            frozenset(['park', 'garden', 'nature', 'outdoor']): "Munich park garden nature outdoor attractions"
        }
        
        for keywords, replacement in query_mappings.items():
            if any(keyword in query_lower for keyword in keywords):
                return replacement
        
        return query
    
    def search_attractions(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Search related attractions"""
        try:
            processed_query = self.preprocess_query(query)
            logger.info(f"Query: {query}" + (f" -> {processed_query}" if processed_query != query else ""))
            
            query_vector = self.embeddings.embed_query(processed_query)
            
            # Try with threshold first, then without
            for score_threshold in [0.3, None]:
                search_params = {
                    "collection_name": self.collection_name,
                    "query_vector": ("dense", query_vector),
                    "limit": limit,
                    "with_payload": True
                }
                if score_threshold:
                    search_params["score_threshold"] = score_threshold
                qdrant_client = get_qdrant_connection()
                search_results = qdrant_client.search(**search_params)
                if search_results:
                    break
            
            results = [{
                "content": result.payload.get("page_content", ""),
                "metadata": result.payload.get("metadata", {}),
                "score": result.score
            } for result in search_results]
            
            logger.info(f"Found {len(results)} relevant results")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def _create_prompt(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """Create prompt based on search results"""
        if not search_results:
            return f"""
The user asked: {question}

Although I don't have specific attraction information for this query, please provide a helpful general response about Munich travel based on common knowledge. Include suggestions about popular attractions, travel tips, and encourage asking more specific questions.

Answer:
"""
        
        context = "\n\n".join([
            f"[Relevance: {result.get('score', 0):.3f}] {result.get('content', '')}"
            for result in search_results
        ])
        
        return f"""
Please answer the user's question based on the following attraction information.

User question: {question}

Related attraction information:
{context}

Guidelines:
1. Use provided information as primary source
2. Supplement with general knowledge if needed (clearly indicate this)
3. For itinerary planning, create reasonable arrangements based on provided attractions
4. Include specific names, addresses, descriptions
5. Answer in English
6. Be helpful and encouraging

Answer:
"""
    
    def _generate_with_timeout(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate answer with timeout and fallback mechanism"""
        current_model = model_manager.get_current_model()
        is_openai = 'gpt' in current_model.model_name.lower() or 'openai' in type(current_model).__name__.lower()
        
        start_time = time.time()
        fallback_used = False
        
        try:
            if is_openai:
                logger.info(f"Using OpenAI model with {self.openai_timeout}s timeout")
            
            answer = model_manager.generate(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
            elapsed_time = time.time() - start_time
            
            if is_openai and elapsed_time > self.openai_timeout:
                logger.warning(f"OpenAI response took {elapsed_time:.2f}s (exceeds {self.openai_timeout}s)")
            else:
                logger.info(f"Response completed in {elapsed_time:.2f}s")
            
            return answer
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.warning(f"Model failed after {elapsed_time:.2f}s: {e}")
            
            # Try fallback for OpenAI timeout-related errors
            if is_openai and (elapsed_time > self.openai_timeout or "timeout" in str(e).lower()):
                if self._handle_model_fallback():
                    try:
                        logger.info("Generating answer with fallback model")
                        answer = model_manager.generate(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
                        self._restore_original_model()
                        return f"[Generated with local model fallback due to OpenAI timeout]\n\n{answer}"
                    except Exception as fallback_error:
                        logger.error(f"Fallback generation failed: {fallback_error}")
                        self._restore_original_model()
            
            return "I encountered an error processing your question. Please try asking a more specific question about Munich attractions, restaurants, or activities."
    
    def generate_answer(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate answer based on search results"""
        prompt = self._create_prompt(question, search_results)
        max_tokens = 500 if not search_results else 1000
        return self._generate_with_timeout(prompt, max_tokens)
    
    def ask(self, question: str) -> Dict[str, Any]:
        """Main Q&A process"""
        logger.info(f"Received question: {question}")
        search_results = self.search_attractions(question)
        answer = self.generate_answer(question, search_results)
        
        return {
            "question": question,
            "search_results": search_results,
            "answer": answer,
            "results_count": len(search_results)
        }


def main():
    """Interactive Q&A"""
    print("🎯 Attraction Q&A System (Multi-model Support)")
    print("=" * 50)
    
    try:
        model_type = getattr(settings, 'llm_model_type', None)
        qa_system = AttractionQASystem(model_type=model_type)
        
        # Display system info
        model_info = qa_system.get_current_model_info()
        print(f"✅ System initialized")
        print(f"🤖 Current model: {model_info['model_name']} ({model_info['model_type']})")
        print(f"🔧 Available models: {', '.join(qa_system.list_available_models())}")
        
        if 'local_ollama' in qa_system.list_available_models():
            print(f"🏠 Local Ollama: {getattr(settings, 'local_ollama_url', 'Not configured')}")
        print()
        
        commands = {
            'quit': lambda: exit(),
            'models': lambda: print(f"🤖 Current: {qa_system.get_current_model_info()['model_name']}\n🔧 Available: {', '.join(qa_system.list_available_models())}"),
        }
        
        while True:
            user_input = input("🔍 Enter question ('quit', 'models', 'switch <model>'): ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'models':
                commands['models']()
                continue
            
            if user_input.lower().startswith('switch '):
                model_name = user_input[7:].strip()
                if qa_system.switch_model(model_name):
                    print(f"✅ Switched to: {qa_system.get_current_model_info()['model_name']}")
                else:
                    print(f"❌ Failed to switch to: {model_name}")
                continue
            
            # Process question
            print("\n" + "=" * 50)
            result = qa_system.ask(user_input)
            print(f"🔍 Found {result['results_count']} results")
            print(f"\n🤖 Answer:\n{result['answer']}")
            print("=" * 50 + "\n")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ System error: {e}")
        logger.error(f"System error: {e}", exc_info=True)


if __name__ == "__main__":
    main()