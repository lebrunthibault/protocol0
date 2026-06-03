# Construit l'exe autonome de l'agent (PyInstaller).
#
# Sortie : src/agent/dist/protocol0-agent.exe
# Prérequis (machine de build seulement) : Poetry + Python 3.11+.
# Le build embarque src/frontend/dist (la SPA Vue 3) -> elle doit être buildée AVANT (npm run build).

# Note PS 5.1 : poetry/pyinstaller écrivent leurs logs sur stderr. Avec
# $ErrorActionPreference="Stop", PowerShell transforme ce stderr en erreur
# terminante même quand l'exit code est 0. On garde donc "Continue" et on juge
# le succès sur $LASTEXITCODE (le vrai code de sortie natif), pas sur le stderr.
$ErrorActionPreference = "Continue"

# This script lives in scripts/windows/, so the repo root is two levels up.
$repoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
$agentDir = Join-Path $repoRoot "src\agent"

# La SPA doit être buildée avant : PyInstaller l'embarque via datas (cf. protocol0-agent.spec).
$frontendIndex = Join-Path $repoRoot "src\frontend\dist\index.html"
if (-not (Test-Path $frontendIndex)) {
    throw "src/frontend/dist/index.html introuvable. Build la SPA d'abord (cd src/frontend; npm ci; npm run build)."
}

Push-Location $agentDir
try {
    Write-Host "Installing agent deps (incl. pyinstaller)..."
    & poetry install
    if ($LASTEXITCODE -ne 0) { throw "poetry install a échoué (exit $LASTEXITCODE)." }

    Write-Host "Building protocol0-agent.exe..."
    & poetry run pyinstaller --clean --noconfirm protocol0-agent.spec
    if ($LASTEXITCODE -ne 0) { throw "pyinstaller a échoué (exit $LASTEXITCODE)." }

    $exe = Join-Path $agentDir "dist\protocol0-agent.exe"
    if (-not (Test-Path $exe)) {
        throw "Build finished but $exe not found."
    }
    Write-Host "OK -> $exe"
} finally {
    Pop-Location
}
