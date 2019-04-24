#!/bin/bash
export TF_LOG_DIR="tf/log/"

# run a simple program that generates logs for tensorboard
mkdir -p ~/tf/log
python3 logistic_regression.py

# start the tensorboard web server. If you have started the webserver on the VM
# a public ip, then you can view Tensorboard on the browser on your workstation
# (not the CloudLab VMs). Navigate to http://<publicip>:6006 on your browser and
# look under "GRAPHS" tab.

# Under the "GRAPHS" tab, use the options on the left to navigate to the "Run" you are interested in.
tensorboard --logdir $TF_LOG_DIR
