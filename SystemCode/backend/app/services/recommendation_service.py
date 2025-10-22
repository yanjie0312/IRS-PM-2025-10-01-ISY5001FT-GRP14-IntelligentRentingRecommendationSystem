from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.property import ResultInfo
from app.models import EnquiryForm, EnquiryEntity, RequestInfo


# todo csgen
async def fetchRecommendProperties(params: RequestInfo) -> List[ResultInfo]:
    return []


async def multi_objective_optimization_ranking(propertyList: List[ResultInfo]) -> List[ResultInfo]:
    return []


async def save_form_to_DB(
    *,
    db: AsyncSession,
    enquiry: EnquiryForm
):
    # 暂不入库
    # enquiry_entity = EnquiryEntity.model_validate(enquiry)

    # db.add(enquiry_entity)
    # await db.commit()
    # await db.refresh(enquiry_entity)
    # print(f"Saved enquiry {enquiry_entity.eid} to database.")
    pass


async def save_recommendation_to_DB(
    *,
    db: AsyncSession,
    recommendation: List[ResultInfo]
):
    # todo qyl 待实现
    pass
