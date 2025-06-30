from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from travel_buddy_ai.models.attractions import AttractionModel, LocationModel, CityModel, OpeningHoursModel
from travel_buddy_ai.core.db import get_database_session
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)


class AttractionRepository:
    """旅游景点数据仓库类"""
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_database_session()
    
    async def get_attraction_by_id(self, attraction_id: int) -> Optional[AttractionModel]:
        """
        根据 ID 获取景点信息
        
        Args:
            attraction_id: 景点 ID
            
        Returns:
            景点模型或 None
        """
        try:
            query = text("""
                SELECT 
                    a.id, a.name, a.description, a.website,
                    a.created_at, a.updated_at,
                    l.id as location_id, l.address, l.country, 
                    l.latitude, l.longitude,
                    c.id as city_id, c.name as city_name, 
                    c.country as city_country, c.description as city_description,
                    c.latitude as city_latitude, c.longitude as city_longitude
                FROM attractions a
                LEFT JOIN locations l ON a.location_id = l.id
                LEFT JOIN cities c ON a.city_id = c.id
                WHERE a.id = :attraction_id
            """)
            
            result = self.session.execute(query, {"attraction_id": attraction_id}).fetchone()
            
            if not result:
                return None
            
            # 获取营业时间
            opening_hours = await self._get_opening_hours(attraction_id)
            
            # 获取照片
            photos = await self._get_photos(attraction_id)
            
            return self._build_attraction_model(result, opening_hours, photos)
        
        except Exception as e:
            logger.error(f"获取景点信息失败 (ID: {attraction_id}): {e}")
            return None
    
    async def list_attractions_with_summary(
        self, 
        limit: int = 100, 
        offset: int = 0,
        city_name: Optional[str] = None
    ) -> List[AttractionModel]:
        """
        获取景点列表（带描述信息，用于向量化）
        
        Args:
            limit: 限制数量
            offset: 偏移量
            city_name: 城市名称过滤
            
        Returns:
            景点模型列表
        """
        try:
            base_query = """
                SELECT 
                    a.id, a.name, a.description, a.website,
                    a.created_at, a.updated_at,
                    l.id as location_id, l.address, l.country, 
                    l.latitude, l.longitude,
                    c.id as city_id, c.name as city_name, 
                    c.country as city_country, c.description as city_description,
                    c.latitude as city_latitude, c.longitude as city_longitude
                FROM attractions a
                LEFT JOIN locations l ON a.location_id = l.id
                LEFT JOIN cities c ON a.city_id = c.id
                WHERE a.description IS NOT NULL AND a.description != ''
            """
            
            params: Dict[str, Any] = {"limit": limit, "offset": offset}
            
            if city_name:
                base_query += " AND c.name = :city_name"
                params["city_name"] = city_name
            
            base_query += " ORDER BY a.id LIMIT :limit OFFSET :offset"
            
            query = text(base_query)
            results = self.session.execute(query, params).fetchall()
            
            attractions = []
            for result in results:
                opening_hours = await self._get_opening_hours(result.id)
                photos = await self._get_photos(result.id)
                attraction = self._build_attraction_model(result, opening_hours, photos)
                if attraction:
                    attractions.append(attraction)
            
            return attractions
        
        except Exception as e:
            logger.error(f"获取景点列表失败: {e}")
            return []
    
    async def get_attractions_by_ids(self, attraction_ids: List[int]) -> List[AttractionModel]:
        """
        根据 ID 列表获取景点信息
        
        Args:
            attraction_ids: 景点 ID 列表
            
        Returns:
            景点模型列表
        """
        if not attraction_ids:
            return []
        
        try:
            placeholders = ", ".join([f":id_{i}" for i in range(len(attraction_ids))])
            params = {f"id_{i}": attraction_id for i, attraction_id in enumerate(attraction_ids)}
            
            query = text(f"""
                SELECT 
                    a.id, a.name, a.description, a.website,
                    a.created_at, a.updated_at,
                    l.id as location_id, l.address, l.country, 
                    l.latitude, l.longitude,
                    c.id as city_id, c.name as city_name, 
                    c.country as city_country, c.description as city_description,
                    c.latitude as city_latitude, c.longitude as city_longitude
                FROM attractions a
                LEFT JOIN locations l ON a.location_id = l.id
                LEFT JOIN cities c ON a.city_id = c.id
                WHERE a.id IN ({placeholders})
            """)
            
            results = self.session.execute(query, params).fetchall()
            
            attractions = []
            for result in results:
                opening_hours = await self._get_opening_hours(result.id)
                photos = await self._get_photos(result.id)
                attraction = self._build_attraction_model(result, opening_hours, photos)
                if attraction:
                    attractions.append(attraction)
            
            return attractions
        
        except Exception as e:
            logger.error(f"批量获取景点信息失败: {e}")
            return []
    
    async def _get_opening_hours(self, attraction_id: int) -> List[OpeningHoursModel]:
        """获取景点营业时间"""
        try:
            query = text("""
                SELECT day_of_week, from_time, to_time
                FROM opening_hours
                WHERE attraction_id = :attraction_id
                ORDER BY 
                    CASE day_of_week
                        WHEN 'MONDAY' THEN 1
                        WHEN 'TUESDAY' THEN 2
                        WHEN 'WEDNESDAY' THEN 3
                        WHEN 'THURSDAY' THEN 4
                        WHEN 'FRIDAY' THEN 5
                        WHEN 'SATURDAY' THEN 6
                        WHEN 'SUNDAY' THEN 7
                    END
            """)
            
            results = self.session.execute(query, {"attraction_id": attraction_id}).fetchall()
            
            return [
                OpeningHoursModel(
                    day=result.day_of_week,
                    from_time=result.from_time,
                    to_time=result.to_time
                )
                for result in results
            ]
        
        except Exception as e:
            logger.error(f"获取营业时间失败 (景点 ID: {attraction_id}): {e}")
            return []
    
    async def _get_photos(self, attraction_id: int) -> List[str]:
        """获取景点照片"""
        try:
            query = text("""
                SELECT photo_url
                FROM photos
                WHERE attraction_id = :attraction_id
                ORDER BY id
            """)
            
            results = self.session.execute(query, {"attraction_id": attraction_id}).fetchall()
            
            return [result.photo_url for result in results if result.photo_url]
        
        except Exception as e:
            logger.error(f"获取照片失败 (景点 ID: {attraction_id}): {e}")
            return []
    
    def _build_attraction_model(
        self, 
        result: Any, 
        opening_hours: List[OpeningHoursModel], 
        photos: List[str]
    ) -> Optional[AttractionModel]:
        """构建景点模型"""
        try:
            # 构建位置模型
            location = LocationModel(
                id=result.location_id,
                address=result.address or "",
                country=result.country or "",
                latitude=float(result.latitude) if result.latitude else 0.0,
                longitude=float(result.longitude) if result.longitude else 0.0
            )
            
            # 构建城市模型
            city = CityModel(
                id=result.city_id,
                name=result.city_name or "",
                country=result.city_country or "",
                description=result.city_description,
                latitude=float(result.city_latitude) if result.city_latitude else None,
                longitude=float(result.city_longitude) if result.city_longitude else None
            )
            
            # 构建景点模型
            return AttractionModel(
                id=result.id,
                name=result.name or "",
                description=result.description or "",
                location=location,
                city=city,
                opening_hours=opening_hours,
                photos=photos,
                website=result.website,
                created_at=result.created_at,
                updated_at=result.updated_at
            )
        
        except Exception as e:
            logger.error(f"构建景点模型失败: {e}")
            return None
