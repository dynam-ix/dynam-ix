# Dynam-IX - Dynamic Interconnection eXchange

Software version
---------------
Ubuntu 16.04 LTS <br/>
Python 2.7.12 <br/>
Pip 8.1.1 <br/>
Curl 7.47 <br/>
Npm 5.5.1 <br/>
Node JS 8.9.3 <br/>
Docker 17.06.0 <br/>
Go language 1.7.1 <br/>
Docker-compose 1.8 <br/>
Pycrypto 2.6.1 <br/>

Preparing your system
--------------
1. Download and install Go Language

- `cd $HOME/ && wget https://storage.googleapis.com/golang/go1.7.1.linux-amd64.tar.gz`

- `tar -xvf go1.7.1.linux-amd64.tar.gz`

2. Configure environment variables

- `export GOROOT=$HOME/go` 
- `export PATH=$PATH:$GOROOT/bin`
- `echo "GOROOT=$HOME/go" >> $HOME/.bashrc`
- `echo "PATH=$PATH:$GOROOT/bin" >> $HOME/.bashrc`

3. Install software

sudo apt-get update
sudo apt-get install python-pip curl npm libltdl7
pip install docker-compose pycrypto

4. Download and install Docker

wget https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/docker-ce_17.06.0~ce-0~ubuntu_amd64.deb
sudo dpkg -i docker-ce_17.06.0~ce-0~ubuntu_amd64.deb

5. Set permissions to run docker

sudo groupadd docker
sudo usermod -aG docker $USER

6. Install NodeJS

curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs

7. Download Hyperledger Fabric 1.05 Docker containers

curl -sSL https://goo.gl/byy2Qj | bash -s 1.0.5

Running the examples
--------------



Creating an experiment
--------------

