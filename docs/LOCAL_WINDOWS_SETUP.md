# Local Windows Node Setup Guide

## Prerequisites

- Windows Machine (Windows 10/11 or Windows Server 2016+)
- Administrator access
- Network connectivity to Docker host (Logstash)

---

## Step 1: Download Winlogbeat

1. Download Winlogbeat from: https://www.elastic.co/downloads/beats/winlogbeat
2. Extract to `C:\Program Files\Winlogbeat`

---

## Step 2: Configure Winlogbeat

Copy `winlogbeat.yml` to `C:\Program Files\Winlogbeat\winlogbeat.yml`

**Important**: Update the Logstash host to point to your Docker host:

```yaml
output.logstash:
  hosts: ["DOCKER_HOST_IP:5044"]  # Replace with your Docker host IP
```

To find Docker host IP:
```powershell
# On Linux Docker host:
hostname -I | awk '{print $1}'
```

---

## Step 3: Install Winlogbeat Service

Run PowerShell as Administrator:

```powershell
cd "C:\Program Files\Winlogbeat"
.\install-service-winlogbeat.ps1
```

If script execution is disabled:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install-service-winlogbeat.ps1
```

---

## Step 4: Generate Sample Events

```powershell
.\generate_windows_events.ps1 -EventCount 100
```

This generates:
- ~80 Event ID 4624 (Logon Success)
- ~20 Event ID 4625 (Logon Failure)

---

## Step 5: Start Winlogbeat

```powershell
Start-Service winlogbeat
Get-Service winlogbeat
```

---

## Step 6: Verify in Kibana

1. Open Kibana: http://DOCKER_HOST_IP:5601
2. Go to **Discover**
3. Create index pattern: `logs-*`
4. Search: `tags: windows`
5. Should see Windows events flowing in

---

## Troubleshooting

**Winlogbeat not starting:**
```powershell
Get-EventLog -LogName Application -Source "Winlogbeat" -Newest 10
```

**Events not showing in Kibana:**
```powershell
Test-NetConnection -ComputerName DOCKER_HOST_IP -Port 5044
```

**View Winlogbeat logs:**
```
C:\ProgramData\winlogbeat\Logs\winlogbeat
```

---

## Quick Command Reference

```powershell
# Check service status
Get-Service winlogbeat

# Stop service
Stop-Service winlogbeat

# Start service
Start-Service winlogbeat

# Restart service
Restart-Service winlogbeat

# View recent events
Get-EventLog -LogName Security -Newest 10

# Generate more events
.\generate_windows_events.ps1 -EventCount 50
```
