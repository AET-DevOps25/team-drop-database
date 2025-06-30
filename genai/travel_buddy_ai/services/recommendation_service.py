from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from travel_buddy_ai.models.attractions import AttractionModel, VectorSearchResult
from travel_buddy_ai.services.vector_service import AttractionVectorService
from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)


class TravelRecommendationService:
    """旅行推荐服务类"""
    
    def __init__(self):
        self.vector_service = AttractionVectorService()
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model="gpt-4",
            temperature=0.7
        )
        
        # 定义推荐系统的提示模板
        self.recommendation_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的旅行推荐助手。基于用户的查询和提供的景点信息，
            请生成个性化的旅行推荐。请确保推荐内容包括：
            1. 景点的详细介绍
            2. 推荐理由
            3. 游览建议（如最佳时间、注意事项等）
            4. 如果有多个景点，建议合理的游览顺序
            
            请用友好、专业的语调回答，并确保信息准确实用。"""),
            ("user", """用户查询：{query}
            
            相关景点信息：
            {attractions_info}
            
            请基于以上信息生成详细的旅行推荐。""")
        ])
        
        self.output_parser = StrOutputParser()
        
        # 构建推荐链
        self.recommendation_chain = (
            self.recommendation_prompt 
            | self.llm 
            | self.output_parser
        )
    
    async def get_travel_recommendations(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.7,
        city_filter: Optional[str] = None,
        country_filter: Optional[str] = None
    ) -> str:
        """
        基于用户查询生成旅行推荐
        
        Args:
            query: 用户查询
            limit: 返回景点数量
            score_threshold: 相似度阈值
            city_filter: 城市过滤器
            country_filter: 国家过滤器
            
        Returns:
            生成的旅行推荐文本
        """
        try:
            # 1. 使用向量搜索查找相关景点
            search_results: List[VectorSearchResult] = await self.vector_service.retrieve_by_similarity(
                query=query,
                score_threshold=score_threshold,
                limit=limit,
                city_filter=city_filter,
                country_filter=country_filter
            )
            
            if not search_results:
                return f"抱歉，没有找到与 '{query}' 相关的景点。请尝试使用不同的关键词或调整搜索条件。"
            
            # 2. 格式化景点信息
            attractions_info = self._format_attractions_info(search_results)
            
            # 3. 使用 LLM 生成推荐
            recommendation = await self.recommendation_chain.ainvoke({
                "query": query,
                "attractions_info": attractions_info
            })
            
            logger.info(f"为查询 '{query}' 生成了基于 {len(search_results)} 个景点的推荐")
            return recommendation
            
        except Exception as e:
            logger.error(f"生成旅行推荐失败: {e}")
            return f"抱歉，生成推荐时出现错误。请稍后再试。"
    
    def _format_attractions_info(self, search_results: List[VectorSearchResult]) -> str:
        """
        格式化景点信息用于 LLM 生成
        
        Args:
            search_results: 搜索结果列表
            
        Returns:
            格式化的景点信息字符串
        """
        formatted_info = []
        
        for i, result in enumerate(search_results, 1):
            attraction = result.attraction
            score = result.score
            
            info = f"""
景点 {i}：
- 名称：{attraction.name}
- 城市：{attraction.city.name}, {attraction.city.country}
- 描述：{attraction.description}
- 地址：{attraction.location.address}
- 相似度评分：{score:.3f}
"""
            
            # 添加营业时间信息（如果有）
            if attraction.opening_hours:
                hours_info = []
                for hours in attraction.opening_hours[:3]:  # 只显示前3个时间段
                    hours_info.append(f"{hours.day}: {hours.from_time}-{hours.to_time}")
                info += f"- 营业时间：{'; '.join(hours_info)}\n"
            
            # 添加网站信息（如果有）
            if attraction.website:
                info += f"- 官方网站：{attraction.website}\n"
            
            formatted_info.append(info)
        
        return "\n".join(formatted_info)
    
    async def get_city_recommendations(
        self,
        city_name: str,
        interest_keywords: Optional[str] = None,
        limit: int = 10
    ) -> str:
        """
        基于城市获取推荐
        
        Args:
            city_name: 城市名称
            interest_keywords: 兴趣关键词
            limit: 返回景点数量
            
        Returns:
            城市旅行推荐
        """
        query = f"{city_name} 旅游"
        if interest_keywords:
            query += f" {interest_keywords}"
        
        return await self.get_travel_recommendations(
            query=query,
            limit=limit,
            city_filter=city_name,
            score_threshold=0.5  # 降低阈值以获取更多结果
        )
    
    async def get_themed_recommendations(
        self,
        theme: str,
        location: Optional[str] = None,
        limit: int = 8
    ) -> str:
        """
        基于主题获取推荐
        
        Args:
            theme: 主题（如：历史文化、自然风光、美食、购物等）
            location: 地点限制
            limit: 返回景点数量
            
        Returns:
            主题旅行推荐
        """
        query = f"{theme} 旅游景点"
        if location:
            query += f" {location}"
        
        city_filter = location if location else None
        
        return await self.get_travel_recommendations(
            query=query,
            limit=limit,
            city_filter=city_filter,
            score_threshold=0.6
        )
