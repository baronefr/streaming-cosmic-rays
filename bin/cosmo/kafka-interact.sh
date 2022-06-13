#!/bin/bash -e

#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 2202 / Barone Nagaro Ninni Valentini
#
#  This script stops a Kafka server (+Zookeper).
#
#--------------------------------------------------------
#  coder: Barone Francesco, last edit: 10 jun 2022
#  Open Access licence
#--------------------------------------------------------

echo " interact kafka | using cfg: $COSMO_CONFIG_PATH"
source <(grep = $COSMO_CONFIG_PATH/kafka.ini)

topic=$2
echo " > connecting to topic $topic"

if [ "$1" == "consumer" ]; then
    # consumer
    $KAFKA_BIN/kafka-console-consumer.sh --topic $topic --bootstrap-server localhost:$BOOTSTRAP_PORT [--from-beginning]
    
elif [ "$1" == "producer" ]; then
    # producer
    $KAFKA_BIN/kafka-console-producer.sh --topic $topic --bootstrap-server localhost:$BOOTSTRAP_PORT
else
    echo 'no arg: use  consumer  or  producer'
fi