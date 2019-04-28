#!/bin/bash
#
# Usage: run_task1-cluster.sh <username> [-profile]

if [ "$#" -lt 1 ]; then
	echo "Usage: run_task1-cluster.sh <username> [-profile]"
	exit
fi

USERNAME=$1

# cluster_utils.sh has helper function to start process on all VMs
# it contains definition for start_cluster and terminate_cluster
source cluster_utils.sh

if [ "$2" == "-profile" ]; then
	echo "Running the experiment and profiling with dstat"
	start_cluster_with_dstat $USERNAME lr_original.py cluster
else
	echo "Running the experiment"
	start_cluster $USERNAME lr_original.py cluster
fi

# defined in cluster_utils.sh to terminate the cluster
terminate_cluster $USERNAME
