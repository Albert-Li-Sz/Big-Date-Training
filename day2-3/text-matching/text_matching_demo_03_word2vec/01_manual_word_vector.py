"""案例 1：手工词向量与余弦相似度。"""

import math
from collections.abc import Sequence


word_vectors = {
    "数据分析": [0.9, 0.1, 0.0],
    "数据挖掘": [0.85, 0.1, 0.05],
    "机器学习": [0.8, 0.1, 0.1],
    "java": [0.1, 0.9, 0.0],
    "spring": [0.1, 0.85, 0.0],
    "linux": [0.1, 0.0, 0.9],
}


def cosine_similarity(
    vector_a: Sequence[float], vector_b: Sequence[float]
) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError("两个向量的维度必须一致")
    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


comparisons = [
    ("数据分析", "数据挖掘"),
    ("数据分析", "java"),
    ("java", "spring"),
]
for left, right in comparisons:
    score = cosine_similarity(word_vectors[left], word_vectors[right])
    print(f"{left} vs {right}：{score:.4f}")
