# Stops the running Protocol0 agent, for manual testing.
#
# With the Startup-folder model there is no scheduled task to disable and no
# restart-on-crash policy to fight: killing the process is enough. It will NOT come back
# until the next logon (or until you run enable_protocol0_agent.ps1 / click the shortcut).
#
# Targets the installed frozen exe (Protocol0.exe). For a source-mode agent
# (`poetry run agent`, which runs under python.exe), use `make kill-agent` instead.
#
# Re-launch with enable_protocol0_agent.ps1.

$ErrorActionPreference = "Stop"

# Get-Process -Name takes the image name WITHOUT .exe -> "Protocol0".
$proc = Get-Process -Name "Protocol0" -ErrorAction SilentlyContinue
if (-not $proc) {
    Write-Host "No Protocol0 agent process is running."
    exit 0
}

taskkill /F /IM Protocol0.exe 2>$null | Out-Null
Start-Sleep -Seconds 1

if (Get-Process -Name "Protocol0" -ErrorAction SilentlyContinue) {
    Write-Host "WARNING: Protocol0 is still running."
    exit 1
}
Write-Host "OK: Protocol0 stopped."
