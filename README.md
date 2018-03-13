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
**Download and install Go Language**<br/>
`cd $HOME/ && wget https://storage.googleapis.com/golang/go1.7.1.linux-amd64.tar.gz`<br/>
`tar -xvf go1.7.1.linux-amd64.tar.gz`<br/>

**Configure environment variables** <br/>
`export GOROOT=$HOME/go` <br/>
`export PATH=$PATH:$GOROOT/bin`<br/>
`echo "GOROOT=$HOME/go" >> $HOME/.bashrc`<br/>
`echo "PATH=$PATH:$GOROOT/bin" >> $HOME/.bashrc`<br/>

**Install software**<br/>
`sudo apt-get update`<br/>
`sudo apt-get install python-pip curl npm libltdl7`<br/>
`pip install docker-compose pycrypto`<br/>

**Download and install Docker**<br/>
`wget https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/docker-ce_17.06.0~ce-0~ubuntu_amd64.deb`<br/>
`sudo dpkg -i docker-ce_17.06.0~ce-0~ubuntu_amd64.deb`<br/>

**Set Docker permissions**<br/>
`sudo groupadd docker`<br/>
`sudo usermod -aG docker $USER`<br/>

**Install NodeJS**<br/>
`curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -`<br/>
`sudo apt-get install -y nodejs`<br/>

**Download Hyperledger Fabric 1.05 Docker images**<br/>
`curl -sSL https://goo.gl/byy2Qj | bash -s 1.0.5`<br/>

Running the examples
--------------



Creating an experiment
--------------

