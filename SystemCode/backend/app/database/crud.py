from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import EnquiryForm, EnquiryEntity, Property

async def save_form_to_DB(
    *,
    db: AsyncSession,
    enquiry: EnquiryForm
):
    # 暂不入库
    return
    enquiry_entity = EnquiryEntity.model_validate(enquiry)

    db.add(enquiry_entity)
    await db.commit()
    await db.refresh(enquiry_entity)
    print(f"Saved enquiry {enquiry_entity.eid} to database.")
    


async def save_recommendation_to_DB(
    *,
    db: AsyncSession,
    recommendation: List[Property]
):
    # todo qyl
    pass