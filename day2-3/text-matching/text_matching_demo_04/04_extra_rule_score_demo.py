"""案例 4：城市、证书和薪资等额外规则评分。"""


def exact_or_unlimited_score(actual: str, expected: str) -> float:
    if not expected or expected in {"不限", "无"}:
        return 100.0
    return 100.0 if actual == expected else 0.0


def certificate_score(owned: set[str], preferred: set[str]) -> float:
    if not preferred:
        return 100.0
    return len(owned & preferred) / len(preferred) * 100


def salary_score(expected_salary: float, offered_salary: float) -> float:
    """期望为 0 表示不设门槛；岗位薪资不足时按比例计分。"""
    if expected_salary < 0 or offered_salary < 0:
        raise ValueError("薪资不能为负数")
    if expected_salary == 0:
        return 100.0
    return min(offered_salary / expected_salary, 1.0) * 100


print(f"城市分：{exact_or_unlimited_score('南昌', '南昌'):.2f}")
print(f"证书分：{certificate_score({'英语四级', '计算机二级'}, {'英语四级'}):.2f}")
print(f"薪资分：{salary_score(5500, 5000):.2f}")
print(f"无薪资门槛时：{salary_score(0, 5000):.2f}")
