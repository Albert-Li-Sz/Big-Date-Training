"""案例 3：手工计算 TF。"""

from collections import Counter


tokens = ["python", "python", "spark", "sql", "数据分析", "项目"]


def calculate_tf(words: list[str]) -> dict[str, float]:
    """TF = 某词出现次数 / 当前文本总词数。"""

    if not words:
        return {}
    counts = Counter(words)
    total_count = len(words)
    return {word: count / total_count for word, count in counts.items()}


print("TF 计算结果：")
for word, tf_value in calculate_tf(tokens).items():
    print(f"{word} => {tf_value:.4f}")
