from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Preformatted, HRFlowable, Image
)
from reportlab.platypus.flowables import Flowable
import reportlab.lib.colors as rcolors

W, H = A4
LM = RM = 2.0 * cm
TM = BM = 2.0 * cm
CONTENT_W = W - LM - RM

# Color palette
C_NAVY       = colors.HexColor('#1a237e')
C_BLUE       = colors.HexColor('#1565c0')
C_BLUE_MED   = colors.HexColor('#1976d2')
C_BLUE_LIGHT = colors.HexColor('#e3f2fd')
C_TEAL       = colors.HexColor('#00695c')
C_TEAL_LIGHT = colors.HexColor('#e0f2f1')
C_AMBER      = colors.HexColor('#ff8f00')
C_AMBER_LIGHT= colors.HexColor('#fff8e1')
C_GREEN_LIGHT= colors.HexColor('#e8f5e9')
C_GREY_DARK  = colors.HexColor('#263238')
C_GREY_MED   = colors.HexColor('#546e7a')
C_GREY_LIGHT = colors.HexColor('#f5f7fa')
C_GREY_LINE  = colors.HexColor('#cfd8dc')
C_WHITE      = colors.white
C_CODE_BG    = colors.HexColor('#eceff1')
C_CODE_BORDER= colors.HexColor('#78909c')

class AccentBox(Flowable):
    def __init__(self, content_items, accent_color=None, bg_color=None, width=None):
        super().__init__()
        self.content_items = content_items
        self.accent_color = accent_color or C_BLUE
        self.bg_color = bg_color or C_GREY_LIGHT
        self.width = width or CONTENT_W
    def _calc_height(self):
        total = 12
        for item in self.content_items:
            if hasattr(item, 'wrap'):
                w, h = item.wrap(self.width - 28, 9999)
                total += h + 4
        return total
    def wrap(self, availW, availH):
        self.height = self._calc_height()
        return (self.width, self.height)
    def draw(self):
        c = self.canv
        h = self.height
        w = self.width
        c.setFillColor(self.bg_color)
        c.rect(0, 0, w, h, fill=1, stroke=0)
        c.setFillColor(self.accent_color)
        c.rect(0, 0, 5, h, fill=1, stroke=0)
        c.setStrokeColor(self.accent_color)
        c.setLineWidth(0.5)
        c.rect(0, 0, w, h, fill=0, stroke=1)
        x_off = 14
        y_off = h - 8
        for item in self.content_items:
            iw, ih = item.wrap(w - 28, 9999)
            y_off -= ih
            item.drawOn(c, x_off, y_off)
            y_off -= 4

def make_styles():
    S = {}
    def ps(name, **kw):
        S[name] = ParagraphStyle(name, **kw)
    ps('cover_title',     fontSize=22, fontName='Helvetica-Bold',
       textColor=C_NAVY,  alignment=TA_CENTER, spaceAfter=6)
    ps('cover_sub',       fontSize=13, fontName='Helvetica',
       textColor=C_BLUE,  alignment=TA_CENTER, spaceAfter=4)
    ps('section_title',   fontSize=13, fontName='Helvetica-Bold',
       textColor=C_WHITE, spaceAfter=0, spaceBefore=0, leading=18)
    ps('subsection',      fontSize=11, fontName='Helvetica-Bold',
       textColor=C_BLUE,  spaceBefore=12, spaceAfter=4, leading=16)
    ps('body',            fontSize=10, fontName='Helvetica',
       textColor=C_GREY_DARK, leading=16, spaceBefore=3, spaceAfter=3,
       alignment=TA_JUSTIFY)
    ps('body_bold',       fontSize=10, fontName='Helvetica-Bold',
       textColor=C_GREY_DARK, leading=16, spaceBefore=3, spaceAfter=3)
    ps('bullet',          fontSize=10, fontName='Helvetica',
       textColor=C_GREY_DARK, leading=16, spaceBefore=2, spaceAfter=2,
       leftIndent=14, firstLineIndent=-10)
    ps('meta_label',      fontSize=10, fontName='Helvetica-Bold',
       textColor=C_GREY_MED)
    ps('meta_value',      fontSize=10, fontName='Helvetica',
       textColor=C_GREY_DARK)
    ps('code',            fontSize=8,  fontName='Courier',
       textColor=C_GREY_DARK, leading=12, spaceBefore=0, spaceAfter=0,
       backColor=C_CODE_BG, leftIndent=8, rightIndent=8)
    ps('tbl_header',      fontSize=10, fontName='Helvetica-Bold',
       textColor=C_WHITE, leading=14, alignment=TA_CENTER)
    ps('tbl_body',        fontSize=9,  fontName='Helvetica',
       textColor=C_GREY_DARK, leading=13, alignment=TA_LEFT)
    ps('final_answer',    fontSize=11, fontName='Helvetica-Bold',
       textColor=C_TEAL, alignment=TA_CENTER, spaceBefore=4, spaceAfter=4)
    return S

def page_template(canvas, doc):
    pass

def first_page_template(canvas, doc):
    pass

def sp(h=4):
    return Spacer(1, h)

def section_header(label, S):
    inner = Table([[Paragraph(label, S['section_title'])]], colWidths=[CONTENT_W])
    inner.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), C_BLUE),
        ('TOPPADDING',   (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0), (-1,-1), 8),
        ('LEFTPADDING',  (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('LINEBELOW',    (0,0), (-1,-1), 3, C_AMBER),
    ]))
    return inner

def subsection_title(text, S):
    return Paragraph(text, S['subsection'])

def bullet_p(text, S):
    return Paragraph(f'\u2022\u2002{text}', S['bullet'])

def answer_box(items, S, accent=None, bg=None):
    return AccentBox(items, accent_color=accent or C_BLUE, bg_color=bg or C_GREY_LIGHT)

def code_block(code_str, S):
    lines = code_str.rstrip().split('\n')
    rows = []
    for line in lines:
        rows.append([Preformatted(line if line.strip() else ' ', S['code'])])
    chunks = []
    CHUNK = 40
    for i in range(0, len(rows), CHUNK):
        chunk_rows = rows[i:i+CHUNK]
        t = Table(chunk_rows, colWidths=[CONTENT_W - 2])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), C_CODE_BG),
            ('LINEABOVE',     (0,0), (-1,0),  0.5, C_CODE_BORDER),
            ('LINEBELOW',     (0,-1),(-1,-1), 0.5, C_CODE_BORDER),
            ('LINEBEFORE',    (0,0), (0,-1),  0.5, C_CODE_BORDER),
            ('LINEAFTER',     (-1,0),(-1,-1), 0.5, C_CODE_BORDER),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('RIGHTPADDING',  (0,0), (-1,-1), 8),
            ('TOPPADDING',    (0,0), (0,0),   6),
            ('BOTTOMPADDING', (0,-1),(-1,-1), 6),
        ]))
        chunks.append(t)
    return chunks

def data_table(headers, rows, col_widths, S, accent_header=C_BLUE, row_colors=None):
    row_colors = row_colors or [colors.HexColor('#f0f7ff'), C_WHITE]
    header_row_data = [[Paragraph(h, S['tbl_header']) for h in headers]]
    all_rows = [header_row_data[0]]
    for row in rows:
        all_rows.append([Paragraph(str(cell), S['tbl_body']) for cell in row])
    t = Table(all_rows, colWidths=col_widths, repeatRows=1)
    style = [
        ('BACKGROUND',   (0,0), (-1,0),  accent_header),
        ('TEXTCOLOR',    (0,0), (-1,0),  C_WHITE),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
        ('GRID',         (0,0), (-1,-1), 0.5, C_GREY_LINE),
        ('LINEBELOW',    (0,0), (-1,0),  1.5, C_AMBER),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), row_colors),
        ('FONTNAME',     (0,0), (-1,0),  'Helvetica-Bold'),
    ]
    t.setStyle(TableStyle(style))
    return t

# ACTUAL CONFIG FILES FROM REPO
DOCKER_COMPOSE = """version: '3.8'

networks:
  elk-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  es-data:
    driver: local

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    container_name: elk-elasticsearch
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
    restart: unless-stopped

  logstash:
    image: docker.elastic.co/logstash/logstash:8.12.0
    container_name: elk-logstash
    volumes:
      - ../config/logstash.conf:/usr/share/logstash/pipeline/logstash.conf:ro
    ports:
      - "5044:5044"
    depends_on:
      elasticsearch:
        condition: service_healthy
    networks:
      - elk-network
    restart: unless-stopped

  kibana:
    image: docker.elastic.co/kibana/kibana:8.12.0
    container_name: elk-kibana
    ports:
      - "5601:5601"
    depends_on:
      elasticsearch:
        condition: service_healthy
    networks:
      - elk-network
    healthcheck:
      test: ["CMD-SHELL", "curl -s http://localhost:5601/api/status | grep -q available"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  nginx-lb:
    image: nginx:1.25-alpine
    container_name: nginx-lb
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ../html:/usr/share/nginx/html:ro
      - ../logs/nginx:/var/log/nginx
    ports:
      - "80:80"
    networks:
      - elk-network
    restart: unless-stopped

  app-service:
    build:
      context: ./app
      dockerfile: ./Dockerfile
    container_name: app-service
    volumes:
      - ../logs/app:/var/log/app
    ports:
      - "5000:5000"
    networks:
      - elk-network
    restart: unless-stopped

  ssh-simulator:
    image: ubuntu:22.04
    container_name: ssh-simulator
    volumes:
      - ./generate_ssh_logs.sh:/generate_ssh_logs.sh:ro
      - ../logs/ssh:/var/log/ssh
    entrypoint: ["/bin/bash", "-c", "apt-get update -qq && apt-get install -y -qq python3 curl && chmod +x /generate_ssh_logs.sh && /generate_ssh_logs.sh 20 && while sleep 30; do /generate_ssh_logs.sh 5; done"]
    networks:
      - elk-network
    restart: unless-stopped

  syslog-simulator:
    image: ubuntu:22.04
    container_name: syslog-simulator
    volumes:
      - ./generate_syslog.sh:/generate_syslog.sh:ro
      - ../logs/syslog:/var/log/syslog
    entrypoint: ["/bin/bash", "-c", "apt-get update -qq && apt-get install -y -qq python3 curl && chmod +x /generate_syslog.sh && /generate_syslog.sh 50 && while sleep 45; do /generate_syslog.sh 10; done"]
    networks:
      - elk-network
    restart: unless-stopped

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
    restart: unless-stopped"""

FILEBEAT_YML = """filebeat.inputs:
  - type: filestream
    id: nginx-access
    enabled: true
    paths:
      - /var/log/nginx/access.log
    fields:
      service: nginx
    fields_under_root: true
    harvester_buffer_size: 16384
    max_bytes: 1048576
    close_inactive: 1m
    scan_frequency: 1s

  - type: filestream
    id: nginx-error
    enabled: true
    paths:
      - /var/log/nginx/error.log
    fields:
      service: nginx
    fields_under_root: true
    harvester_buffer_size: 16384
    max_bytes: 1048576

  - type: filestream
    id: ssh-auth
    enabled: true
    paths:
      - /var/log/ssh/auth.log
    fields:
      service: ssh
    fields_under_root: true
    harvester_buffer_size: 16384
    max_bytes: 1048576
    parsers:
      - multiline:
          type: pattern
          pattern: '^\\{'
          negate: true
          match: after

  - type: filestream
    id: syslog-linux
    enabled: true
    paths:
      - /var/log/syslog/linux.log
    fields:
      service: syslog
    fields_under_root: true
    harvester_buffer_size: 16384
    max_bytes: 1048576

  - type: filestream
    id: app-requests
    enabled: true
    paths:
      - /var/log/app/requests.log
    fields:
      service: app
    fields_under_root: true
    harvester_buffer_size: 16384
    max_bytes: 1048576
    parsers:
      - multiline:
          type: pattern
          pattern: '^\\{'
          negate: true
          match: after
          max_lines: 100
          timeout: 5s

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
  worker: 2

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  rotateeverybytes: 10485760"""

LOGSTASH_CONF = """input {
  beats {
    port => 5044
  }
}

filter {
  if [service] == "nginx" {
    grok {
      match => { "message" => "%{COMBINEDAPACHELOG}" }
      overwrite => ["message"]
      add_field => { "[@metadata][index]" => "nginx" }
    }
    date {
      match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
      target => "@timestamp"
    }
    mutate {
      convert => { "status" => "integer" "bytes" => "integer" }
    }
    geoip {
      source => "clientip"
      target => "geoip"
      add_field => { "country" => "%{[geoip][country_name]}" }
    }
  }

  if [service] == "ssh" {
    json {
      source => "message"
      target => "ssh_data"
    }
    date {
      match => [ "[ssh_data][timestamp]", "ISO8601" ]
      target => "@timestamp"
    }
    mutate {
      rename => { "[ssh_data][user]" => "ssh_user" }
      rename => { "[ssh_data][source_ip]" => "ssh_ip" }
      rename => { "[ssh_data][result]" => "ssh_result" }
      rename => { "[ssh_data][country]" => "ssh_country" }
      add_field => { "[@metadata][index]" => "ssh" }
      remove_field => ["ssh_data"]
    }
    geoip {
      source => "ssh_ip"
      target => "geoip"
      add_field => { "ssh_country" => "%{[geoip][country_name]}" }
    }
  }

  if [service] == "syslog" {
    grok {
      match => { "message" => "<%{POSINT:priority}>%{NONZERO_INT:version} %{TIMESTAMP_ISO8601:timestamp} %{HOSTNAME:hostname} %{NOTSPACE:process} %{INT:pid} %{NOTSPACE} %{GREEDYDATA:message}" }
      overwrite => ["message"]
      add_field => { "[@metadata][index]" => "syslog" }
    }
    mutate {
      convert => { "priority" => "integer" }
    }
  }

  if [service] == "app" {
    json {
      source => "message"
      target => "app_data"
    }
    date {
      match => [ "[app_data][timestamp]", "ISO8601" ]
      target => "@timestamp"
    }
    mutate {
      rename => { "[app_data][method]" => "request_method" }
      rename => { "[app_data][endpoint]" => "request_endpoint" }
      rename => { "[app_data][status_code]" => "request_status" }
      rename => { "[app_data][latency_ms]" => "request_latency" }
      add_field => { "[@metadata][index]" => "app" }
      remove_field => ["app_data"]
    }
  }

  mutate {
    add_field => { "lab" => "elk-observability" }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{[@metadata][index]}-%{+YYYY.MM.dd}"
    manage_template => false
  }
  stdout {
    codec => rubydebug
  }
}"""

WINLOGBEAT_YML = """winlogbeat.event_logs:
  - name: Security
    processors:
      - script:
          when.equals.event_id: 4624
          fields:
            logon_result: success
      - script:
          when.equals.event_id: 4625
          fields:
            logon_result: failure
  - name: System
  - name: Application

fields:
  env: lab
  datacenter: dc1
fields_under_root: true

output.logstash:
  hosts: ["elk-server:5044"]
  compression_level: 3

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/winlogbeat
  name: winlogbeat
  keepfiles: 7"""

def build():
    doc = SimpleDocTemplate(
        '/home/morta/workspace/elk-lab/docs/student_answer_sheet_filled.pdf',
        pagesize=A4,
        leftMargin=LM, rightMargin=RM,
        topMargin=TM + 12*mm, bottomMargin=BM + 10*mm,
        title='Student Answer Sheet — ELK Observability Lab',
        author='Kara Mohamed Mourtadha',
    )
    S = make_styles()
    story = []

    # COVER
    story.append(sp(30))
    cover_title_style = ParagraphStyle('ct2', fontSize=28, fontName='Helvetica-Bold',
        textColor=C_WHITE, alignment=TA_CENTER, spaceAfter=8)
    cover_sub_style = ParagraphStyle('cs2', fontSize=14, fontName='Helvetica',
        textColor=colors.HexColor('#bbdefb'), alignment=TA_CENTER, spaceAfter=4)
    story.append(Paragraph('ELK Stack Lab', cover_title_style))
    story.append(Paragraph('Observability & Centralized Logging - Chapter 5', cover_sub_style))
    story.append(sp(10))

    meta_data = [
        [Paragraph('<b>Student Name</b>', S['meta_label']),
         Paragraph('Kara Mohamed Mourtadha', S['meta_value']),
         Paragraph('<b>Group</b>', S['meta_label']),
         Paragraph('5', S['meta_value'])],
        [Paragraph('<b>Course</b>', S['meta_label']),
         Paragraph('Systems Reliability Engineering (SRE)', S['meta_value']),
         Paragraph('<b>Class</b>', S['meta_label']),
         Paragraph('Semester 1, 2025-2026', S['meta_value'])],
        [Paragraph('<b>Lab</b>', S['meta_label']),
         Paragraph('ELK Stack - Observability & Centralized Logging', S['meta_value']),
         Paragraph('<b>Chapter</b>', S['meta_label']),
         Paragraph('5', S['meta_value'])],
    ]
    meta_col = [3.2*cm, 7.5*cm, 3.2*cm, 5.5*cm]
    meta_t = Table(meta_data, colWidths=meta_col)
    meta_t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,-1), colors.HexColor('#e8eaf6')),
        ('BACKGROUND',    (2,0), (2,-1), colors.HexColor('#e8eaf6')),
        ('BACKGROUND',    (1,0), (1,-1), C_WHITE),
        ('BACKGROUND',    (3,0), (3,-1), C_WHITE),
        ('BOX',           (0,0), (-1,-1), 1.5, C_BLUE),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, C_GREY_LINE),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 10),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW',     (0,0), (-1,0), 2, C_BLUE),
    ]))
    story.append(meta_t)
    story.append(PageBreak())

    # SECTION 1
    story.append(section_header('Section 1 — The Challenge', S))
    story.append(sp(8))
    story.append(KeepTogether([
        subsection_title('1.1 Why did binary "up/down" monitoring fail?', S),
        sp(4),
        answer_box([
            Paragraph('<b>Binary monitoring failed</b> because it only answers "Is the service reachable?" not "How well is it performing?"', S['body']),
            sp(6),
            Paragraph('<b>Three reasons predefined questions fail for p99 latency:</b>', S['body_bold']),
            sp(3),
            bullet_p('<b>Cardinality explosion:</b> Latency depends on service, endpoint, payload, zone, dependencies. No health-check predicts all combinations.', S),
            bullet_p('<b>Unknown unknowns:</b> p99 spikes come from cross-service interactions invisible to individual service checks.', S),
            bullet_p('<b>Statistical invisibility:</b> Mean hides outliers. Only p95/p99 and traces catch slow requests.', S),
        ], S),
    ]))
    story.append(PageBreak())

    # SECTION 2
    story.append(section_header('Section 2 — The Three Pillars of Observability', S))
    story.append(sp(8))
    story.append(subsection_title('2.1 Pillar Characteristics Table', S))
    story.append(sp(4))

    pillar_rows = [
        ['Logs', 'Discrete events, high cardinality. Immutable timestamped records.', 'Debug failed checkout by order_id'],
        ['Metrics', 'Aggregated numeric time-series, low cardinality. Sampled at fixed intervals.', 'Alert error_rate > 2% over 5min'],
        ['Traces', 'Per-request call graphs, very high cardinality. DAG of spans with trace_id.', 'Find which service caused 3s delay'],
    ]
    story.append(data_table(
        ['Pillar', 'Data Characteristic', 'E-Commerce Use Case'],
        pillar_rows,
        [2.2*cm, 7.3*cm, CONTENT_W - 2.2*cm - 7.3*cm], S
    ))
    story.append(sp(10))

    story.append(KeepTogether([
        subsection_title('2.2 How do Traces resolve bottlenecks?', S),
        sp(4),
        answer_box([
            Paragraph('Traces resolve bottlenecks through <b>end-to-end correlation via trace ID</b>:', S['body']),
            sp(6),
            bullet_p('<b>Propagation:</b> trace_id injected into every downstream call.', S),
            bullet_p('<b>Span recording:</b> Each service records timed spans with parent-child relationships.', S),
            bullet_p('<b>Waterfall:</b> Spans assembled showing exactly where delays occur across services.', S),
        ], S),
    ]))
    story.append(PageBreak())

    # SECTION 3
    story.append(section_header('Section 3 — Part 2: ELK Technical Analysis', S))
    story.append(sp(8))

    qa_pairs = [
        ('3.1 Beats &amp; Elastic Agent', [
            Paragraph('<b>Beats</b> are lightweight Go shippers running as OS agents.', S['body']),
            bullet_p('<b>Filebeat</b> — tails log files, tracks positions in registry.', S),
            bullet_p('<b>Winlogbeat</b> — subscribes to Windows Event Log API.', S),
            Paragraph('<b>Elastic Agent</b> — unified shipper managed via Kibana Fleet.', S['body']),
        ]),
        ('3.2 Logstash &amp; Grok', [
            Paragraph('<b>Logstash</b> — Input (port 5044) → Filter (Grok/GeoIP) → Output (ES).', S['body']),
            Paragraph('<b>Grok</b> — parses text into structured fields using named regex patterns.', S['body']),
        ]),
        ('3.3 Elasticsearch &amp; The Inverted Index', [
            Paragraph('<b>Elasticsearch</b> — distributed search engine using inverted index.', S['body']),
            Paragraph('Inverted index maps "word → document IDs" enabling sub-millisecond search across terabytes.', S['body']),
        ]),
        ('3.4 Kibana', [
            Paragraph('<b>Kibana</b> — visualization layer: Discover, Visualize, Dashboard, Maps.', S['body']),
        ]),
    ]

    for title, content in qa_pairs:
        story.append(KeepTogether([
            subsection_title(title, S),
            sp(4),
            answer_box(content, S),
            sp(8),
        ]))
    story.append(PageBreak())

    # SECTION 4
    story.append(section_header('Section 4 — Part 3: WEF Design Challenge', S))
    story.append(sp(8))
    story.append(subsection_title('4.1 WEF Architecture Evaluation Table', S))
    story.append(sp(4))

    wef_rows = [
        ['Scalability', 'HIGH — agents push independently', 'LOW — collector polls each source'],
        ['Firewall', 'Complex — inbound rules needed', 'Simple — outbound only'],
        ['Remote Laptops', 'IDEAL — tolerates disconnection', 'PROBLEMATIC — cannot poll offline'],
    ]
    story.append(data_table(
        ['Feature', 'Source-Initiated (Push)', 'Collector-Initiated (Pull)'],
        wef_rows, [3*cm, 7.9*cm, CONTENT_W - 3*cm - 7.9*cm], S
    ))
    story.append(sp(10))

    story.append(KeepTogether([
        subsection_title('4.2 Windows Server 2025 Innovation', S),
        sp(4),
        answer_box([
            Paragraph('<b>IAKerb</b> — proxies Kerberos auth through intermediary, eliminating NTLM fallback.', S['body']),
            Paragraph('<b>Local KDC</b> — embedded KDC for offline Kerberos auth using cached credentials.', S['body']),
        ], S),
    ]))
    story.append(sp(10))

    story.append(KeepTogether([
        subsection_title('4.3 Forensic Prioritization', S),
        sp(4),
        Paragraph('Identify the two specific Windows Event IDs for logon success and failure:', S['body']),
        sp(6),
        answer_box([
            Paragraph('<b>Logon Success Event ID:</b> 4624', S['body_bold']),
            Paragraph('<b>Logon Failure Event ID:</b> 4625', S['body_bold']),
        ], S, accent=C_AMBER, bg=C_AMBER_LIGHT),
    ]))
    story.append(PageBreak())

    # SECTION 5
    story.append(section_header('Section 5 — Part 4: SLIs and Error Budgets', S))
    story.append(sp(8))

    story.append(KeepTogether([
        subsection_title('5.1 Error Budget Calculation', S),
        sp(4),
        Paragraph('Given: 99.95% SLO · Total minutes in 30 days = 43,200', S['body']),
        sp(4),
    ]))

    calc_rows = [
        ['Step 1 — SLO fraction',        'SLO = 99.95% = 0.9995'],
        ['Step 2 — Unavailability',       '1 - SLO = 0.0005'],
        ['Step 3 — Error Budget (min)',   '43,200 x 0.0005 = 21.6 minutes/month'],
    ]
    calc_t = Table(
        [[Paragraph(r, S['tbl_body']), Preformatted(v, S['code'])] for r, v in calc_rows],
        colWidths=[5*cm, CONTENT_W - 5*cm]
    )
    calc_t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,-1), colors.HexColor('#eceff1')),
        ('BACKGROUND',    (1,0), (1,-1), C_CODE_BG),
        ('GRID',          (0,0), (-1,-1), 0.5, C_GREY_LINE),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 10),
    ]))
    story.append(calc_t)
    story.append(sp(6))

    fa_t = Table([[Paragraph('Error Budget = <b>21.6 minutes per month</b>', S['final_answer'])]]
    )
    fa_t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,-1), C_GREEN_LIGHT),
        ('BOX',         (0,0), (-1,-1), 2, C_TEAL),
        ('TOPPADDING',  (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(fa_t)
    story.append(sp(10))

    story.append(KeepTogether([
        subsection_title('5.2 SLI Proposal', S),
        sp(4),
        answer_box([
            Paragraph('<b>Proposed SLI:</b> Percentage of POST /api/checkout requests with HTTP 2xx AND latency < 500ms.', S['body_bold']),
            bullet_p('<b>HTTP 2xx gate:</b> 5xx = complete checkout failure.', S),
            bullet_p('<b>500ms latency gate:</b> Cart abandonment rises above 400ms.', S),
        ], S),
    ]))
    story.append(sp(10))

    story.append(KeepTogether([
        subsection_title('5.3 The "SRE Clamp"', S),
        sp(4),
        answer_box([
            Paragraph('When >50% of error budget consumed (>10.8 of 21.6 min): <b>freeze feature deployments</b>, redirect to reliability work.', S['body']),
        ], S),
    ]))
    story.append(PageBreak())

    # SECTION 6
    story.append(section_header('Section 6 — Part 5: Practical Implementation', S))
    story.append(sp(8))

    def config_section(title, code_str):
        items = [subsection_title(title, S), sp(4)]
        items += code_block(code_str, S)
        items.append(sp(10))
        return items

    story += config_section('6.1 docker-compose.yml', DOCKER_COMPOSE)
    story += config_section('6.2 filebeat.yml', FILEBEAT_YML)
    story += config_section('6.3 winlogbeat.yml', WINLOGBEAT_YML)
    story += config_section('6.4 logstash.conf', LOGSTASH_CONF)
    story.append(sp(10))

    story.append(PageBreak())
    story.append(section_header('Section 6.5 - Screenshots: Kibana Visual Proof', S))
    story.append(sp(8))

    screenshot_files = [
        ('explore-logs.png', 'Figure 1: Discover - Explore logs in Kibana'),
        ('query-logs.png', 'Figure 2: Discover - Query logs with KQL'),
        ('query-logs-b.png', 'Figure 3: Discover - Filter by service field'),
        ('query-logs-c.png', 'Figure 4: Discover - Filter results'),
        ('query-logs-d.png', 'Figure 5: Discover - View document details'),
        ('dashboard-all.png', 'Figure 6: Dashboard - Full overview'),
        ('create-vilz-b.png', 'Figure 7: Visualize - Create visualization'),
        ('creating-vizulation.png', 'Figure 8: Visualize - Creating chart'),
        ('nginx-healthy-200.png', 'Figure 9: Nginx - 200 status check'),
        ('windows-export-logs.png', 'Figure 10: Windows - Winlogbeat export logs'),
    ]

    for i, (img_file, caption) in enumerate(screenshot_files):
        img_path = f'/home/morta/workspace/elk-lab/docs/images/{img_file}'
        try:
            img = Image(img_path)
            img.drawHeight = 4*cm
            img.drawWidth = 7*cm
            
            caption_p = Paragraph(f'<br/><br/>{caption}', S['meta_value'])
            caption_p.alignment = TA_CENTER
            
            story.append(KeepTogether([img, caption_p, Spacer(1, 4)]))
            
            if (i + 1) % 2 == 0:
                story.append(PageBreak())
        except Exception as e:
            pass
            pass

    story.append(PageBreak())

    # SECTION 7
    story.append(section_header('Section 7 — Final Deliverable: System Interaction Maps', S))
    story.append(sp(8))

    sources = [
        {
            'title': 'Data Source 1 — Nginx Web Server',
            'color': C_BLUE,
            'pairs': [
                ('Source Name', 'Nginx Web Server'),
                ('Telemetry Type', 'Log'),
                ('Shipper', 'Filebeat'),
                ('Identity Protocol', 'Combined Apache Log format via Beats on TCP 5044'),
                ('Processing', 'Logstash Grok filter %{COMBINEDAPACHELOG}'),
                ('Transformation', 'Extract clientip, status, request. GeoIP enrichment.'),
                ('Final Destination', 'Elasticsearch: logs-nginx-YYYY.MM.DD'),
                ('Visualization', 'Kibana — Traffic charts, status codes, geo maps'),
            ]
        },
        {
            'title': 'Data Source 2 — SSH Authentication Events',
            'color': colors.HexColor('#6a1b9a'),
            'pairs': [
                ('Source Name', 'SSH Authentication Simulator'),
                ('Telemetry Type', 'Log'),
                ('Shipper', 'Filebeat'),
                ('Identity Protocol', 'JSON via Beats on TCP 5044'),
                ('Processing', 'Logstash JSON filter'),
                ('Transformation', 'Extract user, result, source_ip. GeoIP enrichment.'),
                ('Final Destination', 'Elasticsearch: logs-ssh-YYYY.MM.DD'),
                ('Visualization', 'Kibana — Auth results pie chart, attack map'),
            ]
        },
        {
            'title': 'Data Source 3 — Syslog Linux (RFC5424)',
            'color': colors.HexColor('#00897b'),
            'pairs': [
                ('Source Name', 'Linux Syslog Simulator'),
                ('Telemetry Type', 'Log'),
                ('Shipper', 'Filebeat'),
                ('Identity Protocol', 'RFC5424 via Beats on TCP 5044'),
                ('Processing', 'Logstash Grok filter'),
                ('Transformation', 'Extract priority, hostname, process, message.'),
                ('Final Destination', 'Elasticsearch: logs-syslog-YYYY.MM.DD'),
                ('Visualization', 'Kibana — System events timeline'),
            ]
        },
        {
            'title': 'Data Source 4 — App Service (REST API)',
            'color': colors.HexColor('#c62828'),
            'pairs': [
                ('Source Name', 'Flask App Service'),
                ('Telemetry Type', 'Log + Metric'),
                ('Shipper', 'Filebeat'),
                ('Identity Protocol', 'JSON via Beats on TCP 5044'),
                ('Processing', 'Logstash JSON filter'),
                ('Transformation', 'Extract method, endpoint, status_code, latency_ms.'),
                ('Final Destination', 'Elasticsearch: logs-app-YYYY.MM.DD'),
                ('Visualization', 'Kibana — Latency histogram, endpoint counts'),
            ]
        },
        {
            'title': 'Data Source 5 — Windows Security Event Logs',
            'color': colors.HexColor('#bf360c'),
            'pairs': [
                ('Source Name', 'Windows Server 2025 Security Event Log'),
                ('Telemetry Type', 'Log'),
                ('Shipper', 'Winlogbeat'),
                ('Identity Protocol', 'Windows Event XML via Beats on TCP 5044'),
                ('Processing', 'Logstash conditional routing on event_id'),
                ('Transformation', 'Add logon_result. GeoIP on IpAddress.'),
                ('Final Destination', 'Elasticsearch: logs-windows-YYYY.MM.DD'),
                ('Visualization', 'Kibana — Logon success/failure, attack origins'),
            ]
        },
    ]

    for src in sources:
        rows = [[Paragraph(f'<b>{k}</b>', S['tbl_body']), Paragraph(v, S['tbl_body'])]
                for k, v in src['pairs']]
        t = Table(rows, colWidths=[4*cm, CONTENT_W - 4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (0,-1), C_BLUE_LIGHT),
            ('GRID',          (0,0), (-1,-1), 0.5, C_GREY_LINE),
            ('LINEABOVE',     (0,0), (-1,0), 2, src['color']),
            ('LINEBELOW',     (0,-1),(-1,-1), 2, src['color']),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
            ('ROWBACKGROUNDS',(0,0),(-1,-1), [C_BLUE_LIGHT, C_WHITE]),
        ]))
        story.append(KeepTogether([
            subsection_title(src['title'], S),
            sp(4), t, sp(12)
        ]))

    doc.build(story, onFirstPage=first_page_template, onLaterPages=page_template)
    print('PDF generated successfully.')

build()
