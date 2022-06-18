#!/bin/bash -e

#  Edit   spark/conf/spark-env.sh
#  to set the worker configuration:
# SPARK_WORKER_CORES, SPARK_WORKER_INSTANCES, SPARK_WORKER_MEMORY

start-master.sh --host localhost --port 7077 --webui-port 8080
start-worker.sh spark://localhost:7077
