"""案例一的可复用文本预处理模块。"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable

import jieba


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_STOPWORDS_PATH = BASE_DIR / "stopwords.json"
DEFAULT_USER_DICT_PATH = BASE_DIR / "user_dict.txt"

PUNCTUATIONS = {
    "，",
    "。",
    "、",
    "；",
    "：",
    "！",
    "？",
    ",",
    ".",
    ";",
    ":",
    "!",
    "?",
    "(",
    ")",
    "（",
    "）",
    "[",
    "]",
    "【",
    "】",
    "{",
    "}",
    "/",
    "\\",
    "|",
    "-",
    "_",
    "\n",
    "\t",
}

# 所有 key 都使用 strip 后的小写形式，英文匹配不区分大小写。
SKILL_MAPPING = {
    "py": "Python",
    "python": "Python",
    "python语言": "Python",
    "python 语言": "Python",
    "spark": "Spark",
    "apache spark": "Spark",
    "sparksql": "SparkSQL",
    "pyspark": "PySpark",
    "sql": "SQL",
    "mysql": "MySQL",
    "my sql": "MySQL",
    "hadoop": "Hadoop",
    "hive": "Hive",
    "机器学习": "Machine Learning",
    "ml": "Machine Learning",
    "深度学习": "Deep Learning",
    "dl": "Deep Learning",
    "自然语言处理": "NLP",
    "nlp": "NLP",
    "数据分析": "Data Analysis",
    "pytorch": "PyTorch",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "数据库": "Database",
}

jieba.setLogLevel(logging.WARNING)
if DEFAULT_USER_DICT_PATH.exists():
    with DEFAULT_USER_DICT_PATH.open("rb") as user_dictionary:
        jieba.load_userdict(user_dictionary)


def load_stopwords(file_path: str | Path = DEFAULT_STOPWORDS_PATH) -> set[str]:
    """从 JSON 数组读取停用词并清理两端空白。"""

    with Path(file_path).open("r", encoding="utf-8") as file:
        words = json.load(file)
    if not isinstance(words, list) or not all(isinstance(word, str) for word in words):
        raise ValueError("stopwords.json 必须是字符串数组")
    return {word.strip() for word in words if word.strip()}


def normalize_skill(word: str) -> str:
    """把技能别名转换成统一写法；未知词保持原样。"""

    cleaned = word.strip()
    return SKILL_MAPPING.get(cleaned.lower(), cleaned)


def unique_in_order(words: Iterable[str]) -> list[str]:
    """去重且保留第一次出现的顺序。"""

    return list(dict.fromkeys(words))


def preprocess_text(text: str, stopwords: set[str] | None = None) -> list[str]:
    """完成分词、清理、停用词过滤、技能标准化和稳定去重。"""

    active_stopwords = load_stopwords() if stopwords is None else stopwords
    result: list[str] = []
    for raw_word in jieba.lcut(text):
        word = raw_word.strip()
        if not word or word in PUNCTUATIONS or word in active_stopwords:
            continue
        normalized = normalize_skill(word)
        if normalized not in result:
            result.append(normalized)
    return result


def calculate_overlap(list_a: Iterable[str], list_b: Iterable[str]) -> list[str]:
    """返回两个词序列的稳定交集，顺序以第一个序列为准。"""

    right = set(list_b)
    return unique_in_order(word for word in list_a if word in right)
