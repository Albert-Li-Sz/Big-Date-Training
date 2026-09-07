#!/usr/bin/env bash
set -Eeuo pipefail

export JAVA_HOME=/usr/local/java
export HADOOP_HOME=/usr/local/hadoop
export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop
export SPARK_HOME=/usr/local/spark
export PYSPARK_PYTHON=/root/ai_env/bin/python3
export PYSPARK_DRIVER_PYTHON=/root/ai_env/bin/python3
export HADOOP_SSH_OPTS='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH"

stop_services() {
  echo '>> stopping YARN ...'
  stop-yarn.sh 2>/dev/null || true
  echo '>> stopping HDFS ...'
  stop-dfs.sh 2>/dev/null || true
}

trap 'stop_services; exit 0' TERM INT

echo ">> [1/4] starting sshd ..."
mkdir -p /run/sshd
service ssh start >/dev/null 2>&1 || /usr/sbin/sshd

for attempt in $(seq 1 30); do
  if ssh -o BatchMode=yes localhost true >/dev/null 2>&1; then
    break
  fi
  if [ "$attempt" -eq 30 ]; then
    echo 'SSH did not become ready' >&2
    exit 1
  fi
  sleep 1
done

echo ">> [2/4] checking NameNode ..."
NAMENODE_DIR="$HADOOP_HOME/data/namenode"
if [ ! -f "$NAMENODE_DIR/current/VERSION" ]; then
  echo ">> first run: formatting NameNode ..."
  hdfs namenode -format -force -nonInteractive
fi

echo ">> [3/4] starting HDFS (start-dfs.sh) ..."
start-dfs.sh

echo ">> [4/4] starting YARN (start-yarn.sh) ..."
start-yarn.sh

for attempt in $(seq 1 60); do
  namenode_ready=0
  yarn_ready=0
  curl -fsS --max-time 2 http://localhost:9870/ >/dev/null 2>&1 && namenode_ready=1 || true
  curl -fsS --max-time 2 http://localhost:8088/ >/dev/null 2>&1 && yarn_ready=1 || true
  if [ "$namenode_ready" -eq 1 ] && [ "$yarn_ready" -eq 1 ]; then
    echo '>>> Hadoop pseudo-distributed services are ready (HDFS 9870, YARN 8088)'
    break
  fi
  if [ "$attempt" -eq 60 ]; then
    echo 'Warning: Hadoop web UIs did not become ready during startup' >&2
  fi
  sleep 2
done

while true; do
  sleep 3600 &
  wait $!
done
