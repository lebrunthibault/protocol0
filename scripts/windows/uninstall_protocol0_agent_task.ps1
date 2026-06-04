# Removes the Protocol0 scheduled task.
# Called by the Inno Setup uninstaller (before the files are deleted).

$ErrorActionPreference = "Stop"

$taskName = "Protocol0"

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Stop-ScheduledTask  -TaskName $taskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed scheduled task: $taskName"
} else {
    Write-Host "No scheduled task named $taskName found."
}

# Kill the process if it is still running: otherwise the uninstaller cannot delete the
# locked exe in Program Files. The task being already removed, it will not restart.
# No agent running -> a true no-op (no spurious non-zero exit from taskkill).
Get-Process -Name protocol0-agent -ErrorAction SilentlyContinue |
    Stop-Process -Force -ErrorAction SilentlyContinue
exit 0
