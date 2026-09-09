"""案例 3：清理标点和空白字符。"""

import logging

import jieba

from preprocess import PUNCTUATIONS


jieba.setLogLevel(logging.WARNING)
text = "熟悉 Python、Spark、SQL，做过数据分析项目；了解机器学习。"
raw_words = jieba.lcut(text)
clean_words = [
    word.strip()
    for word in raw_words
    if word.strip() and word.strip() not in PUNCTUATIONS
]

print("原始分词：", raw_words)
print("清理结果：", clean_words)
