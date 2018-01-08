#!/bin/bash

# Environment variables
DYNAMIX_DIR=$HOME/dynam-ix
NUM_ORGS=$1
EXPERIMENT=${NUM_ORGS}-experiment

echo $DYNAMIX_DIR
echo $NUM_ORGS
echo $EXPERIMENT

# Exit in case of errors
set -ev

# Create directory for the experiment
echo "Creating directory ${DYNAMIX_DIR}/experiments/${EXPERIMENT}"
mkdir -p ${DYNAMIX_DIR}/experiments/${EXPERIMENT}

# Enter experiment directory
echo "Entering directory ${DYNAMIX_DIR}/experiments/${EXPERIMENT}"
cd ${DYNAMIX_DIR}/experiments/${EXPERIMENT}

# Generate crypto-config.yaml
echo "Generating cryto-config.yaml file"
python ${DYNAMIX_DIR}/scripts/generateCryptoConfig.py $NUM_ORGS > crypto-config.yaml
# Generate configtx.yaml
echo "Generating configtx.yaml file"
python ${DYNAMIX_DIR}/scripts/generateConfigtx.py $NUM_ORGS > configtx.yaml

# Generate certifactes
echo "Generating certificates"
$DYNAMIX_DIR/bin/cryptogen generate --config=./crypto-config.yaml 

echo "Generating channel artifacts"
mkdir -p config
# Genesis block
echo "Generating genesis block"
$DYNAMIX_DIR/bin/configtxgen -profile SingleOrgOrdererGenesis -outputBlock ./config/genesis.block
# Channnel
echo "Creating channel"
$DYNAMIX_DIR/bin/configtxgen -profile MultipleOrgChannel -outputCreateChannelTx ./config/channel.tx -channelID mychannel
# Anchor peer update for each org
for (( ASN=0; ASN < $NUM_ORGS; ASN++ )) do
    echo "Updating anchor peer for org $ASN" # TODO Repeat for all peers
    $DYNAMIX_DIR/bin/configtxgen -profile MultipleOrgChannel -outputAnchorPeersUpdate ./config/Org${ASN}MSPanchors.tx -channelID mychannel -asOrg Org${ASN}MSP
done
# Generate docker-compose.yaml
echo "Generating docker-compose.yaml file"
#python ${DYNAMIX_DIR}/scripts/generateDockerCompose.py $NUM_ORGS $HOSTS

echo "Configuration files generated successfully!!!"
echo "Do not forget the commit the files to the repository!"
echo "To run the experiment use ./runExperiment.sh EXPERIMENT_NAME"