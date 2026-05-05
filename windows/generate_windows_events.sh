#!/bin/bash

LOG_DIR="/var/log/windows"
EVENT_COUNT=${1:-50}

mkdir -p "$LOG_DIR"

echo "[$(date)] Generating $EVENT_COUNT sample Windows events..."

for i in $(seq 1 $EVENT_COUNT); do
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    RANDOM_USER=$((RANDOM % 5))
    USERS=("Administrator" "john.doe" "jane.smith" "service_account" "backup_user")
    USER=${USERS[$RANDOM_USER]}
    IP="192.168.1.$((RANDOM % 240 + 10))"

    # 80% success, 20% failure
    if [ $((RANDOM % 10)) -lt 8 ]; then
        EVENT_ID=4624
        MESSAGE="An account was successfully logged on."
    else
        EVENT_ID=4625
        MESSAGE="An account failed to log on."
    fi

    cat >> "$LOG_DIR/security.log" << EOF
<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
  <System>
    <EventID>$EVENT_ID</EventID>
    <TimeCreated SystemTime="$TIMESTAMP" />
    <EventRecordID>$i</EventRecordID>
  </System>
  <EventData>
    <Data Name="SubjectUserName">$USER</Data>
    <Data Name="IpAddress">$IP</Data>
    <Data Name="LogonType">3</Data>
  </EventData>
  <RenderingInfo>
    <Message>$MESSAGE</Message>
  </RenderingInfo>
</Event>
EOF

    if [ $((i % 10)) -eq 0 ]; then
        echo "  Generated $i/$EVENT_COUNT events..."
    fi
done

echo "[$(date)] Generated $EVENT_COUNT events in $LOG_DIR/security.log"
