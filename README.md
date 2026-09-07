# Hadoop 3.3.6 + Spark 3.5.1 伪分布式大数据环境 (Ubuntu 24.04)

依据 `PPT/Class1` 课程教程（仅参考 Ubuntu 虚拟机内的配置，忽略宿主机/桌面本地配置）制作：

| 教程 | 内容 | 镜像中的实现 |
|---|---|---|
| 03.切换软件源 | apt 换阿里云源 | `/etc/apt/sources.list.d/ubuntu.sources`（DEB822，阿里云） |
| 05.安装openssh-server | ssh + 免密登录 | `openssh-server` + `ssh-keygen` 免密登录 localhost |
| 06.安装并配置Java | OpenJDK 8（Ubuntu 24.04 软件源） | `/usr/local/java` |
| 07.Hadoop伪分布式部署 | Hadoop 3.3.6 | `/usr/local/hadoop`（core/hdfs/mapred/yarn-site.xml） |
| 08.安装部署Spark | Spark 3.5.1 + ai_env | `/usr/local/spark` + `/root/ai_env`（pyspark==3.5.1 等） |
| 11.补充安装jupyter | jupyter | 已随 `ai_env` 安装 |

## 一、构建镜像

```bash
docker compose build
```

> 下载源：Hadoop/Spark 来自华为云镜像，apt 和 PyPI 来自阿里云。Java 8 使用 Ubuntu 24.04 的 `openjdk-8-jdk-headless`，会按目标架构自动安装。

> Spark 3.5.1 支持 Java 8/11/17；Java 8 低于 8u371 时会出现弃用提示。本镜像选择 Ubuntu 提供的 Java 8 更新版本，以保证 Ubuntu 24.04 的 amd64/arm64 原生构建。

支持 `linux/amd64` 和 `linux/arm64`。Dockerfile 会按架构选择阿里云的 Ubuntu 镜像路径，以及 Hadoop 对应的二进制包。

## 二、启动项目

```bash
docker compose up -d
docker compose ps          # 等待 health 变为 healthy
```

## 三、验证

```bash
# 1. 查看 Hadoop 进程（应为 NameNode/DataNode/SecondaryNameNode/ResourceManager/NodeManager 5 个）
docker exec hadoop-spark jps

# 2. Web 界面
#    HDFS:  http://localhost:9870
#    YARN:  http://localhost:8088
#    NodeManager: http://localhost:8042

# 3. HDFS 读写测试
docker exec hadoop-spark hdfs dfs -mkdir -p /test
docker exec hadoop-spark hdfs dfs -ls /

# 4. PySpark 本地模式（教程 08 步骤 5）
docker exec -it hadoop-spark bash -lc 'source /root/ai_env/bin/activate && $SPARK_HOME/bin/pyspark --master local[*]'

# 5. PySpark YARN 模式（教程 08 集群模式）
docker exec hadoop-spark bash -lc 'source /root/ai_env/bin/activate && python -c "
from pyspark.sql import SparkSession
s = SparkSession.builder.master(\"yarn\").appName(\"pyspark-yarn-test\").getOrCreate()
print(\"Spark version:\", s.version, \"-> counts:\", s.range(10).count())
s.stop()"'

# 6. Jupyter（可选；该命令前台运行）
docker exec -it hadoop-spark bash -lc 'source /root/ai_env/bin/activate && jupyter notebook --ip=0.0.0.0 --no-browser --allow-root'
# 浏览器访问 http://localhost:8888 ，token 见容器输出
```

## 四、SSH 登录（教程 05 的远程连接）

```bash
ssh root@localhost -p 2222     # 密码 root
```

端口默认只绑定到宿主机 `127.0.0.1`，避免课程环境中的 root SSH 和管理界面暴露到局域网。

## 五、常用管理命令

```bash
docker compose logs -f bigdata   # 查看启动日志
docker exec -it hadoop-spark bash

# 停止（entrypoint 会先停 YARN 再停 HDFS）
docker compose down
# 连同数据卷一起删除（重新格式化 NameNode）
docker compose down -v
```

## 六、目录结构

```
hadoop-spark-docker/
├── Dockerfile            # 镜像构建（基于 ubuntu:24.04）
├── docker-compose.yml    # 单节点伪分布式集群
├── README.md
├── conf/                 # Hadoop / Spark 配置文件
│   ├── core-site.xml     # fs.defaultFS=hdfs://localhost:9000
│   ├── hdfs-site.xml     # dfs.replication=1
│   ├── mapred-site.xml   # mapreduce.framework.name=yarn
│   ├── yarn-site.xml     # aux-services=mapreduce_shuffle
│   ├── workers           # localhost
│   └── spark-env.sh
└── scripts/
    └── entrypoint.sh     # sshd -> format -> start-dfs.sh -> start-yarn.sh
```
