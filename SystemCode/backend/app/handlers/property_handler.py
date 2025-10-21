import json
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from app.database.config import get_session
from app.models import EnquiryForm, EnquiryNL, PropertyLocation, RecommendationResponse, RequestInfo
from app.utils import mock_data, mock_map
from app.services import recommendation_service as rec_service
from app.services import map_service as map_service


def submit_form_handler(
    *,
    db: Session = Depends(get_session),
    enquiry: EnquiryForm
) -> RecommendationResponse:
    
    # 表单存数据库
    rec_service.save_form_to_DB(db=db, enquiry=enquiry)

    # 调用模型拿TopN
    enquiry_dict = enquiry.model_dump()
    requestInfo = RequestInfo.model_validate(enquiry_dict)
    resultInfo = rec_service.fetchRecommendProperties(requestInfo)

    # 多目标优化
    ranked_properties = rec_service.multi_objective_optimization_ranking(resultInfo)

    # 存储最终推荐结果到数据库
    rec_service.save_recommendation_to_DB(recommendation=ranked_properties)

    return RecommendationResponse(properties=ranked_properties)


def submit_description_handler(
    *,
    db: Session = Depends(get_session),
    enquiry: EnquiryNL
) -> RecommendationResponse:
    
    # 自然语言转成表单
    enquiry_form = rec_service.convert_natural_language_to_form(enquiry=enquiry)

    # todo 补充form信息不全返回错误逻辑

    return submit_form_handler(db=db, enquiry=enquiry_form)


def map_handler(
    *,
    location: PropertyLocation   
) -> HTMLResponse:
    return map_service.fetch_map_page(location)