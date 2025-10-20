from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from app.database.config import get_session
from app.models import EnquiryForm, EnquiryNL, PropertyLocation, RecommendationResponse
from app.utils import mock_data

router = APIRouter(prefix="/api/v1/properties", tags=["properties"])

MOCK_MODE = True


# 提交问卷表单
@router.post("/submit-form", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
def submit_form(
    *,
    db: Session = Depends(get_session),
    enquiry: EnquiryForm
):
    if MOCK_MODE:
        return mock_data.create_mock_response()
    else:
        pass


# 提交文字表单
@router.post("/submit-description", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
def submit_description(
    *,
    db: Session = Depends(get_session),
    enquiry: EnquiryNL
):
    if MOCK_MODE:
        return mock_data.create_mock_response()
    else:
        pass


# 获取无表单房源推荐列表
@router.get("/recommendation-no-submit", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
def recommendation_no_submit(
    *,
    db: Session = Depends(get_session),
):
    if MOCK_MODE:
        return mock_data.create_mock_response()
    else:
        pass


# 获取房源地图
@router.get("/map", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
def map(
    *,
    db: Session = Depends(get_session),
    location: PropertyLocation
):
    if MOCK_MODE:
        return mock_data.create_mock_response()
    else:
        pass 

