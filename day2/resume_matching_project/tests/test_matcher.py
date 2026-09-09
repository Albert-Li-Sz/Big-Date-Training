"""核心算法与数据链路的回归测试。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.data_io import load_jobs, load_resumes
from src.matcher import DEFAULT_JOBS, DEFAULT_RESUMES, ResumeJobMatcher
from src.preprocess import normalize_skill, normalize_skill_set, tokenize
from src.scoring import coverage_score, education_score, experience_score, salary_score


class PreprocessTests(unittest.TestCase):
    def test_skill_aliases_are_normalized(self) -> None:
        self.assertEqual(normalize_skill("PySpark"), "spark")
        self.assertEqual(normalize_skill("SpringBoot"), "spring boot")
        self.assertEqual(
            normalize_skill_set("Python;Power BI;K8s"),
            {"python", "powerbi", "kubernetes"},
        )

    def test_tokenize_filters_stopwords(self) -> None:
        tokens = tokenize("负责使用 Python 与 Spark 进行数据分析")
        self.assertIn("python", tokens)
        self.assertIn("spark", tokens)
        self.assertNotIn("负责", tokens)


class ScoringTests(unittest.TestCase):
    def test_rule_scores_have_expected_boundaries(self) -> None:
        self.assertEqual(coverage_score({"python"}, set()), 100)
        self.assertEqual(coverage_score({"python"}, {"python", "sql"}), 50)
        self.assertEqual(education_score("本科", "大专"), 100)
        self.assertEqual(experience_score(1, 2), 50)
        self.assertEqual(salary_score(0, 5000), 100)


class MatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.resumes = load_resumes(DEFAULT_RESUMES)
        cls.jobs = load_jobs(DEFAULT_JOBS)
        cls.matcher = ResumeJobMatcher(cls.resumes, cls.jobs)
        cls.results = cls.matcher.match_all()

    def test_example_data_meets_project_scale(self) -> None:
        self.assertGreaterEqual(len(self.resumes), 10)
        self.assertGreaterEqual(len(self.jobs), 8)

    def test_cross_product_and_scores(self) -> None:
        self.assertEqual(len(self.results), len(self.resumes) * len(self.jobs))
        self.assertTrue(self.results["total_score"].between(0, 100).all())
        self.assertTrue(self.results["skill_score"].between(0, 100).all())
        for _, group in self.results.groupby("resume_id"):
            self.assertEqual(group["resume_rank"].tolist(), list(range(1, len(self.jobs) + 1)))

    def test_obvious_matches_rank_near_top(self) -> None:
        r001 = self.results[self.results["resume_id"] == "R001"].nsmallest(2, "resume_rank")
        self.assertIn("J001", set(r001["job_id"]))
        self.assertIn("J002", set(r001["job_id"]))

    def test_export_creates_both_perspectives(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = self.matcher.export(Path(temp_dir), top_n=3)
            self.assertEqual(set(paths), {"full_matches", "top_matches", "top_candidates"})
            self.assertTrue(all(path.exists() for path in paths.values()))


if __name__ == "__main__":
    unittest.main()
