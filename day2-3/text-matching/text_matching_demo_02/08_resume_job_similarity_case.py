"""案例 8：一份简历使用 TF-IDF 匹配多个岗位。"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


resume_text = "python spark sql 数据分析 数据清洗 可视化 项目"
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

documents = [resume_text] + [job["job_text"] for job in jobs]
tfidf_matrix = TfidfVectorizer().fit_transform(documents)
similarity_scores = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])[0]
results = sorted(
    (
        {"job_name": job["job_name"], "score": float(score)}
        for job, score in zip(jobs, similarity_scores)
    ),
    key=lambda item: item["score"],
    reverse=True,
)

print("岗位匹配结果：")
for rank, item in enumerate(results, start=1):
    print(f"{rank}. {item['job_name']}：{item['score']:.4f}")
