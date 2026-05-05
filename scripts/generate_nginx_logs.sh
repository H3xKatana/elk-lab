#!/bin/bash

LOG_FILE="${1:-/home/morta/workspace/elk-lab/logs/nginx-logs/access.log}"
DURATION=${2:-300}
RPS=${3:-10}

echo "[$(date)] Starting log generator..."
echo "Output: $LOG_FILE"
echo "Duration: ${DURATION}s @ ${RPS} entries/s"
echo "----------------------------------------"

END_TIME=$(($(date +%s) + DURATION))
COUNTER=0

while [ $(date +%s) -lt $END_TIME ]; do
    for i in $(seq 1 $RPS); do
        RAND=$((RANDOM % 9))
        TIMESTAMP=$(date -u -d "-$((RANDOM % 300)) seconds" +"%d/%b/%Y:%H:%M:%S +0000")
        CLIENT_IP="192.168.1.$((RANDOM % 240 + 10))"
        BYTES=$((RANDOM % 8000 + 200))
        METHOD="GET"
        STATUS=200

        case $RAND in
            0) ENDPOINT="/products/123"; STATUS=200 ;;
            1) ENDPOINT="/products/456"; STATUS=200 ;;
            2) ENDPOINT="/products/789"; STATUS=404 ;;
            3) ENDPOINT="/cart"; STATUS=200 ;;
            4) ENDPOINT="/checkout"; STATUS=200 ;;
            5) ENDPOINT="/api/checkout/payment"; STATUS=200 ;;
            6) ENDPOINT="/health"; STATUS=200 ;;
            7) ENDPOINT="/nonexistent"; STATUS=404 ;;
            8) ENDPOINT="/api/checkout/payment"; STATUS=500 ;;
        esac

        if [ $RAND -eq 5 ] || [ $RAND -eq 8 ]; then
            METHOD="POST"
        fi

        echo "$CLIENT_IP - - [$TIMESTAMP] \"$METHOD $ENDPOINT HTTP/1.1\" $STATUS $BYTES \"-\" \"Mozilla/5.0\""
    done >> "$LOG_FILE"
    COUNTER=$((COUNTER + RPS))
    sleep 1
done

echo "----------------------------------------"
echo "[$(date)] Log generation complete!"
echo "Output: $LOG_FILE"
echo "Total entries: $COUNTER"