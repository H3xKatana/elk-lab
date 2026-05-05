# Student Answer Sheet - Observability & Centralized Logging (Chapter 5)

---

## 1. The Challenge (Section 2)

**Explain why binary "up/down" monitoring failed in this instance. Why is monitoring "pre-defined questions" insufficient for identifying p99 latency spikes in a distributed microservices environment?**

### Your Analysis:

**Why Binary Up/Down Monitoring Failed:**

1. **Lack of Granularity**: Binary monitoring only reports "UP" or "DOWN" - it cannot distinguish between a service responding in 10ms versus 5000ms. A service can be "up" but still causing user-facing degradation.

2. **Invisible Degradation**: A microservice can be technically operational (responding to health checks) while exhibiting severe latency spikes at the p99 percentile due to:
   - Resource contention with other services
   - Garbage collection pauses
   - Connection pool exhaustion
   - Downstream dependency slowdowns

3. **Missing Root Cause Context**: Binary monitoring doesn't capture WHY a service is degraded. When service A reports "healthy" and service B reports "healthy" but the user experiences 5-second latencies, the problem is invisible.

4. **p99 Blind Spots**: Pre-defined questions can only answer anticipated scenarios:
   - "Is the database up?" → YES (but queries are 10x slower)
   - "Is the cache responding?" → YES (but hit rate dropped to 0%)
   - "Is the API returning 200?" → YES (but timeout is 30 seconds)

**Why Pre-Defined Questions Insufficient:**

Pre-defined questions can only capture *known unknowns*. Latency spikes at p99 often stem from:
- Uncommon code paths (e.g., handling malformed input)
- Edge cases in distributed transactions
- Resource exhaustion under specific load patterns
- Network partition behaviors

These scenarios are *unknown unknowns* - you don't know to ask about them until they cause an incident.

---

## 2. Part 1: The Three Pillars (Section 3)

### 2.1 Pillar Characteristics Table

Complete the table below:

| Three Pillars of Observability | Data Characteristic | Specific Use Case |
|-------------------------------|-------------------|-------------------|
| **Pillar Name** | (Discrete vs. Aggregated, Cardinality) | (E-Commerce Scenario) |
| **Logs** | Discrete events, HIGH cardinality | Debugging failed checkout (searching individual transaction logs to find exact error), audit compliance, forensic analysis |
| **Metrics** | Aggregated, LOW cardinality | Real-time dashboards (CPU, memory, request rates), alerting on error rate thresholds, capacity planning |
| **Traces** | Discrete but correlated, HIGH cardinality | Identifying which microservice causes slow checkout (trace shows checkout service calls payment, payment calls inventory, inventory is slow) |

### 2.2 Diagnostic Question (Section 3.1)

**How do Traces specifically resolve the problem of identifying bottlenecks in a distributed request lifecycle where every individual service appears healthy but the overall response is delayed?**

### Your Answer:

Traces solve this through **distributed tracing correlation**:

1. **Single Trace ID**: Every request gets a unique trace ID that propagates through ALL services. If checkout-12345 is slow, all services log this trace ID.

2. **Parent-Span Relationships**: Each service creates a "span" with start/end times. The span hierarchy shows:
   ```
   checkout-12345 (trace)
   ├── auth-service (span: 5ms)
   ├── payment-service (span: 2000ms) ← BOTTLENECK FOUND
   │   └── inventory-service (span: 1950ms) ← ROOT CAUSE
   └── confirmation-service (span: 3ms)
   ```

3. **Service Isolation Doesn't Hide the Problem**: While each service appears healthy in isolation (individual health checks pass, CPU is normal), the trace reveals inventory-service has 1950ms latency on EVERY call when payment-service calls it. This only shows up when correlating spans across the distributed path.

4. **Span Timing Reveals Dependencies**: The actual root cause (inventory database lock contention) only becomes visible when you see the time spent IN that service versus the network transit time.

---

## 3. Part 2: ELK Technical Analysis (Section 4)

### 3.1 Beats & Elastic Agent

Beats and Elastic Agent are lightweight data shippers that collect telemetry and forward it to Elasticsearch or Logstash. Key components:

- **Filebeat**: Log files (nginx logs, application logs, syslog)
- **Metricbeat**: System metrics (CPU, memory, network)
- **Packetbeat**: Network traffic analysis
- **Winlogbeat**: Windows Event Logs (Security, System, Application)
- **Heartbeat**: Availability monitoring (ping-based)

**Key advantage**: Minimal footprint, can be deployed on edge systems without significant resource impact.

### 3.2 Logstash & Grok

**Logstash** is the processing pipeline that ingests, transforms, and routes data.

**Grok** is a pattern-matching filter that parses unstructured log data into structured fields using regex patterns.

Example:
```
Input:  192.168.1.50 - - [05/May/2024:14:30:00 +0000] "GET /checkout HTTP/1.1" 200 1234
Grok:   %{IP:clientip} - - %{TIMESTAMP:timestamp} "%{WORD:method} %{PATH:path} HTTP/%{NUMBER:httpversion}" %{NUMBER:status}
Output: { "clientip": "192.168.1.50", "method": "GET", "path": "/checkout", "status": "200" }
```

Grok enables extraction of fields like IP addresses, status codes, latencies from raw text logs.

### 3.3 Elasticsearch & The Inverted Index

**Inverted Index** is the core data structure that makes Elasticsearch fast:

Instead of mapping documents → words, it maps:
- **Terms** (words) → which documents contain them

Example:
```
Document 1: "Checkout failed"
Document 2: "Payment successful"
Document 3: "Checkout payment error"

Inverted Index:
"checkout" → [1, 3]
"payment"  → [2, 3]
"error"    → [3]
```

This allows sub-millisecond search queries even across billions of documents.

### 3.4 Kibana

**Kibana** is the visualization and exploration layer:
- **Discover**: Query and explore raw log data
- **Visualize**: Create charts, maps, histograms
- **Dashboard**: Combine visualizations into monitoring views
- **Stack Management**: Configure index patterns,ilm policies
- **Maps**: GeoIP visualization for security (where are attack sources?)

---

## 4. Part 3: WEF Design Challenge (Section 5)

### 4.1 Architecture Evaluation Table

| Feature | Source-Initiated (Push) | Collector-Initiated (Pull) |
|---------|-------------------------|---------------------------|
| **Scalability** | HIGH - agents send independently, no bottleneck at collector | LOW - collector becomes bottleneck as agent count increases |
| **Firewall** | COMPLEX - must allow inbound rules for agents to reach collector | SIMPLE - only outbound from agents to collector |
| **Configuration** | DISTRIBUTED - each agent has config | CENTRALIZED - collector config manages all agents |
| **Suitability for Remote Laptops** | IDEAL - laptops send when connected, tolerate disconnection | PROBLEMATIC - collector can't poll laptops that are offline |

### 4.2 Windows Server 2025 Innovation (Section 5.2.1)

Windows Server 2025 introduces:

1. **Enhanced Telemetry Integration**: Native support for OTel (OpenTelemetry) protocol in Windows Event Forwarding
2. **Automated Log Compression**: Automatic compression of archived event logs to reduce storage
3. **Cloud-Connected Backup**: Integration with Azure Arc for centralized log management across hybrid environments

### 4.3 Forensic Prioritization (Section 5.2.2)

Identify the two specific Windows Event IDs for logon success and failure:

| Event Type | Event ID |
|------------|----------|
| Logon Success | **4624** - An account was successfully logged on |
| Logon Failure | **4625** - An account failed to log on |

Additional relevant IDs:
- 4626: Logon with explicit credentials
- 4634: Logoff
- 4648: A logon was attempted using explicit credentials

---

## 5. Part 4: SLIs and Error Budgets (Section 6)

### 5.1 Error Budget Calculation (Section 6.1)

**Given**: 99.95% SLO. Total minutes in 30 days = 43,200.

**Show your work:**

```
Error Budget = Total Minutes × (1 - SLO)
             = 43,200 × (1 - 0.9995)
             = 43,200 × 0.0005
             = 21.6 minutes per month
```

### Final Answer: **21.6 minutes per month**

### 5.2 SLI Proposal (Section 6.2)

**Recommendation for the E-Commerce Platform:**

| SLI | Measurement Method | Target |
|-----|-------------------|--------|
| Availability | % of successful checkout transactions (HTTP 2xx / total) | 99.95% |
| Latency | p99 response time for /api/checkout endpoint | < 2000ms |
| Error Rate | % of HTTP 5xx responses / total requests | < 0.05% |
| Throughput | Successful transactions per minute | Monitor only (no SLO target) |

### 5.3 The "SRE Clamp" (Section 6.3)

**SRE Clamp** refers to the practice of capping error budgets to prevent over-consumption:

When an error budget is nearly exhausted (e.g., >50% consumed in first half of period):
- **Clamp** development velocity - freeze new feature deployments
- **Increase** error budget monitoring frequency
- **Implement** automatic rollback policies for new releases

This prevents the "cliff edge" where a team has consumed their entire budget and must immediately go on high alert for the remainder of the period.

---

## 6. Part 5: Practical Implementation (Section 7)

### 6.1 Task 5.1: docker-compose.yml

```yaml
version: '3.8'

networks:
  elk-network:
    driver: bridge

volumes:
  es-data:
    driver: local

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    container_name: elasticsearch
    environment:
      - node.name=es-node-1
      - cluster.name=elk-cluster
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - ES_JAVA_OPTS=-Xms1g -Xmx1g
      - xpack.security.enabled=false
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - es-data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - elk-network
    healthcheck:
      test: ["CMD-SHELL", "curl -s http://localhost:9200 | grep -q cluster_name"]
      interval: 30s
      timeout: 10s
      retries: 5

  logstash:
    image: docker.elastic.co/logstash/logstash:8.12.0
    container_name: logstash
    volumes:
      - ../config/logstash.conf:/usr/share/logstash/pipeline/logstash.conf:ro
    ports:
      - "5044:5044"
    depends_on:
      elasticsearch:
        condition: service_healthy
    networks:
      - elk-network

  kibana:
    image: docker.elastic.co/kibana/kibana:8.12.0
    container_name: kibana
    ports:
      - "5601:5601"
    depends_on:
      elasticsearch:
        condition: service_healthy
    networks:
      - elk-network

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.12.0
    container_name: filebeat
    user: root
    volumes:
      - ../config/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - ../logs:/var/log:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - logstash
    networks:
      - elk-network
```

### 6.2 Task 5.2: filebeat.yml

```yaml
filebeat.inputs:
  - type: filestream
    enabled: true
    paths:
      - /var/log/nginx/access.log
      - /var/log/nginx/error.log
    fields:
      service: nginx
    fields_under_root: true
    tags: ["nginx"]

  - type: filestream
    enabled: true
    paths:
      - /var/log/ssh/auth.log
    fields:
      service: ssh
    fields_under_root: true
    tags: ["ssh"]

  - type: filestream
    enabled: true
    paths:
      - /var/log/syslog/linux.log
    fields:
      service: syslog
    fields_under_root: true
    tags: ["syslog", "linux"]

  - type: filestream
    enabled: true
    paths:
      - /var/log/app/requests.log
    fields:
      service: app
    fields_under_root: true
    tags: ["app", "api"]

filebeat.config.modules:
  path: ${path.config}/modules.d/*.yml
  reload.enabled: false

processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_cloud_metadata: ~
  - add_docker_metadata: ~

output.logstash:
  hosts: ["logstash:5044"]
  bulk_max_size: 2048
  compression_level: 3
```

### 6.3 Task 5.3: winlogbeat.yml

```yaml
winlogbeat.event_logs:
  - name: Security
    processors:
      - script:
          when.equals.event_id: 4624
          fields:
            logon_type: success
      - script:
          when.equals.event_id: 4625
          fields:
            logon_type: failure

  - name: System

  - name: Application

fields:
  env: production
  datacenter: dc1
fields_under_root: true

output.logstash:
  hosts: ["logstash:5044"]
  bulk_max_size: 2048

logging.level: info
```

### 6.4 Task 5.4: logstash.conf

```ruby
input {
  beats {
    port => 5044
  }
}

filter {
  if [service] == "nginx" {
    grok {
      match => { "message" => "%{COMBINEDAPACHELOG}" }
      overwrite => ["message"]
    }
    date {
      match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
      target => "@timestamp"
    }
    geoip {
      source => "clientip"
      target => "geoip"
    }
    mutate {
      add_field => { "[@metadata][index]" => "nginx" }
    }
  }

  if [service] == "ssh" {
    json {
      source => "message"
      target => "ssh"
    }
    date {
      match => [ "timestamp", "ISO8601" ]
      target => "@timestamp"
    }
    geoip {
      source => "[ssh][source_ip]"
      target => "geoip"
    }
    mutate {
      add_field => { "[@metadata][index]" => "ssh" }
    }
  }

  if [service] == "syslog" {
    grok {
      match => { "message" => "<%{POSINT:priority}>%{POSINT:version} %{TIMESTAMP_ISO8601:timestamp} %{HOSTNAME:hostname} %{WORD:process} %{INT:pid} %{NOTSPACE} %{GREEDYDATA:message}" }
    }
    mutate {
      add_field => { "[@metadata][index]" => "syslog" }
    }
  }

  if [service] == "app" {
    json {
      source => "message"
      target => "app"
    }
    date {
      match => [ "timestamp", "ISO8601" ]
      target => "@timestamp"
    }
    mutate {
      add_field => { "[@metadata][index]" => "app" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{[@metadata][index]}-%{+YYYY.MM.dd}"
  }
}
```

### 6.5 Task 5.5: Visual Proof

[Screenshot would be attached here showing Kibana dashboard with:
- SSH attack map (GeoIP visualization)
- Nginx request timeline
- Syslog event pie chart
- App latency histogram]

---

## 7. Final Deliverable: System Interaction Map (Section 8)

Complete one template per data source (minimum three).

### Data Source 1

| Field | Value |
|-------|-------|
| Source Name | Nginx Access Logs |
| Telemetry Type | Log |
| Shipper | Filebeat |
| Identity Protocol/Tool | Filebeat filestream input, container metadata enrichment |
| Processing | Logstash Grok filter (COMBINEDAPACHELOG pattern) + GeoIP enrichment |
| Transformation Step | Raw access.log → Structured fields (clientip, method, path, status, geoip.location) |
| Final Destination | Elasticsearch index: `logs-nginx-YYYY.MM.DD` |
| Storage/Visualization Tool | Kibana Discover + Dashboard |

### Data Source 2

| Field | Value |
|-------|-------|
| Source Name | Windows Security Events |
| Telemetry Type | Log |
| Shipper | Winlogbeat |
| Identity Protocol/Tool | Winlogbeat event log subscription, Event ID filtering |
| Processing | Logstash conditional processing for Event ID 4624/4625 |
| Transformation Step | Raw Windows XML → Structured logon events with logon_type field |
| Final Destination | Elasticsearch index: `logs-windows-YYYY.MM.DD` |
| Storage/Visualization Tool | Kibana Security Dashboard (or custom dashboard) |

### Data Source 3

| Field | Value |
|-------|-------|
| Source Name | SSH Authentication Logs |
| Telemetry Type | Log |
| Shipper | Filebeat |
| Identity Protocol/Tool | Filebeat filestream, JSON parsing |
| Processing | Logstash JSON filter + GeoIP lookup on source_ip |
| Transformation Step | JSON auth log → Fields (user, source_ip, result, country) + GeoIP coordinates |
| Final Destination | Elasticsearch index: `logs-ssh-YYYY.MM.DD` |
| Storage/Visualization Tool | Kibana Maps (geoip.location) + Pie chart (result breakdown) |

---

## Submission Checklist

- [ ] All questions answered
- [ ] docker-compose.yml configuration complete
- [ ] filebeat.yml configuration complete
- [ ] winlogbeat.yml configuration complete
- [ ] logstash.conf pipeline complete
- [ ] Kibana dashboard screenshot attached
- [ ] Three system interaction maps completed