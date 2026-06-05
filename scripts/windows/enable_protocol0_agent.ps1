# Starts the Protocol0 agent now, for manual testing (after disable_protocol0_agent.ps1).
#
# Launches the installed exe directly. The single-instance mutex makes this a no-op if an
# agent is already running. Resolves the exe from the default install dir; override with
# -ExePath for a custom location.

param(
    [string]$ExePath = "$env:ProgramFiles\Protocol0\Protocol0.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ExePath)) {
    Write-Host "Agent exe not found: $ExePath"
    Write-Host "Pass -ExePath <path> or install Protocol 0 first."
    exit 1
}

Start-Process -FilePath $ExePath
Start-Sleep -Seconds 2

# Get-Process -Name takes the image name WITHOUT .exe -> "Protocol0".
if (Get-Process -Name "Protocol0" -ErrorAction SilentlyContinue) {
    Write-Host "OK: Protocol0 is running."
} else {
    Write-Host "WARNING: Protocol0 did not start (check %APPDATA%\Protocol0\logs\agent.log)."
    exit 1
}
