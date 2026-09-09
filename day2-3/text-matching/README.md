# 文本匹配小案例（本地 Docker 版）

本目录实现四份讲义中的全部 35 个代码清单，并补齐了停用词、自定义词典、模型与 CSV 输出目录。示例按讲义顺序分为：

- `text_matching_demo_01`：jieba 分词、停用词、技能词标准化（9 个示例）
- `text_matching_demo_02`：词袋、TF-IDF、余弦相似度（9 个示例）
- `text_matching_demo_03_word2vec`：gensim / PySpark Word2Vec（8 个示例）
- `text_matching_demo_04`：多维评分与可解释匹配（9 个示例）

## 在项目镜像中运行

在 `day1/hadoop-spark-docker` 目录执行：

```bash
docker compose build bigdata
docker compose up -d
docker compose exec bigdata bash -lc \
  'cd /workspace/text-matching && python run_all.py'
```

若只想快速验证非 Spark 示例：

```bash
docker compose exec bigdata bash -lc \
  'cd /workspace/text-matching && python run_all.py --skip-spark'
```

运行单个示例：

```bash
docker compose exec bigdata bash -lc \
  'cd /workspace/text-matching/text_matching_demo_02 && python 08_resume_job_similarity_case.py'
```

运行单元测试：

```bash
docker compose exec bigdata bash -lc \
  'cd /workspace/text-matching && python -m unittest discover -s tests -v'
```

## 综合匹配器与扩展任务

讲义四的综合案例默认输出完整评分表：

```bash
python text_matching_demo_04/09_integrated_explainable_matcher.py
```

课堂扩展任务（证书权重、技能最低门槛、每人 Top 2）可以直接运行：

```bash
python text_matching_demo_04/09_integrated_explainable_matcher.py \
  --profile extended --min-skill-score 30 --top-n 2
```

Compose 会把本目录挂载到容器内的 `/workspace/text-matching`。CSV 结果写入 `output/`。Word2Vec 教学模型写入案例三的 `.artifacts/`；二者均为运行产物，不纳入版本控制。

> 讲义使用的是很小的教学语料。TF-IDF 结果稳定且容易解释；Word2Vec 分数只用于演示训练、推理和语义增强流程，不应当被当成生产模型效果。
