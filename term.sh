#!/bin/bash


function terminate_cluster() {
    echo "Terminating the servers"
#    CMD="ps aux | grep -v 'grep' | grep 'python code_template' | awk -F' ' '{print $2}' | xargs kill -9"
    CMD="ps aux | grep -v 'grep' | grep -v 'bash' | grep -v 'ssh' | grep 'python3*' | awk -F ' ' '{print $2}' | xargs kill -9"
    for i in `seq 0 3`; do
        ssh dporte7@node$i "$CMD" >> serverlog-ps-0.out 2>&1
    done
    echo "Terminated"
}
