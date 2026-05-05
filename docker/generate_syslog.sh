#!/bin/bash

LOG_LINUX="${1:-/var/log/syslog/linux.log}"
LOG_CISCO="${2:-/var/log/syslog/cisco.log}"
EVENT_COUNT="${3:-100}"

mkdir -p "$(dirname "$LOG_LINUX")"
mkdir -p "$(dirname "$LOG_CISCO")"

HOSTNAMES=("webserver-01" "appserver-02" "db-master" "cache-redis" "loadbalancer")
CISCO_HOSTNAMES=("core-switch-01" "dist-switch-02" "edge-router-01")
IPS=("192.168.1.$((RANDOM % 254 + 1))" "10.0.0.$((RANDOM % 254 + 1))" "172.16.0.$((RANDOM % 254 + 1))")

generate_linux_syslog() {
    local pri=$1
    local timestamp=$2
    local hostname=$3
    local app=$4
    local pid=$5
    local msg=$6

    echo "<$pri>1 $timestamp $hostname $app $pid - - $msg"
}

generate_cisco_cef() {
    local device=$1
    local version=$2
    local device_type=$3
    local syslog_id=$4
    local name=$5
    local severity=$6
    local src=$7
    local dst=$8
    local spt=$9
    local dpt=${10}

    echo "CEF:$version|$device|$device_type|$syslog_id|$name|$severity|src=$src dst=$dst spt=$spt dpt=$dpt"
}

HALF=$((EVENT_COUNT / 2))

for i in $(seq 1 $HALF); do
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    HOSTNAME=${HOSTNAMES[$((RANDOM % ${#HOSTNAMES[@]}))]}
    APP=${HOSTNAMES[$((RANDOM % ${#HOSTNAMES[@]}))]}
    PID=$((RANDOM % 65535))
    SRC_IP=${IPS[$((RANDOM % ${#IPS[@]}))]}
    DST_IP=${IPS[$((RANDOM % ${#IPS[@]}))]}
    SPORT=$((RANDOM % 50000 + 1024))
    DPORT=$((RANDOM % 3))
    case $DPORT in
        0) DPORT=22 ;;
        1) DPORT=443 ;;
        2) DPORT=80 ;;
    esac

    MSG_TYPE=$((RANDOM % 8))

    case $MSG_TYPE in
        0) MSG="SSH login attempt from $SRC_IP to $DST_IP port $DPORT";;
        1) MSG="Accepted password for ubuntu from $SRC_IP port $SPORT ssh2";;
        2) MSG="Failed password for invalid user admin from $SRC_IP port $SPORT ssh2";;
        3) MSG="Connection from $SRC_IP port $SPORT: ssh2";;
        4) MSG="Did not receive identification string from $SRC_IP port $SPORT";;
        5) MSG="Server listening on 0.0.0.0 port $DPORT";;
        6) MSG="Received disconnect from $SRC_IP port $SPORT:11: disconnected by user";;
        7) MSG="Invalid user admin from $SRC_IP port $SPORT";;
    esac

    generate_linux_syslog 34 "$TIMESTAMP" "$HOSTNAME" "$APP" "$PID" "$MSG" >> "$LOG_LINUX"
done

for i in $(seq 1 $HALF); do
    DEVICE=${CISCO_HOSTNAMES[$((RANDOM % ${#CISCO_HOSTNAMES[@]}))]}
    SRC_IP=${IPS[$((RANDOM % ${#IPS[@]}))]}
    DST_IP=${IPS[$((RANDOM % ${#IPS[@]}))]}
    SPORT=$((RANDOM % 50000 + 1024))
    DPORT=$((RANDOM % 3))
    case $DPORT in
        0) DPORT=22 ;;
        1) DPORT=443 ;;
        2) DPORT=80 ;;
    esac

    SEVERITY=$((RANDOM % 3 + 3))
    MSG_NUM=$((RANDOM % 5 + 1))

    case $MSG_NUM in
        1) NAME="Login successful";;
        2) NAME="Login failed";;
        3) NAME="Access denied";;
        4) NAME="SSH connection";;
        5) NAME="Network alert";;
    esac

    generate_cisco_cef "$DEVICE" "0" "IOS" "12.4" "$MSG_NUM" "$NAME" "$SEVERITY" "$SRC_IP" "$DST_IP" "$SPORT" "$DPORT" >> "$LOG_CISCO"
done

echo "Generated $EVENT_COUNT syslog events:"
echo "  $HALF Linux RFC5424 events -> $LOG_LINUX"
echo "  $HALF Cisco CEF events -> $LOG_CISCO"
