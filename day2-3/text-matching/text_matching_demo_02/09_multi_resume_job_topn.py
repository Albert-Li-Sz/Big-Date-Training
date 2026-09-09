"""案例 9：多份简历匹配多个岗位，并输出 Top N。"""

from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


resumes = [
    {
        "resume_name": "张同学",
        "resume_text": "python spark sql 数据分析 数据清洗 可视化 项目",
    },
    {
        "resume_name": "李同学",
        "resume_text": "java spring mysql 后端开发 接口 项目",
    },
    {
        "resume_name": "王同学",
        "resume_text": "linux shell 服务器 部署 网络 运维",
    },
]

jobs = [
    {
        "job_name": "大数据开发实习生",
        "job_text": "python spark hadoop sql 数据处理 数据清洗",
    },
    {
        "job_name": "后端开发实习生",
        "job_text": "java spring mysql 接口开发 后端开发",
    },
    {
        "job_name": "数据分析实习生",
        "job_text": "python sql 数据分析 可视化 报表 分析",
    },
    {
        "job_name": "运维实习生",
        "job_text": "linux shell 服务器 网络 部署 运维",
    },
]


def build_topn_result(top_n: int = 2) -> pd.DataFrame:
    if top_n <= 0:
        raise ValueError("top_n 必须大于 0")

    resume_texts = [item["resume_text"] for item in resumes]
    job_texts = [item["job_text"] for item in jobs]
    matrix = TfidfVectorizer().fit_transform(resume_texts + job_texts)
    similarity_matrix = cosine_similarity(
        matrix[: len(resumes)], matrix[len(resumes) :]
    )

    rows = []
    for resume_index, resume in enumerate(resumes):
        ranked = sorted(
            enumerate(similarity_matrix[resume_index]),
            key=lambda item: item[1],
            reverse=True,
        )[:top_n]
        for rank, (job_index, score) in enumerate(ranked, start=1):
            rows.append(
                {
                    "学生": resume["resume_name"],
                    "推荐排名": rank,
                    "推荐岗位": jobs[job_index]["job_name"],
                    "匹配分": round(float(score), 4),
                }
            )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    result_df = build_topn_result(top_n=2)
    print(result_df.to_string(index=False))

    output_path = Path(__file__).resolve().parents[1] / "output" / "resume_job_topn_result.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\nCSV 已保存：{output_path}")
