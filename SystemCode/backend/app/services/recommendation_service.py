from typing import List

from SystemCode.backend.app.services.multiObjectiveOptimization import multi_objective_optimization_main
from app.models.property import ResultInfo
from app.models import EnquiryForm, RequestInfo


# todo csgen
def fetchRecommendProperties(params: RequestInfo) -> List[ResultInfo]:
    return []


def multi_objective_optimization_ranking(propertyList: List[ResultInfo]) -> List[ResultInfo]:
    return [multi_objective_optimization_main(propertyList)]


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





