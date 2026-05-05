#!/bin/bash

LOG_DIR="/var/log/windows"
EVENT_COUNT=${1:-50}

mkdir -p "$LOG_DIR"

for i in $(seq 1 $EVENT_COUNT); do
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    RANDOM_USER=$((RANDOM % 5))
    USERS=("Administrator" "john.doe" "jane.smith" "service_account" "backup_user")
    USER=${USERS[$RANDOM_USER]}
    IP="192.168.1.$((RANDOM % 240 + 10))"

    if [ $((RANDOM % 10)) -lt 8 ]; then
        EVENT_ID=4624
        EVENT_TYPE="Security"
        MESSAGE="An account was successfully logged on."
        LOG_FILE="$LOG_DIR/security.log"
    else
        EVENT_ID=4625
        EVENT_TYPE="Security"
        MESSAGE="An account failed to log on."
        LOG_FILE="$LOG_DIR/security.log"
    fi

    echo "{\"@timestamp\":\"$TIMESTAMP\",\"event_id\":$EVENT_ID,\"event_type\":\"$EVENT_TYPE\",\"user\":\"$USER\",\"source_ip\":\"$IP\",\"message\":\"$MESSAGE\"}" >> "$LOG_FILE"
done

echo "Generated $EVENT_COUNT Windows events in $LOG_DIR"