"""案例 9：TF-IDF + Word2Vec + 规则维度的可解释 Top N 匹配器。"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


RESUMES = [
    {
        "resume_id": "R001",
        "name": "张同学",
        "skills": {"python", "spark", "sql", "excel"},
        "text": "python spark sql 数据清洗 数据分析 可视化 电商项目",
        "education": "本科",
        "experience": 1.0,
        "city": "南昌",
        "certificates": {"英语四级", "计算机二级"},
    },
    {
        "resume_id": "R002",
        "name": "李同学",
        "skills": {"java", "spring", "mysql", "linux"},
        "text": "java spring mysql 后端开发 接口设计 校园项目",
        "education": "本科",
        "experience": 1.5,
        "city": "杭州",
        "certificates": {"英语四级"},
    },
    {
        "resume_id": "R003",
        "name": "王同学",
        "skills": {"linux", "shell", "docker", "hadoop"},
        "text": "linux shell docker hadoop 集群部署 服务器 运维",
        "education": "大专",
        "experience": 2.0,
        "city": "南昌",
        "certificates": set(),
    },
]

JOBS = [
    {
        "job_id": "J001",
        "job_name": "大数据开发实习生",
        "required_skills": {"python", "spark", "hadoop", "sql"},
        "text": "python spark hadoop sql 数据处理 数据仓库",
        "required_education": "本科",
        "required_experience": 1.0,
        "city": "南昌",
        "preferred_certificates": {"英语四级"},
    },
    {
        "job_id": "J002",
        "job_name": "数据分析实习生",
        "required_skills": {"python", "sql", "excel", "powerbi"},
        "text": "python sql excel powerbi 数据分析 可视化 报表",
        "required_education": "本科",
        "required_experience": 0.5,
        "city": "南昌",
        "preferred_certificates": set(),
    },
    {
        "job_id": "J003",
        "job_name": "Java 后端实习生",
        "required_skills": {"java", "spring", "mysql", "git"},
        "text": "java spring mysql git 后端开发 接口 微服务",
        "required_education": "本科",
        "required_experience": 1.0,
        "city": "杭州",
        "preferred_certificates": {"英语四级"},
    },
    {
        "job_id": "J004",
        "job_name": "大数据运维实习生",
        "required_skills": {"linux", "shell", "docker", "hadoop"},
        "text": "linux shell docker hadoop 集群 服务器 运维",
        "required_education": "大专",
        "required_experience": 1.0,
        "city": "南昌",
        "preferred_certificates": set(),
    },
]

EDUCATION_LEVEL = {"不限": 0, "大专": 1, "本科": 2, "硕士": 3, "博士": 4}
WEIGHT_PROFILES = {
    "default": {
        "skill_score": 0.35,
        "semantic_score": 0.30,
        "education_score": 0.15,
        "experience_score": 0.15,
        "city_score": 0.05,
    },
    "extended": {
        "skill_score": 0.35,
        "semantic_score": 0.25,
        "education_score": 0.15,
        "experience_score": 0.15,
        "certificate_score": 0.10,
    },
}


def safe_cosine(left: np.ndarray, right: np.ndarray) -> float:
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator == 0:
        return 0.0
    return float(np.dot(left, right) / denominator)


def sentence_vector(model: Word2Vec, tokens: list[str]) -> np.ndarray:
    vectors = [model.wv[token] for token in tokens if token in model.wv]
    if not vectors:
        return np.zeros(model.vector_size, dtype=float)
    return np.mean(vectors, axis=0)


def coverage(actual: set[str], expected: set[str]) -> float:
    if not expected:
        return 100.0
    return len(actual & expected) / len(expected) * 100


def education_score(actual: str, expected: str) -> float:
    actual_level = EDUCATION_LEVEL.get(actual, 0)
    expected_level = EDUCATION_LEVEL.get(expected, 0)
    if actual_level >= expected_level:
        return 100.0
    return max(0.0, 100.0 - (expected_level - actual_level) * 40)


def experience_score(actual: float, expected: float) -> float:
    if expected <= 0:
        return 100.0
    return min(actual / expected, 1.0) * 100


def build_reason(resume: dict[str, object], job: dict[str, object]) -> str:
    actual = set(resume["skills"])
    expected = set(job["required_skills"])
    matched = sorted(actual & expected)
    missing = sorted(expected - actual)
    parts = [f"命中技能：{'、'.join(matched) if matched else '暂无'}"]
    if missing:
        parts.append(f"待提升：{'、'.join(missing)}")
    parts.append(
        "学历达标"
        if EDUCATION_LEVEL.get(str(resume["education"]), 0)
        >= EDUCATION_LEVEL.get(str(job["required_education"]), 0)
        else "学历有差距"
    )
    parts.append(
        "经验达标"
        if float(resume["experience"]) >= float(job["required_experience"])
        else "经验仍需积累"
    )
    parts.append("城市一致" if resume["city"] == job["city"] else "城市需协调")
    return "；".join(parts) + "。"


def build_result(
    profile: str = "default",
    top_n: int = 3,
    min_skill_score: float = 0.0,
) -> pd.DataFrame:
    if profile not in WEIGHT_PROFILES:
        raise ValueError(f"未知权重方案：{profile}")
    if top_n <= 0:
        raise ValueError("top_n 必须大于 0")
    if not 0 <= min_skill_score <= 100:
        raise ValueError("min_skill_score 必须位于 0~100")

    resume_tokens = [str(item["text"]).split() for item in RESUMES]
    job_tokens = [str(item["text"]).split() for item in JOBS]
    all_tokens = resume_tokens + job_tokens

    tfidf = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
    matrix = tfidf.fit_transform([" ".join(tokens) for tokens in all_tokens])
    tfidf_matrix = cosine_similarity(
        matrix[: len(RESUMES)], matrix[len(RESUMES) :]
    )

    model = Word2Vec(
        sentences=all_tokens,
        vector_size=40,
        window=4,
        min_count=1,
        workers=1,
        seed=42,
        sg=1,
        epochs=120,
    )
    resume_vectors = [sentence_vector(model, tokens) for tokens in resume_tokens]
    job_vectors = [sentence_vector(model, tokens) for tokens in job_tokens]

    weights = WEIGHT_PROFILES[profile]
    rows: list[dict[str, object]] = []
    for resume_index, resume in enumerate(RESUMES):
        candidates: list[dict[str, object]] = []
        for job_index, job in enumerate(JOBS):
            actual_skills = set(resume["skills"])
            required_skills = set(job["required_skills"])
            skill = coverage(actual_skills, required_skills)
            tfidf_value = float(tfidf_matrix[resume_index, job_index]) * 100
            word2vec_value = max(
                0.0,
                safe_cosine(resume_vectors[resume_index], job_vectors[job_index]) * 100,
            )
            semantic = tfidf_value * 0.6 + word2vec_value * 0.4
            scores = {
                "skill_score": skill,
                "semantic_score": semantic,
                "education_score": education_score(
                    str(resume["education"]), str(job["required_education"])
                ),
                "experience_score": experience_score(
                    float(resume["experience"]), float(job["required_experience"])
                ),
                "city_score": 100.0 if resume["city"] == job["city"] else 0.0,
                "certificate_score": coverage(
                    set(resume["certificates"]), set(job["preferred_certificates"])
                ),
            }
            total = sum(scores[name] * weight for name, weight in weights.items())
            candidates.append(
                {
                    "resume_id": resume["resume_id"],
                    "student": resume["name"],
                    "job_id": job["job_id"],
                    "job": job["job_name"],
                    **{name: round(value, 2) for name, value in scores.items()},
                    "total_score": round(total, 2),
                    "eligible": skill >= min_skill_score,
                    "reason": build_reason(resume, job),
                }
            )

        eligible = [item for item in candidates if bool(item["eligible"])]
        ranked = sorted(eligible, key=lambda item: float(item["total_score"]), reverse=True)
        for rank, item in enumerate(ranked[:top_n], start=1):
            item["rank"] = rank
            rows.append(item)

    columns = [
        "resume_id",
        "student",
        "rank",
        "job_id",
        "job",
        "total_score",
        "skill_score",
        "semantic_score",
        "education_score",
        "experience_score",
        "city_score",
        "certificate_score",
        "eligible",
        "reason",
    ]
    return pd.DataFrame(rows, columns=columns)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=sorted(WEIGHT_PROFILES), default="default")
    parser.add_argument("--top-n", type=int, default=3)
    parser.add_argument("--min-skill-score", type=float, default=0.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "output"
        / "explainable_match_result.csv",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_result(args.profile, args.top_n, args.min_skill_score)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(result.to_string(index=False))
    print(f"\n权重方案：{args.profile}；结果已保存：{args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
