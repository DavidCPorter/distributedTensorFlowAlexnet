# CS 494 - Cloud Data Center Systems

## Homework 2

### Setup Script

In order to properly set up the Tensorflow framework for the given network configuration (cluster of 4 machines) do what follows:

- Set up parallel-ssh on the cluster:
	- Do `ssh-keygen -t rsa` on the node-0
	- Copy the public key into __~/.ssh/authorized_keys__ for each machine in the cluster
	- On the master add into a file called __slaves__ the hostname of the nodes in the cluster

- Run __init_script.sh__ with root privileges (don't use  __sudo__ you just have to have root permissions on the cluster)

In our case the __slaves__ file will be like this:
```
node-0
node-1
node-2
node-3
```