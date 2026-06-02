# Construit l'exe autonome du détecteur (PyInstaller).
#
# Sortie : src/detector/dist/protocol0-detector.exe
# Prérequis (machine de build seulement) : Poetry + Python 3.11+.

# Note PS 5.1 : poetry/pyinstaller écrivent leurs logs sur stderr. Avec
# $ErrorActionPreference="Stop", PowerShell transforme ce stderr en erreur
# terminante même quand l'exit code est 0. On garde donc "Continue" et on juge
# le succès sur $LASTEXITCODE (le vrai code de sortie natif), pas sur le stderr.
$ErrorActionPreference = "Continue"

# This script lives in scripts/windows/, so the repo root is two levels up.
$repoRoot    = (Resolve-Path "$PSScriptRoot\..\..").Path
$detectorDir = Join-Path $repoRoot "src\detector"

Push-Location $detectorDir
try {
    Write-Host "Installing detector deps (incl. pyinstaller)..."
    & poetry install
    if ($LASTEXITCODE -ne 0) { throw "poetry install a échoué (exit $LASTEXITCODE)." }

    Write-Host "Building protocol0-detector.exe..."
    & poetry run pyinstaller --clean --noconfirm protocol0-detector.spec
    if ($LASTEXITCODE -ne 0) { throw "pyinstaller a échoué (exit $LASTEXITCODE)." }

    $exe = Join-Path $detectorDir "dist\protocol0-detector.exe"
    if (-not (Test-Path $exe)) {
        throw "Build finished but $exe not found."
    }
    Write-Host "OK -> $exe"
} finally {
    Pop-Location
}
