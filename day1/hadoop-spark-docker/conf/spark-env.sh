# Spark 3.5.1 环境配置（与教程安装脚本一致）
# 让 Spark 识别本机安装的 Hadoop / JDK，实现 Spark on YARN 与 HDFS 读写
export JAVA_HOME=/usr/local/java
export SPARK_HOME=/usr/local/spark
export HADOOP_HOME=/usr/local/hadoop
export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop

# 将 Hadoop 依赖加入 Spark 类路径（HDFS/YARN 客户端所需）
export SPARK_DIST_CLASSPATH=$($HADOOP_HOME/bin/hadoop classpath)

# PySpark 使用 ai_env 虚拟环境中的 Python
export PYSPARK_PYTHON=/root/ai_env/bin/python3
export PYSPARK_DRIVER_PYTHON=/root/ai_env/bin/python3
