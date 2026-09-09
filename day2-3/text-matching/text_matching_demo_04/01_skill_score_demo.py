"""案例 1：用技能集合的覆盖率计算技能匹配分。"""


def skill_score(resume_skills: set[str], required_skills: set[str]) -> float:
    """返回 0~100 的岗位技能覆盖率。"""
    if not required_skills:
        return 100.0
    matched = resume_skills & required_skills
    return len(matched) / len(required_skills) * 100


resume_skills = {"python", "spark", "sql", "excel"}
required_skills = {"python", "spark", "hadoop", "sql"}
matched_skills = sorted(resume_skills & required_skills)
missing_skills = sorted(required_skills - resume_skills)

print(f"已匹配技能：{matched_skills}")
print(f"待提升技能：{missing_skills}")
print(f"技能匹配分：{skill_score(resume_skills, required_skills):.2f}")
