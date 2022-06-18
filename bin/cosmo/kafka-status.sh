#!/bin/bash -e

#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 10 / Barone Nagaro Ninni Valentini
#
#  This script checks the status/properties of a 
#  Kafka server.
#
#--------------------------------------------------------
#  coder: Barone Francesco, last edit: 10 jun 2022
#  Open Access licence
#--------------------------------------------------------

echo " interact kafka | using cfg: $COSMO_CONFIG_PATH"
source <(grep = $COSMO_CONFIG_PATH/main.ini)

if [ "$1" = "list" ]; then
    echo " > list of available topics"
    $KAFKA_BIN/kafka-topics.sh --list --bootstrap-server $KAFKA_BOOTSTRAP
    
elif [ $1 = "describe" ]; then
    echo " > describe topics"
    for i in ${!MANAGED_TOPIC[@]}; do
        echo " -- topic ${MANAGED_TOPIC[$i]}"
        $KAFKA_BIN/kafka-topics.sh --describe --topic ${MANAGED_TOPIC[$i]} --bootstrap-server $KAFKA_BOOTSTRAP
    done
    
else
    echo 'no arg'
fi

