from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import func
import asyncio
from math import isnan
import sys, os
from api_model import RequestInfo, ResultInfo
from SystemCode.db.model import HousingData, District, University, CommuteTime, Park, HawkerCenter, Supermarket, Library, ImageRecord

current_dir = os.path.dirname(__file__) 
project_root = os.path.abspath(os.path.join(current_dir, '..', '..')) 
sys.path.insert(0, project_root) 
from SystemCode.db.envconfig import get_database_url

DATABASE_URL = get_database_url()
async_engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

async def query_housing_data_async(request: RequestInfo) -> list[HousingData]:
    '''根据 RequestInfo 查询符合条件的房源'''

    # 基础查询
    stmt = (
        select(HousingData)
        .join(CommuteTime, HousingData.id == CommuteTime.housing_id)
        .where(
            CommuteTime.university_id == request.school_id,
            HousingData.price >= request.min_monthly_rent,
            HousingData.price <= request.max_monthly_rent,
        )
    )

    # 动态条件
    if request.target_district_id is not None:
        stmt = stmt.where(HousingData.district_id == request.target_district_id)

    if request.max_school_limit is not None:
        stmt = stmt.where(CommuteTime.commute_time_minutes <= request.max_school_limit)

    if request.flat_type_preference:
        stmt = stmt.where(HousingData.type.in_(request.flat_type_preference))

    if request.max_mrt_distance is not None:
        stmt = stmt.where(HousingData.distance_to_mrt <= request.max_mrt_distance)

    # 异步执行查询
    async with AsyncSessionLocal() as session:
        result = await session.execute(stmt)
        housings = result.scalars().all()

        # 若结果少于2条，补充通勤时间最短的10条（不重复）
        if len(housings) < 2:
            existing_ids = [h.id for h in housings]

            fallback_stmt = (
                select(HousingData)
                .join(CommuteTime, HousingData.id == CommuteTime.housing_id)
                .where(
                    CommuteTime.university_id == request.school_id,
                    HousingData.id.notin_(existing_ids),
                )
                .order_by(CommuteTime.commute_time_minutes.asc())
                .limit(10-len(housings))
            )

            fallback_result = await session.execute(fallback_stmt)
            fallback_housings = fallback_result.scalars().all()
            housings.extend(fallback_housings)

        return result.scalars().all()

async def filter_housing_async(housings: list[HousingData], request: RequestInfo):
    '''根据 RequestInfo 对所有房源进行过滤并计算评分'''
    results = []
    
    async with AsyncSessionLocal() as session:
        raw_data = []
        radius_m = 2000

        for housing in housings:
            district = await session.get(District, housing.district_id)
            district_safety_score = district.safety_score if district else 0.0

            # 房源图片
            img = await session.execute(
                select(ImageRecord.public_url).where(ImageRecord.id == housing.id)
            )
            img_url = img.scalar()

            # 通勤时间
            commute_stmt = select(CommuteTime.commute_time_minutes).where(
                CommuteTime.housing_id == housing.id,
                CommuteTime.university_id == request.school_id
            )
            commute_time = (await session.scalar(commute_stmt)) or None

            # 并发查询最近的公共设施
            async def nearest_facility(facility_closest, label: str):
                stmt = (
                    select(
                        facility_closest.name,
                        func.ST_Distance(facility_closest.geog, housing.geog).label("distance")
                    )
                    .where(func.ST_DWithin(facility_closest.geog, housing.geog, radius_m))
                    .order_by("distance")
                    .limit(1)
                )
                row = await session.execute(stmt)
                result = row.first()
                if result:
                    return {
                        "name": result[0],
                        "distance": round(float(result[1]), 1)
                    }
                return None

            park_task = nearest_facility(Park, "Park")
            hawker_task = nearest_facility(HawkerCenter, "Hawker Center")
            library_task = nearest_facility(Library, "Library")
            supermarket_task = nearest_facility(Supermarket, "Supermarket")

            nearest_facilities = [
                res for res in await asyncio.gather(
                    park_task, hawker_task, library_task, supermarket_task
                ) if res
            ]

            # 根据设施数量评分
            facility_score = len(nearest_facilities)

            # 原始数据
            raw_data.append({
                "housing": housing,
                "img": img_url,
                "price": housing.price or 0,
                "commute": commute_time or 9999,
                "facility": facility_score,
                "safety": district_safety_score or 0,
                "district": district.district_name,
                "public_facilities": nearest_facilities
            })

        # === 归一化函数 ===
        def normalize(values, reverse=False):
            vals = [v for v in values if v is not None]
            if not vals:
                return [0 for _ in values]
            min_v, max_v = min(vals), max(vals)
            if max_v == min_v:
                return [1 for _ in values]
            return [
                (max_v - v) / (max_v - min_v) if reverse else (v - min_v) / (max_v - min_v)
                for v in values
            ]

        price_norm = normalize([x["price"] for x in raw_data], reverse=True) # 价格越低越好
        commute_norm = normalize([x["commute"] for x in raw_data], reverse=True) # 通勤时间越短越好
        facility_norm = normalize([x["facility"] for x in raw_data])
        safety_norm = normalize([x["safety"] for x in raw_data])
        neighbour_norm = normalize([(facility_norm[i] * 2 + safety_norm[i]) for i in range(len(raw_data))]) # 邻里综合评分

        for i, data in enumerate(raw_data):
            housing = data["housing"]
            total_score = price_norm[i] + commute_norm[i] + neighbour_norm[i]

            resultInfo = ResultInfo(
                property_id=housing.id,
                img_src=data['img'],
                name=housing.name,
                district=data['district'],
                price=str(housing.price),
                beds=housing.beds_num,
                baths=housing.baths_num,
                area=housing.area_sqft,
                build_time=str(housing.build_time) if housing.build_time else "",
                location=housing.location,
                time_to_school=int(data["commute"]),
                distance_to_mrt=int(housing.distance_to_mrt) if housing.distance_to_mrt else None,
                latitude=housing.latitude,
                longitude=housing.longitude,
                public_facilities=data["public_facilities"],
                facility_type=housing.type,
                costScore=round(price_norm[i], 2),
                commuteScore=round(commute_norm[i], 2),
                neighborhoodScore=round(neighbour_norm[i], 2)
            )
            results.append((resultInfo, total_score))

    # 排序取前 50
    results_sorted = sorted(results, key=lambda pair: pair[1], reverse=True)[:50]
    return [pair[0] for pair in results_sorted]

