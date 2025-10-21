from api_model import RequestInfo, ResultInfo
from func import query_housing_data_async, filter_housing_async
import asyncio

async def fetchRecommendProperties_async(params: RequestInfo) -> list[ResultInfo]:
    '''异步算法接口，根据请求参数返回初步过滤结果及信息'''
    housings = await query_housing_data_async(params)
    results = await filter_housing_async(housings, params)
    return results

def fetchRecommendProperties(params: RequestInfo) -> list[ResultInfo]:
    '''
    同步包装版本，自动检测当前是否存在事件循环；
    如果在异步上下文中，则通过 loop.run_until_complete
    '''
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # 已经在异步环境中
        coro = fetchRecommendProperties_async(params)
        return asyncio.ensure_future(coro)  # 返回一个 Future
    else:
        # 在同步环境中
        return asyncio.run(fetchRecommendProperties_async(params))