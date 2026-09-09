ARG UBUNTU_VERSION=24.04
FROM ubuntu:${UBUNTU_VERSION}

ARG TARGETARCH
ARG HADOOP_URL=
ARG SPARK_URL=https://mirrors.huaweicloud.com/apache/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai

RUN set -eux; \
    arch="${TARGETARCH:-$(dpkg --print-architecture)}"; \
    case "${arch}" in \
      amd64) mirror='http://mirrors.aliyun.com/ubuntu/' ;; \
      arm64) mirror='http://mirrors.aliyun.com/ubuntu-ports/' ;; \
      *) echo "Unsupported target architecture: ${arch}" >&2; exit 1 ;; \
    esac; \
    rm -f /etc/apt/sources.list.d/ubuntu.sources; \
    { \
      printf '%s\n' 'Types: deb' "URIs: ${mirror}" \
        'Suites: noble noble-updates noble-backports' \
        'Components: main restricted universe multiverse' \
        'Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg' ''; \
      printf '%s\n' 'Types: deb' "URIs: ${mirror}" \
        'Suites: noble-security' \
        'Components: main restricted universe multiverse' \
        'Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg'; \
    } > /etc/apt/sources.list.d/ubuntu.sources

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      wget \
      vim \
      net-tools \
      iproute2 \
      iputils-ping \
      procps \
      sudo \
      openssh-server \
      openssh-client \
      python3 \
      python3-venv \
      python3-pip \
      openjdk-8-jdk-headless \
 && rm -rf /var/lib/apt/lists/*

RUN java -version 2>&1 \
 && javac -version \
 && java_home="$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")" \
 && ln -s "${java_home}" /usr/local/java

ENV JAVA_HOME=/usr/local/java \
    HADOOP_HOME=/usr/local/hadoop \
    HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop \
    SPARK_HOME=/usr/local/spark \
    PYSPARK_PYTHON=/root/ai_env/bin/python3 \
    PYSPARK_DRIVER_PYTHON=/root/ai_env/bin/python3 \
    HADOOP_SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
    PATH=/usr/local/java/bin:/usr/local/hadoop/bin:/usr/local/hadoop/sbin:/usr/local/spark/bin:/usr/local/spark/sbin:$PATH

RUN printf '%s\n' \
      'JAVA_HOME="/usr/local/java"' \
      'HADOOP_HOME="/usr/local/hadoop"' \
      'HADOOP_CONF_DIR="/usr/local/hadoop/etc/hadoop"' \
      'SPARK_HOME="/usr/local/spark"' \
      'PYSPARK_PYTHON="/root/ai_env/bin/python3"' \
      'PYSPARK_DRIVER_PYTHON="/root/ai_env/bin/python3"' \
      'HADOOP_SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"' \
      'PATH="/usr/local/java/bin:/usr/local/hadoop/bin:/usr/local/hadoop/sbin:/usr/local/spark/bin:/usr/local/spark/sbin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"' \
    > /etc/environment \
 && printf '%s\n' \
      '#!/bin/sh' \
      'export JAVA_HOME=/usr/local/java' \
      'export HADOOP_HOME=/usr/local/hadoop' \
      'export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop' \
      'export SPARK_HOME=/usr/local/spark' \
      'export PYSPARK_PYTHON=/root/ai_env/bin/python3' \
      'export PYSPARK_DRIVER_PYTHON=/root/ai_env/bin/python3' \
      'export HADOOP_SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"' \
      'export PATH=$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH' \
    > /etc/profile.d/bigdata.sh \
 && chmod 755 /etc/profile.d/bigdata.sh \
 && printf '%s\n' \
      '' \
      'export JAVA_HOME=/usr/local/java' \
      'export HADOOP_HOME=/usr/local/hadoop' \
      'export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop' \
      'export SPARK_HOME=/usr/local/spark' \
      'export PYSPARK_PYTHON=/root/ai_env/bin/python3' \
      'export PYSPARK_DRIVER_PYTHON=/root/ai_env/bin/python3' \
      'export HADOOP_SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"' \
      'export PATH=$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH' \
    >> /root/.bashrc

RUN sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config \
 && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
 && install -d -m 700 /run/sshd /root/.ssh \
 && rm -f /etc/ssh/ssh_host_* /root/.ssh/id_rsa /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys \
 && printf '%s\n' 'Host *' '    StrictHostKeyChecking no' '    UserKnownHostsFile /dev/null' \
    > /root/.ssh/config \
 && chmod 600 /root/.ssh/config

RUN set -eux; \
 hadoop_url="${HADOOP_URL}"; \
 if [ -z "${hadoop_url}" ]; then \
   case "${TARGETARCH:-$(dpkg --print-architecture)}" in \
     arm64) hadoop_url='https://mirrors.huaweicloud.com/apache/hadoop/common/hadoop-3.3.6/hadoop-3.3.6-aarch64.tar.gz' ;; \
     amd64) hadoop_url='https://mirrors.huaweicloud.com/apache/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz' ;; \
     *) echo 'Unsupported target architecture for Hadoop' >&2; exit 1 ;; \
   esac; \
 fi; \
 curl -fL --retry 5 --retry-delay 2 -o /tmp/hadoop.tar.gz "${hadoop_url}" \
 && tar -xzf /tmp/hadoop.tar.gz -C /usr/local \
 && mv /usr/local/hadoop-3.3.6 /usr/local/hadoop \
 && rm -f /tmp/hadoop.tar.gz \
 && mkdir -p /usr/local/hadoop/data/namenode /usr/local/hadoop/data/datanode /usr/local/hadoop/data/tmp /usr/local/hadoop/logs

RUN curl -fL --retry 5 --retry-delay 2 -o /tmp/spark.tgz "${SPARK_URL}" \
 && tar -xzf /tmp/spark.tgz -C /usr/local \
 && mv /usr/local/spark-3.5.1-bin-hadoop3 /usr/local/spark \
 && rm -f /tmp/spark.tgz

COPY conf/core-site.xml ${HADOOP_HOME}/etc/hadoop/core-site.xml
COPY conf/hdfs-site.xml ${HADOOP_HOME}/etc/hadoop/hdfs-site.xml
COPY conf/mapred-site.xml ${HADOOP_HOME}/etc/hadoop/mapred-site.xml
COPY conf/yarn-site.xml ${HADOOP_HOME}/etc/hadoop/yarn-site.xml
COPY conf/workers ${HADOOP_HOME}/etc/hadoop/workers
COPY conf/spark-env.sh ${SPARK_HOME}/conf/spark-env.sh

RUN chmod 755 ${SPARK_HOME}/conf/spark-env.sh \
 && printf '%s\n' \
      '' \
      'export JAVA_HOME=/usr/local/java' \
      'export HDFS_NAMENODE_USER=root' \
      'export HDFS_DATANODE_USER=root' \
      'export HDFS_SECONDARYNAMENODE_USER=root' \
      'export YARN_RESOURCEMANAGER_USER=root' \
      'export YARN_NODEMANAGER_USER=root' \
    >> ${HADOOP_HOME}/etc/hadoop/hadoop-env.sh

COPY requirements-course-projects.txt /tmp/course-project-requirements.txt

RUN python3 -m venv /root/ai_env \
 && /root/ai_env/bin/python -m pip install --no-cache-dir --upgrade pip \
 && /root/ai_env/bin/python -m pip install --no-cache-dir \
      -i https://mirrors.aliyun.com/pypi/simple/ \
      --trusted-host mirrors.aliyun.com \
      -r /tmp/course-project-requirements.txt \
      streamlit jupyter \
 && rm -f /tmp/course-project-requirements.txt

ENV PATH=/root/ai_env/bin:$PATH

RUN /root/ai_env/bin/python -m pip install --no-cache-dir \
      -i https://mirrors.aliyun.com/pypi/simple/ \
      --trusted-host mirrors.aliyun.com \
      setuptools==75.8.2

RUN printf '%s\n' 'export PATH=/root/ai_env/bin:$PATH' > /etc/profile.d/ai-env.sh \
 && chmod 755 /etc/profile.d/ai-env.sh \
 && printf '%s\n' 'export PATH=/root/ai_env/bin:$PATH' >> /root/.bashrc

COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod 755 /usr/local/bin/entrypoint.sh

EXPOSE 22 9000 9870 8088 8042 4040 8888

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
