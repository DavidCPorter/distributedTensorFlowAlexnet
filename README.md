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

### Running the experiments

To run a given experment some useful scripts are given. 

- To run the logistic regression model in asynchronous mode do the following: `run-scripts/run-task1-cluster.sh username`
- To run the logistic regression model in synchronous mode do the following: `run-scripts/run-task2.sh username`
- To run AlexNet in distribute mode do the following: `cd alexnet/alexnet && ./startservers.sh username`

The output of the run will be logged locally. If you want to profile the experiments using __dstat__ just append to each of the above mentioned commands the '-profile' flag. The output of the proifling will be stored in an appropriate directory.  
