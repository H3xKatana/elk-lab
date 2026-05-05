# Windows Exporter - Hybrid Setup

## Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Host                              │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ windows-        │    │  filebeat-      │                │
│  │ simulator       │───▶│  windows        │───┐            │
│  │ (generates      │    │  (ships to      │   │            │
│  │  events)        │    │   Logstash)     │   │            │
│  └─────────────────┘    └─────────────────┘   │            │
│                                              ▼            │
│  ┌─────────────────┐    ┌─────────────────┐   │            │
│  │ nginx-lb        │    │  filebeat-      │   │            │
│  │ (access logs)   │───▶│  nginx          │───┼───────────▶│
│  └─────────────────┘    └─────────────────┘   │            │
│                                              │            │
│                   ┌──────────────────────────┘            │
│                   ▼                                    │
│  ┌───────────────────────────────────────────────────┐   │
│  │                 Logstash (5044)                    │   │
│  │  - Grok parsing                                    │   │
│  │  - GeoIP enrichment (nginx)                       │   │
│  │  - Event categorization (windows)                 │   │
│  └───────────────────────────────────────────────────┘   │
│                          │                               │
│                          ▼                               │
│  ┌───────────────────────────────────────────────────┐   │
│  │              Elasticsearch                         │   │
│  │  - Index: logs-nginx-YYYY.MM.DD                   │   │
│  │  - Index: logs-windows-YYYY.MM.DD                 │   │
│  └───────────────────────────────────────────────────┘   │
│                          │                               │
│                          ▼                               │
│              ┌──────────────────────┐                     │
│              │     Kibana          │                     │
│              │  (port 5601)        │                     │
│              └──────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Local Windows Node (Optional)                   │
│                                                             │
│  ┌─────────────────┐                                        │
│  │  Winlogbeat     │──────────────────────────────────────▶ │
│  │  (reads real    │      Real Windows Events              │
│  │   Security log) │      Event ID 4624, 4625              │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Start Container Stack
```bash
cd /home/morta/workspace/elk-lab/docker
docker compose -f docker-compose.full.yml up -d
```

### 2. Generate Container Windows Events (for testing)
```bash
docker exec windows-simulator /generate_events.sh 50
```

### 3. Generate Nginx Logs
```bash
cd /home/morta/workspace/elk-lab
./scripts/generate_nginx_logs.py
```

### 4. View in Kibana
Open http://localhost:5601
- Create index pattern: `logs-windows-*`
- Create index pattern: `logs-nginx-*`

## Local Windows Node (Real Events)

### On Windows Machine

1. Download Winlogbeat: https://www.elastic.co/downloads/beats/winlogbeat
2. Extract to `C:\Program Files\Winlogbeat`
3. Copy `config/winlogbeat.yml` to `C:\Program Files\Winlogbeat\winlogbeat.yml`
4. Update with your Docker host IP:

```yaml
output.logstash:
  hosts: ["YOUR_DOCKER_HOST_IP:5044"]
```

5. Run PowerShell as Admin:
```powershell
cd "C:\Program Files\Winlogbeat"
.\install-service-winlogbeat.ps1
Start-Service winlogbeat
```

## Event IDs

| Event ID | Description | Logged By |
|----------|-------------|-----------|
| 4624 | Account Logon Success | Container + Real Winlogbeat |
| 4625 | Account Logon Failure | Container + Real Winlogbeat |

## Verification

Check logs are flowing:
```bash
docker logs elk-filebeat-windows -f
docker logs elk-filebeat-nginx -f
docker logs elk-logstash -f
```

Check Elasticsearch:
```bash
curl "localhost:9200/_cat/indices?v"
```