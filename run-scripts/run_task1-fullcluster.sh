#!/bin/bash
#
# Usage: run_task1-fullcluster.sh <username>

if [ "$#" -ne 1 ]; then
	echo "Usage: run_task1-fullcluster.sh <username>"
	exit
fi

USERNAME=$1

# cluster_utils.sh has helper function to start process on all VMs
# it contains definition for start_cluster and terminate_cluster
source cluster_utils.sh
start_cluster $USERNAME lr_original.py cluster2

# defined in cluster_utils.sh to terminate the cluster
terminate_cluster $USERNAME
