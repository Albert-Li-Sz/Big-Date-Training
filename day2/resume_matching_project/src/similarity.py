"""TF-IDF 与 Word2Vec 语义相似度。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class SimilarityResult:
    tfidf: np.ndarray
    word2vec: np.ndarray
    vocabulary_size: int


def _sentence_vector(model: Word2Vec, tokens: list[str]) -> np.ndarray:
    vectors = [model.wv[token] for token in tokens if token in model.wv]
    if not vectors:
        return np.zeros(model.vector_size, dtype=float)
    return np.mean(vectors, axis=0)


def _safe_pairwise_cosine(left: list[np.ndarray], right: list[np.ndarray]) -> np.ndarray:
    if not left or not right:
        return np.zeros((len(left), len(right)), dtype=float)
    matrix = cosine_similarity(np.vstack(left), np.vstack(right))
    return np.clip(matrix, 0.0, 1.0)


def calculate_similarities(
    resume_tokens: list[list[str]],
    job_tokens: list[list[str]],
    seed: int = 42,
) -> SimilarityResult:
    if not resume_tokens or not job_tokens:
        raise ValueError("简历和岗位数据均不能为空")
    documents = resume_tokens + job_tokens
    texts = [" ".join(tokens) for tokens in documents]

    vectorizer = TfidfVectorizer(
        token_pattern=r"(?u)\b[\w+#.\-]+\b",
        sublinear_tf=True,
        ngram_range=(1, 2),
    )
    tfidf_vectors = vectorizer.fit_transform(texts)
    split = len(resume_tokens)
    tfidf_scores = cosine_similarity(tfidf_vectors[:split], tfidf_vectors[split:])

    model = Word2Vec(
        sentences=documents,
        vector_size=80,
        window=5,
        min_count=1,
        workers=1,
        sg=1,
        seed=seed,
        epochs=160,
    )
    resume_vectors = [_sentence_vector(model, tokens) for tokens in resume_tokens]
    job_vectors = [_sentence_vector(model, tokens) for tokens in job_tokens]
    word2vec_scores = _safe_pairwise_cosine(resume_vectors, job_vectors)

    return SimilarityResult(
        tfidf=np.clip(tfidf_scores, 0.0, 1.0),
        word2vec=word2vec_scores,
        vocabulary_size=len(model.wv),
    )
