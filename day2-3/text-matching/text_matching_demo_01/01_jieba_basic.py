"""案例 1：jieba 基础分词。"""

import logging

import jieba


jieba.setLogLevel(logging.WARNING)

texts = [
    "熟悉 Python、Spark、SQL，做过数据分析项目。",
    "岗位要求掌握 Python 编程，熟悉 Spark 大数据处理，有 SQL 基础。",
    "具有 Java、Spring Boot、MySQL 后端开发经验。",
    "了解机器学习、深度学习和自然语言处理。",
    # 讲义课堂练习
    "熟悉 Hadoop、Hive 和 SparkSQL，参与过实时数仓项目。",
]

for text in texts:
    print("=" * 60)
    print("原始文本：", text)
    print("分词结果：", jieba.lcut(text))
