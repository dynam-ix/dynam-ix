Running the experiments
---------------

`bash run.bash HOST_FILE KEY_PATH ORDERER_IP REQUESTS SLEEP`, where: <br/>

* HOST_FILE: File with the addresses of the VMs (one per line) <br/>
* KEY_PATH: Path to the key to connect to the AWS virtual machines <br/>
* ORDERER_IP: IP address of the host running the ordering system <br/>
* REQUESTS: Number of requests each AS will send <br/>
* SLEEP: Interval between two consecutive requests from the same AS <br/>