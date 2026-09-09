"""案例 2：使用 scikit-learn 实现词袋模型。"""

from sklearn.feature_extraction.text import CountVectorizer


documents = [
    "python spark sql 数据分析 python",
    "python spark hadoop 数据处理",
    "java spring mysql 后端开发",
]

vectorizer = CountVectorizer()
count_matrix = vectorizer.fit_transform(documents)
feature_names = vectorizer.get_feature_names_out()

print("词表：", feature_names)
print("\n词频矩阵：")
print(count_matrix.toarray())

print("\n逐段文本词频：")
for doc_index, vector in enumerate(count_matrix.toarray(), start=1):
    print(f"\n第 {doc_index} 段文本：")
    for word, count in zip(feature_names, vector):
        if count > 0:
            print(f"{word}: {count}")
