"""案例 4：使用平滑公式手工计算 IDF。"""

import math


documents = [
    ["python", "spark", "sql", "数据分析"],
    ["python", "spark", "hadoop", "数据处理"],
    ["java", "spring", "mysql", "后端开发"],
]


def calculate_idf(corpus: list[list[str]]) -> dict[str, float]:
    """IDF = log((N + 1) / (df + 1)) + 1。"""

    if not corpus:
        return {}
    total_docs = len(corpus)
    vocab = set().union(*(set(tokens) for tokens in corpus))
    return {
        word: math.log(
            (total_docs + 1)
            / (sum(word in set(tokens) for tokens in corpus) + 1)
        )
        + 1
        for word in vocab
    }


print("IDF 计算结果：")
for word, idf_value in sorted(calculate_idf(documents).items()):
    print(f"{word} => {idf_value:.4f}")
