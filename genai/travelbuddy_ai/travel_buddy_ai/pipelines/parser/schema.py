from typing import List, Optional
from pydantic import BaseModel

class ParsedQuery(BaseModel):
    raw: str                         # 原始输入
    days: Optional[int] = None       # 旅行天数
    start_city: Optional[str] = None
    end_city: Optional[str] = None
    must_visit: List[str] = []       # 必去景点
    preferences: List[str] = []      # 偏好标签（budget、culture…）
