"""案例 6：使用 scikit-learn 计算 TF-IDF。"""

from sklearn.feature_extraction.text import TfidfVectorizer


documents = [
    "python spark sql 数据分析 python",
    "python spark hadoop 数据处理",
    "java spring mysql 后端开发",
]

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)
feature_names = vectorizer.get_feature_names_out()

print("词表：", feature_names)
print("\nTF-IDF 矩阵：")
print(tfidf_matrix.toarray())

print("\n逐段文本 TF-IDF 权重：")
for doc_index, vector in enumerate(tfidf_matrix.toarray(), start=1):
    print(f"\n第 {doc_index} 段文本：")
    word_scores = sorted(
        zip(feature_names, vector), key=lambda item: item[1], reverse=True
    )
    for word, score in word_scores:
        if score > 0:
            print(f"{word}: {score:.4f}")
