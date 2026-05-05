# ELK Lab - Complete Setup

## Overview
Complete ELK (Elasticsearch, Logstash, Kibana) stack with:
- Nginx load balancer and backend services
- Filebeat for Nginx log shipping
- Windows event simulation (container or local node)

---

## Quick Start

### Option 1: Full Container Setup (Everything in Docker)
```bash
./setup_all.sh full container
```

### Option 2: Container ELK + Local Windows Node
```bash
# Start ELK + Nginx in Docker
./setup_all.sh full local

# Then follow LOCAL_WINDOWS_SETUP.md on your Windows machine
```

### Option 3: Just ELK Stack
```bash
./setup_all.sh elk
```

---

## Services

| Service | URL/Port | Description |
|---------|-----------|-------------|
| Elasticsearch | http://localhost:9200 | Search engine |
| Kibana | http://localhost:5601 | Visualization UI |
| Logstash | port 5044 | Log ingestion |
| Nginx LB | http://localhost:80 | Load balancer |
| Filebeat | - | Ships Nginx logs |

---

## Generate Traffic

### Nginx Load
```bash
python3 load_generator.py
# OR
./load_generator.sh
```

### Windows Events (Container)
```bash
docker exec windows-simulator /generate_events.sh 100
```

### Windows Events (Local)
```powershell
.\generate_windows_events.ps1 -EventCount 100
```

---

## File Structure

```
elk-lab/
├── docker-compose.full.yml      # Full stack
├── docker-compose.yml           # Just ELK
├── docker-compose.nginx.yml     # Just Nginx
├── setup_all.sh                 # Master setup script
├── nginx.conf                   # Nginx config
├── filebeat.yml                 # Filebeat config
├── winlogbeat.yml               # Winlogbeat config
├── logstash.conf                # Logstash pipeline
├── load_generator.py            # Python load generator
├── load_generator.sh            # Bash load generator
├── windows_setup.ps1            # Windows setup script
├── generate_windows_events.ps1   # Windows event generator
├── generate_windows_events.sh    # Linux event simulator
├── html/                        # Sample web pages
├── nginx-logs/                  # Nginx log output
├── windows-logs/                # Windows log output
├── LOCAL_WINDOWS_SETUP.md       # Local Windows guide
└── student_answer_sheet-completed.md  # Lab answers
```

---

## Verify Everything Works

1. **Elasticsearch**: `curl http://localhost:9200`
2. **Kibana**: Open http://localhost:5601 in browser
3. **Nginx**: `curl http://localhost/health`
4. **Logs in Kibana**: Create index pattern `logs-*` and view Discover

---

## Cleanup

```bash
# Stop all containers
docker compose -f docker-compose.full.yml down -v

# Remove volumes
docker volume prune -f
```
