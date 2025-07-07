#!/usr/bin/env python3
"""
Attractions数据导入脚本
将PostgreSQL中的景点数据导入到Qdrant向量数据库
"""

import asyncio
import sys
from typing import List
from langchain_core.documents import Document

from travel_buddy_ai.services.generic_vector_service import GenericVectorService
from travel_buddy_ai.repositories.simple_attraction_reader import SimpleAttractionReader
from travel_buddy_ai.models.attractions_simple import SimpleAttractionModel
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)


class AttractionsImporter:
    """景点数据导入器"""
    
    def __init__(self):
        self.vector_service = GenericVectorService("attractions_collection")
        self.reader = SimpleAttractionReader()
    
    def import_attractions(self, batch_size: int = 50) -> None:
        """
        分批导入景点数据
        
        Args:
            batch_size: 批次大小
        """
        try:
            # 获取总数
            total_count = self.reader.count_attractions()
            logger.info(f"开始导入 {total_count} 个景点数据到向量库")
            
            imported_count = 0
            offset = 0
            
            while True:
                # 获取一批数据
                attractions = self.reader.get_all_attractions(
                    limit=batch_size, 
                    offset=offset
                )
                
                if not attractions:
                    break
                
                # 转换为Document格式
                documents = []
                ids = []
                
                for attraction in attractions:
                    doc = Document(
                        page_content=attraction.to_vector_content(),
                        metadata=attraction.to_metadata()
                    )
                    documents.append(doc)
                    ids.append(str(attraction.id))
                
                # 导入到向量库
                self.vector_service.add_documents(documents, ids)
                
                imported_count += len(attractions)
                logger.info(f"已导入 {imported_count}/{total_count} 个景点")
                
                offset += batch_size
            
            logger.info(f"✅ 导入完成！总共导入了 {imported_count} 个景点")
            
            # 获取集合信息
            collection_info = self.vector_service.get_collection_info()
            logger.info(f"集合信息: {collection_info}")
            
        except Exception as e:
            logger.error(f"导入失败: {e}")
            raise
    
    def test_search(self, query: str = "美丽的海滩") -> None:
        """
        测试搜索功能
        
        Args:
            query: 搜索查询
        """
        try:
            logger.info(f"测试搜索: '{query}'")
            
            results = self.vector_service.search(
                query=query,
                limit=5,
                score_threshold=0.5
            )
            
            logger.info(f"找到 {len(results)} 个相关结果:")
            for i, result in enumerate(results, 1):
                metadata = result["metadata"]
                logger.info(f"{i}. {metadata.get('name', 'Unknown')} (城市: {metadata.get('city', 'Unknown')}) - 得分: {result['score']:.3f}")
            
        except Exception as e:
            logger.error(f"搜索测试失败: {e}")


def main():
    """主函数"""
    print("🚀 开始导入景点数据到 Qdrant")
    print("=" * 50)
    
    importer = AttractionsImporter()
    
    try:
        # 导入数据
        importer.import_attractions(batch_size=50)
        
        print("\n" + "=" * 50)
        print("🧪 测试搜索功能")
        
        # 测试搜索
        test_queries = [
            "美丽的海滩",
            "历史文化遗址", 
            "自然风景",
            "适合拍照的地方",
            "博物馆"
        ]
        
        for query in test_queries:
            print(f"\n🔍 搜索: {query}")
            importer.test_search(query)
        
        print("\n🎉 导入和测试完成！")
        print("💡 现在可以通过API进行向量搜索了")
        print("📝 示例API调用:")
        print("curl -X POST http://localhost:8000/api/v1/vector/search \\")
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"query": "美丽的海滩", "limit": 5}\'')
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
