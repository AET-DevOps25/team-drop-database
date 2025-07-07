from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SimpleAttractionModel(BaseModel):
    """简化的旅游景点模型 - 用于数据导入"""
    id: int
    name: str
    description: str
    city_name: str
    country: str
    address: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    website: Optional[str] = None
    
    def to_vector_content(self) -> str:
        """生成用于向量化的文本内容"""
        content_parts = [
            f"景点名称: {self.name}",
            f"城市: {self.city_name}, {self.country}",
            f"描述: {self.description}",
            f"地址: {self.address}",
        ]
        
        if self.website:
            content_parts.append(f"网站: {self.website}")
            
        return "\n".join(content_parts)
    
    def to_metadata(self) -> dict:
        """生成元数据"""
        return {
            "id": str(self.id),
            "name": self.name,
            "city": self.city_name,
            "country": self.country,
            "latitude": self.latitude or "0.0",
            "longitude": self.longitude or "0.0",
            "type": "attraction"
        }
