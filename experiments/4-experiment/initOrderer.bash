#!/bin/sh

# Environment variables
export DYNAMIX_DIR=$HOME/dynam-ix 
export AS=$1               #1234
export ADDRESS=$2          #10.0.0.1:5000
export SERVICE=$3          #"Transit Provider"
export INTENT_FILE=$4      #/path/to/intent/file
export ORDERER_IP=$5       #192.168.1.130
export MODE=$6
export USER="org${AS}"
export COMPOSE_PROJECT_NAME="net"

# Exit in case of errors
#set -v

# Erase previous CA-Server DB
sudo rm ca-server-config/fabric-ca-server.db

# Getting KEYFILE
echo "Getting KEYFILE"
cd crypto-config/peerOrganizations/org${AS}.example.com/ca/
export KEYFILE=$(ls *_sk) 
cd ../../../../

# Cleaning any previous experiment
echo "Cleaning docker environment"
docker rm -f $(docker ps -aq)
docker rmi $(docker images dev-* -q)
docker network prune -f
docker-compose -f docker-compose-base.yml down

# Start Docker Containers
echo "Staring docker containers"
docker-compose -f docker-compose-base.yml up -d orderer cli