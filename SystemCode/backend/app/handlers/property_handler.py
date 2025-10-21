import openai
from fastapi import status, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlmodel import Session

from app.models import EnquiryForm, EnquiryNL, PropertyLocation, RecommendationResponse, RequestInfo
from app.services import recommendation_service as rec_service
from app.services import map_service as map_service
from app.llm import service as llm_service


def submit_form_handler(
    *,
    db: Session,
    enquiry: EnquiryForm
) -> RecommendationResponse:
    
    # temp
    print(enquiry.model_dump_json(indent=2))

    # save to db
    rec_service.save_form_to_DB(db=db, enquiry=enquiry)

    # get TopN recommendation
    enquiry_dict = enquiry.model_dump()
    requestInfo = RequestInfo.model_validate(enquiry_dict)
    resultInfo = rec_service.fetchRecommendProperties(requestInfo)

    # multi-objective optimization ranking
    ranked_properties = rec_service.multi_objective_optimization_ranking(resultInfo)

    # save recommendation result
    rec_service.save_recommendation_to_DB(recommendation=ranked_properties)

    return RecommendationResponse(properties=ranked_properties)


def submit_description_handler(
    *,
    db: Session,
    client: openai.OpenAI,
    enquiry: EnquiryNL,
) -> RecommendationResponse:

    # natural language -> dict
    extracted_dict = llm_service.convert_natural_language_to_form(enquiry=enquiry, client=client)


    # check valid
    if not checkValid(extracted_dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing necessary information"
        )
    
    # create form
    try:
        enquiry_form = EnquiryForm.model_validate(extracted_dict)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error validating extracted preferences from LLM: {e}"
        )

    print('llm success!')
    return submit_form_handler(db=db, enquiry=enquiry_form)


def checkValid(extracted_dict: dict) -> bool:
    required_fields = ['min_monthly_rent', 'max_monthly_rent', 'school_id']
    for field in required_fields:
        if (field not in extracted_dict) or (extracted_dict.get(field) is None):
            return False
    return True


def map_handler(
    *,
    location: PropertyLocation   
) -> HTMLResponse:
    return map_service.fetch_map_page(location)