#!/bin/bash -e

#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 10 / Barone Nagaro Ninni Valentini
#
#  This is a cluster manager for our MAPD project about
#  streaming analysis of cosmic rays.
#
#  --------------------------------------------------
#  [!]  please add to .bashrc the following lines:
#
#   COSMO_CONFIG_PATH='config/localhost'
#   cosmo() {
#        YOUR_ABSOLUTE_PATH/cosmo.sh "$@"
#   }
#   export -f cosmo
#   export COSMO_CONFIG_PATH
#
#--------------------------------------------------------
#  coder: Barone Francesco, last edit: 19 jun 2022
#  Open Access licence
#--------------------------------------------------------

# the binaries to use
COSMO_BINARIES='bin/cosmo'
cd $(dirname $0)
source $COSMO_BINARIES/general.sh

# select a config directory, this script will manage the rest
if [ -z "${COSMO_CONFIG_PATH+xxx}" ]; then
    echo "config not set, using default";
    COSMO_CONFIG_PATH='config/cloud'
fi

###########################
echo -e " ${cbBLUE}** COSMO **${cNC} - ver 1.0"
export COSMO_CONFIG_PATH
echo "loaded configuration: $COSMO_CONFIG_PATH"
echo -e "*****************************\n"
###########################

help() {
    echo " routines _____"
    echo "   init       | start Spark & Kafka cluster"
    echo "   run        | execute the streaming analysis"
    echo "   halt       | stop the streaming analysis"
    echo "   dismiss    | stop cluster"
    echo ""
    echo "   beat       | heartbeat"
    echo ""
    echo " - alternatively, insert a specific function name (dev)"
    echo " - type help_kafka  to navigate the Kafka sources"
    echo " - type  wanda  to ask for a fairly oddparent"
    echo "-------------------------------------------------------"
    echo " MAPD B: Group 10 // Barone, Nagaro, Ninni, Valentini"
    echo " coded by Barone Francesco - @github.com/baronefr"
}


#####################
#  general config   #
#####################

read_ini

LAST_BCKPID=none

LOG_HIDDEN1='log/nohup1.log'
LOG_HIDDEN2='log/nohup2.log'
COSMO_SESSION='log/session.cosmo'


#####################
#   dev functions   #
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

dashboard() {
    bokeh serve --show $DBOARD_BIN --port $DBOARD_UI --allow-websocket-origin=$SSH_HOSTNAME:$DBOARD_UI\
    --args $COSMO_CONFIG_PATH/main.ini
}
dashboard_hidden() {
    nohup bokeh serve --show $DBOARD_BIN --port $DBOARD_UI --allow-websocket-origin=$SSH_HOSTNAME:$DBOARD_UI\
    --args $COSMO_CONFIG_PATH/main.ini > $LOG_HIDDEN1 2>&1 &
    LAST_BCKPID=$!
}


stream_minidt() {
    $DSTR_BIN $COSMO_CONFIG_PATH/main.ini
}
stream_minidt_hidden() {
    nohup $DSTR_BIN $COSMO_CONFIG_PATH/main.ini > $LOG_HIDDEN1 2>&1 &
    LAST_BCKPID=$!
}

stream_fake_analytics() {
    echo -e "${cbRED}[ ERR ]: component deprecated${cNC} (development)"
    #./bin/fake_analytics.py
}

spark_deploy() {
    $SPARK_CLUSTER_ON
}

spark_stop() {
    $SPARK_CLUSTER_OFF
}

spark_exe() {
    $SPARK_EXE $COSMO_CONFIG_PATH/main.ini
}
spark_exe_hidden() {
    nohup $SPARK_EXE $COSMO_CONFIG_PATH/main.ini > $LOG_HIDDEN2 2>&1 &
    LAST_BCKPID=$!
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
if [ "$1" == "init" ]; then
    ###  This routine initializes the Spark & Kafka servers
    
    echo -e "${cbGREEN}deploy spark${cNC}"
    spark_deploy
    
    echo -e "\n${cbGREEN}deploy kafka${cNC}"
    kafka_deploy
    

elif [ "$1" == "dismiss" ]; then
    ###  This routine dismiss the clusters
    
    echo -e "${cbRED}stop spark${cNC}"
    spark_stop
    echo -e "\n${cbRED}stop kafka${cNC}"
    kafka_stop


elif [ "$1" == "run" ]; then
    ###  This routine run the analysis
    
    # create a session file (store the PIDs)
    SESSION_ID="$(date)"
    echo "spawn run on $SESSION_ID"
    echo "COSMO | $SESSION_ID" > $COSMO_SESSION

    echo -e "${cbYELLOW}spawn spark application${cNC}"
    spark_exe_hidden
    echo "spark/$LAST_BCKPID" >> $COSMO_SESSION
    
    echo -e "${cbYELLOW}spawn dashboard${cNC}"
    dashboard_hidden
    echo "dashboard/$LAST_BCKPID" >> $COSMO_SESSION
    
    echo 'wait spawn time...'
    sleep $SPAWN_TIME
    
    echo -e "\n${cbYELLOW}spawn minidt streamer${cNC}"
    stream_minidt_hidden
    echo "stream/$LAST_BCKPID" >> $COSMO_SESSION
    

elif [ "$1" == "halt" ]; then
    ###  This routine stops the analysis
    
    set +e
    get_pid stream
    echo -e "killing ${cbRED}stream${cNC} @ $READ_PID"
    kill -9 $READ_PID
    
    get_pid spark
    echo -e "killing ${cbRED}spark${cNC} @ $READ_PID"
    kill -9 $READ_PID
    
    get_pid dashboard
    echo -e "killing ${cbRED}dashboard${cNC} @ $READ_PID"
    kill -9 $READ_PID
    set -e
    
    echo "halted $(date)" >> $COSMO_SESSION
    
elif [ "$1" == "beat" ]; then
    # heartbeat routine

    get_pid stream
    check_pid 'stream' $READ_PID
    
    get_pid spark
    check_pid 'spark ' $READ_PID
    
    get_pid dashboard
    check_pid 'dash  ' $READ_PID

elif [ "$1" == "help" ]; then
    help
elif [ "$1" == "-h" ]; then
    help
    
elif [ "$1" == "wanda" ]; then
    cat $COSMO_BINARIES/fairy.ans
else
    echo -e "${cYELLOW}dev mode${cNC}"
    # execute function by name
    $1 "${@:2}"
fi

exit 0