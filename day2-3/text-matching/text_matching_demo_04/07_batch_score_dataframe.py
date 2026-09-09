"""案例 7：用 DataFrame 批量计算并排序多维匹配结果。"""

import pandas as pd


WEIGHTS = {
    "skill_score": 0.35,
    "semantic_score": 0.30,
    "education_score": 0.15,
    "experience_score": 0.15,
    "city_score": 0.05,
}


rows = [
    {
        "job_name": "大数据开发实习生",
        "skill_score": 75,
        "semantic_score": 82,
        "education_score": 100,
        "experience_score": 70,
        "city_score": 100,
    },
    {
        "job_name": "数据分析实习生",
        "skill_score": 67,
        "semantic_score": 88,
        "education_score": 100,
        "experience_score": 90,
        "city_score": 100,
    },
    {
        "job_name": "后端开发实习生",
        "skill_score": 25,
        "semantic_score": 35,
        "education_score": 100,
        "experience_score": 70,
        "city_score": 0,
    },
]


def score_dataframe(data: list[dict[str, object]]) -> pd.DataFrame:
    frame = pd.DataFrame(data)
    frame["total_score"] = sum(
        frame[column] * weight for column, weight in WEIGHTS.items()
    )
    frame = frame.sort_values("total_score", ascending=False).reset_index(drop=True)
    frame.insert(0, "rank", frame.index + 1)
    return frame


if __name__ == "__main__":
    print(score_dataframe(rows).round(2).to_string(index=False))
