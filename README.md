# CS 494 - Cloud Data Center Systems

## Homework 2

### Setup Script

In order to properly set up the Tensorflow framework for the given network configuration (cluster of 4 machines) do what follows:

- Clone this repository on your local machine 
- Set up locally the following alias for the cluster machines in the __~/.ssh/config__ file:

	`Host nodei
		Hostname <nodei_IP>
	` 

	Where `nodei` is something like `node0`,`node1` ...      
- Run __init.sh__ _username_ . Where _username_ is your name on CloudLab. The script will update the system and install the required packages. 

In our case the __~/.ssh/config__ file will be something like:
```
Host node0
        HostName node0_id_code.cloudlab.us

Host node1
        HostName node1_id_code.cloudlab.us

Host node2
        HostName node2_id_code.wisc.cloudlab.us 

Host node3
        HostName node3_id_code.wisc.cloudlab.us

```

__OBS:__ Do not use the Utah cluster, it seems to have problems with tensorflow and python3