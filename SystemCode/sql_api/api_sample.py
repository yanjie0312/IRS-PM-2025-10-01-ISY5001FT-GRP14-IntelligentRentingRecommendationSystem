from api_model import RequestInfo, ResultInfo
from api import fetchRecommendProperties, fetchRecommendProperties_async
import asyncio

if __name__ == "__main__":
    # 示例请求参数
    request_params = RequestInfo(
        min_monthly_rent=1000,
        max_monthly_rent=3000,
        school_id=3,
        # target_district_id=3,
        max_school_limit=60,
        flat_type_preference=["HDB", "Condo", "Apartment"],
        max_mrt_distance=1000,
        importance_rent=5,
        importance_location=4,
        importance_facility=3
    )

    # 异步调用示例
    # # 获取过滤房源
    # async def main():
    #     filtered_properties = await fetchRecommendProperties_async(request_params)
    #     print(f'找到{len(filtered_properties)}个房源。')

    #     # 返回结果
    #     for property in filtered_properties:
    #         print(property.model_dump_json())
    # asyncio.run(main())

    # 同步调用示例
    filtered_properties = fetchRecommendProperties(request_params)
    print(f'找到{len(filtered_properties)}个房源。')

    # 返回结果
    for property in filtered_properties:
        print(property.model_dump_json())