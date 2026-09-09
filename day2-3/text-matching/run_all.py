"""依次运行四份讲义中的全部可执行示例。"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPARK_DEMO = "08_pyspark_word2vec_preview.py"


def discover_scripts(skip_spark: bool) -> list[Path]:
    scripts = sorted(ROOT.glob("text_matching_demo_*/[0-9][0-9]_*.py"))
    if skip_spark:
        scripts = [script for script in scripts if script.name != SPARK_DEMO]
    return scripts


def run_script(script: Path) -> None:
    relative = script.relative_to(ROOT)
    print(f"\n{'=' * 88}\n运行 {relative}\n{'=' * 88}", flush=True)
    env = os.environ.copy()
    env.setdefault("PYTHONHASHSEED", "0")
    env.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
    subprocess.run(
        [sys.executable, script.name],
        cwd=script.parent,
        env=env,
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-spark",
        action="store_true",
        help="跳过启动较慢的 PySpark MLlib 示例",
    )
    args = parser.parse_args()

    scripts = discover_scripts(args.skip_spark)
    if not scripts:
        raise RuntimeError("没有找到案例脚本")

    for script in scripts:
        run_script(script)

    print(f"\n全部通过：成功运行 {len(scripts)} 个示例。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
