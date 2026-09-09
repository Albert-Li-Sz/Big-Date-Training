"""案例 4：使用平均词向量表示一段文本。"""

from _word2vec_support import get_sentence_vector, load_or_train_model


model = load_or_train_model()
resume_tokens = ["python", "sql", "数据分析", "可视化"]
resume_vector = get_sentence_vector(resume_tokens, model)

print("句向量维度：", len(resume_vector))
print("句向量前 5 个值：")
print(resume_vector[:5])
