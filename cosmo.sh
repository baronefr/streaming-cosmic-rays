#!/bin/bash -e

#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 2202 / Barone Nagaro Ninni Valentini
#
#  This is a cluster manager for our MAPD project about
#  streaming analysis of cosmic rays.
#
#--------------------------------------------------------
#  coder: Barone Francesco, last edit: 10 jun 2022
#  Open Access licence
#--------------------------------------------------------

# the binaries to use
COSMO_BINARIES='bin/cosmo'
source $COSMO_BINARIES/general.sh

# select a config directory, this script will manage the rest
COSMO_CONFIG_PATH='config/cayde'

###########################
echo -e " ${cbBLUE}** COSMO **${cNC} - ver 0.0"
export COSMO_CONFIG_PATH
echo "loaded configuration: $COSMO_CONFIG_PATH"
echo -e "*****************************\n"
###########################

help() {
    echo " COSMO - insert a command to execute"
}



#####################
#   functions       #
#####################

kafka_deploy() {
    $COSMO_BINARIES/kafka-deploy.sh
}

kafka_stop() {
    $COSMO_BINARIES/kafka-stop.sh
}

kafka_status() {
    $COSMO_BINARIES/kafka-status.sh "$@"
}

kafka_interact() {
    $COSMO_BINARIES/kafka-interact.sh "$@"
}

dash_deploy() {
    #bokeh serve --show bin/mydash/
    bokeh serve --show bin/mydash/ --allow-websocket-origin=cayde.go:5006 # for cayde remote
}

minidt_stream() {
    ./bin/minidt_streamer.py
}

fake_analytics() {
    ./bin/fake_analytics.py
}



#####################
#   routines        #
#####################


# no command prompted
if [ $# -eq 0 ];  then
    help
    exit 0
fi


# EXECUTE ROUTINES
if [ "$1" == "start" ]; then
    kafka_deploy 
elif [ "$1" == "stop" ]; then
    kafka_stop
else
    # execute command by name
    $1 "${@:2}"
fi

exit 0