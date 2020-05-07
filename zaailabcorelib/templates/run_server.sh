"""
./run_server.sh
This script is created to automatically controll process running in background
Author: congvm

To use this script, you need to specify SERVICE_NAME, SERVICE_DIR, DAEMON
Then invoke 
- ./run_server.sh start [environment]
- ./run_server.sh stop
- ./run_server.sh restart
- ./run_server.sh status

[environment] should be production, staging or development
Regarding to restart, PRODUCTION environment is set in default.

Eg: ./run_server.sh start production
"""

#====================================================
export SERVICE_NAME="<service_name>"
export SERVICE_DIR="$<service_dir>"
export DAEMON="<path_to_daemon>"

export EXEC_FILE=$SERVICE_DIR/server.py
export SERVICE_ENV_SETTING="PRODUCTION"
export DAEMONOPTS="-u $EXEC_FILE"

export LOG_DIR=$SERVICE_DIR/logs/
export LOG_FILE=$SERVICE_DIR/logs/server.log

export PID_DIR=$SERVICE_DIR/pid/
export PID_FILE=$PID_DIR/$SERVICE_NAME.pid
export FULL_DAEMON_PATH="$DAEMON $DAEMONOPTS"
#====================================================

case "$2" in
production)
    export SERVICE_ENV_SETTING="PRODUCTION"
    ;;

staging)
    export SERVICE_ENV_SETTING="STAGING"
    ;;

development)
    export SERVICE_ENV_SETTING="DEVELOPMENT"
    ;;
*)
    # printf "SERVICE_ENV_SETTING is not set. Use PRODUCTION instead\n"
    ;;
esac

list_descendants() {
    local children=$(ps -o pid= --ppid "$1")

    for pid in $children; do
        list_descendants "$pid"
    done

    printf "$children"
}

init_folder() {
    printf "\n"
    if
        [[ -d "$LOG_DIR" ]]
    then
        printf "$LOG_DIR exists on your filesystem.\n"
    else
        printf "Create $LOG_DIR...\n"
        mkdir -p $LOG_DIR
    fi

    if
        [[ -d "$PID_DIR" ]]
    then
        printf "$PID_DIR exists on your filesystem.\n"
    else
        printf "Create $PID_DIR...\n"
        mkdir -p $PID_DIR
    fi

}

case "$1" in
start)
    printf "Starting $SERVICE_NAME...\t$SERVICE_ENV_SETTING\n"
    cd $SERVICE_DIR
    # Check service started
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID >/dev/null; then
            export CUR_DAEMON_PATH="$(ps -ef | grep $PID | grep -v grep | awk '{print $8" "$9" "$10}')"
            if [[ $CUR_DAEMON_PATH == $FULL_DAEMON_PATH ]]; then
                printf "\nService has already been running!\n"
                exit 1
            else
                echo "Cannot check\n"
            fi
        fi
    fi

    init_folder
    $DAEMON $DAEMONOPTS $SERVICE_ENV_SETTING >$LOG_FILE 2>&1 &
    PID=$(echo -n $!)

    if [ -z $PID ]; then
        printf "%s\n" "Failed"
    else
        echo $PID >$PID_FILE
        printf "%s\n" "Service has been started."
    fi
    ;;
status)
    printf "Checking $SERVICE_NAME...\n"
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if [ -z "$(ps axf | grep ${PID} | grep -v grep)" ]; then
            printf "%s\n" "Process dead but PID_FILE exists"
        else
            printf "\nRunning on main process : $PID"
            printf "\nSubprocess : \n---------\n$(list_descendants $PID)\n---------\n"
        fi
    else
        printf "%s\n" "Service not running"
    fi
    ;;

stop)
    printf "Stopping $SERVICE_NAME\n"
    PID=$(cat $PID_FILE)
    cd $SERVICE_DIR
    if [ -f $PID_FILE ]; then
        printf "\n---------\n $PID \t\n$(list_descendants $PID)\n---------\n"
        kill -HUP $(list_descendants $PID)
        kill -HUP $PID
        printf "Service has been stopped.\n"
        rm -f $PID_FILE
    else
        printf "%s\n" "PID_FILE not found"
    fi
    ;;

restart)
    $0 stop
    printf "\nRestarting ...\n"
    $0 start $SERVICE_ENV_SETTING
    ;;

*)
    echo "Usage: $0 {status|start|stop|restart}"
    exit 1
    ;;
esac
