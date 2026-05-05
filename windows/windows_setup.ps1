Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Windows Edge Node Setup for ELK Lab" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$LogstashHost = "localhost"
$LogstashPort = 5044
$WinlogbeatDir = "C:\Program Files\Winlogbeat"

Write-Host "[1/5] Checking Winlogbeat installation..." -ForegroundColor Yellow
if (Test-Path $WinlogbeatDir) {
    Write-Host "  Winlogbeat already installed at $WinlogbeatDir" -ForegroundColor Green
} else {
    Write-Host "  Winlogbeat not found. Please install from:" -ForegroundColor Red
    Write-Host "  https://www.elastic.co/downloads/beats/winlogbeat" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[1/5] Checking Winlogbeat installation..." -ForegroundColor Yellow
if (Test-Path $WinlogbeatDir) {
    Write-Host "  Winlogbeat already installed at $WinlogbeatDir" -ForegroundColor Green
} else {
    Write-Host "  Winlogbeat not found. Please install from:" -ForegroundColor Red
    Write-Host "  https://www.elastic.co/downloads/beats/winlogbeat" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[2/5] Configuring Winlogbeat..." -ForegroundColor Yellow
Copy-Item -Path ".\winlogbeat.yml" -Destination "$WinlogbeatDir\winlogbeat.yml" -Force

Write-Host ""
Write-Host "[3/5] Generating sample Windows events..." -ForegroundColor Yellow
.\generate_windows_events.ps1 2>$null

Write-Host ""
Write-Host "[4/5] Starting Winlogbeat service..." -ForegroundColor Yellow
Set-Location $WinlogbeatDir
.\install-service-winlogbeat.ps1
Start-Service winlogbeat
Write-Host "  Winlogbeat service started" -ForegroundColor Green

Write-Host ""
Write-Host "[5/5] Verifying setup..." -ForegroundColor Yellow
$Service = Get-Service winlogbeat -ErrorAction SilentlyContinue
if ($Service.Status -eq "Running") {
    Write-Host "  Winlogbeat is running successfully!" -ForegroundColor Green
} else {
    Write-Host "  Winlogbeat is NOT running. Check logs at C:\ProgramData\winlogbeat\Logs" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Windows Edge Node Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Verify events in Kibana: http://localhost:5601" -ForegroundColor Yellow
Write-Host "  2. Check Logstash logs: docker logs elk-logstash" -ForegroundColor Yellow
Write-Host "  3. Generate more events: .\generate_windows_events.ps1" -ForegroundColor Yellow
