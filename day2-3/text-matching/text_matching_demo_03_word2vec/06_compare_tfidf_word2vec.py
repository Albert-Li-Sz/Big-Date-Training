"""案例 6：对比 TF-IDF 与 Word2Vec 相似度。"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from _word2vec_support import get_sentence_vector, load_or_train_model


resume_tokens = ["python", "sql", "数据分析", "可视化"]
jobs = [
    {
        "job_name": "数据分析实习生",
        "tokens": ["python", "sql", "数据分析", "报表"],
    },
    {
        "job_name": "数据挖掘实习生",
        "tokens": ["python", "数据挖掘", "机器学习", "模型"],
    },
    {
        "job_name": "后端开发实习生",
        "tokens": ["java", "spring", "mysql", "后端开发"],
    },
]

documents = [" ".join(resume_tokens)] + [
    " ".join(job["tokens"]) for job in jobs
]
tfidf_matrix = TfidfVectorizer().fit_transform(documents)
tfidf_scores = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])[0]

model = load_or_train_model()
resume_w2v = get_sentence_vector(resume_tokens, model)
rows = []
for index, job in enumerate(jobs):
    job_w2v = get_sentence_vector(job["tokens"], model)
    word2vec_score = float(cosine_similarity([resume_w2v], [job_w2v])[0][0])
    rows.append(
        {
            "job_name": job["job_name"],
            "tfidf_score": float(tfidf_scores[index]) * 100,
            "word2vec_score": word2vec_score * 100,
        }
    )

print("TF-IDF 与 Word2Vec 对比：")
for row in rows:
    print(
        f"{row['job_name']}  "
        f"TF-IDF: {row['tfidf_score']:.2f}  "
        f"Word2Vec: {row['word2vec_score']:.2f}"
    )
