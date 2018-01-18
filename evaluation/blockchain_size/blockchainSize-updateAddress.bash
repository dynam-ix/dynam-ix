#!/bin/bash

TRANSACTIONS=0
SIZE=$(docker exec -it couchdb-1 du -h data/ | tail -n 1 | cut -f 1)
echo $TRANSACTIONS $SIZE
TRANSACTIONS=$((TRANSACTIONS+1))

docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp" cli peer chaincode invoke -o orderer.example.com:7050 -C mychannel -n dynamix -c '{"function":"registerAS","Args":["AS1", "200.132.227.120:50000", "Transit Provider", "0", "0", "asihd9asjd98asud0asid0asdsajd08as8hd98asj0djsa0djas"]}'
echo $TRANSACTIONS $SIZE
TRANSACTIONS=$((TRANSACTIONS+1))

for (( T=1; T <= 5000; T++ )) do

    docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp" cli peer chaincode invoke -o orderer.example.com:7050 -C mychannel -n dynamix -c '{"function":"updateAddress","Args":["AS1", "200.132.227.150:40000"]}'

    SIZE=$(docker exec -it couchdb-1 du -b data/ | tail -n 1 | cut -f 1)
    echo $TRANSACTIONS $SIZE
    TRANSACTIONS=$((TRANSACTIONS+1))

    docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" -e "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp" cli peer chaincode invoke -o orderer.example.com:7050 -C mychannel -n dynamix -c '{"function":"updateAddress","Args":["AS1", "200.132.227.150:50000"]}'

    SIZE=$(docker exec -it couchdb-1 du -b data/ | tail -n 1 | cut -f 1)
    echo $TRANSACTIONS $SIZE
    TRANSACTIONS=$((TRANSACTIONS+1))

done



