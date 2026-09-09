"""案例 8：比较不同岗位场景下的权重方案。"""


def calculate(scores: dict[str, float], weights: dict[str, float]) -> float:
    if set(scores) != set(weights):
        raise ValueError("评分项与权重项必须完全一致")
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError("权重之和必须等于 1")
    return sum(scores[name] * weights[name] for name in scores)


candidate = {
    "skill": 70,
    "semantic": 90,
    "education": 100,
    "experience": 60,
    "city": 100,
}

general_weights = {
    "skill": 0.35,
    "semantic": 0.30,
    "education": 0.15,
    "experience": 0.15,
    "city": 0.05,
}
technical_weights = {
    "skill": 0.45,
    "semantic": 0.30,
    "education": 0.10,
    "experience": 0.10,
    "city": 0.05,
}

print(f"通用岗位权重得分：{calculate(candidate, general_weights):.2f}")
print(f"技术岗位权重得分：{calculate(candidate, technical_weights):.2f}")
