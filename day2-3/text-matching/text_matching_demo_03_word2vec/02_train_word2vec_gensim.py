"""案例 2：使用 gensim 训练并保存 Word2Vec 模型。"""

from _word2vec_support import MODEL_PATH, train_model


model = train_model(save=True)
python_vector = model.wv["python"]

print("python 的词向量维度：", len(python_vector))
print("python 的前 5 个向量值：")
print(python_vector[:5])
print("模型已保存：", MODEL_PATH)
