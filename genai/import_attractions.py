#!/usr/bin/env python3
"""
Attractions data import script
Import attraction data from PostgreSQL to Qdrant vector database
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
    """Attraction data importer"""
    
    def __init__(self):
        self.vector_service = GenericVectorService("attractions_collection")
        self.reader = SimpleAttractionReader()
    
    def import_attractions(self, batch_size: int = 50) -> None:
        """
        Import attraction data in batches
        
        Args:
            batch_size: Batch size
        """
        try:
            # Get total count
            total_count = self.reader.count_attractions()
            logger.info(f"Starting to import {total_count} attraction records to vector database")
            
            imported_count = 0
            offset = 0
            
            while True:
                # Get a batch of data
                attractions = self.reader.get_all_attractions(
                    limit=batch_size, 
                    offset=offset
                )
                
                if not attractions:
                    break
                
                # Convert to Document format
                documents = []
                ids = []
                
                for attraction in attractions:
                    doc = Document(
                        page_content=attraction.to_vector_content(),
                        metadata=attraction.to_metadata()
                    )
                    documents.append(doc)
                    ids.append(str(attraction.id))
                
                # Import to vector database
                self.vector_service.add_documents(documents, ids)
                
                imported_count += len(attractions)
                logger.info(f"Imported {imported_count}/{total_count} attractions")
                
                offset += batch_size
            
            logger.info(f"✅ Import completed! Total imported {imported_count} attractions")
            
            # Get collection info
            collection_info = self.vector_service.get_collection_info()
            logger.info(f"Collection info: {collection_info}")
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            raise
    
    def test_search(self, query: str = "beautiful beach") -> None:
        """
        Test search functionality
        
        Args:
            query: Search query
        """
        try:
            logger.info(f"Testing search: '{query}'")
            
            results = self.vector_service.search(
                query=query,
                limit=5,
                score_threshold=0.5
            )
            
            logger.info(f"Found {len(results)} relevant results:")
            for i, result in enumerate(results, 1):
                metadata = result["metadata"]
                logger.info(f"{i}. {metadata.get('name', 'Unknown')} (City: {metadata.get('city', 'Unknown')}) - Score: {result['score']:.3f}")
            
        except Exception as e:
            logger.error(f"Search test failed: {e}")


def main():
    """Main function"""
    print("🚀 Starting to import attraction data to Qdrant")
    print("=" * 50)
    
    importer = AttractionsImporter()
    
    try:
        # Import data
        importer.import_attractions(batch_size=50)
        
        print("\n" + "=" * 50)
        print("🧪 Testing search functionality")
        
        # Test search
        test_queries = [
            "beautiful beach",
            "historical cultural sites", 
            "natural scenery",
            "good places for photography",
            "museum"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Search: {query}")
            importer.test_search(query)
        
        print("\n🎉 Import and testing completed!")
        print("💡 Now you can perform vector search through API")
        print("📝 Example API call:")
        print("curl -X POST http://localhost:8000/api/v1/vector/search \\")
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"query": "beautiful beach", "limit": 5}\'')
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
