"""案例 3：按实际年限与最低要求计算经验分。"""


def experience_score(actual_years: float, required_years: float) -> float:
    if actual_years < 0 or required_years < 0:
        raise ValueError("经验年限不能为负数")
    if required_years == 0:
        return 100.0
    return min(actual_years / required_years, 1.0) * 100


for actual in [0.5, 1, 2, 3]:
    print(
        f"实际经验={actual:g} 年，岗位要求=2 年，"
        f"经验分={experience_score(actual, 2):.2f}"
    )
