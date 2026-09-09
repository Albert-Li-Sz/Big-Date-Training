"""案例 6：把数值评分转成容易理解的推荐理由。"""


def build_reason(
    matched: set[str],
    missing: set[str],
    education_ok: bool,
    experience_ok: bool,
    same_city: bool,
) -> str:
    parts = []
    if matched:
        parts.append(f"已匹配核心技能：{'、'.join(sorted(matched))}")
    if missing:
        parts.append(f"建议补充：{'、'.join(sorted(missing))}")
    parts.append("学历达到要求" if education_ok else "学历暂未达到岗位要求")
    parts.append("经验达到要求" if experience_ok else "经验年限仍有差距")
    parts.append("城市一致" if same_city else "工作城市需要协调")
    return "；".join(parts) + "。"


reason = build_reason(
    matched={"python", "spark", "sql"},
    missing={"hadoop"},
    education_ok=True,
    experience_ok=False,
    same_city=True,
)
print(reason)
