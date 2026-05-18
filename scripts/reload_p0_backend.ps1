# Reload the p0_backend scheduled task.
#
# `Stop-ScheduledTask` only kills the top-level action process (the wrapper
# powershell), not always its grandchildren (uvicorn). If uvicorn survives,
# the next `Start-ScheduledTask` finds the backend port taken (read from .env
# below) and the new instance crashes silently, leaving the stale build
# running. So:
#   1. Stop the task (best-effort).
#   2. Kill whatever is still listening on the backend port.
#   3. Start the task.
#   4. Poll /ping to confirm the new instance actually came up.

$ErrorActionPreference = "Stop"

$taskName = "p0_backend"

$envFile = Join-Path $PSScriptRoot "..\.env"
$port = $null
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*P0_BACKEND_PORT\s*=\s*"?(\d+)"?') { $port = [int]$Matches[1] }
}
if (-not $port) { throw "P0_BACKEND_PORT not found in $envFile" }

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

# Poll /ping until the new instance answers, up to ~10s. Uses a fresh
# WebClient per attempt because HttpWebRequest caches DNS / connection state
# in ways that can mask the "not listening yet" condition.
$pingUrl = "http://127.0.0.1:$port/ping"
$deadline = (Get-Date).AddSeconds(10)
$pingOk = $false
while ((Get-Date) -lt $deadline) {
    try {
        $resp = (New-Object System.Net.WebClient).DownloadString($pingUrl)
        # FastAPI JSON-serializes the str return, so /ping yields the literal `"pong"` (with quotes).
        if ($resp.Trim() -eq '"pong"') { $pingOk = $true; break }
    } catch {}
    Start-Sleep -Milliseconds 500
}

if ($pingOk) {
    Write-Host "p0_backend reloaded (ping OK)"
} else {
    Write-Host "p0_backend started but /ping failed after 10s -- check .logs\backend.log"
    exit 1
}
