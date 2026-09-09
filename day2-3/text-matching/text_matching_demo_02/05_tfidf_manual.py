"""案例 5：手工计算 TF-IDF。"""

import math
from collections import Counter


documents = [
    ["python", "spark", "sql", "数据分析", "python"],
    ["python", "spark", "hadoop", "数据处理"],
    ["java", "spring", "mysql", "后端开发"],
]


def calculate_tf(tokens: list[str]) -> dict[str, float]:
    if not tokens:
        return {}
    counts = Counter(tokens)
    return {word: count / len(tokens) for word, count in counts.items()}


def calculate_idf(corpus: list[list[str]]) -> dict[str, float]:
    if not corpus:
        return {}
    total_docs = len(corpus)
    document_sets = [set(tokens) for tokens in corpus]
    vocab = set().union(*document_sets)
    return {
        word: math.log(
            (total_docs + 1)
            / (sum(word in tokens for tokens in document_sets) + 1)
        )
        + 1
        for word in vocab
    }


def calculate_tfidf(
    tokens: list[str], idf_dict: dict[str, float]
) -> dict[str, float]:
    return {
        word: tf_value * idf_dict[word]
        for word, tf_value in calculate_tf(tokens).items()
    }


idf_dict = calculate_idf(documents)
tfidf_result = calculate_tfidf(documents[0], idf_dict)
print("第 1 篇文本的 TF-IDF：")
for word, score in sorted(
    tfidf_result.items(), key=lambda item: item[1], reverse=True
):
    print(f"{word} => {score:.4f}")
