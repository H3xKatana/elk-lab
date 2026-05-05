#!/bin/bash

NGINX_URL="${1:-http://localhost}"
DURATION=${2:-300}
RPS=${3:-10}

echo "[$(date)] Starting bash load generator..."
echo "Target: $NGINX_URL"
echo "Duration: ${DURATION}s @ ${RPS} req/s"
echo "----------------------------------------"

END_TIME=$(($(date +%s) + DURATION))
REQUEST_COUNT=0
declare -A STATUS_COUNTS

while [ $(date +%s) -lt $END_TIME ]; do
    for i in $(seq 1 $RPS); do
        RAND=$((RANDOM % 9))
        case $RAND in
            0) curl -s -o /dev/null -w "%{http_code}" "$NGINX_URL/products/123" ;;
            1) curl -s -o /dev/null -w "%{http_code}" "$NGINX_URL/products/456" ;;
            2) curl -s -o /dev/null -w "%{http_code}" "$NGINX_URL/products/789" ;;
            3) curl -s -o /dev/null -w "%{http_code}" "$NGINX_URL/cart" ;;
            4) curl -s -o /dev/null -w "%{http_code}" "$NGINX_URL/checkout" ;;
            5) curl -s -o /dev/null -w "%{http_code}" "$NGINX_URL/api/checkout/payment" ;;
            6) curl -s -o /dev/null -w "%{http_code}" "$NGINX_URL/health" ;;
            7) curl -s -o /dev/null -w "%{http_code}" "$NGINX_URL/nonexistent" ;;
            8) curl -s -o /dev/null -w "%{http_code}" "$NGINX_URL/api/checkout/payment" ;;
        esac
        REQUEST_COUNT=$((REQUEST_COUNT + 1))
    done
    sleep 1
    if [ $((REQUEST_COUNT % 50)) -eq 0 ]; then
        echo "[$(date)] Requests: $REQUEST_COUNT"
    fi
done

echo "----------------------------------------"
echo "[$(date)] Load generation complete!"
echo "Total requests: $REQUEST_COUNT"
