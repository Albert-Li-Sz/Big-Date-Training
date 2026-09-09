# 大数据与 AI 课程作业

工作区已经按课程进度整理，并统一使用 `day1/hadoop-spark-docker` 构建的本地镜像运行。

## 目录

```text
bdt/
├── day1/
│   ├── hadoop-spark-docker/   # Ubuntu 24.04 + Hadoop 3.3.6 + Spark 3.5.1 镜像
│   └── PPT/                   # 昨天的课程资料与任务
├── day2/
│   ├── 学生项目任务书：基于大数据+AI的简历-岗位人才匹配系统.pdf
│   └── resume_matching_project/  # 完整人岗匹配系统、报告与答辩 PPT
└── day2-3/
    ├── 文本匹配小案例一…四.pdf
    └── text-matching/         # 四份讲义的 35 个可运行案例
```

## 一键验证

首次下载项目：

```bash
git clone https://github.com/Albert-Li-Sz/Big-Date-Training.git
cd Big-Date-Training
```

在仓库根目录执行：

```bash
cd day1/hadoop-spark-docker
docker compose build bigdata
docker compose up -d

# day2：本地算法 + HDFS + PySpark + MLlib
docker compose exec -T bigdata bash -lc \
  'cd /workspace/resume_matching_project && python run_pipeline.py --with-hdfs'

# day2-3：按讲义顺序运行全部 35 个案例
docker compose exec -T bigdata bash -lc \
  'cd /workspace/text-matching && python run_all.py'

# day2：启动可视化界面
docker compose exec bigdata bash -lc \
  'cd /workspace/resume_matching_project && streamlit run app.py'
```

界面地址为 <http://localhost:8888>，HDFS 为 <http://localhost:9870>，YARN 为 <http://localhost:8088>。

详细说明分别见 [day1 镜像环境](day1/hadoop-spark-docker/README.md)、[day2 完整项目](day2/resume_matching_project/README.md) 与 [day2-3 文本匹配案例](day2-3/text-matching/README.md)。
