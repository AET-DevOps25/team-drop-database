#!/usr/bin/env python3
"""
景点问答系统（修正版）
直接适配现有的attractions_collection数据格式
支持多种LLM模型（OpenAI, GPT4All, LLaMA等）
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
    """景点问答系统"""
    
    def __init__(self, model_type: str = None):
        self.qdrant_client = get_qdrant_connection()
        self.collection_name = "attractions_collection"
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large", 
            api_key=settings.openai_api_key
        )
        
        # 设置LLM模型
        if model_type:
            if not model_manager.set_model(model_type):
                logger.warning(f"模型 {model_type} 不可用，使用默认模型")
        
        # 检查是否有可用模型
        if not model_manager.get_current_model():
            raise RuntimeError("没有可用的LLM模型，请检查配置")
        
        current_model = model_manager.get_current_model()
        logger.info(f"使用LLM模型: {current_model.model_name}")
        logger.info(f"可用模型列表: {model_manager.list_available_models()}")
    
    def switch_model(self, model_type: str) -> bool:
        """
        切换LLM模型
        
        Args:
            model_type: 模型类型 (openai, gpt4all, llamacpp, ollama)
            
        Returns:
            是否切换成功
        """
        success = model_manager.set_model(model_type)
        if success:
            current_model = model_manager.get_current_model()
            logger.info(f"已切换到模型: {current_model.model_name}")
        return success
    
    def list_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return model_manager.list_available_models()
    
    def get_current_model_info(self) -> Dict[str, str]:
        """获取当前模型信息"""
        current_model = model_manager.get_current_model()
        if current_model:
            return {
                "model_name": current_model.model_name,
                "model_type": type(current_model).__name__
            }
        return {"model_name": "None", "model_type": "None"}
    
    def preprocess_query(self, query: str) -> str:
        """
        预处理查询，将一般性问题转换为更具体的景点搜索查询
        
        Args:
            query: 原始查询
            
        Returns:
            处理后的查询
        """
        query_lower = query.lower()
        
        # 行程规划类问题
        if any(keyword in query_lower for keyword in ['行程', '规划', '几天', '安排', '计划', 'itinerary', 'plan']):
            return "慕尼黑景点 推荐景点 旅游景点"
        
        # 直接返回原查询
        return query
    
    def search_attractions(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """
        搜索相关景点
        
        Args:
            query: 搜索查询
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        try:
            # 预处理查询
            processed_query = self.preprocess_query(query)
            logger.info(f"原始查询: {query}")
            if processed_query != query:
                logger.info(f"处理后查询: {processed_query}")
            
            # 对查询进行向量化
            query_vector = self.embeddings.embed_query(processed_query)
            
            # 在Qdrant中搜索
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=("dense", query_vector),  # 指定使用dense向量
                limit=limit,
                score_threshold=0.3,  # 降低阈值以获取更多结果
                with_payload=True
            )
            
            results = []
            for result in search_results:
                results.append({
                    "content": result.payload.get("page_content", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "score": result.score
                })
            
            logger.info(f"向量搜索找到 {len(results)} 个相关结果")
            return results
            
        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            return []
    
    def generate_answer(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """
        基于搜索结果生成回答
        
        Args:
            question: 用户问题
            search_results: 向量搜索结果
            
        Returns:
            生成的回答
        """
        if not search_results:
            return "抱歉，我没有找到相关的景点信息。"
        
        # 构建上下文
        context_parts = []
        for result in search_results:
            content = result.get("content", "")
            score = result.get("score", 0)
            context_parts.append(f"[相关度: {score:.3f}] {content}")
        
        context = "\n\n".join(context_parts)
        
        # 构建提示词
        prompt = f"""
请基于以下景点信息回答用户的问题。

用户问题: {question}

相关景点信息:
{context}

请注意:
1. 只使用提供的景点信息来回答
2. 如果用户问的是行程规划类问题，请基于提供的景点信息制定合理的行程安排
3. 回答要详细、有用，包含具体的景点名称、地址、描述等
4. 用中文回答
5. 如果有多个相关景点，可以推荐多个
6. 对于行程规划，可以按天数安排，考虑景点的地理位置和类型

回答:
"""
        
        try:
            answer = model_manager.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            logger.info(f"LLM生成回答成功，长度: {len(answer)} 字符")
            return answer
            
        except Exception as e:
            logger.error(f"LLM生成回答失败: {e}")
            return f"抱歉，生成回答时出现错误: {str(e)}"
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        问答主流程
        
        Args:
            question: 用户问题
            
        Returns:
            问答结果，包含搜索结果和生成的回答
        """
        logger.info(f"收到问题: {question}")
        
        # 1. 向量搜索
        search_results = self.search_attractions(question)
        
        # 2. 生成回答
        answer = self.generate_answer(question, search_results)
        
        # 3. 返回结果
        return {
            "question": question,
            "search_results": search_results,
            "answer": answer,
            "results_count": len(search_results)
        }


def main():
    """交互式问答"""
    print("🎯 景点问答系统（多模型支持版）")
    print("=" * 50)
    
    try:
        # 可以通过环境变量或命令行参数指定模型
        model_type = settings.llm_model_type if hasattr(settings, 'llm_model_type') else None
        qa_system = AttractionQASystem(model_type=model_type)
        
        # 显示当前模型信息
        model_info = qa_system.get_current_model_info()
        print(f"✅ 问答系统初始化成功")
        print(f"🤖 当前模型: {model_info['model_name']} ({model_info['model_type']})")
        print(f"🔧 可用模型: {', '.join(qa_system.list_available_models())}")
        print()
        
        while True:
            user_input = input("🔍 请输入您的问题 (输入 'quit' 退出, 'models' 查看模型, 'switch <model>' 切换模型): ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 再见！")
                break
            
            if user_input.lower() == 'models':
                model_info = qa_system.get_current_model_info()
                print(f"🤖 当前模型: {model_info['model_name']} ({model_info['model_type']})")
                print(f"🔧 可用模型: {', '.join(qa_system.list_available_models())}")
                continue
            
            if user_input.lower().startswith('switch '):
                model_name = user_input[7:].strip()
                if qa_system.switch_model(model_name):
                    model_info = qa_system.get_current_model_info()
                    print(f"✅ 已切换到模型: {model_info['model_name']}")
                else:
                    print(f"❌ 切换失败，模型 {model_name} 不可用")
                continue
            
            if not user_input:
                print("❌ 请输入有效的问题")
                continue
            
            print("\n" + "=" * 50)
            result = qa_system.ask(user_input)
            
            print(f"🔍 搜索到 {result['results_count']} 个相关结果")
            print(f"\n🤖 AI回答:\n{result['answer']}")
            print("=" * 50 + "\n")
            
    except KeyboardInterrupt:
        print("\n👋 再见！")
    except Exception as e:
        print(f"❌ 系统错误: {e}")
        logger.error(f"系统错误: {e}", exc_info=True)


if __name__ == "__main__":
    main()
