#!/bin/bash
set -e

echo "Setting up Nginx with ELK Stack..."

# Create nginx logs directory if not exists
mkdir -p /home/morta/workspace/elk-lab/nginx-logs

# Start the ELK stack first
echo "Starting ELK stack..."
cd /home/morta/workspace/elk-lab
docker compose -f docker-compose.yml up -d

echo "Waiting for ELK stack to be ready..."
sleep 30

# Start Nginx container
echo "Starting Nginx load balancer..."
docker compose -f docker-compose.nginx.yml up -d

echo "Verifying services..."
docker ps

echo ""
echo "Services running:"
echo "  - Elasticsearch: http://localhost:9200"
echo "  - Kibana: http://localhost:5601"
echo "  - Nginx LB: http://localhost:80"
echo ""
echo "To generate load: python3 load_generator.py"
echo "To view Nginx logs: tail -f nginx-logs/access.log"
