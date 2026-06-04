# Installer assets

## `protocol0.ico`

Windows icon of the launcher (`protocol0-launcher.exe`) and its shortcuts (Start Menu +
desktop). It is the "P" badge from the site, rendered at multiple resolutions
(16/32/48/64/128/256).

**Generated**, not hand-drawn: `python scripts/windows/generate_icon.py` (Pillow required,
already a dev dependency of `src/agent`). The visual source is `src/website/favicon.svg`;
the generator reproduces its badge (rounded dark-gradient square, blue "P" `#4d9fff`).

Committed to the repo because `src/agent/protocol0-launcher.spec` references it directly: a
launcher-only build must not fail for lack of an icon. The full build
(`scripts/windows/build_agent_exe.ps1`) regenerates it anyway before packaging, to stay in
sync with the source badge.

The companion `protocol0.png` (256 px, visual debugging) is gitignored.
