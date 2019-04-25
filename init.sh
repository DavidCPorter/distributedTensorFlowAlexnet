#! /bin/bash
#
# Usage: init.sh <username>

if [ "$#" -ne 1 ]; then
	echo 'init.sh <username>'
	exit
fi

USERNAME=$1

# FIle with host names
HOSTS='./hosts'

# Checks ssh connection and fingerprints
#ssh-keyscan -f $HOSTS >> ~/.ssh/known_hosts


# Installs trensorflow on the cluster
source cluster_utils.sh
install_tensorflow $USERNAME

