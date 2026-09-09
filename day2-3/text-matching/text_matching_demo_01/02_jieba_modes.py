"""案例 2：对比 jieba 三种分词模式。"""

import logging

import jieba


jieba.setLogLevel(logging.WARNING)
text = "我熟悉大数据分析、机器学习和自然语言处理"

print("原始文本：", text)
print("=" * 60)
print("精确模式：", jieba.lcut(text))
print("全模式：", jieba.lcut(text, cut_all=True))
print("搜索引擎模式：", jieba.lcut_for_search(text))
