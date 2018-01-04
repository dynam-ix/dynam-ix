#!/bin/sh

export CORE_PEER_ENDORSER_ENABLED=true
export CORE_PEER_PROFILE_ENABLED=true
export CORE_PEER_ADDRESS=peer0:7051
export CORE_PEER_CHAINCODELISTENADDRESS=peer0:7052
export CORE_PEER_ID=org0-peer0
export CORE_PEER_LOCALMSPID=Org0MSP
export CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer0:7051
export CORE_PEER_GOSSIP_USELEADERELECTION=true
export CORE_PEER_GOSSIP_ORGLEADER=false
export CORE_PEER_TLS_ENABLED=false
export CORE_PEER_TLS_KEY_FILE=/home/hyperledger/dynam-ix/distributed-network/crypto-config/peerOrganizations/org0/peers/peer0.org0/tls/server.key
export CORE_PEER_TLS_CERT_FILE=/home/hyperledger/dynam-ix/distributed-network/crypto-config/peerOrganizations/org0/peers/peer0.org0/tls/server.crt
export CORE_PEER_TLS_ROOTCERT_FILE=/home/hyperledger/dynam-ix/distributed-network/crypto-config/peerOrganizations/org0/peers/peer0.org0/tls/ca.crt
export CORE_PEER_TLS_SERVERHOSTOVERRIDE=peer0
export CORE_VM_DOCKER_ATTACHSTDOUT=true
export CORE_PEER_MSPCONFIGPATH=/home/hyperledger/dynam-ix/distributed-network/crypto-config/peerOrganizations/org0/peers/peer0.org0/msp
peer node start --peer-defaultchain=false