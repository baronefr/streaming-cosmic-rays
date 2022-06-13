#!/bin/bash -e

#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 2202 / Barone Nagaro Ninni Valentini
#
#  This script deploys a Kafka server (+Zookeper).
#
#--------------------------------------------------------
#  coder: Barone Francesco, last edit: 10 jun 2022
#  Open Access licence
#--------------------------------------------------------

echo " deploy kafka | using cfg: $COSMO_CONFIG_PATH"
source <(grep = $COSMO_CONFIG_PATH/kafka.ini)

# parameters for this script
WAIT_ZOOKEPER=6
WAIT_BROKER=3


#####################
#   deploy servers  #
#####################

echo ' > deploy Zookeeper server'
$KAFKA_BIN/zookeeper-server-start.sh -daemon $COSMO_CONFIG_PATH/zookeeper.properties
# default port: 2181
echo "   waiting ..."
sleep $WAIT_ZOOKEPER


echo ' > deploy kafka server'
$KAFKA_BIN/kafka-server-start.sh -daemon $COSMO_CONFIG_PATH/kafka-server.properties
# default port: 9092
echo "   waiting ..."
sleep $WAIT_BROKER



#####################
#   create topics   #
#####################

echo ' > creating topics'

for i in ${!TOPICS[@]}; do
    echo " -- processing ${TOPICS[$i]}"
    $KAFKA_BIN/kafka-topics.sh --create --topic ${TOPICS[$i]} --bootstrap-server localhost:$BOOTSTRAP_PORT ${TOPICS_ARGS[$i]}
done

echo " > list of available topics"
$KAFKA_BIN/kafka-topics.sh --list --bootstrap-server localhost:$BOOTSTRAP_PORT


#####################

echo ' > deploy kafka | done'
exit 0