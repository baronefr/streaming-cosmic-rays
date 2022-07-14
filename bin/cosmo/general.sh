#!/bin/bash

# color definitions
cRED='\033[0;31m'
cGREEN='\033[0;32m'
cYELLOW='\033[0;33m'
cBLUE='\033[0;34m'

cbRED='\033[1;31m'
cbGREEN='\033[1;32m'
cbYELLOW='\033[1;33m'
cbBLUE='\033[1;34m'

cNC='\033[0m' # No Color


# help prints
help_kafka() {
    echo " kafka hints:"
    echo "   kafka_status    list      <TOPIC>"
    echo "                   describe  <TOPIC>"
    echo "   kafka_interact  producer  <TOPIC>"
    echo "                   consumer  <TOPIC>"
}

# ini source
read_ini() {
    source <(grep = $COSMO_CONFIG_PATH/main.ini)
}

# process management
get_pid() {
    session_str=$(cat $COSMO_SESSION | grep $1)
    READ_PID=${session_str#*/}
}

check_pid() {
    # arg:  process name, pid
    if ps -p $2 > /dev/null
    then
       echo -e "$1  ... ${cbGREEN}running${cNC}"
    else
       echo -e "$1  ... ${cbRED}not running${cNC}"
    fi
}