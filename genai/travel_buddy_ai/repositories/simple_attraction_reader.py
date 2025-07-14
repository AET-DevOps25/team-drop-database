from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from travel_buddy_ai.models.attractions_simple import SimpleAttractionModel
from travel_buddy_ai.core.db import get_database_session
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)


class SimpleAttractionReader:
    """Simplified attraction data reader"""
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_database_session()
    
    def get_all_attractions(self, limit: int = 1000, offset: int = 0) -> List[SimpleAttractionModel]:
        """
        Get all attraction data
        
        Args:
            limit: Limit count
            offset: Offset value
            
        Returns:
            List of attraction models
        """
        try:
            query = text("""
                SELECT 
                    a.id, 
                    a.name, 
                    a.description, 
                    c.name as city_name,
                    l.country,
                    l.address,
                    l.latitude,
                    l.longitude,
                    a.website
                FROM attractions a
                LEFT JOIN location l ON a.location_id = l.id
                LEFT JOIN cities c ON a.city_id = c.id
                WHERE a.description IS NOT NULL 
                AND a.description != ''
                AND LENGTH(a.description) > 20
                ORDER BY a.id
                LIMIT :limit OFFSET :offset
            """)
            
            results = self.session.execute(query, {"limit": limit, "offset": offset}).fetchall()
            
            attractions = []
            for result in results:
                try:
                    attraction = SimpleAttractionModel(
                        id=result.id,
                        name=result.name or f"Attraction_{result.id}",
                        description=result.description or "",
                        city_name=result.city_name or "Unknown City",
                        country=result.country or "Unknown Country",
                        address=result.address or "",
                        latitude=str(result.latitude) if result.latitude else None,
                        longitude=str(result.longitude) if result.longitude else None,
                        website=result.website
                    )
                    attractions.append(attraction)
                except Exception as e:
                    logger.warning(f"Skipping attraction ID {result.id}: {e}")
                    continue
            
            return attractions
        
        except Exception as e:
            logger.error(f"Failed to get attraction data: {e}")
            return []
    
    def count_attractions(self) -> int:
        """Get total count of attractions"""
        try:
            query = text("""
                SELECT COUNT(*) as count
                FROM attractions a
                WHERE a.description IS NOT NULL 
                AND a.description != ''
                AND LENGTH(a.description) > 20
            """)
            
            result = self.session.execute(query).fetchone()
            return result.count if result else 0
        
        except Exception as e:
            logger.error(f"Failed to get attraction count: {e}")
            return 0
