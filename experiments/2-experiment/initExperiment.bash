#!/bin/sh

# Environment variables
export DYNAMIX_DIR=$HOME/dynam-ix 
export AS=$1               #1234
export ADDRESS=$2          #10.0.0.1:5000
export SERVICE=$3          #"Transit Provider"
export INTENT_FILE=$4      #/path/to/intent/file
export ORDERER_IP=$5       #192.168.1.130
export USER=org{$AS}
export COMPOSE_PROJECT_NAME="net"

# Exit in case of errors
set -v

# Getting KEYFILE
echo "Getting KEYFILE ${AS}"
cd crypto-config/peerOrganizations/org${AS}.example.com/ca/
export KEYFILE=$(ls *_sk) 
cd ../../../../

echo $KEYFILE

# Cleaning any previous experiment
docker rm -f $(docker ps -aq)
docker rmi $(docker images dev-* -q)
docker network prune -f
docker-compose -f docker-compose-base.yml down

# Start Docker Containers
echo "Staring docker containers"
docker-compose -f docker-compose-base.yml up -d peer ca couchdb cli orderer

# Create channel
docker exec -e "CORE_PEER_LOCALMSPID=Org${AS}MSP" -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@org${AS}.example.com/msp" peer0.org${AS}.example.com peer channel create -o orderer.example.com:7050 -c mychannel -f /etc/hyperledger/configtx/channel.tx

docker exec -e "CORE_PEER_LOCALMSPID=Org${AS}MSP" -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@org${AS}.example.com/msp" peer0.org${AS}.example.com cp mychannel.block /etc/hyperledger/configtx/

# Share the block 
git add config/mychannel.block
git commit -m "new block"
git push

# Join channel
docker exec -e "CORE_PEER_LOCALMSPID=Org${AS}MSP" -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@org${AS}.example.com/msp" peer0.org${AS}.example.com peer channel join -b /etc/hyperledger/configtx/mychannel.block

# Install chaincode
docker exec -e "CORE_PEER_LOCALMSPID=Org${AS}MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org${AS}.example.com/users/Admin@org${AS}.example.com/msp" cli peer chaincode install -n dynamix -v 1.0 -p github.com/
# Instantiate chaincode
docker exec -e "CORE_PEER_LOCALMSPID=Org${AS}MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org${AS}.example.com/users/Admin@org${AS}.example.com/msp" cli peer chaincode instantiate -o orderer.example.com:7050 -C mychannel -n dynamix -v 1.0 -c '{"Args":[""]}'
# Init (Invoke) chaincode
sleep 10
docker exec -e "CORE_PEER_LOCALMSPID=Org${AS}MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org${AS}.example.com/users/Admin@org${AS}.example.com/msp" cli peer chaincode invoke -o orderer.example.com:7050 -C mychannel -n dynamix -c '{"function":"initLedger","Args":[""]}'

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
