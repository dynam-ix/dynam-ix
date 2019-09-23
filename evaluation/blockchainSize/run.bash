#!/bin/bash

export AS=1
export ORDERER_IP=$1
export MODE=$2
export SIZE=$3

# Get list of experiments
DIRS=($(ls))

for DIR in "${DIRS[@]}"; do
    test -d $DIR || continue
    TIMEOUT=($(echo $DIR | cut -d - -f 5))
    echo "Starting experiment $DIR"
    cd $DIR
    bash initExperiment.bash $ORDERER_IP $TIMEOUT
    cd ..
    if [ "$MODE" == 'score' ]; then
        echo "BABABBABABABA"
        bash blockchainSize2.bash > $DIR-$MODE.log
    fi
    if [ "$MODE" == 'report' ]; then
        echo "lalalallala"
        bash blockchainSize-report2.bash $SIZE > $DIR-$MODE-$SIZE.log
    fi
done