# Builds the Protocol0 Windows exe (PyInstaller): the resident agent.
#
# Output:
#   - src/agent/dist/Protocol0.exe   (resident agent: keyboard hook + web server + systray)
# Also generates installer/assets/protocol0.ico BEFORE the build, because the agent now
# embeds it (the systray icon, agent/tray.py loads it via _MEIPASS).
#
# There is no longer a separate protocol0-launcher.exe: the Start-Menu/desktop shortcut
# launches `Protocol0.exe --open` (start-on-click, AutoHotkey style), which opens the
# config page and then either becomes resident or exits via the single-instance mutex.
#
# Prerequisites (build machine only): Poetry + Python 3.11+.
# The agent embeds src/frontend/dist (the Vue 3 SPA) -> it must be built FIRST (npm run build).

# PS 5.1 note: poetry/pyinstaller write their logs to stderr. With
# $ErrorActionPreference="Stop", PowerShell turns that stderr into a terminating error
# even when the exit code is 0. So we keep "Continue" and judge success on
# $LASTEXITCODE (the real native exit code), not on stderr.
$ErrorActionPreference = "Continue"

# This script lives in scripts/windows/, so the repo root is two levels up.
$repoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
$agentDir = Join-Path $repoRoot "src\agent"

# The SPA must be built first: PyInstaller embeds it via datas (see protocol0-agent.spec).
$frontendIndex = Join-Path $repoRoot "src\frontend\dist\index.html"
if (-not (Test-Path $frontendIndex)) {
    throw "src/frontend/dist/index.html not found. Build the SPA first (cd src/frontend; npm ci; npm run build)."
}

Push-Location $agentDir
try {
    Write-Host "Installing agent deps (incl. pyinstaller)..."
    & poetry install
    if ($LASTEXITCODE -ne 0) { throw "poetry install failed (exit $LASTEXITCODE)." }

    # Icon: regenerated on every build to stay in sync with the source badge
    # (src/website/favicon.svg). Must come BEFORE the agent build, which embeds it
    # (datas in protocol0-agent.spec) for the systray.
    Write-Host "Generating icon (protocol0.ico)..."
    & poetry run python (Join-Path $repoRoot "scripts\windows\generate_icon.py")
    if ($LASTEXITCODE -ne 0) { throw "generate_icon.py failed (exit $LASTEXITCODE)." }

    Write-Host "Building protocol0-agent.exe..."
    & poetry run pyinstaller --clean --noconfirm protocol0-agent.spec
    if ($LASTEXITCODE -ne 0) { throw "pyinstaller (agent) failed (exit $LASTEXITCODE)." }

    $exe = Join-Path $agentDir "dist\Protocol0.exe"
    if (-not (Test-Path $exe)) {
        throw "Build finished but $exe not found."
    }
    Write-Host "OK -> $exe"
} finally {
    Pop-Location
}
