"""案例 8：对比加载自定义领域词典前后的分词结果。"""

import logging
from pathlib import Path

import jieba


jieba.setLogLevel(logging.WARNING)
text = "熟悉大数据开发、数据仓库、机器学习和自然语言处理"
print("添加自定义词前：")
print(jieba.lcut(text))

user_dict = Path(__file__).with_name("user_dict.txt")
jieba.load_userdict(str(user_dict))
print("添加自定义词后：")
print(jieba.lcut(text))
