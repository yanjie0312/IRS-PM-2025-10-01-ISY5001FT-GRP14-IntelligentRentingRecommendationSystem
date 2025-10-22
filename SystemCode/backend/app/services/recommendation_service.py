from typing import List
import os, sys

from sqlmodel.ext.asyncio.session import AsyncSession
from app.services.multiObjectiveOptimization import multi_objective_optimization_main
from app.models.property import ResultInfo
from app.models import EnquiryForm, EnquiryEntity, RequestInfo
# from dataservice.sql_api.api_model import RequestInfo as reqinfo, ResultInfo as resinfo
# from dataservice.sql_api.api import fetchRecommendProperties_async


async def fetchRecommendProperties(params: RequestInfo) -> List[ResultInfo]:
    # todo qyl 临时
    return []
    req = reqinfo(
        min_monthly_rent=params.min_monthly_rent,
        max_monthly_rent=params.max_monthly_rent,
        school_id=params.school_id,
        max_school_limit=params.max_school_limit,
        flat_type_preference=params.flat_type_preference,
        max_mrt_distance=params.max_mrt_distance,
        importance_rent=params.importance_rent,
        importance_location=params.importance_location,
        importance_facility=params.importance_facility
    )
    filtered_properties = await fetchRecommendProperties_async(req)
    results = [resinfo(
        property_id=p.property_id,
        img_src=p.img_src,
        name=p.name,
        district=p.district,
        price=p.price,
        beds=p.beds,
        baths=p.baths,
        area=p.area,
        build_time=p.build_time,
        location=p.location,
        time_to_school=p.time_to_school,
        distance_to_mrt=p.distance_to_mrt,
        latitude=p.latitude,
        longitude=p.longitude,
        public_facilities=p.public_facilities,
        facility_type=p.facility_type,
        costScore=p.costScore,
        commuteScore=p.commuteScore,
        neighborhoodScore=p.neighborhoodScore
    ) for p in filtered_properties]
    
    print(f'返回房源数量：len(results)')
    return results


def multi_objective_optimization_ranking(propertyList: List[ResultInfo]) -> List[ResultInfo]:
    return [multi_objective_optimization_main(propertyList)]


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
    # todo qyl
    pass


if __name__ == "__main__":
    request_params = RequestInfo(
        min_monthly_rent=1000,
        max_monthly_rent=3000,
        school_id=3,
        target_district_id=3,
        max_school_limit=60,
        flat_type_preference=["HDB", "Condo", "Apartment"],
        max_mrt_distance=1000,
        importance_rent=5,
        importance_location=4,
        importance_facility=3
    )
    import asyncio
    asyncio.run(fetchRecommendProperties(request_params))

