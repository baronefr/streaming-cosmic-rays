#!/bin/bash

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

echo " stop kafka | using cfg: $COSMO_CONFIG_PATH"
source <(grep = $COSMO_CONFIG_PATH/kafka.ini)


# note:  make sure that  delete.topic.enable  is true in kafka config file
echo " > deleting topics"
for i in ${!TOPICS[@]}; do
    $KAFKA_BIN/kafka-topics.sh --delete --topic ${TOPICS[$i]}  --bootstrap-server localhost:$BOOTSTRAP_PORT
done

echo " > stopping servers"
$KAFKA_BIN/kafka-server-stop.sh
echo "waiting ..."
sleep 3
$KAFKA_BIN/zookeeper-server-stop.sh

exit 0