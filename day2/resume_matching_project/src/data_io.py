"""CSV 数据读取、字段校验与基础清洗。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


RESUME_REQUIRED = {
    "resume_id",
    "name",
    "education",
    "skills",
    "experience_years",
    "city",
}
JOB_REQUIRED = {
    "job_id",
    "job_title",
    "company",
    "required_education",
    "required_skills",
    "min_experience_years",
    "city",
}
RESUME_DEFAULTS = {
    "major": "",
    "expected_salary": 0,
    "certificates": "",
    "project_experience": "",
    "self_description": "",
}
JOB_DEFAULTS = {
    "salary": 0,
    "preferred_certificates": "",
    "job_description": "",
}


def _validate_columns(frame: pd.DataFrame, required: set[str], kind: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{kind} CSV 缺少字段：{', '.join(missing)}")


def clean_resumes(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    _validate_columns(data, RESUME_REQUIRED, "简历")
    for column, default in RESUME_DEFAULTS.items():
        if column not in data:
            data[column] = default
    data = data.dropna(subset=["resume_id", "name"]).drop_duplicates("resume_id")
    data["resume_id"] = data["resume_id"].astype(str).str.strip()
    data["name"] = data["name"].astype(str).str.strip()
    data["experience_years"] = pd.to_numeric(
        data["experience_years"], errors="coerce"
    ).fillna(0).clip(lower=0)
    data["expected_salary"] = pd.to_numeric(
        data["expected_salary"], errors="coerce"
    ).fillna(0).clip(lower=0)
    text_columns = [
        "education",
        "major",
        "skills",
        "city",
        "certificates",
        "project_experience",
        "self_description",
    ]
    data[text_columns] = data[text_columns].fillna("").astype(str)
    return data.reset_index(drop=True)


def clean_jobs(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    _validate_columns(data, JOB_REQUIRED, "岗位")
    for column, default in JOB_DEFAULTS.items():
        if column not in data:
            data[column] = default
    data = data.dropna(subset=["job_id", "job_title"]).drop_duplicates("job_id")
    data["job_id"] = data["job_id"].astype(str).str.strip()
    data["job_title"] = data["job_title"].astype(str).str.strip()
    data["min_experience_years"] = pd.to_numeric(
        data["min_experience_years"], errors="coerce"
    ).fillna(0).clip(lower=0)
    data["salary"] = pd.to_numeric(data["salary"], errors="coerce").fillna(0).clip(lower=0)
    text_columns = [
        "company",
        "required_education",
        "required_skills",
        "city",
        "preferred_certificates",
        "job_description",
    ]
    data[text_columns] = data[text_columns].fillna("").astype(str)
    return data.reset_index(drop=True)


def load_resumes(path: str | Path) -> pd.DataFrame:
    return clean_resumes(pd.read_csv(path, encoding="utf-8-sig"))


def load_jobs(path: str | Path) -> pd.DataFrame:
    return clean_jobs(pd.read_csv(path, encoding="utf-8-sig"))
