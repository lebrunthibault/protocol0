# Builds the Protocol0 Windows exe (Rust): the resident agent.
#
# Output:
#   - src/agent-rust/target/release/Protocol0.exe   (resident agent: keyboard hook + web
#                                                     server + systray)
#
# The agent is now a native Rust binary (crate src/agent-rust), NOT a PyInstaller bundle:
#   - no bundled CPython -> ~2 MB instead of ~14-15 MB, instant start, and the PyInstaller
#     shared-bootloader AV false-positive class disappears;
#   - the Vue SPA (src/frontend/dist) is baked in via rust-embed at compile time;
#   - the "P" icon (installer/assets/protocol0.ico) is embedded as a PE resource by build.rs
#     AND loaded by the systray via include_bytes! -> generate it FIRST (below).
#
# The Python agent (src/agent) is kept for dev/reference but is NO LONGER packaged by the
# installer: this build produces the Rust exe only, with zero Python shipped.
#
# There is no separate launcher exe: the Start-Menu/desktop shortcut launches
# `Protocol0.exe --open` (start-on-click, AutoHotkey style), which opens the config page and
# then either becomes resident or exits via the single-instance mutex.
#
# Prerequisites (build machine only):
#   - Rust toolchain (rustup, stable-x86_64-pc-windows-msvc) + VS C++ Build Tools (linker).
#   - Python 3 on PATH ONLY to regenerate the icon (generate_icon.py). The exe itself needs
#     no Python.
#   - The SPA must be built first (npm run build): rust-embed bakes src/frontend/dist in.

# PS 5.1 note: cargo writes its progress to stderr. With $ErrorActionPreference="Stop",
# PowerShell turns that stderr into a terminating error even when the exit code is 0. So we
# keep "Continue" and judge success on $LASTEXITCODE (the real native exit code).
$ErrorActionPreference = "Continue"

# This script lives in scripts/windows/, so the repo root is two levels up.
$repoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
$crateDir = Join-Path $repoRoot "src\agent-rust"

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

# Icon: regenerated on every build to stay in sync with the source badge
# (src/website/favicon.svg). Must come BEFORE the cargo build, which embeds it (build.rs as a
# PE resource, tray.rs via include_bytes!). Regeneration needs Pillow; if it's missing on a
# bare build machine we fall back to the committed installer\assets\protocol0.ico (best-effort,
# so a Python-less Rust build still works). We only HARD-fail if the icon is absent entirely.
$ico = Join-Path $repoRoot "installer\assets\protocol0.ico"
Write-Host "Generating icon (protocol0.ico)..."
& python (Join-Path $repoRoot "scripts\windows\generate_icon.py")
if ($LASTEXITCODE -ne 0) {
    if (Test-Path $ico) {
        Write-Warning "generate_icon.py failed (exit $LASTEXITCODE); using the committed installer\assets\protocol0.ico."
    } else {
        throw "generate_icon.py failed (exit $LASTEXITCODE) and no committed icon at $ico."
    }
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
