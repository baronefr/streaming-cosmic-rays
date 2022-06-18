#!/bin/bash

#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 10 / Barone Nagaro Ninni Valentini
#
#  This script stops a Kafka server (+Zookeper).
#
#--------------------------------------------------------
#  coder: Barone Francesco, last edit: 17 jun 2022
#  Open Access licence
#--------------------------------------------------------

echo " stop kafka | using cfg: $COSMO_CONFIG_PATH"
source <(grep = $COSMO_CONFIG_PATH/main.ini)


# note:  make sure that  delete.topic.enable  is true in kafka config file
echo " > deleting topics"
for i in ${!MANAGED_TOPIC[@]}; do
    $KAFKA_BIN/kafka-topics.sh --delete --topic ${MANAGED_TOPIC[$i]}  --bootstrap-server $KAFKA_BOOTSTRAP
done

echo " > stopping servers"
$KAFKA_BIN/kafka-server-stop.sh
echo "waiting ..."
sleep 3
$KAFKA_BIN/zookeeper-server-stop.sh

exit 0