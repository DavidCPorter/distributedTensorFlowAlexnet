#!/bin/bash
#
# cluster_utils.sh has helper function to start process on all VMs
# it contains definition for start_cluster and terminate_cluster
source cluster_utils_sync.sh
start_cluster lr_sync.py cluster

# defined in cluster_utils.sh to terminate the cluster
terminate_cluster
#
# wait $!
#
# source cluster_utils_sync.sh
# start_cluster code_sync_SGD.py cluster
#
# # defined in cluster_utils.sh to terminate the cluster
# terminate_cluster
