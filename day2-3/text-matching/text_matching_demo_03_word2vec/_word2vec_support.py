"""Word2Vec 案例共享的教学语料与辅助函数。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from gensim.models import Word2Vec


MODEL_PATH = Path(__file__).resolve().parent / ".artifacts" / "word2vec_resume_job.model"

SENTENCES = [
    ["python", "sql", "数据分析", "报表", "可视化"],
    ["python", "数据挖掘", "机器学习", "模型", "预测"],
    ["python", "spark", "hadoop", "数据处理", "大数据"],
    ["java", "spring", "mysql", "后端开发", "接口"],
    ["linux", "shell", "服务器", "部署", "运维"],
    ["excel", "数据分析", "统计分析", "报表", "可视化"],
    ["spark", "pyspark", "数据清洗", "数据处理", "hadoop"],
    ["java", "springboot", "接口开发", "mysql", "后端服务"],
]


def train_model(save: bool = True) -> Word2Vec:
    """用固定种子和单线程训练可复现的课堂小模型。"""

    model = Word2Vec(
        sentences=SENTENCES,
        vector_size=20,
        window=3,
        min_count=1,
        workers=1,
        seed=42,
    )
    if save:
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(MODEL_PATH))
    return model


def load_or_train_model() -> Word2Vec:
    """加载前一案例的模型；文件不存在或损坏时自动重训。"""

    if MODEL_PATH.exists():
        try:
            return Word2Vec.load(str(MODEL_PATH))
        except (EOFError, ValueError):
            pass
    return train_model(save=True)


def get_sentence_vector(tokens: list[str], model: Word2Vec) -> np.ndarray:
    """使用有效词向量的算术平均值表示一段文本。"""

    vectors = [model.wv[word] for word in tokens if word in model.wv]
    if not vectors:
        return np.zeros(model.vector_size, dtype=float)
    return np.mean(vectors, axis=0)
