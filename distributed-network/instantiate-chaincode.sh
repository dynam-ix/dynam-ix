PEERS=( 'peer0' 'peer1' 'peer2' 'peer3' 'peer4' 'peer5' 'peer6' 'peer7' )
NPEERS_PER_ORG=2

setGlobals () {
    PEER_ID=$1
    ORG_ID=$(($PEER_ID/$NPEERS_PER_ORG))
    export CORE_PEER_LOCALMSPID="Org${ORG_ID}MSP"
    export CORE_PEER_MSPCONFIGPATH=/root/bcnetwork/conf/crypto-config/peerOrganizations/org${ORG_ID}/users/Admin@org${ORG_ID}/msp
    export CORE_PEER_ADDRESS=${PEERS[$PEER_ID]}:7051
}

instantiateChaincode () {
    PEER=$1
    setGlobals $PEER
    peer chaincode instantiate -o orderer0:7050 -C $CHANNEL_NAME -n dynamix -v 1.0 -c '{"Args":["init"]}' -P "AND ('Org0MSP.member','Org1MSP.member', 'Org2MSP.member', 'Org3MSP.member')" >&log.txt
}

instantiateChaincode 0