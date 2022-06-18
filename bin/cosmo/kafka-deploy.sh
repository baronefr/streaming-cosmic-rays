#!/bin/bash -e

#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 10 / Barone Nagaro Ninni Valentini
#
#  This script initializes a Kafka server (+Zookeper).
#
#--------------------------------------------------------
#  coder: Barone Francesco, last edit: 17 jun 2022
#  Open Access licence
#--------------------------------------------------------

echo " deploy kafka | using cfg: $COSMO_CONFIG_PATH"
source <(grep = $COSMO_CONFIG_PATH/main.ini)

# parameters for this script
WAIT_ZOOKEPER=4
WAIT_BROKER=3


#####################
#   deploy servers  #
#####################

echo ' > deploy Zookeeper server'
$KAFKA_BIN/zookeeper-server-start.sh $DEPLOY_ZOOKEPER_ARG
# default port: 2181
echo "   waiting ..."
sleep $WAIT_ZOOKEPER


echo ' > deploy kafka server'
$KAFKA_BIN/kafka-server-start.sh $DEPLOY_KAFKA_ARG
# default port: 9092
echo "   waiting ..."
sleep $WAIT_BROKER


#####################
#   create topics   #
#####################

echo ' > creating topics'

for i in ${!MANAGED_TOPIC[@]}; do
    echo " -- add ${MANAGED_TOPIC[$i]}"
    $KAFKA_BIN/kafka-topics.sh --create --topic ${MANAGED_TOPIC[$i]} --bootstrap-server $KAFKA_BOOTSTRAP ${MANAGED_TOPIC_ARGS[$i]}
done

echo -e "\n > list of available topics"
$KAFKA_BIN/kafka-topics.sh --list --bootstrap-server $KAFKA_BOOTSTRAP


#####################

echo ' > deploy kafka | done'
exit 0