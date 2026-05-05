# ELK Lab - Observability & Centralized Logging

**Course:** Systems Reliability Engineering (SRE)  
**Topic:** Logs, Metrics, and the ELK Stack Pipeline

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Infrastructure                             │
│                                                                  │
│   ┌──────────────┐         ┌──────────────┐                       │
│   │  Nginx LB   │         │  App Service │    External Sources    │
│   │  (port 80)  │         │   (Python)   │                       │
│   └──────┬───────┘         └──────┬───────┘                       │
│          │                        │                              │
│          └────────┬─────────────┘                              │
│                   ▼                                            │
│   ┌──────────────────────────────────────┐                     │
│   │           Log Directory              │                     │
│   │  nginx/access.log                    │                     │
│   │  ssh/auth.log                        │                     │
│   │  syslog/linux.log                    │                     │
│   │  syslog/cisco.log                    │                     │
│   │  app/requests.log                    │                     │
│   └──────────────────┬───────────────────┘                     │
│                      ▼                                          │
│   ┌──────────────────────────────────────┐                     │
│   │           Filebeat Sidecar           │                     │
│   │  Reads all logs → ships to Logstash  │                     │
│   └──────────────────┬───────────────────┘                     │
│                      │ :5044                                    │
└──────────────────────┼──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ELK Stack                                  │
│                                                                  │
│   ┌──────────────┐                                              │
│   │  Logstash    │  Port 5044 (Beats input)                     │
│   │              │  ┌─────────────┐                             │
│   │  • Grok      │  │   GeoIP     │  Parsing & Enrichment          │
│   │  • Filter   │──▶│ Enrichment │                             │
│   │              │  └─────────────┘                             │
│   └──────┬───────┘                                              │
│          │ :9200                                                │
│          ▼                                                      │
│   ┌──────────────┐                                              │
│   │Elasticsearch│  Indices:                                     │
│   │             │  • logs-nginx-YYYY.MM.DD                      │
│   │             │  • logs-ssh-YYYY.MM.DD                         │
│   │             │  • logs-syslog-YYYY.MM.DD                      │
│   │             │  • logs-app-YYYY.MM.DD                         │
│   └──────┬───────┘                                              │
│          │ :5601                                                │
│          ▼                                                      │
│   ┌──────────────┐                                              │
│   │   Kibana     │  Visualization & Analysis                    │
│   └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Infrastructure Components

### Log Sources

| Service | Format | Log File | Description |
|---------|--------|----------|-------------|
| **Nginx** | Apache Combined | `nginx/access.log` | HTTP requests, status codes |
| **SSH Simulator** | JSON | `ssh/auth.log` | Auth attempts with GeoIP data |
| **Syslog (Linux)** | RFC5424 | `syslog/linux.log` | System events from Linux hosts |
| **Syslog (Cisco)** | CEF | `syslog/cisco.log` | Network device events |
| **App Service** | JSON | `app/requests.log` | Custom API logging with latency |

### Docker Services

| Container | Image | Purpose |
|-----------|-------|---------|
| `elasticsearch` | elasticsearch:8.12.0 | Search and analytics engine |
| `logstash` | logstash:8.12.0 | Log processing pipeline |
| `kibana` | kibana:8.12.0 | Visualization UI |
| `nginx-lb` | nginx:1.25-alpine | Load balancer + access logs |
| `app-service` | python:3.11-slim | Flask app generating JSON logs |
| `ssh-simulator` | ubuntu:22.04 | Generates SSH auth log events |
| `syslog-simulator` | ubuntu:22.04 | Generates Linux + Cisco syslog |
| `filebeat` | filebeat:8.12.0 | Ships all logs to Logstash |

---

## Data Flow

```
1. Start stack:   docker compose up -d
2. Simulators generate logs
   • nginx-lb → access.log (HTTP requests)
   • ssh-simulator → auth.log (JSON, 80% success / 20% failure)
   • syslog-sim → linux.log + cisco.log
   • app-service → requests.log (JSON API logs)

3. Filebeat reads logs from shared volume
   filebeat → Logstash :5044

4. Logstash processing
   Input (Beats) → Grok Filter → GeoIP Enrichment → Output (ES)

5. Elasticsearch indexing
   logs-{source}-YYYY.MM.DD

6. Kibana visualization
   Students create dashboards, maps, charts
```

---

## Prerequisites

### System Requirements
- **OS:** Linux, macOS, Windows (WSL2 recommended)
- **Docker:** Version 20.10+
- **Docker Compose:** Version 2.0+
- **RAM:** 4GB minimum (8GB recommended)
- **Disk:** 10GB free space

### Recommended Docker Memory
```bash
# Edit Docker Desktop settings → Resources → Memory: 4GB+
```

---

## Quick Start

### 1. Clone and Start
```bash
git clone https://github.com/H3xKatana/elk-lab.git
cd elk-lab
docker compose up -d
```

### 2. Wait for Services (30-60 seconds)
```bash
# Check health
docker compose ps

# Verify Elasticsearch
curl http://localhost:9200

# Verify Kibana
curl http://localhost:5601/api/status
```

### 3. Access Kibana
```
http://localhost:5601
```

### 4. Create Index Patterns
1. Go to **Stack Management** → **Index Patterns**
2. Create patterns:
   - `logs-*` (catch-all)
   - `logs-nginx-*`
   - `logs-ssh-*`
   - `logs-syslog-*`
   - `logs-app-*`

### 5. Explore Data
- **Discover** - View raw log entries
- **Visualize** - Create charts/maps
- **Dashboard** - Build monitoring dashboards

---

## Generating Logs

### Nginx Access Logs (auto-generated on request)
```bash
curl http://localhost:80
curl http://localhost:80/health
curl http://localhost:80/products/123
```

### SSH Auth Logs
```bash
docker exec ssh-simulator generate_ssh_logs.sh 50
# Generates 50 events:
#   - 80% success (valid logins)
#   - 20% failure (brute-force attempts from various IPs)
```

### Syslog Events
```bash
docker exec syslog-simulator generate_syslog.sh 100
# Generates 100 events:
#   - 50 Linux RFC5424 format events
#   - 50 Cisco CEF format events
```

### App Request Logs (auto-generated every 5 seconds)
```bash
# Manual API calls:
curl http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"item":"prod123","user_id":"user-456"}'
```

---

## Log Format Reference

### Nginx Access Log
```
192.168.1.50 - - [05/May/2024:14:30:00 +0000] "GET /checkout HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
```

### SSH Auth Event (JSON)
```json
{
  "timestamp": "2024-05-05T14:30:00Z",
  "event": "ssh_auth",
  "user": "admin",
  "source_ip": "185.234.72.45",
  "port": 54321,
  "auth_method": "password",
  "session_id": "ABC123DEF",
  "result": "failure",
  "country": "RU"
}
```

### Syslog Linux (RFC5424)
```
<34>1 2024-05-05T14:30:00Z webserver ssh 1234 - Failed password for invalid user root from 185.234.72.45 port 54321 ssh2
```

### Syslog Cisco (CEF)
```
CEF:0|Cisco|IOS|12.4|5|SSH login attempt|3|src=192.168.1.100 dst=10.0.0.5 spt=54321 dpt=22
```

### App Request Event (JSON)
```json
{
  "timestamp": "2024-05-05T14:30:00Z",
  "level": "INFO",
  "service": "checkout-api",
  "request_id": "req-abc123",
  "method": "POST",
  "endpoint": "/api/checkout",
  "status_code": 200,
  "latency_ms": 145,
  "user_id": "user-456"
}
```

---

## Learning Objectives

By completing this lab, students will:

1. **Configure shippers** - Set up Filebeat to read multiple log sources
2. **Parse unstructured logs** - Use Grok filters to extract fields
3. **Enrich telemetry data** - Add GeoIP to correlate IP addresses with geography
4. **Index management** - Create daily indices per log source
5. **Visualize data** - Build Kibana dashboards correlating different telemetry types
6. **Analyze security events** - Identify brute-force attacks using SSH logs + GeoIP
7. **Monitor application health** - Track latency, error rates from app logs

---

## File Structure

```
elk-lab/
├── docker-compose.yml          # Main stack (ELK + simulators)
├── docker/
│   ├── nginx.conf             # Nginx configuration
│   ├── generate_ssh_logs.sh   # SSH simulator script
│   ├── generate_syslog.sh     # Syslog simulator script
│   └── app/
│       └── app.py             # Flask API application
├── config/
│   ├── filebeat.yml           # Filebeat config (all log sources)
│   └── logstash.conf          # Logstash pipeline (Grok + GeoIP)
├── logs/                      # Shared log directory
│   ├── nginx/
│   ├── ssh/
│   ├── syslog/
│   └── app/
└── docs/
    └── README.md              # This file
```

---

## Troubleshooting

### Services Not Starting
```bash
docker compose logs elasticsearch
docker compose restart
```

### No Logs in Kibana
```bash
# Check filebeat is reading
docker exec filebeat filebeat test output

# Check Logstash received logs
docker compose logs logstash | grep "input"

# Verify indices exist
curl http://localhost:9200/_cat/indices?v
```

### GeoIP Not Working
```bash
# Verify GeoIP database is downloaded
docker exec logstash ls -la /usr/share/logstash/vendor/geoip/

# Check Logstash GeoIP filter config
docker compose logs logstash | grep "geoip"
```

### High Memory Usage
```bash
# Increase Docker memory limit to 4GB+
# Docker Desktop → Settings → Resources → Memory
```

---

## Cleanup

```bash
# Stop all containers
docker compose down

# Remove volumes (clean slate)
docker compose down -v

# Remove all images
docker compose down --rmi all
```
