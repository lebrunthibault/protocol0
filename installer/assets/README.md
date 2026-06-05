# Installer assets

## `protocol0.ico`

Windows icon of the agent (`Protocol0.exe`): embedded in the exe (so the Start Menu /
desktop shortcuts show it) and loaded at runtime by the systray (`agent/tray.py`). It is the
"P" badge from the site, rendered at multiple resolutions (16/32/48/64/128/256).

**Generated**, not hand-drawn: `python scripts/windows/generate_icon.py` (Pillow required,
a runtime dependency of `src/agent`). The visual source is `src/website/favicon.svg`;
the generator reproduces its badge (rounded dark-gradient square, blue "P" `#4d9fff`).

Committed to the repo because `src/agent/protocol0-agent.spec` embeds it (via datas): the
build must not fail for lack of an icon. The full build
(`scripts/windows/build_agent_exe.ps1`) regenerates it before packaging, to stay in sync
with the source badge.

The companion `protocol0.png` (256 px, visual debugging) is gitignored.
