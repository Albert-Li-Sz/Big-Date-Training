"""案例 7：把预处理步骤封装成函数。"""

from preprocess import load_stopwords, preprocess_text


if __name__ == "__main__":
    stopwords = load_stopwords()
    resume_text = "熟悉 py、Spark、SQL，具有数据分析相关项目经验。"
    job_text = "岗位要求掌握 Python 编程，熟悉 Apache Spark 大数据处理，有 SQL 基础。"

    print("简历原文：", resume_text)
    print("简历处理结果：", preprocess_text(resume_text, stopwords))
    print("岗位原文：", job_text)
    print("岗位处理结果：", preprocess_text(job_text, stopwords))
