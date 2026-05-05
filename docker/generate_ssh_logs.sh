#!/bin/bash

LOG_FILE="${1:-/var/log/ssh/auth.log}"
EVENT_COUNT="${2:-50}"

mkdir -p "$(dirname "$LOG_FILE")"

USERS=("admin" "root" "ubuntu" "centos" "user" "guest" "backup" "service")
METHODS=("password" "publickey" "keyboard-interactive")
SUCCESS_RESULT="success"
FAILURE_RESULT="failure"

ATTACK_IPS=(
    "185.234.72.45"
    "103.75.152.78"
    "5.8.18.120"
    "103.42.58.33"
    "45.142.120.53"
    "192.168.1.50"
    "192.168.1.100"
    "10.0.0.25"
    "172.16.0.5"
    "203.167.89.42"
    "91.236.75.16"
    "181.214.206.93"
    "102.176.94.27"
)

generate_event() {
    local event_id=$1
    local user=$2
    local source_ip=$3
    local port=$4
    local auth_method=$5
    local session_id=$6
    local result=$7
    local timestamp=$8

    python3 -c "
import json
import uuid

event = {
    'timestamp': '$timestamp',
    'event': 'ssh_auth',
    'event_id': $event_id,
    'user': '$user',
    'source_ip': '$source_ip',
    'port': $port,
    'auth_method': '$auth_method',
    'session_id': '$session_id',
    'result': '$result',
    'message': 'SSH $result for $user from $source_ip port $port using $auth_method'
}

print(json.dumps(event))
"
}

for i in $(seq 1 $EVENT_COUNT); do
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    SESSION_ID=$(python3 -c "import uuid; print(uuid.uuid4().hex[:12].upper())")
    PORT=$((RANDOM % 50000 + 1024))

    if [ $((RANDOM % 100)) -lt 20 ]; then
        SOURCE_IP=${ATTACK_IPS[$((RANDOM % ${#ATTACK_IPS[@]}))]}
        USER=${USERS[$((RANDOM % ${#USERS[@]}))]}
        AUTH_METHOD="password"
        generate_event 1000 "$USER" "$SOURCE_IP" $PORT "$AUTH_METHOD" "$SESSION_ID" "failure" "$TIMESTAMP" >> "$LOG_FILE"
    else
        SOURCE_IP=${ATTACK_IPS[$((RANDOM % 5 + 5))]}
        USER=${USERS[$((RANDOM % 3))]}
        AUTH_METHOD=${METHODS[$((RANDOM % 2))]}
        generate_event 1001 "$USER" "$SOURCE_IP" $PORT "$AUTH_METHOD" "$SESSION_ID" "success" "$TIMESTAMP" >> "$LOG_FILE"
    fi
done

echo "Generated $EVENT_COUNT SSH events in $LOG_FILE"
LINES=$(wc -l < "$LOG_FILE")
echo "Total lines: $LINES"
