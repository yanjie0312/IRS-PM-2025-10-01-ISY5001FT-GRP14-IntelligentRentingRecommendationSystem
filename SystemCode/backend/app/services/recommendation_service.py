from typing import List

from app.models.property import ResultInfo
from app.models import EnquiryForm, RequestInfo


# todo csgen
def fetchRecommendProperties(params: RequestInfo) -> List[ResultInfo]:
    return []


def multi_objective_optimization_ranking(propertyList: List[ResultInfo]) -> List[ResultInfo]:
    return []


def save_form_to_DB(
    *,
    db,
    enquiry: EnquiryForm
):
    # 生成 EnquiryEntity
    pass


def save_recommendation_to_DB(
        *,
        recommendation: List[ResultInfo]
):
    pass

