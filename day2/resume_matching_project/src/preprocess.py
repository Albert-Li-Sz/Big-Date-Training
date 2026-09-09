"""文本清洗、jieba 分词、停用词过滤与技能词标准化。"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import jieba


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_STOPWORDS_PATH = DATA_DIR / "stopwords.txt"
DEFAULT_ALIASES_PATH = DATA_DIR / "skill_alias.json"
MULTI_VALUE_PATTERN = re.compile(r"[;；,，、/|]+")
NON_TEXT_PATTERN = re.compile(r"[^0-9a-zA-Z+#.\-\u4e00-\u9fff]+")


@lru_cache(maxsize=8)
def load_stopwords(path: str | Path = DEFAULT_STOPWORDS_PATH) -> frozenset[str]:
    file_path = Path(path)
    return frozenset(
        line.strip().lower()
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


@lru_cache(maxsize=8)
def load_skill_aliases(path: str | Path = DEFAULT_ALIASES_PATH) -> dict[str, str]:
    file_path = Path(path)
    aliases = json.loads(file_path.read_text(encoding="utf-8"))
    normalized = {
        str(alias).strip().lower(): str(canonical).strip().lower()
        for alias, canonical in aliases.items()
        if str(alias).strip() and str(canonical).strip()
    }
    for canonical in sorted(set(normalized.values())):
        jieba.add_word(canonical)
    for alias in sorted(normalized, key=len, reverse=True):
        jieba.add_word(alias)
    return normalized


def split_multi_value(value: object) -> list[str]:
    if value is None:
        return []
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return []
    return [item.strip() for item in MULTI_VALUE_PATTERN.split(text) if item.strip()]


def normalize_skill(
    skill: object,
    aliases: dict[str, str] | None = None,
) -> str:
    aliases = aliases or load_skill_aliases()
    cleaned = str(skill).strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return aliases.get(cleaned, cleaned)


def normalize_skill_set(
    value: object,
    aliases: dict[str, str] | None = None,
) -> set[str]:
    aliases = aliases or load_skill_aliases()
    return {
        normalize_skill(skill, aliases)
        for skill in split_multi_value(value)
        if normalize_skill(skill, aliases)
    }


def replace_aliases(text: object, aliases: dict[str, str] | None = None) -> str:
    aliases = aliases or load_skill_aliases()
    normalized = str(text or "").lower()
    for alias in sorted(aliases, key=len, reverse=True):
        normalized = normalized.replace(alias, aliases[alias])
    return normalized


def tokenize(
    text: object,
    stopwords: Iterable[str] | None = None,
    aliases: dict[str, str] | None = None,
) -> list[str]:
    aliases = aliases or load_skill_aliases()
    blocked = set(stopwords) if stopwords is not None else set(load_stopwords())
    normalized = replace_aliases(text, aliases)
    normalized = NON_TEXT_PATTERN.sub(" ", normalized)
    tokens = []
    for raw in jieba.lcut(normalized, cut_all=False):
        token = normalize_skill(raw, aliases).strip(" .-")
        if not token or token in blocked:
            continue
        if len(token) == 1 and token not in {"c", "r"} and not token.isdigit():
            continue
        tokens.append(token)
    return tokens


def build_document(
    skills: object,
    *text_fields: object,
    aliases: dict[str, str] | None = None,
    stopwords: Iterable[str] | None = None,
) -> tuple[list[str], set[str]]:
    """把结构化技能和自然语言字段合成用于相似度计算的词序列。"""
    aliases = aliases or load_skill_aliases()
    skill_set = normalize_skill_set(skills, aliases)
    body = " ".join(str(field or "") for field in text_fields)
    body_tokens = tokenize(body, stopwords=stopwords, aliases=aliases)
    # 技能字段可信度较高，重复一次使其在 TF-IDF/Word2Vec 文档中更突出。
    tokens = sorted(skill_set) + sorted(skill_set) + body_tokens
    return tokens, skill_set


def display_skill(skill: str) -> str:
    labels = {
        "python": "Python",
        "pyspark": "PySpark",
        "spark": "Spark",
        "hadoop": "Hadoop",
        "hive": "Hive",
        "hbase": "HBase",
        "sql": "SQL",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "java": "Java",
        "spring boot": "Spring Boot",
        "redis": "Redis",
        "linux": "Linux",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "shell": "Shell",
        "git": "Git",
        "github": "GitHub",
        "excel": "Excel",
        "powerbi": "Power BI",
        "tableau": "Tableau",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "sklearn": "Scikit-learn",
        "tensorflow": "TensorFlow",
        "pytorch": "PyTorch",
        "nlp": "NLP",
        "bert": "BERT",
        "opencv": "OpenCV",
        "javascript": "JavaScript",
        "html": "HTML",
        "css": "CSS",
        "vue": "Vue",
        "scrapy": "Scrapy",
        "airflow": "Airflow",
        "nginx": "Nginx",
        "prometheus": "Prometheus",
        "scala": "Scala",
        "spss": "SPSS",
    }
    return labels.get(skill, skill)
