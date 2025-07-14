#!/usr/bin/env python3
"""
Attraction Q&A System (Fixed Version)
Directly adapts to existing attractions_collection data format
Supports multiple LLM models (OpenAI, GPT4All, LLaMA, etc.)
"""

import asyncio
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
        self.qdrant_client = get_qdrant_connection()
        self.collection_name = "attractions_collection"
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large", 
            api_key=settings.openai_api_key
        )
        
        # Set LLM model
        if model_type:
            if not model_manager.set_model(model_type):
                logger.warning(f"Model {model_type} not available, using default model")
        
        # Check if there's an available model
        if not model_manager.get_current_model():
            raise RuntimeError("No available LLM model, please check configuration")
        
        current_model = model_manager.get_current_model()
        logger.info(f"Using LLM model: {current_model.model_name}")
        logger.info(f"Available models list: {model_manager.list_available_models()}")
    
    def switch_model(self, model_type: str) -> bool:
        """
        Switch LLM model
        
        Args:
            model_type: Model type (openai, gpt4all, llamacpp, ollama)
            
        Returns:
            Whether switch was successful
        """
        success = model_manager.set_model(model_type)
        if success:
            current_model = model_manager.get_current_model()
            logger.info(f"Switched to model: {current_model.model_name}")
        return success
    
    def list_available_models(self) -> List[str]:
        """Get list of available models"""
        return model_manager.list_available_models()
    
    def get_current_model_info(self) -> Dict[str, str]:
        """Get current model information"""
        current_model = model_manager.get_current_model()
        if current_model:
            return {
                "model_name": current_model.model_name,
                "model_type": type(current_model).__name__
            }
        return {"model_name": "None", "model_type": "None"}
    
    def preprocess_query(self, query: str) -> str:
        """
        Preprocess query, convert general questions to more specific attraction search queries
        
        Args:
            query: Original query
            
        Returns:
            Processed query
        """
        query_lower = query.lower()
        
        # Itinerary planning questions
        if any(keyword in query_lower for keyword in ['itinerary', 'plan', 'days', 'schedule', 'trip', '行程', '规划', '几天', '安排', '计划']):
            return "Munich attractions recommended attractions tourist attractions"
        
        # Add more query expansions for common travel terms
        if any(keyword in query_lower for keyword in ['food', 'restaurant', 'eat', 'dining', '美食', '餐厅', '吃']):
            return "Munich restaurant food dining attractions"
        
        if any(keyword in query_lower for keyword in ['shopping', 'shop', 'buy', 'market', '购物', '商店', '市场']):
            return "Munich shopping market attractions"
        
        if any(keyword in query_lower for keyword in ['museum', 'art', 'culture', 'history', '博物馆', '艺术', '文化', '历史']):
            return "Munich museum art culture history attractions"
        
        if any(keyword in query_lower for keyword in ['park', 'garden', 'nature', 'outdoor', '公园', '花园', '自然', '户外']):
            return "Munich park garden nature outdoor attractions"
        
        # Return original query directly
        return query
    
    def search_attractions(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Search related attractions
        
        Args:
            query: Search query
            limit: Result count limit
            
        Returns:
            List of search results
        """
        try:
            # Preprocess query
            processed_query = self.preprocess_query(query)
            logger.info(f"Original query: {query}")
            if processed_query != query:
                logger.info(f"Processed query: {processed_query}")
            
            # 对查询进行向量化
            query_vector = self.embeddings.embed_query(processed_query)
            
            # 在Qdrant中搜索 - 降低分数阈值
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=("dense", query_vector),  # 指定使用dense向量
                limit=limit,
                score_threshold=0.3,  # 大幅降低阈值以获取更多结果
                with_payload=True
            )
            
            # 如果没有找到结果，尝试不使用阈值
            if not search_results:
                logger.info("No results with threshold, trying without threshold")
                search_results = self.qdrant_client.search(
                    collection_name=self.collection_name,
                    query_vector=("dense", query_vector),
                    limit=limit,
                    with_payload=True
                )
            
            results = []
            for result in search_results:
                results.append({
                    "content": result.payload.get("page_content", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "score": result.score
                })
            
            logger.info(f"Vector search found {len(results)} relevant results")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def generate_answer(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """
        Generate answer based on search results
        
        Args:
            question: User question
            search_results: Vector search results
            
        Returns:
            Generated answer
        """
        # 如果没有搜索结果，提供通用的旅游建议
        if not search_results:
            fallback_prompt = f"""
The user asked: {question}

Although I don't have specific attraction information for this query, please provide a helpful general response about Munich travel based on common knowledge. Include suggestions about:
- Popular types of attractions in Munich
- General travel tips
- Recommendations for finding more specific information

Please be helpful and encouraging, suggesting they ask more specific questions about Munich attractions, museums, restaurants, or activities.

Answer:
"""
            try:
                answer = model_manager.generate(
                    prompt=fallback_prompt,
                    max_tokens=500,
                    temperature=0.7
                )
                return answer
            except Exception as e:
                logger.error(f"Fallback answer generation failed: {e}")
                return "I understand you're asking about Munich travel. While I don't have specific information for your exact question, Munich is a wonderful city with many attractions including historic sites, museums, parks, and excellent food. Could you please ask a more specific question about Munich attractions, restaurants, or activities you're interested in?"
        
        # Build context
        context_parts = []
        for result in search_results:
            content = result.get("content", "")
            score = result.get("score", 0)
            context_parts.append(f"[Relevance: {score:.3f}] {content}")
        
        context = "\n\n".join(context_parts)
        
        # Build prompt
        prompt = f"""
Please answer the user's question based on the following attraction information.

User question: {question}

Related attraction information:
{context}

Please note:
1. Use the provided attraction information as the primary source for your answer
2. If the provided information doesn't fully answer the question, supplement with general knowledge but clearly indicate what comes from the provided data vs. general knowledge
3. If the user asks about itinerary planning, please create reasonable itinerary arrangements based on the provided attraction information
4. Answer should be detailed and useful, including specific attraction names, addresses, descriptions, etc.
5. Answer in English
6. If there are multiple relevant attractions, you can recommend multiple ones
7. For itinerary planning, arrange by days, considering the geographical location and types of attractions
8. Be helpful and encouraging, even if the match isn't perfect

Answer:
"""
        
        try:
            answer = model_manager.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            logger.info(f"LLM answer generated successfully, length: {len(answer)} characters")
            return answer
            
        except Exception as e:
            logger.error(f"LLM answer generation failed: {e}")
            return f"I understand you're asking about Munich travel. While I encountered an error processing your specific question ({str(e)}), I'd be happy to help if you could ask a more specific question about Munich attractions, restaurants, or activities."
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Main Q&A process
        
        Args:
            question: User question
            
        Returns:
            Q&A result, including search results and generated answer
        """
        logger.info(f"Received question: {question}")
        
        # 1. Vector search
        search_results = self.search_attractions(question)
        
        # 2. Generate answer
        answer = self.generate_answer(question, search_results)
        
        # 3. Return result
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
        # Can specify model through environment variables or command line arguments
        model_type = settings.llm_model_type if hasattr(settings, 'llm_model_type') else None
        qa_system = AttractionQASystem(model_type=model_type)
        
        # Display current model information
        model_info = qa_system.get_current_model_info()
        print(f"✅ Q&A system initialized successfully")
        print(f"🤖 Current model: {model_info['model_name']} ({model_info['model_type']})")
        print(f"🔧 Available models: {', '.join(qa_system.list_available_models())}")
        print()
        
        while True:
            user_input = input("🔍 Please enter your question (type 'quit' to exit, 'models' to view models, 'switch <model>' to switch model): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'models':
                model_info = qa_system.get_current_model_info()
                print(f"🤖 Current model: {model_info['model_name']} ({model_info['model_type']})")
                print(f"🔧 Available models: {', '.join(qa_system.list_available_models())}")
                continue
            
            if user_input.lower().startswith('switch '):
                model_name = user_input[7:].strip()
                if qa_system.switch_model(model_name):
                    model_info = qa_system.get_current_model_info()
                    print(f"✅ Switched to model: {model_info['model_name']}")
                else:
                    print(f"❌ Switch failed, model {model_name} not available")
                continue
            
            if not user_input:
                print("❌ Please enter a valid question")
                continue
            
            print("\n" + "=" * 50)
            result = qa_system.ask(user_input)
            
            print(f"🔍 Found {result['results_count']} relevant results")
            print(f"\n🤖 AI Answer:\n{result['answer']}")
            print("=" * 50 + "\n")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ System error: {e}")
        logger.error(f"System error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
