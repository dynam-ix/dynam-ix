#!/bin/bash

export AS=1
export ORDERER_IP=$1
export MODE=$2

# Get list of experiments
DIRS=($(ls))

for DIR in "${DIRS[@]}"; do
    test -d $DIR || continue
    TIMEOUT=($(echo $DIR | cut -d - -f 5))
    echo "Starting experiment $DIR"
    cd $DIR
    bash initExperiment.bash $ORDERER_IP $TIMEOUT
    cd ..
    bash blockchainSize.bash > $DIR-$MODE.log
done