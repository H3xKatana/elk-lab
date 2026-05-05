<!--
marp: true
theme: default
paginate: true
-->

<!-- _class: lead -->
<!-- _footer: "ELK Lab - Observability & Centralized Logging" -->

# ELK Lab: Observability & Centralized Logging

**Systems Reliability Engineering (SRE)**

---

## Agenda

1. Architecture Overview
2. The 6 Log Sources
3. ELK Stack Components
4. Setting Up the Stack
5. Windows Event Forwarding
6. Error Budgets & SLOs
7. Configuring Kibana
8. Learning Outcomes

---

## Agenda

- Architecture Overview
- The 6 Log Sources (Linux + Windows)
- Setting Up the Stack
- Windows Event Forwarding Setup
- Configuring Kibana
- Generating Test Data
- Learning Outcomes

<!-- _footer: "" -->

---

## Architecture Overview

```
Linux/Cloud Endpoints              Windows Endpoints
┌─────────────────┐               ┌──────────────────┐
│  Nginx          │               │  Windows Server   │
│  SSH Simulator  │               │  Winlogbeat       │
│  Syslog         │               │  (Security,System,│
│  App Service    │               │   Application)    │
└────────┬────────┘               └────────┬─────────┘
         │                                 │
         │ Filebeat :5044        Winlogbeat :5044
         │                                 │
         └────────────┬───────────────────┘
                      │
               ┌──────▼──────┐
               │  Logstash   │  Parse • Enrich • Route
               │  (Grok+Geo) │
               └──────┬──────┘
                      │ :9200
               ┌──────▼──────┐
               │Elasticsearch│  Store • Index
               └──────┬──────┘
                      │ :5601
               ┌──────▼──────┐
               │   Kibana    │  Visualize • Analyze
               └─────────────┘
```

**Data Flow:**
- **Linux:** Logs → Filebeat → Logstash → Elasticsearch ← Kibana
- **Windows:** Windows Events → Winlogbeat → Logstash → Elasticsearch ← Kibana

<!-- _footer: "" -->

---

## The 6 Log Sources

| Source | Shipper | Format | Key Fields | Use Case |
|--------|---------|--------|------------|----------|
| **Nginx** | Filebeat | Combined Apache Log | clientip, status, request | Web traffic |
| **SSH** | Filebeat | JSON | user, result, source_ip, geoip | Security |
| **Syslog (Linux)** | Filebeat | RFC5424 | hostname, process, message | System events |
| **Syslog (Cisco)** | Filebeat | CEF | src_ip, dst_ip, severity | Network logs |
| **App Service** | Filebeat | JSON | method, endpoint, latency | App health |
| **Windows Events** | Winlogbeat | Windows XML | EventID, LogonType, IpAddress | Windows security |

<!-- _footer: "" -->

---

## Log Source: Windows Event Logs

**Shipper:** Winlogbeat (official Elastic Beats for Windows)

**Format:** Windows Event XML (rendered as JSON by Winlogbeat)

**Key Security Events:**

| Event ID | Channel | Description | Critical For |
|----------|---------|-------------|-------------|
| **4624** | Security | Account successfully logged on | Tracking valid logins |
| **4625** | Security | Account failed to log on | Detecting brute force |
| **4634** | Security | Logoff | Session tracking |
| **4648** | Security | Explicit credentials used | Silver ticket attacks |
| **4672** | Security | Special privileges assigned | Privilege escalation |
| **4688** | Security | New process created | Execution monitoring |
| **4698** | Security | Scheduled task created | Persistence detection |

**LogonType Codes (from 4624/4625):**

| Code | Name | Description | Risk Level |
|------|------|-------------|------------|
| **2** | Interactive | Local keyboard login | Medium |
| **3** | Network | File/print sharing, RDP tunnel | Low |
| **4** | Batch | Scheduled task | Medium |
| **5** | Service | Service account | Low |
| **7** | Unlock | Workstation unlocked | Low |
| **8** | NetworkCleartext | Creds sent in cleartext | HIGH |
| **9** | NewCredentials | RunAs / credential delegation | HIGH |
| **10** | RemoteInteractive | RDP/Virtual machines | Medium |
| **11** | CachedInteractive | Offline login | Low |

**Target Account Analysis (4624/4625):**
- `TargetUserName` → Who logged in
- `TargetDomainName` → Which domain
- `TargetLogonId` → Unique session ID
- `IpAddress` → Source IP (valuable for attack mapping)
- `LogonType` → HOW they logged in (method)"

<!-- _footer: "" -->

<!-- _footer: "" -->

---

## WEF Architecture: Push vs Pull

| Feature | Source-Initiated (Push) | Collector-Initiated (Pull) |
|---------|-------------------------|---------------------------|
| **Scalability** | HIGH - independent agents | LOW - collector bottleneck |
| **Firewall** | Complex - inbound rules | Simple - outbound only |
| **Remote Laptops** | IDEAL - tolerates disconnection | PROBLEMATIC - can't poll offline |

**Recommendation:** Push for roaming devices, Pull for always-on servers

### Windows Server 2025: IAKerb & Local KDC
- Reduces NTLM dependency for remote/hybrid workers
- Local KDC enables offline authentication with cached credentials

<!-- _footer: "" -->

<!-- _footer: "" -->

---

## Log Source: Nginx

**Format:** Combined Apache Log

```
192.168.1.50 - - [05/May/2024:14:30:00 +0000] "GET /checkout HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
```

**Enriched Fields:**
- `clientip` → GeoIP lookup (country, location)
- `timestamp` → Parsed via date filter
- `status` → HTTP status code
- `request` → URL path and method

<!-- _footer: "" -->

---

## Log Source: SSH

**Format:** JSON (structured)

```json
{
  "timestamp": "2024-05-05T14:30:00Z",
  "event": "ssh_auth",
  "user": "admin",
  "source_ip": "185.234.72.45",
  "result": "failure"
}
```

**Key Insight:** 80% successful logins (internal IPs) vs 20% failures (external attack IPs)

<!-- _footer: "" -->

---

## Log Source: Syslog (Linux)

**Format:** RFC5424

```
<34>1 2024-05-05T14:30:00Z webserver ssh 1234 - - Failed password for invalid user admin from 185.234.72.45 port 54321 ssh2
```

**Parsed Fields:**
- `priority` → severity + facility
- `hostname` → origin system
- `process` → service name
- `message` → the actual event

<!-- _footer: "" -->

---

## Log Source: Syslog (Cisco)

**Format:** CEF (Common Event Format)

```
CEF:0|Cisco|IOS|12.4|5|SSH login attempt|3|src=192.168.1.100 dst=10.0.0.5 spt=54321 dpt=22
```

**Fields:** Device type, severity level, source/destination IPs, ports

<!-- _footer: "" -->

---

## Log Source: App Service

**Format:** JSON (structured)

```json
{
  "timestamp": "2024-05-05T14:30:00Z",
  "method": "POST",
  "endpoint": "/api/checkout",
  "status_code": 200,
  "latency_ms": 145
}
```

**Metrics Tracked:** Response times, error rates, endpoint popularity

<!-- _footer: "" -->

---

## Setting Up: Windows Endpoints

### Winlogbeat: Official Elastic Shipper for Windows Events

Winlogbeat monitors Windows Event Logs and streams them to Logstash.

**Architecture:**
```
┌─────────────────┐         ┌──────────────┐         ┌──────────────┐
│  Windows Server │         │   Logstash   │         │Elasticsearch │
│                 │ Winlog  │              │         │              │
│ Security.evtx   │────────▶│  :5044       │────────▶│ logs-windows │
│ System.evtx     │         │  (Grok+Geo)  │         │     YYYY.MM.DD
│ Application.evtx│         └──────────────┘         └──────────────┘
└─────────────────┘                                       │
                                                          ▼
                                                      ┌────────┐
                                                      │ Kibana │
                                                      └────────┘
```

**Full winlogbeat.yml Configuration:**
```yaml
winlogbeat.event_logs:
  - name: Security
    fields:
      log_source: windows_server
    processors:
      - script:
          when.equals.event_id: 4624
          fields:
            logon_result: success
            event_category: authentication
      - script:
          when.equals.event_id: 4625
          fields:
            logon_result: failure
            event_category: authentication
      - script:
          when.equals.event_id: 4672
          fields:
            event_category: privileged_access
      - script:
          when.equals.event_id: 4688
          fields:
            event_category: process_creation

  - name: System
    fields:
      log_source: windows_server

  - name: Application
    fields:
      log_source: windows_server

output.logstash:
  hosts: ["10.5.0.175:5044"]  # Your ELK server IP
  compression_level: 3

fields:
  env: lab
  datacenter: dc1
fields_under_root: true

logging.level: info
logging.to_files: true
```

**Installation Steps (Windows Server):**
```powershell
# 1. Download Winlogbeat from https://www.elastic.co/downloads/beats/winlogbeat

# 2. Extract to C:\Program Files\Winlogbeat\

# 3. Open PowerShell as Administrator
cd C:\Program Files\Winlogbeat

# 4. Install as Windows service
.\install-service-winlogbeat.ps1

# 5. Copy your winlogbeat.yml to C:\Program Files\Winlogbeat\

# 6. Start the service
Start-Service winlogbeat

# 7. Verify it's running
Get-Service winlogbeat

# 8. Test configuration
.\winlogbeat test config -c winlogbeat.yml

# 9. View logs
.\winlogbeat -e -d "*"
```

**Event ID Reference (Security Log):**

| Event ID | Description | Fields Extracted |
|----------|-------------|------------------|
| **4624** | Account logon success | TargetUserName, LogonType, IpAddress, ProcessName |
| **4625** | Account logon failure | TargetUserName, LogonType, IpAddress, Status, FailureReason |
| **4634** | Logoff | TargetUserName, LogonType |
| **4648** | Explicit credentials | SubjectUserName, TargetUserName, IpAddress |
| **4672** | Special privileges assigned | PrivilegeList (SeDebugPrivilege, etc.) |
| **4688** | Process creation | NewProcessName, ParentProcessName, CreatorProcessId |
| **4698** | Scheduled task created | TaskName, UserContext |

**Key Kibana Visualizations for Windows:**

1. **Brute Force Detection** (Pie Chart)
   - Filter: `winlog.event_id: 4625`
   - Group by: `winlog.network.ip_address`

2. **Attack Origin Map** (Maps)
   - Source: `logs-windows-*`
   - Layer: Terms on `geoip.location`
   - Filter: `logon_result: failure`

3. **Successful Logins Timeline** (Line Chart)
   - X-axis: Date histogram
   - Split by: LogonType (2, 3, 10)

4. **Privilege Escalation Alert** (Data Table)
   - Filter: `winlog.event_id: 4672`
   - Show: TargetUserName, PrivilegeList

<!-- _footer: "" -->

<!-- _footer: "" -->

---

## Setting Up: Start the Stack

### Step 1: Navigate to docker directory

```bash
cd elk-lab/docker
```

### Step 2: Launch all services

```bash
docker compose up -d
```

### Step 2: Wait for initialization (30-60 seconds)

```bash
docker compose ps
```

### Step 3: Verify services are running

```bash
curl http://localhost:9200        # Elasticsearch
curl http://localhost:5601/api/status  # Kibana
```

<!-- _footer: "" -->

---

## Accessing Kibana

**Open in browser:**

```
http://localhost:5601
```

**First Time Setup:**
1. Click "Explore on my own" (skip tutorial)
2. Stack Management → Index Patterns
3. Create patterns for each log source

<!-- _footer: "" -->

---

## Configuring Kibana: Index Patterns

### Create these patterns in order:

| Pattern | Time Field |
|---------|------------|
| `logs-nginx-*` | @timestamp |
| `logs-ssh-*` | @timestamp |
| `logs-syslog-*` | @timestamp |
| `logs-cisco-*` | @timestamp |
| `logs-app-*` | @timestamp |
| `logs-windows-*` | @timestamp |

**Note:** You can also use `logs-*` to query all sources at once

<!-- _footer: "" -->

---

## Configuring Kibana: Create Visualizations

### Recommended Visualizations:

1. **SSH Attack Map** (Maps)
   - Layer: Terms on `geoip.location`
   - Source: `logs-ssh-*`

2. **SSH Auth Results** (Pie Chart)
   - Slice by: Terms → `ssh_result`

3. **Nginx Traffic Over Time** (Line Chart)
   - X-axis: Date histogram → `@timestamp`

4. **HTTP Status Codes** (Bar Chart)
   - X-axis: Terms → `status`

5. **App Latency Distribution** (Histogram)
   - X-axis: Number → `latency_ms`

6. **Windows Logon Success/Failure** (Pie Chart)
   - Slice by: Terms → `winlog.channel` (Security)
   - Filter: `winlog.event_id` in [4624, 4625]

7. **Windows Attack Sources** (Map)
   - Layer: Terms on `winlog.network.ip_address`
   - Source: `logs-windows-*`

<!-- _footer: "" -->

---

## Build a Dashboard

### Steps:
1. Click **Dashboard** → **Create dashboard**
2. Add all saved visualizations
3. Arrange and resize panels
4. Save as "ELK Lab Overview"

**Pro Tip:** Use `logs-*` pattern to see all data, or filter by specific source using the `service` field

<!-- _footer: "" -->

---

## Generating Test Data

### Nginx Logs (web traffic)

```bash
curl http://localhost:80
curl http://localhost:80/products/123
curl http://localhost:80/checkout
```

### SSH Logs (security events)

```bash
docker exec ssh-simulator /generate_ssh_logs.sh 50
# Generates 80% success (internal) + 20% failure (external)
```

<!-- _footer: "" -->

---

## Generating Test Data (continued)

### Syslog Events

```bash
docker exec syslog-simulator /generate_syslog.sh 100
# 50 Linux RFC5424 + 50 Cisco CEF events
```

### App Logs (API requests)

```bash
curl http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"item":"test","user_id":"user-123"}'
```

<!-- _footer: "" -->

---

## Verifying Data Arrived

### In Kibana Discover:

1. Click **Discover** (left sidebar)
2. Select `logs-*` index pattern
3. Set time range to "Last 15 minutes"
4. You should see documents appearing

### Via Command Line:

```bash
curl localhost:9200/_cat/indices?v
```

Look for indices like: `logs-nginx-2024.05.05`

<!-- _footer: "" -->

---

## Logstash Pipeline: How It Works

```
input { beats { port => 5044 } }  # Accepts BOTH Filebeat AND Winlogbeat

filter {
  # NGINX: Parse Apache Combined Log format
  if [service] == "nginx" {
    grok { match => { "message" => "%{COMBINEDAPACHELOG}" } }
    geoip { source => "clientip" target => "geoip" }
    mutate { add_field => { "[@metadata][index]" => "nginx" } }
  }

  # SSH: Parse JSON with country codes
  if [service] == "ssh" {
    json { source => "message" target => "ssh_data" }
    date  { match => [ "[ssh_data][timestamp]" "ISO8601" ] }
    geoip { source => "[ssh_data][source_ip]" target => "geoip" }
    mutate { rename => { "[ssh_data][result]" => "ssh_result" }
            add_field => { "[@metadata][index]" => "ssh" } }
  }

  # WINDOWS: Route Security events by Event ID
  if [winlog][channel] == "Security" {
    if [winlog][event_id] == 4624 {
      mutate { add_field => { "logon_result" => "success"
                             "[@metadata][index]" => "windows" } }
    }
    if [winlog][event_id] == 4625 {
      mutate { add_field => { "logon_result" => "failure"
                             "[@metadata][index]" => "windows" } }
    }
    # GeoIP on source IP for attack mapping
    geoip { source => "[winlog][network][ip_address]" target => "geoip" }
  }

  # SYSLOG LINUX: RFC5424 format
  if [service] == "syslog" {
    grok { match => { "message" => "<%{POSINT:priority}>..." } }
    mutate { add_field => { "[@metadata][index]" => "syslog" } }
  }

  # CISCO: CEF format
  if [service] == "cisco" {
    grok { match => { "message" => "CEF:%{NOTSPACE}..." } }
    mutate { add_field => { "[@metadata][index]" => "cisco" } }
  }

  # APP: JSON API logs
  if [service] == "app" {
    json { source => "message" target => "app_data" }
    mutate { rename => { "[app_data][latency_ms]" => "request_latency" }
            add_field => { "[@metadata][index]" => "app" } }
  }
}

output {
  elasticsearch { index => "logs-%{[@metadata][index]}-%{+YYYY.MM.dd}" }
}
```

**Key Points:**
- Single input port (5044) accepts logs from ALL shippers
- Dynamic index naming: `logs-{service}-YYYY.MM.DD`
- GeoIP runs on both Linux (SSH) and Windows events
- Windows events enriched with `geoip.location` for map visualization

<!-- _footer: "" -->

<!-- _footer: "" -->

---

## ELK Stack Components

### Shippers: Filebeat & Winlogbeat
- **Filebeat**: Ships logs from Linux/Windows files
- **Winlogbeat**: Ships Windows Event Logs (Security, System, Application)

### Logstash Pipeline
- **Input**: Receives from Beats on port 5044
- **Filter**: Grok parsing + GeoIP enrichment
- **Output**: Routes to Elasticsearch indices by service

### Elasticsearch
- **Inverted Index**: Enables sub-millisecond search across terabytes
- **Daily indices**: `logs-{service}-YYYY.MM.DD`

### Kibana
- **Discover**: Query raw logs
- **Visualize**: Charts, maps, histograms
- **Dashboard**: Combined panels

<!-- _footer: "" -->

By completing this lab, you will be able to:

1. **Configure log shippers** - Set up Filebeat to read multiple sources
2. **Parse unstructured logs** - Use Grok filters for field extraction
3. **Enrich telemetry** - Add GeoIP for geographic context
4. **Manage indices** - Create daily indices per log source
5. **Build dashboards** - Visualize correlated telemetry
6. **Analyze security events** - Identify brute-force attacks via SSH + Windows events
7. **Monitor app health** - Track latency and error rates
8. **Calculate error budgets** - Determine SLO compliance and feature freeze decisions

<!-- _footer: "" -->

---

## Error Budgets & SLOs

**99.95% SLO → 21.6 min/month allowed downtime**

```
43,200 min × (1 - 0.9995) = 21.6 min/month
```

**Why p95/p99?** Mean hides outliers. p99 = 99% of users get acceptable latency.

**The "SRE Clamp":** When budget >50% consumed → freeze feature deployments.

<!-- _footer: "" -->

---

## Key Commands Reference

```bash
# Start/stop
docker compose up -d
docker compose down

# View logs
docker compose logs -f filebeat
docker compose logs -f logstash

# Test Elasticsearch
curl localhost:9200/_cat/indices?v

# Generate data
docker exec ssh-simulator /generate_ssh_logs.sh 50
docker exec syslog-simulator /generate_syslog.sh 100

# Restart a service
docker compose restart filebeat
```

### Windows Event IDs (Security Log)

| Event | Description |
|-------|-------------|
| **4624** | Account successfully logged on |
| **4625** | Account failed to log on |
| **4634** | Logoff |
| **4648** | Explicit credentials used |

### Winlogbeat (Windows)

```powershell
# Install
.\install-service-winlogbeat.ps1

# Start
Start-Service winlogbeat

# Test config
.\winlogbeat test config -c winlogbeat.yml
```

<!-- _footer: "" -->

---

## Troubleshooting

**No data in Kibana?**
```bash
# Check Filebeat
docker exec filebeat filebeat test config
docker logs filebeat

# Check Logstash
docker compose logs logstash | tail -50

# Verify indices exist
curl localhost:9200/_cat/indices?v
```

**Services not healthy?**
```bash
docker compose restart
docker compose logs --tail=100
```

<!-- _footer: "" -->

---

## Summary

| Component | Purpose | Key Config |
|-----------|---------|------------|
| Filebeat | Ship logs from files | filebeat.yml |
| Logstash | Parse & enrich | logstash.conf |
| Elasticsearch | Store & index | docker-compose.yml |
| Kibana | Visualize | Index patterns |

**Next Steps:** Explore the data, create custom visualizations, build your own dashboard!

<!-- _footer: "" -->

---

# Questions?

**Lab Repository:** https://github.com/H3xKatana/elk-lab

<!-- _class: lead -->

---

## Backup: File Structure

```
elk-lab/
├── docker/
│   ├── docker-compose.yml
│   ├── nginx.conf
│   ├── generate_ssh_logs.sh
│   ├── generate_syslog.sh
│   └── app/
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

<!-- _footer: "" -->