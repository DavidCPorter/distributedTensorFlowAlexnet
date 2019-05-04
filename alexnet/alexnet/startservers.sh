#!/bin/bash
#
# Usage: run_task1-fullcluster.sh <username> [-profile]

if [ "$#" -lt 2 ]; then
	echo "Usage: startserver.sh <username> <mode> [-profile]"
	exit
fi

USERNAME=$1
MODE=$2

source cluster_utils_alex.sh

#start_cluster startserver.py single

if [ "$3" == "-profile" ]; then
	echo "Running the experiment and profiling with dstat"
	start_cluster_with_dstat $USERNAME startserver.py $MODE
else
	echo "Running the experiment"
	start_cluster_alex $USERNAME startserver.py $MODE
fi


# defined in cluster_utils.sh to terminate the cluster
terminate_cluster $USERNAME
