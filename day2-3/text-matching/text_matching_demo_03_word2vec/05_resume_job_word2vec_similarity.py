"""案例 5：使用 Word2Vec 计算简历与多个岗位的相似度。"""

from sklearn.metrics.pairwise import cosine_similarity

from _word2vec_support import get_sentence_vector, load_or_train_model


resume = {
    "name": "张同学",
    "tokens": ["python", "sql", "数据分析", "可视化", "报表"],
}
jobs = [
    {
        "job_name": "数据分析实习生",
        "tokens": ["python", "sql", "数据分析", "报表", "excel"],
    },
    {
        "job_name": "大数据开发实习生",
        "tokens": ["python", "spark", "hadoop", "数据处理"],
    },
    {
        "job_name": "后端开发实习生",
        "tokens": ["java", "spring", "mysql", "后端开发"],
    },
]

model = load_or_train_model()
resume_vector = get_sentence_vector(resume["tokens"], model)
results = []
for job in jobs:
    job_vector = get_sentence_vector(job["tokens"], model)
    score = float(cosine_similarity([resume_vector], [job_vector])[0][0])
    results.append(
        {"job_name": job["job_name"], "word2vec_score": score * 100}
    )

results.sort(key=lambda item: item["word2vec_score"], reverse=True)
print("Word2Vec 岗位相似度排序：")
for item in results:
    print(f"{item['job_name']} => {item['word2vec_score']:.2f}")
