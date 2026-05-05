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

## Quick Start

### 1. Start the Stack
```bash
cd elk-lab/docker
docker compose up -d

# Wait 30-60 seconds for services to initialize
docker compose ps
```

### 2. Verify Services
```bash
# Elasticsearch
curl http://localhost:9200

# Kibana
curl http://localhost:5601/api/status
```

### 3. Access Kibana
```
http://localhost:5601
```

---

## Kibana Configuration (MUST DO)

### Step 1: Create Index Patterns

1. Click **Stack Management** (gear icon, bottom-left)
2. Click **Index Patterns** → **Create index pattern**
3. Create each pattern:

| Pattern | Time Field |
|---------|------------|
| `logs-*` | `@timestamp` |
| `logs-nginx-*` | `@timestamp` |
| `logs-ssh-*` | `@timestamp` |
| `logs-syslog-*` | `@timestamp` |
| `logs-app-*` | `@timestamp` |

### Step 2: Generate Test Data
```bash
# SSH logs
docker exec ssh-simulator /generate_ssh_logs.sh 50

# Syslog
docker exec syslog-simulator /generate_syslog.sh 100

# App logs
curl http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"item":"test","user_id":"user-123"}'

# Nginx
curl http://localhost:80
curl http://localhost:80/checkout
```

### Step 3: Verify Data in Discover
1. Click **Discover** (left sidebar)
2. Select `logs-*` index pattern
3. You should see documents appearing

### Step 4: Create Visualizations

#### 4.1 SSH Map (GeoIP Visualization)
1. Click **Visualize** → **Create visualization**
2. Select **Maps**
3. Select `logs-ssh-*` index
4. Add layer:
   - **Aggregation**: Terms
   - **Field**: `geoip.country_name` or `geoip.location`
5. Save as "SSH Attack Sources"

#### 4.2 SSH Success vs Failure (Pie Chart)
1. **Visualize** → **Create** → **Pie chart**
2. Select `logs-ssh-*`
3. Buckets:
   - **Slice by**: Terms → `ssh_result`
4. Save as "SSH Auth Results"

#### 4.3 Nginx Requests Over Time (Line Chart)
1. **Visualize** → **Create** → **Line chart**
2. Select `logs-nginx-*`
3. Buckets:
   - **X-axis**: Date histogram → `@timestamp`
4. Save as "Nginx Traffic"

#### 4.4 HTTP Status Codes (Bar Chart)
1. **Visualize** → **Create** → **Bar chart**
2. Select `logs-nginx-*`
3. Buckets:
   - **X-axis**: Terms → `status`
4. Save as "HTTP Status Codes"

#### 4.5 App Latency (histogram)
1. **Visualize** → **Create** → **histogram**
2. Select `logs-app-*`
3. Buckets:
   - **X-axis**: Number histogram → `response_time`
4. Save as "App Latency Distribution"

### Step 5: Build Dashboard
1. Click **Dashboard** → **Create dashboard**
2. Add all saved visualizations
3. Arrange and resize panels
4. Save as "ELK Lab Overview"

---

## Generating Logs

### Nginx Access Logs
```bash
curl http://localhost:80
curl http://localhost:80/products/123
curl http://localhost:80/checkout
```

### SSH Auth Logs
```bash
docker exec ssh-simulator /generate_ssh_logs.sh 50
# 80% success, 20% failure from various IPs
```

### Syslog Events
```bash
docker exec syslog-simulator /generate_syslog.sh 100
# 50 Linux RFC5424 + 50 Cisco CEF events
```

### App Request Logs
```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/products
curl -X POST http://localhost:5000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"item":"prod-101","quantity":2}'
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
  "result": "failure"
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
  "request_id": "req-abc123",
  "method": "POST",
  "endpoint": "/api/checkout",
  "status_code": 200,
  "latency_ms": 145
}
```

---

## Learning Objectives

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
├── docker/
│   ├── docker-compose.yml
│   ├── nginx.conf
│   ├── generate_ssh_logs.sh
│   ├── generate_syslog.sh
│   └── app/
│       ├── app.py
│       └── Dockerfile
├── config/
│   ├── filebeat.yml
│   └── logstash.conf
├── logs/
│   ├── nginx/
│   ├── ssh/
│   ├── syslog/
│   └── app/
└── docs/
    └── README.md
```

---

## Troubleshooting

### No Data in Kibana
```bash
# Check Filebeat
docker exec filebeat filebeat test config
docker logs filebeat

# Check Logstash
docker compose logs logstash | tail -50

# Check Elasticsearch indices
curl localhost:9200/_cat/indices?v
```

### Services Not Running
```bash
docker compose restart
docker compose logs --tail=100
```

### GeoIP Not Working
```bash
# Check Logstash has GeoIP database
docker exec logstash ls -la /usr/share/logstash/vendor/geoip/
```

---

## Cleanup

```bash
docker compose down -v
```
