from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import ARRAY, JSON, Column, DateTime, String, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .recommendation import Recommendation


class EnquiryBase(SQLModel):
    min_monthly_rent: int
    max_monthly_rent: int
    school_id: int
    target_district_id: Optional[int] = Field(default=None)
    max_school_limit: Optional[int] = Field(default=None)
    flat_type_preference: Optional[List[str]] = Field(default=None)
    max_mrt_distance: Optional[int] = Field(default=None)
    importance_rent: int = Field(default=3)
    importance_location: int = Field(default=3)
    importance_facility: int = Field(default=3)
    

class EnquiryCore(EnquiryBase):
    device_id: Optional[str] = Field(default=None, max_length=100, index=True)


# 前端请求问卷模型
class EnquiryForm(EnquiryCore):
    pass


# 前端请求自然语言段落模型，处理时要先转换成 EnquiryForm
class EnquiryNL(SQLModel):
    device_id: Optional[str] = Field(default=None, max_length=100, index=True)
    requirement_description: Optional[str] = Field(default=None, max_length=500)


# 从数据苦查询返给前端的模型，暂时没用到
class EnquiryRead(EnquiryCore):
    eid: int
    create_time: datetime


# 存到数据库的模型
class EnquiryEntity(EnquiryCore, table=True):
    __tablename__ = "enquiries"

    # extra
    eid: Optional[int] = Field(default=None, primary_key=True)
    create_time: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )

    # cover
    flat_type_preference: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))

    # DB relation
    recommendation: Optional["Recommendation"] = Relationship(back_populates="enquiry")


# 请求算法推荐模型
class RequestInfo(EnquiryBase):
    pass

