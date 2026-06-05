# Builds the Protocol0 Windows exe (Rust): the resident agent.
#
# Output:
#   - src/agent/target/release/Protocol0.exe   (resident agent: keyboard hook + web
#                                                server + systray)
#
# The agent is now a native Rust binary (crate src/agent), NOT a PyInstaller bundle:
#   - no bundled CPython -> ~2-3 MB instead of ~14-15 MB, instant start, and the PyInstaller
#     shared-bootloader AV false-positive class disappears;
#   - the Vue SPA (src/frontend/dist) is baked in via rust-embed at compile time;
#   - the "P" icon (installer/windows/assets/protocol0.ico) is a versioned asset in the repo, embedded
#     as a PE resource by build.rs AND loaded by the systray via include_bytes!.
#
# This build produces the Rust exe only, with zero Python shipped. The build itself
# needs NO Python at all: the icon is the committed installer/windows/assets/protocol0.ico, not
# regenerated here (regenerate it manually with installer/windows/generate_icon.py only when the
# source badge src/website/favicon.svg changes).
#
# There is no separate launcher exe: the Start-Menu/desktop shortcut launches
# `Protocol0.exe --open` (start-on-click, AutoHotkey style), which opens the config page and
# then either becomes resident or exits via the single-instance mutex.
#
# Prerequisites (build machine only):
#   - Rust toolchain (rustup, stable-x86_64-pc-windows-msvc) + VS C++ Build Tools (linker).
#   - The SPA must be built first (npm run build): rust-embed bakes src/frontend/dist in.

# PS 5.1 note: cargo writes its progress to stderr. With $ErrorActionPreference="Stop",
# PowerShell turns that stderr into a terminating error even when the exit code is 0. So we
# keep "Continue" and judge success on $LASTEXITCODE (the real native exit code).
$ErrorActionPreference = "Continue"

# This script lives in installer/windows/, so the repo root is two levels up.
$repoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
$crateDir = Join-Path $repoRoot "src\agent"

# The SPA must be built first: rust-embed bakes src/frontend/dist into the binary.
$frontendIndex = Join-Path $repoRoot "src\frontend\dist\index.html"
if (-not (Test-Path $frontendIndex)) {
    throw "src/frontend/dist/index.html not found. Build the SPA first (cd src/frontend; npm ci; npm run build)."
}

# Make sure cargo is on PATH (rustup installs it under ~/.cargo/bin).
$cargoBin = Join-Path $env:USERPROFILE ".cargo\bin"
if (Test-Path $cargoBin) { $env:Path = "$cargoBin;$env:Path" }
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    throw "cargo not found. Install Rust via rustup (https://rustup.rs) and the VS C++ Build Tools."
}

# Icon: a versioned asset in the repo (installer\windows\assets\protocol0.ico), embedded by
# build.rs (PE resource) and tray.rs (include_bytes!). NOT regenerated here - the committed .ico
# is the source of truth for the build, so no Python/Pillow is needed. Regenerate it manually with
# installer\windows\generate_icon.py only when the source badge changes.
$ico = Join-Path $repoRoot "installer\windows\assets\protocol0.ico"
if (-not (Test-Path $ico)) {
    throw "Icon not found at $ico. It is a committed asset; restore it or regenerate it with installer\windows\generate_icon.py."
}

Push-Location $crateDir
try {
    Write-Host "Building Protocol0.exe (cargo build --release)..."
    & cargo build --release
    if ($LASTEXITCODE -ne 0) { throw "cargo build failed (exit $LASTEXITCODE)." }

    $exe = Join-Path $crateDir "target\release\Protocol0.exe"
    if (-not (Test-Path $exe)) {
        throw "Build finished but $exe not found."
    }
    $mb = [math]::Round((Get-Item $exe).Length / 1MB, 2)
    Write-Host "OK -> $exe ($mb MB)"
} finally {
    Pop-Location
}
