"""运行本地匹配；可选继续执行 HDFS/PySpark 数据链路。"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from src.hdfs_utils import upload_raw, upload_results
from src.matcher import ResumeJobMatcher


ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-hdfs", action="store_true")
    parser.add_argument("--skip-spark-word2vec", action="store_true")
    parser.add_argument("--top-n", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    matcher = ResumeJobMatcher.from_csv()
    paths = matcher.export(top_n=args.top_n)
    print(f"本地匹配完成：{len(matcher.resumes)} × {len(matcher.jobs)}")
    for path in paths.values():
        print(path)

    if args.with_hdfs:
        upload_raw()
        spark_command = ["spark-submit", str(ROOT / "src" / "spark_job.py")]
        if args.skip_spark_word2vec:
            spark_command.append("--skip-word2vec")
        subprocess.run(spark_command, cwd=ROOT, check=True)
        upload_results()
        print("HDFS 上传、PySpark 清洗和结果回写均已完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
