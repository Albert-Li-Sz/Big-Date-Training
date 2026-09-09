"""端到端人岗匹配、双向 Top N 排名与 CSV 导出。"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .data_io import clean_jobs, clean_resumes, load_jobs, load_resumes
from .preprocess import build_document, load_skill_aliases, load_stopwords
from .scoring import DEFAULT_WEIGHTS, score_pair
from .similarity import calculate_similarities


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESUMES = PROJECT_ROOT / "data" / "resumes.csv"
DEFAULT_JOBS = PROJECT_ROOT / "data" / "jobs.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "output"


class ResumeJobMatcher:
    def __init__(
        self,
        resumes: pd.DataFrame,
        jobs: pd.DataFrame,
        weights: dict[str, float] | None = None,
        seed: int = 42,
    ) -> None:
        self.resumes = clean_resumes(resumes)
        self.jobs = clean_jobs(jobs)
        self.weights = weights or DEFAULT_WEIGHTS
        self.seed = seed
        self.vocabulary_size = 0

    @classmethod
    def from_csv(
        cls,
        resumes_path: str | Path = DEFAULT_RESUMES,
        jobs_path: str | Path = DEFAULT_JOBS,
        **kwargs: object,
    ) -> "ResumeJobMatcher":
        return cls(load_resumes(resumes_path), load_jobs(jobs_path), **kwargs)

    def match_all(self) -> pd.DataFrame:
        aliases = load_skill_aliases()
        stopwords = load_stopwords()
        resume_tokens = []
        for row in self.resumes.to_dict("records"):
            tokens, _ = build_document(
                row["skills"],
                row["major"],
                row["project_experience"],
                row["self_description"],
                aliases=aliases,
                stopwords=stopwords,
            )
            resume_tokens.append(tokens)

        job_tokens = []
        for row in self.jobs.to_dict("records"):
            tokens, _ = build_document(
                row["required_skills"],
                row["job_title"],
                row["company"],
                row["job_description"],
                aliases=aliases,
                stopwords=stopwords,
            )
            job_tokens.append(tokens)

        similarities = calculate_similarities(resume_tokens, job_tokens, self.seed)
        self.vocabulary_size = similarities.vocabulary_size

        rows: list[dict[str, object]] = []
        resumes = self.resumes.to_dict("records")
        jobs = self.jobs.to_dict("records")
        for resume_index, resume in enumerate(resumes):
            for job_index, job in enumerate(jobs):
                pair = score_pair(
                    resume,
                    job,
                    float(similarities.tfidf[resume_index, job_index]),
                    float(similarities.word2vec[resume_index, job_index]),
                    self.weights,
                )
                rows.append(
                    {
                        "resume_id": resume["resume_id"],
                        "student_name": resume["name"],
                        "education": resume["education"],
                        "major": resume["major"],
                        "resume_city": resume["city"],
                        "experience_years": resume["experience_years"],
                        "job_id": job["job_id"],
                        "job_title": job["job_title"],
                        "company": job["company"],
                        "job_city": job["city"],
                        "salary": job["salary"],
                        **pair.values,
                    }
                )

        result = pd.DataFrame(rows)
        result = result.sort_values(
            ["resume_id", "total_score", "job_id"],
            ascending=[True, False, True],
            kind="mergesort",
        )
        result["resume_rank"] = result.groupby("resume_id").cumcount() + 1
        job_order = result.sort_values(
            ["job_id", "total_score", "resume_id"],
            ascending=[True, False, True],
            kind="mergesort",
        )
        job_ranks = job_order.groupby("job_id").cumcount() + 1
        result.loc[job_order.index, "job_rank"] = job_ranks.to_numpy()
        result["job_rank"] = result["job_rank"].astype(int)
        return result.sort_values(["resume_id", "resume_rank"]).reset_index(drop=True)

    def export(
        self,
        output_dir: str | Path = DEFAULT_OUTPUT,
        top_n: int = 5,
        min_skill_score: float = 0.0,
    ) -> dict[str, Path]:
        if top_n <= 0:
            raise ValueError("top_n 必须大于 0")
        if not 0 <= min_skill_score <= 100:
            raise ValueError("min_skill_score 必须位于 0~100")
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        full = self.match_all()
        eligible = full[full["skill_score"] >= min_skill_score].copy()
        eligible = eligible.sort_values(
            ["resume_id", "total_score", "job_id"],
            ascending=[True, False, True],
        )
        eligible["filtered_resume_rank"] = eligible.groupby("resume_id").cumcount() + 1
        top_matches = eligible[eligible["filtered_resume_rank"] <= top_n].copy()
        eligible = eligible.sort_values(
            ["job_id", "total_score", "resume_id"],
            ascending=[True, False, True],
        )
        eligible["filtered_job_rank"] = eligible.groupby("job_id").cumcount() + 1
        top_candidates = eligible[eligible["filtered_job_rank"] <= top_n].copy()

        paths = {
            "full_matches": output / "full_matches.csv",
            "top_matches": output / "top_matches.csv",
            "top_candidates": output / "top_candidates.csv",
        }
        full.to_csv(paths["full_matches"], index=False, encoding="utf-8-sig")
        top_matches.to_csv(paths["top_matches"], index=False, encoding="utf-8-sig")
        top_candidates.to_csv(paths["top_candidates"], index=False, encoding="utf-8-sig")
        return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resumes", type=Path, default=DEFAULT_RESUMES)
    parser.add_argument("--jobs", type=Path, default=DEFAULT_JOBS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--min-skill-score", type=float, default=0.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    matcher = ResumeJobMatcher.from_csv(args.resumes, args.jobs)
    paths = matcher.export(args.output_dir, args.top_n, args.min_skill_score)
    print(
        f"已完成 {len(matcher.resumes)} 份简历 × {len(matcher.jobs)} 个岗位的全量匹配；"
        f"Word2Vec 词表大小：{matcher.vocabulary_size}。"
    )
    for label, path in paths.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
