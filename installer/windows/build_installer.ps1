# Builds the full Protocol0 Windows installer.
#
# Chains: build the Vue 3 SPA -> build the agent exe (which embeds the SPA) ->
# stage the remote script -> ISCC (Inno Setup).
# Output: dist-installer/Protocol0-Setup-<version>.exe
#
# Prerequisites (build machine only):
#   - Node 20+ (npm)              (build the SPA src/frontend)
#   - Rust (rustup, MSVC) + VS C++ Build Tools  (native agent exe, src/agent)
#   - Python 3                    (agent icon + remote-script staging, stdlib-only)
#   - Inno Setup 6 (ISCC.exe) on PATH, or at a standard location.

$ErrorActionPreference = "Stop"

# This script lives in installer/windows/, so the repo root is two levels up.
$repoRoot   = (Resolve-Path "$PSScriptRoot\..\..").Path
$iss        = Join-Path $repoRoot "installer\windows\protocol0.iss"
$frontendDir = Join-Path $repoRoot "src\frontend"

Write-Host "== 1/4 Build frontend (Vite) =="
# The SPA must be built before the exe: the Rust agent embeds src/frontend/dist via rust-embed.
# npm writes to stderr -> judge success on $LASTEXITCODE, not on stderr.
Push-Location $frontendDir
try {
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & npm ci
    if ($LASTEXITCODE -ne 0) { throw "npm ci failed (exit $LASTEXITCODE)." }
    & npm run build
    if ($LASTEXITCODE -ne 0) { throw "npm run build failed (exit $LASTEXITCODE)." }
    $ErrorActionPreference = $prevEAP
} finally {
    Pop-Location
}

Write-Host "== 2/4 Build agent exe =="  # also generates the icon (embedded for the systray)
& (Join-Path $PSScriptRoot "build_agent_exe.ps1")

Write-Host "== 3/4 Stage remote script =="
# Portable stdlib-only staging script. CI provides python on PATH (Setup Python step);
# judge success on $LASTEXITCODE.
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
    throw "ISCC.exe (Inno Setup) not found. Install Inno Setup 6 or add ISCC.exe to PATH."
}

# ISCC may write to stderr: do not let PS 5.1 turn it into a terminating error.
# Judge success on $LASTEXITCODE.
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& $iscc $iss
$isccExit = $LASTEXITCODE
$ErrorActionPreference = $prevEAP
if ($isccExit -ne 0) { throw "ISCC failed (exit $isccExit)." }

$outDir = Join-Path $repoRoot "dist-installer"
Write-Host ""
Write-Host "OK -> installer in $outDir"
$exe = Get-ChildItem $outDir -Filter "Protocol0-Setup-*.exe" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$exe | Format-Table -AutoSize Name, Length, LastWriteTime
if ($exe) {
    Write-Host ""
    Write-Host "Run the installer with:"
    Write-Host "  dist-installer/$($exe.Name)"
}
