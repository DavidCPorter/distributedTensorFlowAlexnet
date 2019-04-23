#!/bin/bash
export TF_RUN_DIR="~/tf"
export TF_LOG_DIR="tf/log/"
export SERVER_LOG=''


function terminate_cluster() {
    echo "Terminating the servers"
#    CMD="ps aux | grep -v 'grep' | grep 'python code_template' | awk -F' ' '{print $2}' | xargs kill -9"
    CMD="ps aux | grep -v 'grep' | grep -v 'bash' | grep -v 'ssh' | grep 'python' | awk -F' ' '{print $2}' | xargs kill -9"
    for i in `seq 0 3`; do
        ssh dporte7@node$i "$CMD" >> sync_serverlog-ps-0.out 2>&1
    done
    echo "Terminated"
}


function install_tensorflow() {
    for i in `seq 0 3`; do
        nohup ssh dporte7@node$i "sudo apt update; sudo apt install --assume-yes python-pip python-dev; sudo pip install tensorflow"
    done
}


function start_cluster() {
    if [ -z $2 ]; then
        echo "Usage: start_cluster <python script> <cluster mode>"
        echo "Here, <python script> contains the cluster spec that assigns an ID to all server."
    else
        echo "Create $TF_RUN_DIR on remote hosts if they do not exist."
        echo "Copying the script to all the remote hosts."
        for i in `seq 0 3`; do
            # added log for tensorboard
            ssh dporte7@node$i "mkdir -p $TF_RUN_DIR/{log}"
            # ssh dporte7@node$i "mkdir $SERVER_LOG"
            scp lr_code/$1 dporte7@node$i:$TF_RUN_DIR
            # scp task2_output/* dporte7@node$i:$SERVER_LOG
            # ssh dporte7@node$i "tensorboard --logdir $TF_LOG_DIR"

        done
        echo "Starting tensorflow servers on all hosts based on the spec in $1"
        echo "The server output is logged to sync_serverlog-i.out, where i = 0, ..., 3 are the VM numbers."
        if [ "$2" = "single" ]; then
            nohup ssh dporte7@node0 "cd ~/tf ; python3 $1 --deploy_mode=single" > sync_serverlog-0.out 2>&1
        elif [ "$2" = "cluster" ]; then
            nohup ssh dporte7@node0 "cd ~/tf ; python3 -u $1 --deploy_mode=cluster  --job_name=ps" > sync_serverlog-ps-0.out 2>&1&
            nohup ssh dporte7@node0 "cd ~/tf ; python3 -u $1 --deploy_mode=cluster  --task_index=0" > sync_serverlog-0.out 2>&1&
            nohup ssh dporte7@node1 "cd ~/tf ; python3 -u $1 --deploy_mode=cluster  --task_index=1" > sync_serverlog-1.out 2>&1

        else
            nohup ssh dporte7@node0 "cd ~/tf ; python3 $1 --deploy_mode=cluster2  --job_name=ps" > sync_serverlog-ps-0.out 2>&1&
            nohup ssh dporte7@node0 "cd ~/tf ; python3 $1 --deploy_mode=cluster2  --task_index=0" > sync_serverlog-0.out 2>&1&
            nohup ssh dporte7@node1 "cd ~/tf ; python3 $1 --deploy_mode=cluster2  --task_index=1" > sync_serverlog-1.out 2>&1&
            nohup ssh dporte7@node2 "cd ~/tf ; python3 $1 --deploy_mode=cluster2  --task_index=2" > sync_serverlog-2.out 2>&1&
            nohup ssh dporte7@node3 "cd ~/tf ; python3 $1 --deploy_mode=cluster2  --task_index=3" > sync_serverlog-3.out 2>&1
        fi
    fi
}
