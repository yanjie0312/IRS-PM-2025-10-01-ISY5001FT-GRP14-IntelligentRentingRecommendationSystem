from fastapi import APIRouter, Depends, status
from fastapi.responses import HTMLResponse
from sqlmodel.ext.asyncio.session import AsyncSession
import openai

from app.dependencies import get_async_session, get_async_openai_client
from app.dependencies import get_async_openai_client
from app.models import EnquiryForm, EnquiryNL, PropertyLocation, RecommendationResponse
from app.utils import mock_data, mock_map
from app.handlers import property_handler


router = APIRouter(prefix="/api/v1/properties", tags=["properties"])

MOCK_MODE = False


# 提交问卷表单
@router.post("/submit-form", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def submit_form(
    *,
    db: AsyncSession = Depends(get_async_session),
    client: openai.AsyncOpenAI = Depends(get_async_openai_client),
    enquiry: EnquiryForm
):
    if MOCK_MODE:
        return mock_data.create_mock_response()
    else:
        return await property_handler.submit_form_handler(db=db, client=client, enquiry=enquiry)


# 提交文字表单
@router.post("/submit-description", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def submit_description(
    *,
    db: AsyncSession = Depends(get_async_session),
    client: openai.AsyncOpenAI = Depends(get_async_openai_client),
    enquiry: EnquiryNL
):
    if MOCK_MODE:
        return mock_data.create_mock_response()
    else:
        return await property_handler.submit_description_handler(db=db, client=client, enquiry=enquiry)


# 获取无表单房源推荐列表
@router.get("/recommendation-no-submit", response_model=RecommendationResponse, status_code=status.HTTP_200_OK)
async def recommendation_no_submit(
    *,
    db: AsyncSession = Depends(get_async_session)
):
    return RecommendationResponse(properties=[])


# 获取房源地图
@router.post("/map", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def map(
    *,
    location: PropertyLocation
):
    if MOCK_MODE:
        return HTMLResponse(content=mock_map.create_mock_response())
    else:
        return await property_handler.map_handler(location=location) 
