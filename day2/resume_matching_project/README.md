# 基于大数据 + AI 的简历—岗位人才匹配系统

本项目完整实现任务书要求：CSV 数据管理、jieba 清洗与技能标准化、TF-IDF/Word2Vec 语义相似度、学历/经验/城市/证书等规则评分、学生找岗位与岗位找人才双向 Top N、自然语言推荐理由、CSV 下载、HDFS 数据目录、PySpark 清洗及 MLlib Word2Vec 特征，并提供 Streamlit 可视化界面。

## 1. 项目结构

```text
resume_matching_project/
├── app.py                    # Streamlit 双向匹配界面
├── run_pipeline.py           # 本地或 HDFS + Spark 一键流程
├── data/
│   ├── resumes.csv           # 12 份示例简历
│   ├── jobs.csv              # 12 个示例岗位
│   ├── stopwords.txt
│   └── skill_alias.json
├── src/
│   ├── preprocess.py         # jieba、停用词、技能标准化
│   ├── similarity.py         # TF-IDF + gensim Word2Vec
│   ├── scoring.py            # 七维加权与解释
│   ├── matcher.py            # 全量配对与双向 Top N
│   ├── hdfs_utils.py         # HDFS 上传、查看、下载
│   └── spark_job.py          # PySpark 清洗 + MLlib Word2Vec
├── output/                   # 运行后生成的三份匹配结果
├── tests/                    # 自动化回归测试
└── docs/                     # 报告、答辩 PPT、设计稿与实测截图
```

主要交付文档：

- `docs/基于大数据与AI的简历岗位人才匹配系统项目报告.docx`：17 页项目报告；
- `docs/基于大数据与AI的简历岗位人才匹配系统答辩汇报.pptx`：12 页可编辑答辩演示；
- `docs/screenshots/`：Streamlit、HDFS、YARN 与 Spark 的本地实测截图。

## 2. 在课程镜像中运行

先进入镜像工程目录：

```bash
cd ../../day1/hadoop-spark-docker
docker compose build bigdata
docker compose up -d
docker compose ps
```

### 本地算法与结果导出

```bash
docker compose exec -T bigdata bash -lc \
  'cd /workspace/resume_matching_project && python -m src.matcher --top-n 5'
```

输出文件：

- `output/full_matches.csv`：12 × 12 的全量配对及全部维度分数；
- `output/top_matches.csv`：从学生视角推荐岗位；
- `output/top_candidates.csv`：从岗位视角推荐候选人。

权重为：技能 30%、TF-IDF 20%、Word2Vec 15%、学历 15%、经验 10%、城市 5%、证书 5%。薪资分单独计算并展示，不计入默认总分，便于教师或小组后续调整。

### Streamlit 可视化界面

```bash
docker compose exec bigdata bash -lc \
  'cd /workspace/resume_matching_project && streamlit run app.py'
```

浏览器访问 <http://localhost:8888>。界面可切换“学生找岗位 / 岗位找人才”，支持 Top N、最低分、城市筛选、自定义 CSV 上传、七维评分图和 CSV 下载。

### HDFS + PySpark 全流程

HDFS 服务由镜像启动脚本自动拉起。下面的命令会初始化 `/resume_matching`，上传原始 CSV，执行 PySpark 清洗和 MLlib Word2Vec，再把本地匹配结果写回 HDFS：

```bash
docker compose exec -T bigdata bash -lc \
  'cd /workspace/resume_matching_project && python run_pipeline.py --with-hdfs'
```

HDFS 结构：

```text
/resume_matching/
├── raw_data/                 # resumes.csv、jobs.csv
├── cleaned_data/
│   ├── resumes/              # PySpark 清洗后的 CSV
│   ├── jobs/                 # PySpark 清洗后的 CSV
│   └── word2vec_features/    # MLlib 特征 Parquet
└── results/                  # 匹配 CSV 与 Spark 汇总
```

查看 HDFS 文件：

```bash
docker compose exec -T bigdata bash -lc \
  'cd /workspace/resume_matching_project && python -m src.hdfs_utils list'
```

管理页面：HDFS <http://localhost:9870>，YARN <http://localhost:8088>。

## 3. 自动化测试

```bash
docker compose exec -T bigdata bash -lc \
  'cd /workspace/resume_matching_project && python -m unittest discover -s tests -v'
```

测试覆盖技能别名、停用词、评分边界、数据规模、全量笛卡尔积、排序合理性和双向 CSV 导出。

## 4. 自定义数据字段

简历必需字段：`resume_id,name,education,skills,experience_years,city`。

岗位必需字段：`job_id,job_title,company,required_education,required_skills,min_experience_years,city`。

技能、证书使用英文分号 `;` 分隔。可选字段缺失时系统会自动补空值；数值字段无法解析时按 0 处理；重复 ID 保留第一条。

## 5. 结果解释与边界

TF-IDF 更强调字面关键词重合，Word2Vec 用项目内语料补充语义邻近，结构化规则保证学历、经验、城市和证书可控。示例语料规模有限，模型用于课程演示和工程闭环，不应直接替代真实招聘决策。实际部署应扩大训练语料、做偏差审计，并保留人工复核。
