PEERS=( 'peer0' 'peer1' 'peer2' 'peer3' 'peer4' 'peer5' 'peer6' 'peer7' )
NPEERS_PER_ORG=2

setGlobals () {
    PEER_ID=$1
    ORG_ID=$(($PEER_ID/$NPEERS_PER_ORG))
    export CORE_PEER_LOCALMSPID="Org${ORG_ID}MSP"
    export CORE_PEER_MSPCONFIGPATH=/root/bcnetwork/conf/crypto-config/peerOrganizations/org${ORG_ID}/users/Admin@org${ORG_ID}/msp
    export CORE_PEER_ADDRESS=${PEERS[$PEER_ID]}:7051
}

installChaincode () {
    PEER_ID=$1
    setGlobals $PEER_ID
    peer chaincode install -n dynamix -v 1.0 -p github.com/hyperledger/fabric/examples/chaincode/go/dynam-ix &gt;&amp;log.txt
}

for ((i=0; i<8; i++))
do
    installChaincode $i
done