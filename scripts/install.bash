#/bin/bash

# Downloading and installing Go Language
cd $HOME/ && wget https://storage.googleapis.com/golang/go1.7.1.linux-amd64.tar.gz
tar -xvf go1.7.1.linux-amd64.tar.gz

mkdir $HOME/gopath
export GOPATH=$HOME/gopath 
export GOROOT=$HOME/go 
export PATH=$PATH:$GOROOT/bin

# write on $HOME/.bashrc
echo "GOPATH=$HOME/gopath" >> $HOME/.bashrc
echo "GOROOT=$HOME/go" >> $HOME/.bashrc
echo "PATH=$PATH:$GOROOT/bin" >> $HOME/.bashrc

# Download and install docker
wget https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/docker-ce_17.06.0~ce-0~ubuntu_amd64.deb
dpkg -i docker-ce_17.06.0~ce-0~ubuntu_amd64.deb

# Fix docker user issue
sudo groupadd docker
sudo usermod -aG docker $USER

# logout and login

# Verify docker installation
docker run hello-world 
apt-get install python-pip curl npm
pip install docker-compose pycrypto

# Download plaftorm specific binaries (necessary to run Dynam-IX using docker containers)
curl -sSL https://goo.gl/byy2Qj | bash -s 1.0.5
