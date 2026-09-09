"""案例 7：不用第三方库手工计算余弦相似度。"""

import math
from collections.abc import Sequence


def dot_product(vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError("两个向量的维度必须一致")
    return sum(a * b for a, b in zip(vector_a, vector_b))


def vector_norm(vector: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def cosine_similarity(
    vector_a: Sequence[float], vector_b: Sequence[float]
) -> float:
    dot = dot_product(vector_a, vector_b)
    norm_a = vector_norm(vector_a)
    norm_b = vector_norm(vector_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


resume_vector = [1, 1, 1, 0]
job_vector_1 = [1, 1, 0, 1]
job_vector_2 = [0, 0, 0, 1]

print("简历与岗位 1 的相似度：", round(cosine_similarity(resume_vector, job_vector_1), 4))
print("简历与岗位 2 的相似度：", round(cosine_similarity(resume_vector, job_vector_2), 4))
