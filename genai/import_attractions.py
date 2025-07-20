#!/usr/bin/env python3
"""
Attractions data import script
Import attraction data from PostgreSQL to Qdrant vector database
"""

import sys
from langchain_core.documents import Document
from travel_buddy_ai.services.generic_vector_service import GenericVectorService
from travel_buddy_ai.repositories.simple_attraction_reader import SimpleAttractionReader
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)


class AttractionsImporter:
    """Attraction data importer"""
    
    def __init__(self, collection_name: str = "attractions_collection"):
        self.vector_service = None
        self.reader = None
    
    def import_attractions(self, batch_size: int = 50):
        """Import attraction data in batches"""
        logger.info("🔄 Starting import process...")
        
        try:
            if not self.vector_service:
                logger.info("📡 Initializing vector service...")
                self.vector_service = GenericVectorService(collection_name="attractions_collection")
                logger.info("✅ Vector service initialized")
                
                logger.info("🏗️ Creating collection...")
                self.vector_service.create_collection(self.vector_service.collection_name)
                logger.info("✅ Collection created")
                
            if not self.reader:
                logger.info("📖 Initializing attraction reader...")
                self.reader = SimpleAttractionReader()
                logger.info("✅ Attraction reader initialized")
                
            logger.info("🔢 Counting attractions...")
            total = self.reader.count_attractions()
            logger.info(f"🚚 Importing {total} attractions to Qdrant...")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise

        imported, offset = 0, 0
        while True:
            attractions = self.reader.get_all_attractions(limit=batch_size, offset=offset)
            if not attractions:
                break

            docs, ids = [], []
            for attr in attractions:
                docs.append(Document(page_content=attr.to_vector_content(), metadata=attr.to_metadata()))
                ids.append(str(attr.id))

            self.vector_service.add_documents(docs, ids)
            imported += len(docs)
            logger.info(f"✅ Imported {imported}/{total}")
            offset += batch_size

        logger.info(f"🎉 Import complete. Total: {imported}")
        logger.debug(f"📊 Collection info: {self.vector_service.get_collection_info()}")

    def test_search(self, query: str = "beautiful beach"):
        """Run a simple semantic search test"""
        logger.info(f"🔍 Testing search for: '{query}'")
        results = self.vector_service.search(query=query, limit=5, score_threshold=0.5)
        for i, res in enumerate(results, 1):
            meta = res["metadata"]
            logger.info(f"{i}. {meta.get('name')} ({meta.get('city')}) | Score: {res['score']:.3f}")


def main():
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
    
    print("🚀 Starting import...")
    logger.info("🚀 Import script started")
    importer = AttractionsImporter()

    try:
        logger.info("🔧 Starting attractions import...")
        importer.import_attractions()
        logger.info("✅ Import completed successfully")
        
        print("🧪 Running test searches...\n")
        logger.info("🧪 Starting test searches...")
        for q in ["beach", "museum", "nature", "historic places"]:
            print(f"\n🔍 {q}")
            logger.info(f"🔍 Testing search for: {q}")
            importer.test_search(q)

        print("\n✅ Done! You can now call:")
        print("curl -X POST http://localhost:8000/api/v1/vector/search -d '{\"query\": \"beach\"}'")
        logger.info("🎉 All operations completed successfully")

    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        logger.exception("Full error details:")
        sys.exit(1)


if __name__ == "__main__":
    main()
