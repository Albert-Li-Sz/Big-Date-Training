"""案例 7：把 TF-IDF 与 Word2Vec 合成为综合语义分。"""


jobs = [
    {"job_name": "数据分析实习生", "tfidf_score": 78, "word2vec_score": 82},
    {"job_name": "数据挖掘实习生", "tfidf_score": 45, "word2vec_score": 76},
    {"job_name": "后端开发实习生", "tfidf_score": 10, "word2vec_score": 18},
]


def calculate_semantic_score(
    tfidf_score: float,
    word2vec_score: float,
    tfidf_weight: float = 0.6,
) -> float:
    if not 0 <= tfidf_weight <= 1:
        raise ValueError("tfidf_weight 必须在 0 到 1 之间")
    return tfidf_score * tfidf_weight + word2vec_score * (1 - tfidf_weight)


for job in jobs:
    job["semantic_score"] = calculate_semantic_score(
        job["tfidf_score"], job["word2vec_score"]
    )

jobs.sort(key=lambda item: item["semantic_score"], reverse=True)
print("综合语义分排序：")
for job in jobs:
    print(
        f"{job['job_name']}  TF-IDF: {job['tfidf_score']}  "
        f"Word2Vec: {job['word2vec_score']}  "
        f"综合语义分: {job['semantic_score']:.2f}"
    )
