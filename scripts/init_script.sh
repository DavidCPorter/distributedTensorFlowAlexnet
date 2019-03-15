#! /bin/bash

##############################################################################################
# Run the following script to set up Tensorflow on a cluster of 
# 4 machines running Ubuntu. The script has to be executed on the 
# Master machine. 
# The following assumptions holds:
# - Private network IPs: 
# 		10.10.1.1 (node-0)
# 		10.10.1.2 (node-1)
# 		10.10.1.3 (node-2)
# 		10.10.1.4 (node-3)
# - parallel-ssh configured on all cluster machines
# - root privileges of the executor
#
# Author: Claudio Montanari 
# Mail: c.montanari.95@gmail.com
##############################################################################################


USER="$(whoami)"
ABS_PATH="$(pwd)"

echo 'Testing the parallel-ssh connection...'
if [ ! -f ./slaves ]; then
	echo 'Create a file named slaves with the list of the host-name present in the cluster'
	exit
fi

parallel-ssh -i -h slaves -O StrictHostKeyChecking=no hostname

# Update the system, download and install Tensorflow

echo 'Updating the system and installing Tensorflow...'

parallel-ssh -h ./slaves -t 0 -P sudo apt-get update
parallel-ssh -h ./slaves -t 0 -P sudo apt-get install --assume-yes python-pip python-dev
parallel-ssh -h ./slaves -t 0 -P sudo pip install tensorflow

echo "Installation completed, downloading template code scripts..."

if [ ! -f ./hw2 ]; then
	mkdir hw2
fi

cd ./hw2

wget https://www2.cs.uic.edu/~brents/cs494-cdcs/assets/run_code_template.sh
wget https://www2.cs.uic.edu/~brents/cs494-cdcs/assets/cluster_utils.sh 

exit