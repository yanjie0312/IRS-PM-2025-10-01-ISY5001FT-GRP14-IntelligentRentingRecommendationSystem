from typing import List
import os, sys

from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import EnquiryEntity, EnquiryForm, Property

# csgen
from app.dataservice.sql_api.api_model import RequestInfo as reqinfo, ResultInfo as resinfo
from app.dataservice.sql_api.api import fetchRecommendProperties_async


# Get recommended property list (unsorted)
async def fetchRecommendProperties(params: EnquiryForm) -> List[Property]:
    # return []
    try:
        req = reqinfo.model_validate(params.model_dump(), strict=False)
    except ValidationError as e:
        print(f"fail to convert EnquiryForm into reqinfo: {e}")
        return []

    filtered_properties = await fetchRecommendProperties_async(req)

    try:
        results = [Property.model_validate(p.model_dump(), strict=False) for p in filtered_properties]
    except ValidationError as e:
        print(f"fail to convert resinfo into Property: {e}")
        return []
    
    return results


# csgen
# async def fetchRecommendProperties(params: EnquiryForm) -> List[Property]:
#     req = reqinfo(
#         min_monthly_rent=params.min_monthly_rent,
#         max_monthly_rent=params.max_monthly_rent,
#         school_id=params.school_id,
#         max_school_limit=params.max_school_limit,
#         flat_type_preference=params.flat_type_preference,
#         max_mrt_distance=params.max_mrt_distance,
#         importance_rent=params.importance_rent,
#         importance_location=params.importance_location,
#         importance_facility=params.importance_facility
#     )
#     filtered_properties = await fetchRecommendProperties_async(req)
#     results = [resinfo(
#         property_id=p.property_id,
#         img_src=p.img_src,
#         name=p.name,
#         district=p.district,
#         price=p.price,
#         beds=p.beds,
#         baths=p.baths,
#         area=p.area,
#         build_time=p.build_time,
#         location=p.location,
#         time_to_school=p.time_to_school,
#         distance_to_mrt=p.distance_to_mrt,
#         latitude=p.latitude,
#         longitude=p.longitude,
#         public_facilities=p.public_facilities,
#         facility_type=p.facility_type,
#         costScore=p.costScore,
#         commuteScore=p.commuteScore,
#         neighborhoodScore=p.neighborhoodScore
#     ) for p in filtered_properties]
    
#     print(f'返回房源数量：len(results)')
#     return results

# if __name__ == "__main__":
#     request_params = EnquiryForm(
#         min_monthly_rent=1000,
#         max_monthly_rent=3000,
#         school_id=3,
#         target_district_id=3,
#         max_school_limit=60,
#         flat_type_preference=["HDB", "Condo", "Apartment"],
#         max_mrt_distance=1000,
#         importance_rent=5,
#         importance_location=4,
#         importance_facility=3
#     )
#     import asyncio
#     asyncio.run(fetchRecommendProperties(request_params))


# todo qyl 确认是否会阻塞I/O需要async？
# Sort recommended property list
def multi_objective_optimization_ranking(
        *,
        enquiry: EnquiryForm,
        propertyList: List[Property]
) -> List[Property]:

    if not propertyList:
        return []

    valid_properties = _validate_and_filter(propertyList)
    if not valid_properties:
        return []

    normalized_properties = _normalize_scores(valid_properties)

    pareto_layers = _pareto_front_layering(normalized_properties)

    properties_with_crowding = _calculate_crowding_distance(pareto_layers)

    ranked_properties = _final_ranking(properties_with_crowding, enquiry)

    return ranked_properties


def _validate_and_filter(propertyList: List[Property]) -> List[Property]:
    valid_properties = []

    for prop in propertyList:
        if (hasattr(prop, 'costScore') and hasattr(prop, 'commuteScore') and hasattr(prop, 'neighborhoodScore')):
            if (0 < prop.costScore <= 1 and 0 < prop.commuteScore <= 1 and 0 < prop.neighborhoodScore <= 1):
                valid_properties.append(prop)

    return valid_properties


def _normalize_scores(properties: List[Property]) -> List[Property]:
    if len(properties) == 1:
        return properties

    cost_scores = [p.costScore for p in properties]
    commute_scores = [p.commuteScore for p in properties]
    neighborhood_scores = [p.neighborhoodScore for p in properties]

    cost_min, cost_max = min(cost_scores), max(cost_scores)
    commute_min, commute_max = min(commute_scores), max(commute_scores)
    neighborhood_min, neighborhood_max = min(neighborhood_scores), max(neighborhood_scores)

    for prop in properties:
        prop.costScore = _safe_normalize(prop.costScore, cost_min, cost_max)
        prop.commuteScore = _safe_normalize(prop.commuteScore, commute_min, commute_max)
        prop.neighborhoodScore = _safe_normalize(prop.neighborhoodScore, neighborhood_min, neighborhood_max)

    return properties


def _safe_normalize(value: float, min_val: float, max_val: float) -> float:
    if max_val - min_val < 1e-6:
        return 1.0
    return (value - min_val) / (max_val - min_val)


def _pareto_front_layering(properties: List[Property]) -> List[List[Property]]:
    layers = []
    remaining = properties.copy()

    while remaining:
        current_layer = []
        dominated = []

        for prop in remaining:
            is_dominated = False

            for layer_prop in current_layer:
                if _dominates(layer_prop, prop):
                    is_dominated = True
                    break

            if not is_dominated:
                new_layer = []
                for layer_prop in current_layer:
                    if not _dominates(prop, layer_prop):
                        new_layer.append(layer_prop)
                    else:
                        dominated.append(layer_prop)

                new_layer.append(prop)
                current_layer = new_layer
            else:
                dominated.append(prop)

        layers.append(current_layer)
        remaining = dominated

    return layers


def _dominates(prop_a: Property, prop_b: Property) -> bool:
    not_worse = (
        prop_a.costScore >= prop_b.costScore and
        prop_a.commuteScore >= prop_b.commuteScore and
        prop_a.neighborhoodScore >= prop_b.neighborhoodScore
    )

    strictly_better = (
        prop_a.costScore > prop_b.costScore or
        prop_a.commuteScore > prop_b.commuteScore or
        prop_a.neighborhoodScore > prop_b.neighborhoodScore
    )

    return not_worse and strictly_better


def _calculate_crowding_distance(layers: List[List[Property]]) -> List[tuple]:
    properties_with_crowding = []

    for layer_idx, layer in enumerate(layers):
        if len(layer) <= 2:
            for prop in layer:
                properties_with_crowding.append((prop, layer_idx, float('inf')))
            continue

        crowding_distances = {id(prop): 0.0 for prop in layer}

        for objective in ['costScore', 'commuteScore', 'neighborhoodScore']:
            sorted_layer = sorted(layer, key=lambda p: getattr(p, objective), reverse=True)

            crowding_distances[id(sorted_layer[0])] = float('inf')
            crowding_distances[id(sorted_layer[-1])] = float('inf')

            obj_range = (getattr(sorted_layer[0], objective) - getattr(sorted_layer[-1], objective))

            if obj_range < 1e-6:
                continue

            for i in range(1, len(sorted_layer) - 1):
                if crowding_distances[id(sorted_layer[i])] != float('inf'):
                    distance = (getattr(sorted_layer[i - 1], objective) - getattr(sorted_layer[i + 1], objective)) / obj_range
                    crowding_distances[id(sorted_layer[i])] += distance

        for prop in layer:
            properties_with_crowding.append((prop, layer_idx, crowding_distances[id(prop)]))

    return properties_with_crowding


def _final_ranking(properties_with_crowding: List[tuple], enquiry: EnquiryForm) -> List[Property]:

    ranked_data = []
    for prop, layer_idx, crowding_dist in properties_with_crowding:
        weighted_score = (
            enquiry.importance_rent * prop.costScore +
            enquiry.importance_location * prop.commuteScore +
            enquiry.importance_facility * prop.neighborhoodScore
        )

        ranked_data.append({
            'property': prop,
            'layer': layer_idx,
            'crowding': crowding_dist,
            'weighted_score': weighted_score
        })

    ranked_data.sort(
        key=lambda x: (
            x['layer'],
            -x['crowding'] if x['crowding'] != float('inf') else float('-inf'),
            -x['weighted_score']
        )
    )

    return [item['property'] for item in ranked_data]
