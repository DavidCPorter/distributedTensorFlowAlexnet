#!/bin/bash
#
# Usage: run_task_claudio.sh <username> <mode> [-profile]

if [ "$#" -lt 1 ]; then
	echo "Usage: run_task_claudio.sh <username> <mode> [-profile]"
	exit
fi

USERNAME=$1
MODE=$2

# cluster_utils.sh has helper function to start process on all VMs
# it contains definition for start_cluster and terminate_cluster
source cluster_utils.sh

if [ "$3" == "-profile" ]; then
	echo "Running the experiment and profiling with dstat"
	start_cluster_with_dstat $USERNAME lr_claudio.py $MODE
else
	echo "Running the experiment"
	start_cluster $USERNAME lr_claudio.py $MODE
fi

# defined in cluster_utils.sh to terminate the cluster
terminate_cluster $USERNAME
