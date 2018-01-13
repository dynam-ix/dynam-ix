#!/bin/bash

export AS=$1
export NUM_TRANSACTIONS=$2
export SLEEP=$3


for (( T=1; T <= $NUM_TRANSACTIONS; T++ )) do

    # Generate agreement ID
    IA=$(date +%s%N |md5sum)

    # Register Agreement
    docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp" cli peer chaincode invoke -o orderer.example.com:7050 -C mychannel -n dynamix -c '{"function":"registerAgreement","Args":["IA-'"${IA}"'", "usahdiashmdiuuhasiudhasiudhasiuhdiusauhdiuashdiuashdiuasssaudhas", "'"${AS}"'", "'"${AS}"'", "uisaduihasiudhasiudhiuasuhdiuashdashdsaiudhiuashdas", "uisaduihasiudhasuhd12345678iuashdashdsaiudhiuashdas"]}'

    #docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp" cli peer chaincode invoke -o orderer.example.com:7050 -C mychannel -n dynamix -c '{"function":"updateCustRep","Args":["AS'"${AS}"'", "1"]}'

    sleep $SLEEP

done
