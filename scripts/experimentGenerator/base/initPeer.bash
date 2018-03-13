#!/bin/sh

# Environment variables
export DYNAMIX_DIR=$HOME/dynam-ix-beta 
export AS=$1               #1234
export SERVICE=$2          #"Transit Provider"
export INTENT_FILE=$3      #/path/to/intent/file
export ORDERER_IP=$4       #192.168.1.130
export MODE=$5
export REQUESTS=$6
export INTERVAL=$7
export USER="org${AS}"
export COMPOSE_PROJECT_NAME="net"

# Exit in case of errors
set -e

# Get IP address
export ADDRESS=$(ifconfig eth0 | grep "inet addr" | cut -d ':' -f 2 | cut -d ' ' -f 1):7052 # You may need to change the network interface (eth0)

# Erase previous CA-Server DB
sudo rm ca-server-config/fabric-ca-server.db

# Getting KEYFILE
echo "Getting KEYFILE"
cd crypto-config/peerOrganizations/org${AS}.example.com/ca/
export KEYFILE=$(ls *_sk) 

# Cleaning any previous experiment
echo "Cleaning docker environment"
docker rm -f $(docker ps -aq)
docker rmi $(docker images dev-* -q)
docker network prune -f
docker-compose -f docker-compose-base.yml down # use $HOME/.local/bin/docker-compose in case of errors

# Start Docker Containers
echo "Staring docker containers"
docker-compose -f docker-compose-base.yml up -d peer ca couchdb cli # use $HOME/.local/bin/docker-compose in case of errors

# Wait the proper initialization of the containers
echo "Waiting the proper initialization of the containers"
sleep 12    #increase in case of errors

# Do not forget to pull the repository to get the genesis block. You only need to do this once

# Join channel
echo "Joining channel"
docker exec -e "CORE_PEER_LOCALMSPID=Org${AS}MSP" -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@org${AS}.example.com/msp" peer0.org${AS}.example.com peer channel join -b /etc/hyperledger/configtx/mychannel.block

# Install chaincode
echo "Installing chaincode"
docker exec -e "CORE_PEER_LOCALMSPID=Org${AS}MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org${AS}.example.com/users/Admin@org${AS}.example.com/msp" cli peer chaincode install -n dynamix -v 1.0 -p github.com/

# Dynam-IX
echo "Entering Dynam-IX directory"
cd $DYNAMIX_DIR/src

# Install node depencies
echo "Installing dependencies"
npm install

# Remove previous keys
echo "Cleaning previous keys"
rm -rf hfc-key-store/

# Enroll admin user
echo "Creating admin"
node enrollAdmin.js Org${AS}MSP

# Register regular user
echo "Registering user"
node registerUser.js org${AS} Org${AS}MSP

# Run Dynam-IX
echo "Starting Dynam-IX with $AS, $ADDRESS, $SERVICE, $INTENT_FILE, $USER, $ORDERER_IP, $MODE, $REQUESTS, $INTERVAL"
python dynamix.py AS${AS} $ADDRESS $SERVICE $INTENT_FILE $USER $ORDERER_IP $MODE $REQUESTS $INTERVAL