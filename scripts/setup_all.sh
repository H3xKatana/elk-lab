#!/bin/bash
set -e

MODE=${1:-full}
WINDOWS_MODE=${2:-container}

echo "Mode: $MODE"
echo "Windows: $WINDOWS_MODE"
echo ""

if [ "$MODE" = "full" ] || [ "$MODE" = "elk" ]; then
    echo "[1/3] Starting ELK Stack..."
    docker compose -f docker-compose.full.yml up -d elasticsearch logstash kibana
    sleep 30
fi

if [ "$MODE" = "full" ] || [ "$MODE" = "nginx" ]; then
    echo ""
    echo "[2/3] Starting Nginx + Filebeat..."
    docker compose -f docker-compose.full.yml up -d nginx-lb checkout-service product-service filebeat
fi

if [ "$MODE" = "full" ] || [ "$MODE" = "windows" ]; then
    if [ "$WINDOWS_MODE" = "container" ]; then
        echo ""
        echo "[3/3] Starting Windows Simulator (container)..."
        docker compose -f docker-compose.full.yml up -d windows-simulator
    else
        echo ""
        echo "[3/3] Windows Local Node Mode"
        echo "  Follow instructions in LOCAL_WINDOWS_SETUP.md"
    fi
fi

echo ""
echo "Services Running:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "Next Steps:"
echo "  1. Generate traffic: python3 load_generator.py"
echo "  2. Generate Windows events:"
if [ "$WINDOWS_MODE" = "container" ]; then
    echo "     docker exec windows-simulator /generate_events.sh 100"
else
    echo "     On Windows: .\\generate_windows_events.ps1 -EventCount 100"
fi
echo "  3. Kibana: http://localhost:5601"
echo "  4. Logs: docker logs elk-logstash -f"
