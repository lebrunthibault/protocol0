# Register p0_backend as a Windows Scheduled Task that:
#   - starts at user logon (runs under the current user -> poetry venv reachable)
#   - restarts on crash (3x at 1-min intervals)
#   - writes logs to <repo>/.logs/backend.log via P0_LOG_FILE env var
#
# Run from a regular PowerShell (no admin needed for logon-triggered tasks).
# Idempotent: re-registers cleanly. Use uninstall_p0_backend_task.ps1 to remove.

$ErrorActionPreference = "Stop"

$taskName   = "p0_backend"
$repoRoot   = (Resolve-Path "$PSScriptRoot\..").Path
$backendDir = Join-Path $repoRoot "backend"
$logsDir    = Join-Path $repoRoot ".logs"
$logFile    = Join-Path $logsDir "backend.log"

Push-Location $backendDir
try {
    $venv = (& poetry env info -p).Trim()
} finally {
    Pop-Location
}
$backendExe = Join-Path $venv "Scripts\backend.cmd"
if (-not (Test-Path $backendExe)) {
    throw "$backendExe not found. Run 'poetry install' from $backendDir first."
}

New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

# Use PowerShell directly so we can set the env var and cd to the project dir
# without an extra .cmd wrapper. -WindowStyle Hidden keeps no console popping up.
# Stderr is captured to a side-file because uvicorn's startup errors print
# there before loguru's file sink is configured.
$stderrFile = Join-Path $logsDir "backend.err.log"
$argTemplate = @(
    '-NoProfile'
    '-WindowStyle', 'Hidden'
    '-Command',
    "& { `$env:P0_LOG_FILE = '$logFile'; Set-Location '$backendDir'; & '$backendExe' *>> '$stderrFile' }"
) -join ' '

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument $argTemplate

# Two triggers:
#  1. At user logon (current user). Switch to "AtStartup" if you want it
#     running even before login, but that forces SYSTEM context -> no venv access.
#  2. Repeat every 2 minutes forever. Combined with -MultipleInstances IgnoreNew
#     below, this is a no-op while the backend is alive and becomes the
#     restart-on-crash mechanism when it dies. Simpler and more reliable than
#     event-based triggers (which need Microsoft-Windows-TaskScheduler/Operational
#     enabled — disabled by default).
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$repeatTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) `
    -RepetitionInterval (New-TimeSpan -Minutes 2)
$trigger = @($logonTrigger, $repeatTrigger)

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Write-Host "Removing existing task $taskName..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Protocol0 FastAPI backend (auto-start at logon, retried every 2 min)." | Out-Null

Write-Host "Starting $taskName..."
Start-ScheduledTask -TaskName $taskName

Start-Sleep -Seconds 2
Get-ScheduledTask -TaskName $taskName | Format-Table -AutoSize TaskName, State
Write-Host ""
Write-Host "Logs: $logFile"
Write-Host "Manage with:"
Write-Host "  Stop-ScheduledTask  -TaskName $taskName"
Write-Host "  Start-ScheduledTask -TaskName $taskName"
Write-Host "  taskschd.msc        (GUI)"
