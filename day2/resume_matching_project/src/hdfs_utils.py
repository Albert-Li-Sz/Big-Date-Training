"""HDFS 目录初始化、数据上传、查看与结果下载工具。"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HDFS_BASE = "/resume_matching"


def hdfs_binary() -> str:
    executable = shutil.which("hdfs")
    if not executable:
        raise RuntimeError("未找到 hdfs 命令，请在项目 Docker 镜像内执行")
    return executable


def run_hdfs(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [hdfs_binary(), "dfs", *args],
        check=check,
        text=True,
        capture_output=False,
    )


def init_directories() -> None:
    run_hdfs(
        "-mkdir",
        "-p",
        f"{HDFS_BASE}/raw_data",
        f"{HDFS_BASE}/cleaned_data",
        f"{HDFS_BASE}/results",
    )


def upload_raw(data_dir: Path = PROJECT_ROOT / "data") -> None:
    init_directories()
    run_hdfs("-put", "-f", str(data_dir / "resumes.csv"), f"{HDFS_BASE}/raw_data/")
    run_hdfs("-put", "-f", str(data_dir / "jobs.csv"), f"{HDFS_BASE}/raw_data/")


def upload_results(output_dir: Path = PROJECT_ROOT / "output") -> None:
    init_directories()
    for name in ["full_matches.csv", "top_matches.csv", "top_candidates.csv"]:
        path = output_dir / name
        if not path.exists():
            raise FileNotFoundError(f"请先运行本地匹配，缺少：{path}")
        run_hdfs("-put", "-f", str(path), f"{HDFS_BASE}/results/")


def list_tree() -> None:
    run_hdfs("-ls", "-R", HDFS_BASE)


def download_results(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    run_hdfs("-get", "-f", f"{HDFS_BASE}/results/*", str(destination))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=["init", "upload", "upload-results", "list", "download-results"],
    )
    parser.add_argument("--destination", type=Path, default=PROJECT_ROOT / "hdfs_download")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "init":
        init_directories()
    elif args.command == "upload":
        upload_raw()
    elif args.command == "upload-results":
        upload_results()
    elif args.command == "list":
        list_tree()
    elif args.command == "download-results":
        download_results(args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
