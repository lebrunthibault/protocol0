# Désactive manuellement le détecteur Protocol0, pour les tests.
#
# Disable-ScheduledTask seul ne suffit PAS : il empêche les futurs déclenchements
# (logon-trigger) mais ne tue pas le process déjà lancé, et Stop-ScheduledTask seul
# ne suffit pas non plus car la politique de restart-on-crash (RestartCount 999) le
# relancerait. On fait donc les deux dans le bon ordre :
#   1. Disable  -> coupe le trigger ET le restart automatique
#   2. taskkill -> tue le process en cours
#
# Réactiver avec enable_protocol0_task.ps1.

$ErrorActionPreference = "Stop"

$taskName = "Protocol0"

if (-not (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue)) {
    Write-Host "No scheduled task named '$taskName' found."
    exit 1
}

Disable-ScheduledTask -TaskName $taskName | Out-Null

# Tue le process déjà lancé (le scheduler ne le relance pas : la tâche est disabled).
taskkill /F /IM protocol0-detector.exe 2>$null | Out-Null

Start-Sleep -Seconds 1

$state = (Get-ScheduledTask -TaskName $taskName).State
$alive = Get-Process -Name "protocol0-detector" -ErrorAction SilentlyContinue
if ($state -eq "Disabled" -and -not $alive) {
    Write-Host "OK: '$taskName' is Disabled and no detector process is running."
} else {
    Write-Host "WARNING: state=$state, process running=$([bool]$alive)"
    exit 1
}
