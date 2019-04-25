#!/bin/bash
export TF_RUN_DIR="~/tf"
export TF_LOG_DIR="tf/log/"
export SERVER_LOG=''


function terminate_cluster() {

    if [ "$#" -ne 1 ]; then
        echo "Usage: terminate_cluster <username>"
        exit 
    fi
    USER=$1

    echo "Terminating the servers"
#    CMD="ps aux | grep -v 'grep' | grep 'python code_template' | awk -F' ' '{print $2}' | xargs kill -9"
    CMD="ps aux | grep -v 'grep' | grep -v 'bash' | grep -v 'ssh' | grep 'python' | awk -F' ' '{print $2}' | xargs kill -9"
    for i in `seq 0 3`; do
        ssh $USER@node$i "$CMD" >> sync_serverlog-ps-0.out 2>&1
    done
    CMD="ps aux | grep python | grep $USER | awk -F' ' '{print \$2}' | xargs kill -9"
    for i in `seq 0 3`; do
        ssh $USER@node$i "$CMD" >> serverlog-ps-0.out 2>&1
    done
    echo "Terminated"
}


function install_tensorflow() {

    if [ "$#" -ne 1 ]; then
        echo "Usage: install_tensorflow <username>"
        exit 
    fi
    USER=$1
    PK_LIST=('tensorflow' 'sklearn')

    for i in `seq 0 3`; do
        nohup ssh $USER@node$i "sudo apt update; sudo apt install --assume-yes htop python3-pip python-dev;"
    done

    for p in ${PK_LIST[@]}; do
        echo "installing $p"
        install_py_package $USER $p
    done
}

function install_py_package() {
    
    if [ "$#" -ne 2 ]; then
        echo "Usage: install_tensorflow <username> <package_name>"
        exit 
    fi
    USER=$1
    PACKAGE=$2

    for i in `seq 0 3`; do
        nohup ssh $USER@node$i "sudo pip3 install $PACKAGE;"
    done

}

function start_cluster() {
    if [ "$#" -ne $3 ]; then
        echo "Usage: start_cluster <username> <python script> <cluster mode>"
        echo "Here, <python script> contains the cluster spec that assigns an ID to all server."
    else
        USER=$1
        PY_SCRIPT=$2
        CLUSTER_MODE=$3

        echo "Create $TF_RUN_DIR on remote hosts if they do not exist."
        echo "Copying the script to all the remote hosts."
        for i in `seq 0 3`; do
            # added log for tensorboard
            ssh $USER@node$i "mkdir -p $TF_RUN_DIR/{log}"
            # ssh $USER@node$i "mkdir $SERVER_LOG"
            scp lr_code/$PY_SCRIPT $USER@node$i:$TF_RUN_DIR
            # scp task2_output/* $USER@node$i:$SERVER_LOG
            # ssh $USER@node$i "tensorboard --logdir $TF_LOG_DIR"

        done
        echo "Starting tensorflow servers on all hosts based on the spec in $PY_SCRIPT"
        echo "The server output is logged to sync_serverlog-i.out, where i = 0, ..., 3 are the VM numbers."
        if [ "$CLUSTER_MODE" = "single" ]; then
            nohup ssh $USER@node0 "cd ~/tf ; python3 $USER --deploy_mode=single" > sync_serverlog-0.out 2>&1
        elif [ "$CLUSTER_MODE" = "cluster" ]; then
            nohup ssh $USER@node0 "cd ~/tf ; python3 -u $PY_SCRIPT --deploy_mode=cluster  --job_name=ps" > sync_serverlog-ps-0.out 2>&1&
            nohup ssh $USER@node0 "cd ~/tf ; python3 -u $PY_SCRIPT --deploy_mode=cluster  --task_index=0" > sync_serverlog-0.out 2>&1&
            nohup ssh $USER@node1 "cd ~/tf ; python3 -u $PY_SCRIPT --deploy_mode=cluster  --task_index=1" > sync_serverlog-1.out 2>&1

        else
            nohup ssh $USER@node0 "cd ~/tf ; python3 $PY_SCRIPT --deploy_mode=cluster2  --job_name=ps" > sync_serverlog-ps-0.out 2>&1&
            nohup ssh $USER@node0 "cd ~/tf ; python3 $PY_SCRIPT --deploy_mode=cluster2  --task_index=0" > sync_serverlog-0.out 2>&1&
            nohup ssh $USER@node1 "cd ~/tf ; python3 $PY_SCRIPT --deploy_mode=cluster2  --task_index=1" > sync_serverlog-1.out 2>&1&
            nohup ssh $USER@node2 "cd ~/tf ; python3 $PY_SCRIPT --deploy_mode=cluster2  --task_index=2" > sync_serverlog-2.out 2>&1&
            nohup ssh $USER@node3 "cd ~/tf ; python3 $PY_SCRIPT --deploy_mode=cluster2  --task_index=3" > sync_serverlog-3.out 2>&1
        fi
    fi
}
