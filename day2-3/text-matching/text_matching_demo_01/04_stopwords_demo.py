"""案例 4：使用内置集合过滤停用词。"""

import logging

import jieba

from preprocess import PUNCTUATIONS


jieba.setLogLevel(logging.WARNING)
text = "熟悉 Python 和 Spark，具有数据分析相关项目经验。"
stopwords = {
    "的",
    "了",
    "和",
    "与",
    "或",
    "以及",
    "熟悉",
    "掌握",
    "具有",
    "相关",
    "经验",
    "负责",
    "参与",
    "能够",
    "进行",
}

raw_words = jieba.lcut(text)
filtered_words = []
for raw_word in raw_words:
    word = raw_word.strip()
    if not word or word in PUNCTUATIONS or word in stopwords:
        continue
    filtered_words.append(word)

print("原始文本：", text)
print("分词结果：", raw_words)
print("过滤后：", filtered_words)
