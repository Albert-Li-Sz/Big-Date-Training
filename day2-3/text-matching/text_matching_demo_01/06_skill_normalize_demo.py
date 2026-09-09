"""案例 6：技能词标准化与稳定去重。"""

from preprocess import normalize_skill, unique_in_order


raw_skills = [
    "py",
    "python",
    "Python 语言",
    "spark",
    "Apache Spark",
    "mysql",
    "机器学习",
    "Pyspark",
    "sklearn",
    "Scikit Learn",
    "数据库",
]
normalized_skills = [normalize_skill(skill) for skill in raw_skills]

print("原始技能：", raw_skills)
print("标准化后：", normalized_skills)
print("去重结果：", unique_in_order(normalized_skills))
