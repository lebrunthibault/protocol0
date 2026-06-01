# Construit l'installeur Windows complet de Protocol0 (Jalon 1).
#
# Enchaîne : build de l'exe détecteur -> staging du remote script -> ISCC (Inno Setup).
# Sortie : dist-installer/Protocol0-Setup-<version>.exe
#
# Prérequis (machine de build seulement) :
#   - Poetry + Python 3.11+   (exe détecteur + rien pour le script, stdlib-only)
#   - Inno Setup 6 (ISCC.exe) sur le PATH, ou à un emplacement standard.

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$iss      = Join-Path $repoRoot "installer\protocol0.iss"

Write-Host "== 1/3 Build detector exe =="
& (Join-Path $PSScriptRoot "build_detector_exe.ps1")

Write-Host "== 2/3 Stage remote script =="
& (Join-Path $PSScriptRoot "stage_remote_script.ps1")

Write-Host "== 3/3 Compile installer (Inno Setup) =="
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
