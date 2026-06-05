# Installer assets

## `protocol0.ico`

Windows icon of the agent (`Protocol0.exe`): embedded in the exe (so the Start Menu /
desktop shortcuts show it) and loaded at runtime by the systray (`src/agent/src/tray.rs` via
`include_bytes!`). It is the "P" badge from the site, rendered at multiple resolutions
(16/32/48/64/128/256).

**Generated**, not hand-drawn: `python installer/windows/generate_icon.py` (Pillow required —
a dependency of that generator script only, not of the agent). The visual source is
`src/website/favicon.svg`; the generator reproduces its badge (rounded dark-gradient square,
blue "P" `#4d9fff`).

Committed to the repo because `src/agent/build.rs` embeds it as a PE resource (via `winres`):
the build must not fail for lack of an icon. It is the committed `.ico` that the build uses —
regenerate it manually with the generator above only when the source badge changes.

The companion `protocol0.png` (256 px, visual debugging) is gitignored.
