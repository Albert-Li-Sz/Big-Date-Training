"""多维评分、权重合成与可解释推荐理由。"""

from __future__ import annotations

from dataclasses import dataclass

from .preprocess import display_skill, normalize_skill_set, split_multi_value


EDUCATION_LEVEL = {
    "不限": 0,
    "中专": 1,
    "高中": 1,
    "大专": 2,
    "本科": 3,
    "硕士": 4,
    "博士": 5,
}

DEFAULT_WEIGHTS = {
    "skill_score": 0.30,
    "tfidf_score": 0.20,
    "word2vec_score": 0.15,
    "education_score": 0.15,
    "experience_score": 0.10,
    "city_score": 0.05,
    "certificate_score": 0.05,
}


@dataclass(frozen=True)
class PairScore:
    values: dict[str, float | str | bool]
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]


def coverage_score(actual: set[str], expected: set[str]) -> float:
    if not expected:
        return 100.0
    return len(actual & expected) / len(expected) * 100


def education_score(actual: str, required: str) -> float:
    actual_level = EDUCATION_LEVEL.get(str(actual).strip(), 0)
    required_level = EDUCATION_LEVEL.get(str(required).strip(), 0)
    if actual_level >= required_level:
        return 100.0
    return max(0.0, 100.0 - (required_level - actual_level) * 35.0)


def experience_score(actual: float, required: float) -> float:
    if required <= 0:
        return 100.0
    return min(max(actual, 0.0) / required, 1.0) * 100


def city_score(actual: str, required: str) -> float:
    if not required or required in {"不限", "全国", "远程"}:
        return 100.0
    return 100.0 if actual == required else 0.0


def salary_score(expected: float, offered: float) -> float:
    if expected <= 0:
        return 100.0
    return min(max(offered, 0.0) / expected, 1.0) * 100


def _reason_level(score: float) -> str:
    if score >= 75:
        return "语义经历高度相关"
    if score >= 45:
        return "语义经历部分相关"
    return "语义经历相关度较低"


def score_pair(
    resume: dict[str, object],
    job: dict[str, object],
    tfidf_similarity: float,
    word2vec_similarity: float,
    weights: dict[str, float] | None = None,
) -> PairScore:
    weights = weights or DEFAULT_WEIGHTS
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError("权重之和必须等于 1")

    resume_skills = normalize_skill_set(resume.get("skills", ""))
    job_skills = normalize_skill_set(job.get("required_skills", ""))
    matched = tuple(sorted(resume_skills & job_skills))
    missing = tuple(sorted(job_skills - resume_skills))
    owned_certificates = set(split_multi_value(resume.get("certificates", "")))
    preferred_certificates = set(
        split_multi_value(job.get("preferred_certificates", ""))
    )

    dimensions = {
        "skill_score": coverage_score(resume_skills, job_skills),
        "tfidf_score": min(max(tfidf_similarity, 0.0), 1.0) * 100,
        "word2vec_score": min(max(word2vec_similarity, 0.0), 1.0) * 100,
        "education_score": education_score(
            str(resume.get("education", "")),
            str(job.get("required_education", "")),
        ),
        "experience_score": experience_score(
            float(resume.get("experience_years", 0) or 0),
            float(job.get("min_experience_years", 0) or 0),
        ),
        "city_score": city_score(
            str(resume.get("city", "")), str(job.get("city", ""))
        ),
        "certificate_score": coverage_score(
            owned_certificates, preferred_certificates
        ),
    }
    total = sum(dimensions[name] * weight for name, weight in weights.items())
    salary = salary_score(
        float(resume.get("expected_salary", 0) or 0),
        float(job.get("salary", 0) or 0),
    )

    matched_label = "、".join(display_skill(skill) for skill in matched) or "暂无"
    missing_label = "、".join(display_skill(skill) for skill in missing) or "无"
    reasons = [f"命中技能：{matched_label}", f"待提升技能：{missing_label}"]
    reasons.append(
        "学历达到要求" if dimensions["education_score"] == 100 else "学历存在差距"
    )
    reasons.append(
        "经验达到要求" if dimensions["experience_score"] == 100 else "经验仍需积累"
    )
    reasons.append(_reason_level((dimensions["tfidf_score"] + dimensions["word2vec_score"]) / 2))
    reasons.append("城市一致" if dimensions["city_score"] == 100 else "工作城市需协调")
    if preferred_certificates:
        reasons.append(
            "证书符合偏好"
            if dimensions["certificate_score"] == 100
            else "偏好证书可继续补充"
        )
    if salary < 100:
        reasons.append("岗位薪资低于当前期望")

    values: dict[str, float | str | bool] = {
        **{name: round(value, 2) for name, value in dimensions.items()},
        "salary_score": round(salary, 2),
        "total_score": round(total, 2),
        "matched_skills": ";".join(display_skill(skill) for skill in matched),
        "missing_skills": ";".join(display_skill(skill) for skill in missing),
        "reason": "；".join(reasons) + "。",
    }
    return PairScore(values=values, matched_skills=matched, missing_skills=missing)
