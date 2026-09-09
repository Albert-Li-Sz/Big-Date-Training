"""案例 1：不用第三方库手工实现词袋模型。"""


resume_tokens = ["python", "spark", "sql", "数据分析", "python"]
job_tokens = ["python", "spark", "hadoop", "数据处理"]


def build_count_vector(tokens: list[str], vocab: list[str]) -> list[int]:
    """按照统一词表统计一段文本的词频。"""

    return [tokens.count(word) for word in vocab]


vocab = sorted(set(resume_tokens + job_tokens))
resume_vector = build_count_vector(resume_tokens, vocab)
job_vector = build_count_vector(job_tokens, vocab)

print("词表：", vocab)
print("简历词频向量：", resume_vector)
print("岗位词频向量：", job_vector)
print("\n词语与词频：")
for word, resume_count, job_count in zip(vocab, resume_vector, job_vector):
    print(f"{word:<12} 简历={resume_count} 岗位={job_count}")
