"""案例 8：在 PySpark MLlib 中训练 Word2Vec 并生成文本向量。"""

from pyspark.ml.feature import Word2Vec
from pyspark.sql import SparkSession


spark = (
    SparkSession.builder.appName("Word2VecPreview")
    .master("local[2]")
    .config("spark.ui.enabled", "false")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

try:
    data = [
        (0, ["python", "sql", "数据分析", "可视化"]),
        (1, ["python", "数据挖掘", "机器学习", "模型"]),
        (2, ["java", "spring", "mysql", "后端开发"]),
    ]
    frame = spark.createDataFrame(data, ["id", "words"])
    estimator = Word2Vec(
        vectorSize=20,
        minCount=1,
        maxIter=5,
        inputCol="words",
        outputCol="word2vec_features",
        seed=42,
    )
    result = estimator.fit(frame).transform(frame)
    result.select("id", "words", "word2vec_features").show(truncate=False)
finally:
    spark.stop()
