# Builds the Protocol0 Windows exes (PyInstaller): the resident agent AND the launcher.
#
# Outputs:
#   - src/agent/dist/protocol0-agent.exe    (resident agent, keyboard hook + web server)
#   - src/agent/dist/protocol0-launcher.exe (the clicked "shortcut": opens the web page)
# Also generates installer/assets/protocol0.ico (the launcher icon) before its build.
#
# Prerequisites (build machine only): Poetry + Python 3.11+.
# The agent embeds src/frontend/dist (the Vue 3 SPA) -> it must be built FIRST (npm run build).
# The launcher embeds installer/assets/protocol0.ico -> generated here just before its build.

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

    Write-Host "Building protocol0-agent.exe..."
    & poetry run pyinstaller --clean --noconfirm protocol0-agent.spec
    if ($LASTEXITCODE -ne 0) { throw "pyinstaller (agent) failed (exit $LASTEXITCODE)." }

    $exe = Join-Path $agentDir "dist\protocol0-agent.exe"
    if (-not (Test-Path $exe)) {
        throw "Build finished but $exe not found."
    }
    Write-Host "OK -> $exe"

    # Launcher icon: regenerated on every build to stay in sync with the source badge
    # (src/website/favicon.svg). Pillow is a dev dependency (poetry install above).
    Write-Host "Generating launcher icon (protocol0.ico)..."
    & poetry run python (Join-Path $repoRoot "scripts\windows\generate_icon.py")
    if ($LASTEXITCODE -ne 0) { throw "generate_icon.py failed (exit $LASTEXITCODE)." }

    Write-Host "Building protocol0-launcher.exe..."
    & poetry run pyinstaller --clean --noconfirm protocol0-launcher.spec
    if ($LASTEXITCODE -ne 0) { throw "pyinstaller (launcher) failed (exit $LASTEXITCODE)." }

    $launcherExe = Join-Path $agentDir "dist\protocol0-launcher.exe"
    if (-not (Test-Path $launcherExe)) {
        throw "Build finished but $launcherExe not found."
    }
    Write-Host "OK -> $launcherExe"
} finally {
    Pop-Location
}
