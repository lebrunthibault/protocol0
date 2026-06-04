# Registers the Protocol0 agent as a Windows scheduled task that:
#   - starts at user logon (interactive session: required for global keyboard capture +
#     the foreground-window check; a service in session 0 would see neither keyboard nor focus)
#   - restarts on a crash detected by the Task Scheduler (up to 999x, 1 min interval)
#   - runs with a hidden window (the exe is no-console, so no flash -- no VBS shim)
#
# The agent logs to %APPDATA%\Protocol0\logs\agent.log itself: no stderr redirection
# here (which would reintroduce a console).
#
# Called by the Inno Setup installer with -ExePath. Idempotent. See
# uninstall_protocol0_agent_task.ps1 for removal.

param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath
)

$ErrorActionPreference = "Stop"

$taskName = "Protocol0"

if (-not (Test-Path $ExePath)) {
    throw "Agent exe not found: $ExePath"
}

$action = New-ScheduledTaskAction -Execute $ExePath

# At the current user's logon. Crash recovery via RestartCount below.
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

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

# Kill any agent already running before we (re)start the task. Unregistering the task
# does NOT stop a process it previously launched, and a manually-launched agent is
# unknown to the task entirely -- either way a leftover means two agents in parallel,
# which makes a single shortcut fire twice (cf. docs/debug-double-shortcut.md). After
# this, the Start-ScheduledTask below leaves exactly one agent running.
#
# When NO agent is running, taskkill exits 128 ("process not found"). With
# $ErrorActionPreference = "Stop" and the installer running this hidden, that non-zero
# exit must not abort the script before Register-ScheduledTask -- a fresh install (no
# prior agent) is the common case. Stop-Process is a cmdlet: -ErrorAction
# SilentlyContinue makes the "no such process" case a true no-op.
Get-Process -Name protocol0-agent -ErrorAction SilentlyContinue |
    Stop-Process -Force -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Protocol0 agent -- keyboard shortcuts + local web UI (auto-start at logon, restart on crash)." | Out-Null

Write-Host "Starting $taskName..."
Start-ScheduledTask -TaskName $taskName

Start-Sleep -Seconds 2
Get-ScheduledTask -TaskName $taskName | Format-Table -AutoSize TaskName, State
Write-Host ""
Write-Host "Logs: %APPDATA%\Protocol0\logs\agent.log"
Write-Host "Manage with:"
Write-Host "  scripts\windows\disable_protocol0_task.ps1   (disable + kill, for manual testing)"
Write-Host "  scripts\windows\enable_protocol0_task.ps1    (re-enable + start)"
Write-Host "  taskschd.msc                         (GUI)"
