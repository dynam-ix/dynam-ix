#!/bin/bash

# Environment variables
DYNAMIX_DIR=$HOME/dynam-ix-beta
NUM_ORGS=$1
EXPERIMENT=${NUM_ORGS}-ASes

# Exit in case of errors
set -e

# Create directory for the experiment
mkdir -p ${DYNAMIX_DIR}/experiments/

# Create directory for the experiment
echo "Creating directory ${DYNAMIX_DIR}/experiments/${EXPERIMENT}"
mkdir -p ${DYNAMIX_DIR}/experiments/${EXPERIMENT}

# Enter experiment directory
echo "Entering directory ${DYNAMIX_DIR}/experiments/${EXPERIMENT}"
cd ${DYNAMIX_DIR}/experiments/${EXPERIMENT}

# Configure FABRIC_CFG_PATH
export FABRIC_CFG_PATH=$PWD

# Generate crypto-config.yaml
echo "Generating cryto-config.yaml file"
python ${DYNAMIX_DIR}/tools/experimentGenerator/generateCryptoConfig.py $NUM_ORGS > crypto-config.yaml
# Generate configtx.yaml
echo "Generating configtx.yaml file"
python ${DYNAMIX_DIR}/tools/experimentGenerator/generateConfigtx.py $NUM_ORGS > configtx.yaml

# Generate certifactes
echo "Generating certificates"
$DYNAMIX_DIR/tools/experimentGenerator/HLFConfig/cryptogen generate --config=./crypto-config.yaml 

echo "Generating channel artifacts"
mkdir -p config
# Genesis block
echo "Generating genesis block"
$DYNAMIX_DIR/tools/experimentGenerator/HLFConfig/configtxgen -profile SingleOrgOrdererGenesis -outputBlock ./config/genesis.block
# Channnel
echo "Creating channel"
$DYNAMIX_DIR/tools/experimentGenerator/HLFConfig/configtxgen -profile MultipleOrgChannel -outputCreateChannelTx ./config/channel.tx -channelID mychannel
# Anchor peer update for each org
for (( ASN=1; ASN <= $NUM_ORGS; ASN++ )) do
    echo "Updating anchor peer for org $ASN" # TODO Repeat for all peers
    $DYNAMIX_DIR/tools/experimentGenerator/HLFConfig/configtxgen -profile MultipleOrgChannel -outputAnchorPeersUpdate ./config/Org${ASN}MSPanchors.tx -channelID mychannel -asOrg Org${ASN}MSP
done

# Generate ca-file
echo "Generating CA config file"
mkdir -p ca-server-config
python ${DYNAMIX_DIR}/tools/experimentGenerator/generateCAConfig.py $NUM_ORGS > ca-server-config/fabric-ca-server-config.yaml

# Copy base files
echo "Copying experiment base files"
cp ${DYNAMIX_DIR}/tools/experimentGenerator/base/docker-compose-base.yml ${DYNAMIX_DIR}/experiments/${EXPERIMENT}
cp ${DYNAMIX_DIR}/tools/experimentGenerator/base/initExperiment.bash ${DYNAMIX_DIR}/experiments/${EXPERIMENT}
cp ${DYNAMIX_DIR}/tools/experimentGenerator/base/initPeer.bash ${DYNAMIX_DIR}/experiments/${EXPERIMENT}
cp ${DYNAMIX_DIR}/tools/experimentGenerator/base/initOrderer.bash ${DYNAMIX_DIR}/experiments/${EXPERIMENT}

# Print instructions
echo "Configuration files generated successfully!!!"
echo "Do not forget the commit the files to the repository!"
echo "To run the experiment, go to ${DYNAMIX_DIR}/experiments/${EXPERIMENT} and run ./initExperiment.bash ASN IP:PORT SERVICE INTENTFILE ORDERER_IP"
echo "Then, on the (remote) peers, pull the git repository, go to ${DYNAMIX_DIR}/experiments/${EXPERIMENT} and run ./initPeer.bash ASN IP:PORT SERVICE INTENTFILE ORDERER_IP"