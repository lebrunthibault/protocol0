# Reload the p0_backend scheduled task.
#
# `Stop-ScheduledTask` only kills the top-level action process (the wrapper
# powershell), not always its grandchildren (uvicorn). If uvicorn survives,
# the next `Start-ScheduledTask` finds port 8000 taken and the new instance
# crashes silently, leaving the stale build running. So:
#   1. Stop the task (best-effort).
#   2. Kill whatever is still listening on the backend port.
#   3. Start the task.

$ErrorActionPreference = "Stop"

$taskName = "p0_backend"
$port = if ($env:P0_BACKEND_PORT) { [int]$env:P0_BACKEND_PORT } else { 8000 }

try { Stop-ScheduledTask -TaskName $taskName -ErrorAction Stop } catch {}

# Get-NetTCPConnection is the cleanest way; fall back to netstat parsing if
# the cmdlet is unavailable (Server Core, restricted PowerShell).
$pids = @()
try {
    $pids = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction Stop |
        Select-Object -ExpandProperty OwningProcess -Unique
} catch {
    $pids = netstat -ano | Select-String ":$port\s+.*LISTENING" |
        ForEach-Object { ($_ -split "\s+")[-1] } | Sort-Object -Unique
}

foreach ($processId in $pids) {
    if ($processId -and $processId -ne 0) {
        try {
            Stop-Process -Id $processId -Force -ErrorAction Stop
            Write-Host "killed stale backend pid $processId"
        } catch {
            Write-Host "could not kill pid ${processId}: $_"
        }
    }
}

Start-ScheduledTask -TaskName $taskName
Write-Host "p0_backend reloaded"
