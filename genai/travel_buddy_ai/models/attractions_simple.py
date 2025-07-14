from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SimpleAttractionModel(BaseModel):
    """Simplified tourism attraction model - for data import"""
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
        """Generate text content for vectorization"""
        content_parts = [
            f"Attraction name: {self.name}",
            f"City: {self.city_name}, {self.country}",
            f"Description: {self.description}",
            f"Address: {self.address}",
        ]
        
        if self.website:
            content_parts.append(f"Website: {self.website}")
            
        return "\n".join(content_parts)
    
    def to_metadata(self) -> dict:
        """Generate metadata"""
        return {
            "id": str(self.id),
            "name": self.name,
            "city": self.city_name,
            "country": self.country,
            "latitude": self.latitude or "0.0",
            "longitude": self.longitude or "0.0",
            "type": "attraction"
        }
