Running the experiments
---------------

**Start the ordering system**<br/>
Connect to the VM responsible for running the ordering system and run the following command: <br/>
`bash initOrderer.bash` <br/>

**Start the ordering system**<br/>
Connect to the VM responsible for running AS that will receive all the requests and run the following command: <br/>
`bash initExperiment.bash ASN IP:PORT SERVICE_DESCRIPTION INTENT_FILE ORDERER_IP MODE`, where: <br/>

* ASN: contains the Autonomous System Number (in this case, 1)
* IP:PORT: contains the IP of host and the PORT that it is going to be used by the Dynam-IX peer (e.g., 7052)
* SERVICE_DESCRIPTION: describes the type of service being offered by the AS (e.g., Transit)
* INTENT_FILE: path (relative to the src/ folder) to the intent file
* ORDERER_IP: IP address of the host running the ordering system (in this case, the same IP of the AS)
* MODE: regular or autonomous. In this case, the mode is regular.

**Start all the other ASes**<br/>
To automate the initialization process, you can run the following command from a remote host <br/>
`bash run.bash HOST_FILE KEY_PATH ORDERER_IP REQUESTS SLEEP`, where: <br/>

* HOST_FILE: File with the addresses of the VMs (one per line) <br/>
* KEY_PATH: Path to the key to connect to the AWS virtual machines <br/>
* ORDERER_IP: IP address of the host running the ordering system <br/>
* REQUESTS: Number of requests each AS will send <br/>
* SLEEP: Interval between two consecutive requests from the same AS <br/>