"""案例 3：查看词语相似度。"""

from _word2vec_support import load_or_train_model


model = load_or_train_model()
similar_words = model.wv.most_similar("数据分析", topn=5)

print("与 数据分析 最相似的词：")
for word, score in similar_words:
    print(f"{word} => {score:.4f}")

print("\n两个词之间的相似度：")
print("数据分析 vs 数据挖掘：", round(model.wv.similarity("数据分析", "数据挖掘"), 4))
print("数据分析 vs java：", round(model.wv.similarity("数据分析", "java"), 4))
