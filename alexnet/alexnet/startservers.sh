#!/bin/bash
#
# Usage: run_task1-fullcluster.sh <username> [-profile]

if [ "$#" -lt 1 ]; then
	echo "Usage: startserver.sh <username> [-profile]"
	exit
fi

USERNAME=$1

source cluster_utils_claudio.sh

#start_cluster startserver.py single

if [ "$2" == "-profile" ]; then
	echo "Running the experiment and profiling with dstat"
	start_cluster_with_dstat $USERNAME startserver.py single
else
	echo "Running the experiment"
	start_cluster_alex $USERNAME startserver.py single
fi

# defined in cluster_utils.sh to terminate the cluster
terminate_cluster $USERNAME
