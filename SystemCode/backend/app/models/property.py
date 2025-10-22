from decimal import Decimal
from typing import List, Optional

from sqlmodel import Field, SQLModel


class PropertyBase(SQLModel):
    property_id: int  
    latitude: Optional[Decimal] = Field(default=None)
    longitude: Optional[Decimal] = Field(default=None)


class PropertyCore(PropertyBase):
    img_src: Optional[str] = Field(default=None, max_length=500)
    name: Optional[str] = Field(default=None, max_length=100)
    district: Optional[str] = Field(default=None, max_length=100)
    price: Optional[str] = Field(default=None, max_length=50)
    beds: Optional[int] = Field(default=None)
    baths: Optional[int] = Field(default=None)
    area: Optional[int] = Field(default=None)
    build_time: Optional[str] = Field(default=None, max_length=50)
    location: Optional[str] = Field(default=None, max_length=100)
    time_to_school: Optional[int] = Field(default=None)
    distance_to_mrt: Optional[int] = Field(default=None)
    public_facilities: Optional[dict] = Field(default=None)
    facility_type: Optional[str] = Field(default=None, max_length=50)


# 返回给前端房源模型
class PropertyRecommand(PropertyCore):
    recommend_reason: Optional[str] = Field(default=None, max_length=500)


# 算法返回房源模型
class ResultInfo(PropertyRecommand):
    costScore: float # range(0, 1]
    commuteScore: float # range(0, 1]
    neighborhoodScore: float # range(0, 1]


# 请求地图模型
class PropertyLocation(PropertyBase):
    pass