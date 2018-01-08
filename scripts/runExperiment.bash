#!/bin/sh

# Environment variables

DYNAMIX_DIR=$HOME/dynam-ix
ASN=$1
IP=$2
SERVICE=$3
INTENT_FILE=$4
EXPERIMENT=$5
USER=org{$ASN}

set -ev

# Start Docker Containers

# orderer

# peers
    docker-compose -f docker-compose.yml -d peer0.org${ASN}.example.com ca.org${ASN}.example.com couchdb-${ASN} cli

# Create channel

# IMPORTANT !!!! copy block to shared area

# Join channel

# Install chaincode
docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp" cli peer chaincode install -n dynamix -v 1.0 -p github.com/
# Instantiate chaincode (adapt policy)
docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp" cli peer chaincode instantiate -o orderer.example.com:7050 -C mychannel -n dynamix -v 1.0 -c '{"Args":[""]}' -P "OR ('Org1MSP.member','Org2MSP.member')"
# Init (Invoke) chaincode
sleep 10
docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp" cli peer chaincode invoke -o orderer.example.com:7050 -C mychannel -n dynamix -c '{"function":"initLedger","Args":[""]}'

# Dynam-IX
cd $DYNAMIX_DIR/app

# Install node depencies
npm install

# Enroll admin user

node enrollAdmin.js Org{$ASN}MSP

# Register regular user

node registerUser.js org{$ASN} Org{$ASN}MSP

# Run Dynam-IX
python dynamix.py AS{$ASN} $IP:$PORT $SERVICE $INTENT_FILE $USER