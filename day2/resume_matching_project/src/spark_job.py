"""从 HDFS 读取原始 CSV，使用 PySpark 清洗去重并生成 MLlib Word2Vec 特征。"""

from __future__ import annotations

import argparse
import os

from pyspark.ml.feature import RegexTokenizer, Word2Vec
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


DEFAULT_FS = "hdfs://localhost:9000"
BASE_PATH = "/resume_matching"


def build_spark(default_fs: str) -> SparkSession:
    master = os.getenv("SPARK_MASTER", "local[2]")
    return (
        SparkSession.builder.appName("ResumeJobDataPipeline")
        .master(master)
        .config("spark.hadoop.fs.defaultFS", default_fs)
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )


def read_csv(spark: SparkSession, uri: str) -> DataFrame:
    return spark.read.option("header", True).option("inferSchema", True).csv(uri)


def clean_frame(
    frame: DataFrame,
    id_column: str,
    text_columns: list[str],
) -> DataFrame:
    cleaned = frame.dropna(subset=[id_column]).dropDuplicates([id_column])
    cleaned = cleaned.fillna("")
    available = [F.coalesce(F.col(column).cast("string"), F.lit("")) for column in text_columns]
    match_text = F.lower(F.concat_ws(" ", *available))
    match_text = F.regexp_replace(match_text, r"[^0-9a-zA-Z+#.\-\u4e00-\u9fff]+", " ")
    return cleaned.withColumn("match_text", F.trim(match_text))


def generate_word2vec_features(
    resumes: DataFrame,
    jobs: DataFrame,
    output_uri: str,
) -> None:
    resume_docs = resumes.select(
        F.col("resume_id").alias("entity_id"),
        F.lit("resume").alias("entity_type"),
        "match_text",
    )
    job_docs = jobs.select(
        F.col("job_id").alias("entity_id"),
        F.lit("job").alias("entity_type"),
        "match_text",
    )
    documents = resume_docs.unionByName(job_docs)
    tokenizer = RegexTokenizer(
        inputCol="match_text",
        outputCol="tokens",
        pattern=r"\s+",
        minTokenLength=1,
    )
    tokenized = tokenizer.transform(documents)
    estimator = Word2Vec(
        inputCol="tokens",
        outputCol="features",
        vectorSize=60,
        minCount=1,
        maxIter=20,
        seed=42,
    )
    model = estimator.fit(tokenized)
    model.transform(tokenized).select(
        "entity_id", "entity_type", "match_text", "tokens", "features"
    ).write.mode("overwrite").parquet(output_uri)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--default-fs", default=DEFAULT_FS)
    parser.add_argument("--base-path", default=BASE_PATH)
    parser.add_argument("--skip-word2vec", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_uri = f"{args.default_fs}{args.base_path}"
    spark = build_spark(args.default_fs)
    spark.sparkContext.setLogLevel("WARN")
    try:
        resumes = clean_frame(
            read_csv(spark, f"{base_uri}/raw_data/resumes.csv"),
            "resume_id",
            ["name", "education", "major", "skills", "project_experience", "self_description"],
        )
        jobs = clean_frame(
            read_csv(spark, f"{base_uri}/raw_data/jobs.csv"),
            "job_id",
            ["job_title", "company", "required_skills", "job_description"],
        )

        resumes.write.mode("overwrite").option("header", True).csv(
            f"{base_uri}/cleaned_data/resumes"
        )
        jobs.write.mode("overwrite").option("header", True).csv(
            f"{base_uri}/cleaned_data/jobs"
        )
        if not args.skip_word2vec:
            generate_word2vec_features(
                resumes, jobs, f"{base_uri}/cleaned_data/word2vec_features"
            )

        summary = spark.createDataFrame(
            [
                ("resumes", resumes.count()),
                ("jobs", jobs.count()),
            ],
            ["dataset", "row_count"],
        )
        summary.coalesce(1).write.mode("overwrite").option("header", True).csv(
            f"{base_uri}/results/spark_summary"
        )
        summary.show(truncate=False)
        print(f"PySpark 清洗完成，输出目录：{base_uri}/cleaned_data")
    finally:
        spark.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
