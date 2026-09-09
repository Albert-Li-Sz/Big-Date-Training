"""案例 9：多份简历与岗位的完整预处理和关键词交集。"""

from preprocess import calculate_overlap, load_stopwords, preprocess_text


resumes = [
    {
        "resume_id": "R001",
        "name": "张三",
        "text": "熟悉 py、Spark、SQL，做过数据分析项目，了解机器学习。",
    },
    {
        "resume_id": "R002",
        "name": "李四",
        "text": "熟悉机器学习、深度学习、Python 和 PyTorch，做过图像分类项目。",
    },
]

jobs = [
    {
        "job_id": "J001",
        "job_title": "数据分析师",
        "text": "岗位要求掌握 Python 编程，熟悉 SQL，有数据分析经验。",
    },
    {
        "job_id": "J002",
        "job_title": "大数据工程师",
        "text": "岗位要求熟悉 Hadoop、Hive、Apache Spark，有大数据处理经验。",
    },
    {
        "job_id": "J003",
        "job_title": "Java 后端工程师",
        "text": "岗位要求掌握 Java、Spring Boot、MySQL，有后端开发经验。",
    },
    {
        "job_id": "J004",
        "job_title": "算法工程师",
        "text": "要求熟悉 Python、机器学习、深度学习，有模型训练经验。",
    },
    {
        "job_id": "J005",
        "job_title": "数据库工程师",
        "text": "要求熟悉 MySQL、SQL 优化、数据库设计和数据备份。",
    },
]


def main() -> None:
    stopwords = load_stopwords()
    prepared_jobs = [
        (job, preprocess_text(job["text"], stopwords)) for job in jobs
    ]

    for resume in resumes:
        resume_words = preprocess_text(resume["text"], stopwords)
        print("=" * 80)
        print(f"候选人：{resume['name']} ({resume['resume_id']})")
        print("简历预处理结果：", resume_words)
        for job, job_words in prepared_jobs:
            overlap = calculate_overlap(resume_words, job_words)
            print(
                f"- {job['job_title']} ({job['job_id']})："
                f"共同关键词 {overlap}"
            )


if __name__ == "__main__":
    main()
