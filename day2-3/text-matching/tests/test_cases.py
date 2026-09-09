"""四组 35 个教学案例的轻量回归测试。"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TeachingCaseTests(unittest.TestCase):
    def test_all_35_scripts_exist(self) -> None:
        scripts = sorted(ROOT.glob("text_matching_demo_*/[0-9][0-9]_*.py"))
        self.assertEqual(len(scripts), 35)

    def test_case_one_preprocessing(self) -> None:
        module = load_module(
            "case_one_preprocess", "text_matching_demo_01/preprocess.py"
        )
        self.assertEqual(module.normalize_skill("PySpark"), "PySpark")
        tokens = module.preprocess_text("我会 Python、Spark 和 SQL")
        self.assertIn("Python", tokens)
        self.assertIn("Spark", tokens)

    def test_case_four_rule_scores(self) -> None:
        skill = load_module(
            "case_four_skill", "text_matching_demo_04/01_skill_score_demo.py"
        )
        education = load_module(
            "case_four_education", "text_matching_demo_04/02_education_score_demo.py"
        )
        experience = load_module(
            "case_four_experience", "text_matching_demo_04/03_experience_score_demo.py"
        )
        rules = load_module(
            "case_four_rules", "text_matching_demo_04/04_extra_rule_score_demo.py"
        )
        self.assertEqual(skill.skill_score({"python"}, {"python", "sql"}), 50)
        self.assertEqual(education.education_score("本科", "本科"), 100)
        self.assertEqual(experience.experience_score(1, 2), 50)
        self.assertEqual(rules.salary_score(0, 5000), 100)

    def test_integrated_matcher_ranks_every_student(self) -> None:
        module = load_module(
            "integrated_matcher",
            "text_matching_demo_04/09_integrated_explainable_matcher.py",
        )
        result = module.build_result(profile="extended", top_n=2)
        self.assertEqual(len(result), len(module.RESUMES) * 2)
        self.assertTrue(result["total_score"].between(0, 100).all())
        self.assertEqual(set(result["rank"]), {1, 2})


if __name__ == "__main__":
    unittest.main()
