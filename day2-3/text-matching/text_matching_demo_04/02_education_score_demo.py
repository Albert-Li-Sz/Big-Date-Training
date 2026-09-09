"""案例 2：学历要求评分。"""


EDUCATION_LEVEL = {
    "不限": 0,
    "中专": 1,
    "高中": 1,
    "大专": 2,
    "本科": 3,
    "硕士": 4,
    "博士": 5,
}


def education_score(candidate: str, required: str) -> float:
    """达到岗位学历要求得满分，否则按等级差距递减。"""
    if candidate not in EDUCATION_LEVEL or required not in EDUCATION_LEVEL:
        raise ValueError("学历必须来自预定义等级")
    gap = EDUCATION_LEVEL[required] - EDUCATION_LEVEL[candidate]
    if gap <= 0:
        return 100.0
    return max(0.0, 100.0 - gap * 35.0)


for candidate in ["大专", "本科", "硕士"]:
    print(
        f"候选人学历={candidate}，岗位要求=本科，"
        f"学历分={education_score(candidate, '本科'):.2f}"
    )
