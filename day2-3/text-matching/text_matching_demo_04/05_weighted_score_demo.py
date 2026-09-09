"""案例 5：把技能、语义、学历、经验和城市合成为总分。"""


DEFAULT_WEIGHTS = {
    "skill": 0.35,
    "semantic": 0.30,
    "education": 0.15,
    "experience": 0.15,
    "city": 0.05,
}


def weighted_score(scores: dict[str, float], weights: dict[str, float]) -> float:
    missing = set(weights) - set(scores)
    if missing:
        raise ValueError(f"缺少评分项：{sorted(missing)}")
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError("权重之和必须等于 1")
    return sum(scores[name] * weight for name, weight in weights.items())


scores = {
    "skill": 75,
    "semantic": 81,
    "education": 100,
    "experience": 60,
    "city": 100,
}

print("各维度分：", scores)
print(f"综合匹配分：{weighted_score(scores, DEFAULT_WEIGHTS):.2f}")
