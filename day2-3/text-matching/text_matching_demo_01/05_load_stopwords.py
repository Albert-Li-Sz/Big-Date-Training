"""案例 5：从 JSON 文件读取停用词。"""

import logging

import jieba

from preprocess import DEFAULT_STOPWORDS_PATH, PUNCTUATIONS, load_stopwords


jieba.setLogLevel(logging.WARNING)
text = "熟悉 Python 和 Spark，具有数据分析相关项目经验。"
stopwords = load_stopwords(DEFAULT_STOPWORDS_PATH)

result = []
for raw_word in jieba.lcut(text):
    word = raw_word.strip()
    if not word or word in PUNCTUATIONS or word in stopwords:
        continue
    result.append(word)

print("停用词数量：", len(stopwords))
print("过滤结果：", result)
