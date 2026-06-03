# Retire la tâche planifiée Protocol0.
# Appelé par l'uninstaller Inno Setup (avant suppression des fichiers).

$ErrorActionPreference = "Stop"

$taskName = "Protocol0"

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Stop-ScheduledTask  -TaskName $taskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed scheduled task: $taskName"
} else {
    Write-Host "No scheduled task named $taskName found."
}

# Tuer le process s'il tourne encore : sans ça l'uninstaller ne peut pas supprimer
# l'exe verrouillé dans Program Files. La tâche étant déjà retirée, il ne redémarre pas.
taskkill /F /IM protocol0-agent.exe 2>$null
exit 0
