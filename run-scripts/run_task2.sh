#!/bin/bash
#
# Usage: run_task2.sh <username> [-profile]

if [ "$#" -lt 1 ]; then
	echo "Usage: run_task2.sh <username> [-profile]"
	exit
fi

USERNAME=$1


# cluster_utils.sh has helper function to start process on all VMs
# it contains definition for start_cluster and terminate_cluster
source cluster_utils_sync.sh
if [ "$2" == "-profile" ]; then
	echo "Running the experiment and profiling with dstat"
	start_cluster_with_dstat $USERNAME lr_SYNC.py cluster
else
	echo "Running the experiment"
	start_cluster $USERNAME lr_SYNC.py cluster
fi

# defined in cluster_utils.sh to terminate the cluster
terminate_cluster $USERNAME
#
# wait $!
#
# source cluster_utils_sync.sh
# start_cluster code_sync_SGD.py cluster
#
# # defined in cluster_utils.sh to terminate the cluster
# terminate_cluster
