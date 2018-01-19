#!/bin/bash

export HOST_FILE=$1
export KEY_PATH=$2
export EXP_NUM=$3
export ORDERER_IP=$4
export REQUESTS=$5
export SLEEP=$6

AS=2

while IFS='' read -r line || [[ -n "$line" ]]; do

    echo $line
    #rsh -i "${KEY_PATH}" ubuntu@${line} "echo $line ; ls " &

    rsh -i "${KEY_PATH}" ubuntu@${line} "cd dynam-ix/experiments/${EXP_NUM}-experiment ; ./initPeer.bash ${AS} Transit intents.json ${ORDERER_IP} autonomous ${REQUESTS} ${SLEEP} > run.log" &

    AS=$((AS+1))

done < $HOST_FILE