# Réactive le détecteur Protocol0 après un disable_protocol0_task.ps1.
# Ré-enable la tâche planifiée puis la démarre immédiatement (sans attendre le
# prochain logon).

$ErrorActionPreference = "Stop"

$taskName = "Protocol0"

if (-not (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue)) {
    Write-Host "No scheduled task named '$taskName' found."
    exit 1
}

Enable-ScheduledTask -TaskName $taskName | Out-Null
Start-ScheduledTask  -TaskName $taskName

Start-Sleep -Seconds 2

$state = (Get-ScheduledTask -TaskName $taskName).State
Write-Host "OK: '$taskName' state is $state."
