from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class LocationModel(BaseModel):
    """位置信息模型"""
    id: Optional[int] = None
    address: str
    country: str
    latitude: float
    longitude: float


class CityModel(BaseModel):
    """城市信息模型"""
    id: Optional[int] = None
    name: str
    country: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class OpeningHoursModel(BaseModel):
    """营业时间模型"""
    day: str
    from_time: str
    to_time: str


class AttractionModel(BaseModel):
    """旅游景点模型"""
    id: Optional[int] = None
    name: str
    description: str
    location: LocationModel
    city: CityModel
    opening_hours: List[OpeningHoursModel] = []
    photos: List[str] = []
    website: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def content_for_vector(self) -> str:
        """
        生成用于向量化的文本内容
        
        Returns:
            格式化的文本内容
        """
        content_parts = [
            f"景点名称: {self.name}",
            f"城市: {self.city.name}, {self.city.country}",
            f"描述: {self.description}",
            f"地址: {self.location.address}",
        ]
        
        if self.opening_hours:
            hours_text = ", ".join([
                f"{oh.day}: {oh.from_time}-{oh.to_time}" 
                for oh in self.opening_hours
            ])
            content_parts.append(f"营业时间: {hours_text}")
        
        if self.website:
            content_parts.append(f"网站: {self.website}")
            
        return "\n".join(content_parts)


class VectorSearchRequest(BaseModel):
    """向量搜索请求模型"""
    query: str
    limit: int = 10
    score_threshold: float = 0.7
    city_filter: Optional[str] = None
    country_filter: Optional[str] = None


class VectorSearchResult(BaseModel):
    """向量搜索结果模型"""
    attraction: AttractionModel
    score: float
    
    
class AttractionIndexRequest(BaseModel):
    """景点索引请求模型"""
    attraction_ids: List[int]
    force_reindex: bool = False
