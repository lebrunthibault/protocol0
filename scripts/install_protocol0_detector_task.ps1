# Enregistre protocol0-detector comme tâche planifiée Windows qui :
#   - démarre à l'ouverture de session (session interactive : requis pour la capture
#     clavier globale + le check de fenêtre au premier plan ; un service en session 0
#     ne verrait pas le clavier ni le focus)
#   - redémarre sur crash détecté par le Task Scheduler (jusqu'à 999x, intervalle 1 min)
#   - tourne fenêtre cachée (l'exe est no-console, donc aucun flash — pas de shim VBS,
#     contrairement à install_p0_backend_task.ps1 qui lance un powershell.exe à console)
#
# Le détecteur logge lui-même dans %APPDATA%\Protocol0\logs\detector.log : pas de
# redirection stderr ici (qui réintroduirait une console).
#
# Appelé par l'installeur Inno Setup avec -ExePath. Idempotent. Voir
# uninstall_protocol0_detector_task.ps1 pour le retrait.

param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath
)

$ErrorActionPreference = "Stop"

$taskName = "protocol0-detector"

if (-not (Test-Path $ExePath)) {
    throw "Detector exe not found: $ExePath"
}

$action = New-ScheduledTaskAction -Execute $ExePath

# Au logon de l'utilisateur courant. Crash recovery via RestartCount ci-dessous.
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

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Protocol0 keyboard-shortcut detector (auto-start at logon, restart on crash)." | Out-Null

Write-Host "Starting $taskName..."
Start-ScheduledTask -TaskName $taskName

Start-Sleep -Seconds 2
Get-ScheduledTask -TaskName $taskName | Format-Table -AutoSize TaskName, State
Write-Host ""
Write-Host "Logs: %APPDATA%\Protocol0\logs\detector.log"
Write-Host "Manage with:"
Write-Host "  Stop-ScheduledTask  -TaskName $taskName"
Write-Host "  Start-ScheduledTask -TaskName $taskName"
Write-Host "  taskschd.msc        (GUI)"
