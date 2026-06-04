# Construit l'installeur Windows complet de Protocol0.
#
# Enchaîne : build de la SPA Vue 3 -> build de l'exe agent (qui embarque la SPA) ->
# staging du remote script -> ISCC (Inno Setup).
# Sortie : dist-installer/Protocol0-Setup-<version>.exe
#
# Prérequis (machine de build seulement) :
#   - Node 20+ (npm)          (build de la SPA src/frontend)
#   - Poetry + Python 3.11+   (exe agent + rien pour le script, stdlib-only)
#   - Inno Setup 6 (ISCC.exe) sur le PATH, ou à un emplacement standard.

$ErrorActionPreference = "Stop"

# This script lives in scripts/windows/, so the repo root is two levels up.
$repoRoot   = (Resolve-Path "$PSScriptRoot\..\..").Path
$iss        = Join-Path $repoRoot "installer\protocol0.iss"
$frontendDir = Join-Path $repoRoot "src\frontend"

Write-Host "== 1/4 Build frontend (Vite) =="
# La SPA doit être buildée avant l'exe : PyInstaller embarque src/frontend/dist via datas.
# npm écrit sur stderr -> juger le succès sur $LASTEXITCODE, pas sur le stderr.
Push-Location $frontendDir
try {
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & npm ci
    if ($LASTEXITCODE -ne 0) { throw "npm ci a échoué (exit $LASTEXITCODE)." }
    & npm run build
    if ($LASTEXITCODE -ne 0) { throw "npm run build a échoué (exit $LASTEXITCODE)." }
    $ErrorActionPreference = $prevEAP
} finally {
    Pop-Location
}

Write-Host "== 2/4 Build agent + launcher exes =="  # also generates the launcher icon
& (Join-Path $PSScriptRoot "build_agent_exe.ps1")

Write-Host "== 3/4 Stage remote script =="
# Portable stdlib-only staging script (replaces the old stage_remote_script.ps1).
# CI provides python on PATH (Setup Python step); judge success on $LASTEXITCODE.
& python (Join-Path $repoRoot "scripts\stage_remote_script.py")
if ($LASTEXITCODE -ne 0) { throw "stage_remote_script.py failed (exit $LASTEXITCODE)." }

Write-Host "== 4/4 Compile installer (Inno Setup) =="
$iscc = (Get-Command "ISCC.exe" -ErrorAction SilentlyContinue).Source
if (-not $iscc) {
    foreach ($p in @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    )) {
        if (Test-Path $p) { $iscc = $p; break }
    }
}
if (-not $iscc) {
    throw "ISCC.exe (Inno Setup) introuvable. Installe Inno Setup 6 ou ajoute ISCC.exe au PATH."
}

# ISCC peut écrire sur stderr : ne pas laisser PS 5.1 le transformer en erreur
# terminante. On juge le succès sur $LASTEXITCODE.
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& $iscc $iss
$isccExit = $LASTEXITCODE
$ErrorActionPreference = $prevEAP
if ($isccExit -ne 0) { throw "ISCC a échoué (exit $isccExit)." }

$outDir = Join-Path $repoRoot "dist-installer"
Write-Host ""
Write-Host "OK -> installeur dans $outDir"
Get-ChildItem $outDir -Filter "Protocol0-Setup-*.exe" -ErrorAction SilentlyContinue |
    Format-Table -AutoSize Name, Length, LastWriteTime
