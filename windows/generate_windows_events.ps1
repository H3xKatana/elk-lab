param(
    [int]$EventCount = 50,
    [string]$LogName = "Security"
)

Write-Host "Generating $EventCount sample Windows security events..." -ForegroundColor Cyan

$EventID_Success = 4624
$EventID_Failure = 4625

for ($i = 1; $i -le $EventCount; $i++) {
    $IsSuccess = (Get-Random -Minimum 1 -Maximum 11) -le 8

    if ($IsSuccess) {
        $EventID = $EventID_Success
        $Message = "An account was successfully logged on."
        $Level = "Information"
    } else {
        $EventID = $EventID_Failure
        $Message = "An account failed to log on."
        $Level = "Warning"
    }

    $UserList = @("Administrator", "john.doe", "jane.smith", "service_account", "backup_user")
    $User = $UserList[(Get-Random -Minimum 0 -Maximum $UserList.Count)]
    $IP = "192.168.1.$((Get-Random -Minimum 10 -Maximum 250))"

    # Create the event (requires admin rights for Security log)
    try {
        $EventParams = @{
            LogName = $LogName
            Source = "Microsoft-Windows-Security-Auditing"
            EventID = $EventID
            EntryType = $Level
            Message = "$Message`n`nAccount: $User`nSource IP: $IP`nLogon Type: 3 (Network)"
        }
        Write-EventLog @EventParams -ErrorAction Stop
    } catch {
        # If we can't write to Security log, write to Application log instead
        Write-EventLog -LogName "Application" `
                     -Source "ELK-Lab-Simulator" `
                     -EventID $EventID `
                     -EntryType $Level `
                     -Message "$Message`nAccount: $User`nSource IP: $IP"
    }

    if ($i % 10 -eq 0) {
        Write-Host "  Generated $i/$EventCount events..." -ForegroundColor Yellow
    }
}

Write-Host "Successfully generated $EventCount events!" -ForegroundColor Green
Write-Host "  - Event ID 4624 (Success): $(($EventCount * 0.8))" -ForegroundColor Green
Write-Host "  - Event ID 4625 (Failure): $(($EventCount * 0.2))" -ForegroundColor Red
