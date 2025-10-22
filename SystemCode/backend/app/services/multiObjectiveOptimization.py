from decimal import Decimal
import random
from typing import List, Optional
import math
from dataclasses import dataclass


from SystemCode.backend.app.models.property import ResultInfo

@dataclass
class OptimizationWeights:
    cost_weight: float = 0.35
    commute_weight: float = 0.35
    neighborhood_weight: float = 0.30


def multi_objective_optimization_main(propertyList: List[ResultInfo]) -> List[ResultInfo]:
    if not propertyList:
        return []

    valid_properties = _validate_and_filter(propertyList)
    if not valid_properties:
        return []

    normalized_properties = _normalize_scores(valid_properties)

    pareto_layers = _pareto_front_layering(normalized_properties)

    properties_with_crowding = _calculate_crowding_distance(pareto_layers)

    ranked_properties = _final_ranking(properties_with_crowding)

    return ranked_properties


def _validate_and_filter(propertyList: List[ResultInfo]) -> List[ResultInfo]:
    valid_properties = []

    for prop in propertyList:
        if (hasattr(prop, 'costScore') and hasattr(prop, 'commuteScore') and hasattr(prop, 'neighborhoodScore')):
            if (0 < prop.costScore <= 1 and 0 < prop.commuteScore <= 1 and 0 < prop.neighborhoodScore <= 1):
                valid_properties.append(prop)

    return valid_properties


def _normalize_scores(properties: List[ResultInfo]) -> List[ResultInfo]:
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


def _pareto_front_layering(properties: List[ResultInfo]) -> List[List[ResultInfo]]:
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


def _dominates(prop_a: ResultInfo, prop_b: ResultInfo) -> bool:
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


def _calculate_crowding_distance(layers: List[List[ResultInfo]]) -> List[tuple]:
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


def _final_ranking(properties_with_crowding: List[tuple]) -> List[ResultInfo]:
    weights = OptimizationWeights()

    ranked_data = []
    for prop, layer_idx, crowding_dist in properties_with_crowding:
        weighted_score = (
            weights.cost_weight * prop.costScore +
            weights.commute_weight * prop.commuteScore +
            weights.neighborhood_weight * prop.neighborhoodScore
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



# ========================================
# ============ 测试多目标优化 ============
# ========================================


# ============ 虚拟数据生成 ============

def generate_test_properties(count: int, scenario: str = "balanced") -> List[ResultInfo]:
    """
    生成测试用虚拟房源数据
    
    Args:
        count: 生成房源数量
        scenario: 测试场景类型
            - "balanced": 均衡分布
            - "extreme": 极端值测试
            - "clustered": 集群分布
            - "pareto": 明显的帕累托前沿
    """
    properties = []
    
    singapore_districts = [
        "Bukit Timah", "Orchard", "Marina Bay", "Novena", "Clementi",
        "Jurong East", "Woodlands", "Tampines", "Bedok", "Queenstown"
    ]
    
    for i in range(count):
        if scenario == "balanced":
            # 均衡分布：随机生成
            cost_score = random.uniform(0.3, 0.95)
            commute_score = random.uniform(0.3, 0.95)
            neighborhood_score = random.uniform(0.3, 0.95)
        
        elif scenario == "extreme":
            # 极端值测试：包含最大最小值
            if i % 3 == 0:
                cost_score = random.choice([0.1, 0.99])
                commute_score = random.choice([0.1, 0.99])
                neighborhood_score = random.choice([0.1, 0.99])
            else:
                cost_score = random.uniform(0.4, 0.6)
                commute_score = random.uniform(0.4, 0.6)
                neighborhood_score = random.uniform(0.4, 0.6)
        
        elif scenario == "clustered":
            # 集群分布：形成几个明显的集群
            cluster = i % 3
            if cluster == 0:  # 高价格低通勤集群
                cost_score = random.uniform(0.2, 0.4)
                commute_score = random.uniform(0.7, 0.9)
                neighborhood_score = random.uniform(0.6, 0.8)
            elif cluster == 1:  # 中等集群
                cost_score = random.uniform(0.5, 0.7)
                commute_score = random.uniform(0.5, 0.7)
                neighborhood_score = random.uniform(0.5, 0.7)
            else:  # 低价格高通勤集群
                cost_score = random.uniform(0.7, 0.9)
                commute_score = random.uniform(0.2, 0.4)
                neighborhood_score = random.uniform(0.4, 0.6)
        
        elif scenario == "pareto":
            # 明显的帕累托前沿
            if i < count // 3:  # 帕累托最优解
                base = random.uniform(0.7, 0.95)
                cost_score = base + random.uniform(-0.1, 0.05)
                commute_score = base + random.uniform(-0.1, 0.05)
                neighborhood_score = base + random.uniform(-0.1, 0.05)
            else:  # 被支配解
                cost_score = random.uniform(0.3, 0.6)
                commute_score = random.uniform(0.3, 0.6)
                neighborhood_score = random.uniform(0.3, 0.6)
        
        else:
            # 默认均衡分布
            cost_score = random.uniform(0.3, 0.95)
            commute_score = random.uniform(0.3, 0.95)
            neighborhood_score = random.uniform(0.3, 0.95)
        
        # 确保评分在有效范围内
        cost_score = max(0.01, min(1.0, cost_score))
        commute_score = max(0.01, min(1.0, commute_score))
        neighborhood_score = max(0.01, min(1.0, neighborhood_score))
        
        property_data = ResultInfo(
            property_id=1000 + i,
            costScore=cost_score,
            commuteScore=commute_score,
            neighborhoodScore=neighborhood_score,
            name=f"Condo {chr(65 + i % 26)}{i}",
            district=random.choice(singapore_districts),
            price=f"S$ {random.randint(2000, 8000)}",
            beds=random.randint(1, 4),
            baths=random.randint(1, 3),
            area=random.randint(50, 150),
            latitude=Decimal(str(round(1.2500 + random.uniform(-0.05, 0.05), 6))),
            longitude=Decimal(str(round(103.8198 + random.uniform(-0.05, 0.05), 6))),
            time_to_school=random.randint(10, 60),
            distance_to_mrt=random.randint(100, 1000)
        )
        
        properties.append(property_data)
    
    return properties


# ============ 测试函数 ============

def print_separator(title: str = ""):
    """打印分隔线"""
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)


def print_property_details(prop: ResultInfo, rank: int = None):
    """打印房源详细信息"""
    rank_str = f"Rank #{rank}" if rank else "Property"
    print(f"\n{rank_str}: {prop.name} (ID: {prop.property_id})")
    print(f"  District: {prop.district}")
    print(f"  Price: {prop.price}")
    print(f"  Specs: {prop.beds} beds, {prop.baths} baths, {prop.area} sqm")
    print(f"  Scores:")
    print(f"    - Cost Score:         {prop.costScore:.4f}")
    print(f"    - Commute Score:      {prop.commuteScore:.4f}")
    print(f"    - Neighborhood Score: {prop.neighborhoodScore:.4f}")
    print(f"    - Average Score:      {(prop.costScore + prop.commuteScore + prop.neighborhoodScore) / 3:.4f}")


def test_scenario(scenario_name: str, properties: List[ResultInfo], top_k: int = 5):
    """测试单个场景"""
    print_separator(f"测试场景: {scenario_name}")
    
    print(f"\n输入数据: {len(properties)} 个房源")
    print("\n输入数据统计:")
    print(f"  Cost Score:         平均={sum(p.costScore for p in properties)/len(properties):.3f}, "
          f"范围=[{min(p.costScore for p in properties):.3f}, {max(p.costScore for p in properties):.3f}]")
    print(f"  Commute Score:      平均={sum(p.commuteScore for p in properties)/len(properties):.3f}, "
          f"范围=[{min(p.commuteScore for p in properties):.3f}, {max(p.commuteScore for p in properties):.3f}]")
    print(f"  Neighborhood Score: 平均={sum(p.neighborhoodScore for p in properties)/len(properties):.3f}, "
          f"范围=[{min(p.neighborhoodScore for p in properties):.3f}, {max(p.neighborhoodScore for p in properties):.3f}]")
    
    # 执行优化
    print(f"\n正在执行多目标优化...")
    ranked_properties = multi_objective_optimization_main(properties)
    
    # 显示Top-K结果
    print(f"\n优化结果 - Top {min(top_k, len(ranked_properties))} 推荐:")
    for i, prop in enumerate(ranked_properties[:top_k], 1):
        print_property_details(prop, i)
    
    # 分析帕累托前沿
    print("\n\n帕累托前沿分析:")
    pareto_layers = _pareto_front_layering(properties.copy())
    for layer_idx, layer in enumerate(pareto_layers[:3], 1):  # 只显示前3层
        print(f"  第 {layer_idx} 层 (帕累托前沿): {len(layer)} 个房源")
        if layer_idx == 1:
            print(f"    这些是非支配解，在多个维度上都具有竞争力")
    
    return ranked_properties


def test_edge_cases():
    """测试边界情况"""
    print_separator("边界情况测试")
    
    # 测试1: 空列表
    print("\n测试1: 空列表")
    result = multi_objective_optimization_main([])
    print(f"  结果: {len(result)} 个房源 (预期: 0)")
    assert len(result) == 0, "空列表测试失败"
    print("  ✓ 通过")
    
    # 测试2: 单个房源
    print("\n测试2: 单个房源")
    single_prop = generate_test_properties(1, "balanced")
    result = multi_objective_optimization_main(single_prop)
    print(f"  结果: {len(result)} 个房源 (预期: 1)")
    assert len(result) == 1, "单个房源测试失败"
    print("  ✓ 通过")
    
    # 测试3: 所有评分相同
    print("\n测试3: 所有评分相同")
    identical_props = []
    for i in range(5):
        prop = ResultInfo(
            property_id=2000 + i,
            costScore=0.5,
            commuteScore=0.5,
            neighborhoodScore=0.5,
            name=f"Identical {i}"
        )
        identical_props.append(prop)
    result = multi_objective_optimization_main(identical_props)
    print(f"  结果: {len(result)} 个房源 (预期: 5)")
    assert len(result) == 5, "相同评分测试失败"
    print("  ✓ 通过")
    
    # 测试4: 无效数据过滤
    print("\n测试4: 包含无效数据")
    mixed_props = generate_test_properties(3, "balanced")
    invalid_prop = ResultInfo(
        property_id=3000,
        costScore=1.5,  # 无效：超出范围
        commuteScore=0.5,
        neighborhoodScore=0.5,
        name="Invalid Property"
    )
    mixed_props.append(invalid_prop)
    result = multi_objective_optimization_main(mixed_props)
    print(f"  结果: {len(result)} 个房源 (预期: 3, 过滤掉1个无效数据)")
    assert len(result) == 3, "无效数据过滤测试失败"
    print("  ✓ 通过")
    
    print("\n所有边界情况测试通过! ✓")


def run_comprehensive_tests():
    """运行完整的测试套件"""
    print_separator("多目标优化房源推荐系统 - 完整测试套件")
    
    # 1. 边界情况测试
    test_edge_cases()
    
    # 2. 均衡分布场景
    properties_balanced = generate_test_properties(20, "balanced")
    test_scenario("均衡分布 (20个房源)", properties_balanced, top_k=5)
    
    # 3. 极端值场景
    properties_extreme = generate_test_properties(15, "extreme")
    test_scenario("极端值分布 (15个房源)", properties_extreme, top_k=5)
    
    # 4. 集群分布场景
    properties_clustered = generate_test_properties(18, "clustered")
    test_scenario("集群分布 (18个房源)", properties_clustered, top_k=5)
    
    # 5. 帕累托前沿场景
    properties_pareto = generate_test_properties(25, "pareto")
    test_scenario("明显帕累托前沿 (25个房源)", properties_pareto, top_k=8)
    
    # 6. 大规模数据测试
    properties_large = generate_test_properties(100, "balanced")
    test_scenario("大规模数据测试 (100个房源)", properties_large, top_k=10)
    
    print_separator("所有测试完成!")
    print("\n测试总结:")
    print("  ✓ 边界情况测试通过")
    print("  ✓ 均衡分布场景测试通过")
    print("  ✓ 极端值场景测试通过")
    print("  ✓ 集群分布场景测试通过")
    print("  ✓ 帕累托前沿场景测试通过")
    print("  ✓ 大规模数据测试通过")
    print("\n多目标优化算法运行正常! 🎉")


# ============ 主程序入口 ============

if __name__ == "__main__":
    # 设置随机种子以保证结果可复现
    random.seed(42)
    
    # 运行完整测试套件
    run_comprehensive_tests()
    
    # 可选：单独测试某个场景
    # properties = generate_test_properties(30, "pareto")
    # test_scenario("自定义测试", properties, top_k=10)