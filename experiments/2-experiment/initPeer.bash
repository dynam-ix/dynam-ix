#!/bin/sh

# Environment variables
DYNAMIX_DIR=$HOME/dynam-ix 
AS=$1               #1234
ADDRESS=$2          #10.0.0.1:5000
SERVICE=$3          #"Transit Provider"
INTENT_FILE=$4      #/path/to/intent/file
ORDERER_IP=$5       #192.168.1.130
USER=org{$AS}
COMPOSE_PROJECT_NAME="net"

# Exit in case of errors
set -ev

# Make sure to have the block to join the channel 
git pull

# Getting KEYFILE
echo "Getting KEYFILE"
cd crypto-config/peerOrganizations/org${AS}.example.com/ca/
KEYFILE = $(ls *_sk) 
cd ../../../../

# Cleaning any previous experiment
docker rm -f $(docker ps -aq)
docker rmi $(docker images dev-* -q)
docker network prune -f
docker-compose -f docker-compose-base.yml down

# Start Docker Containers
echo "Staring docker containers"
docker-compose -f docker-compose-base.yml -d peer ca couchdb cli

# Join channel
docker exec -e "CORE_PEER_LOCALMSPID=Org${AS}MSP" -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@org${AS}.example.com/msp" peer0.org${AS}.example.com peer channel join -b /etc/hyperledger/configtx/mychannel.block

# Install chaincode
docker exec -e "CORE_PEER_LOCALMSPID=Org${AS}MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org${AS}.example.com/users/Admin@org${AS}.example.com/msp" cli peer chaincode install -n dynamix -v 1.0 -p github.com/

# Dynam-IX
cd $DYNAMIX_DIR/app

# Install node depencies
npm install

# Remove previous keys
rm -rf hfc-key-store/

# Enroll admin user
node enrollAdmin.js Org${AS}MSP

# Register regular user
node registerUser.js org${AS} Org${AS}MSP

# Run Dynam-IX
python dynamix.py AS{$AS} $ADDRESS $SERVICE $INTENT_FILE $USER $ORDERER_IP