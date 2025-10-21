from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from app.models.property import ResultInfo
from app.database.config import get_session
from app.models import EnquiryForm, EnquiryNL, PropertyLocation, RecommendationResponse, RequestInfo
from app.utils import mock_data, mock_map


# todo csgen
def fetchRecommendProperties(params: RequestInfo) -> List[ResultInfo]:
    pass


def multi_objective_optimization_ranking(propertyList: List[ResultInfo]) -> List[ResultInfo]:
    pass


def convert_natural_language_to_form(
        *, 
        enquiry: EnquiryNL
) -> EnquiryForm:
    pass


def save_form_to_DB(
    *,
    db: Session = Depends(get_session),
    enquiry: EnquiryForm
):
    # 生成 EnquiryEntity
    pass


def save_recommendation_to_DB(
        *,
        recommendation: List[ResultInfo]
):
    pass

