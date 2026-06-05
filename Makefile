# Thin cross-platform dispatcher. All per-OS logic lives in the stdlib-only
# scripts/*.py (no PowerShell, no pyenv). Override PY on a fresh machine where
# `python` isn't a 3.x, e.g. `make PY=python3 bootstrap`.
PY ?= python

# One-command local setup for a fresh checkout: both poetry envs + deploy the
# remote script into Ableton. After this, `make agent` is all you need.
bootstrap:
	@$(PY) scripts/bootstrap.py
.PHONY: bootstrap

# Redeploy just the remote script into Ableton (after editing it).
install:
	@$(PY) scripts/install_remote_script.py
.PHONY: install

# kill-agent first: a leftover agent (frozen exe from the Startup-folder autostart, or a
# stale source run) coexisting with this one means a single shortcut fires twice
# (cf. docs/debug-double-shortcut.md). Cleaning up before launch guarantees one agent.
agent: kill-agent
	@cd src/agent && poetry run agent
.PHONY: agent

# One command for the whole dev stack: agent + frontend (Vue) + website (landing), all
# detached in the background (no second terminal), then it prints the real URLs and tails the
# combined Ableton+agent logs (i.e. `make logs`). Ctrl-C stops the tail; the services keep
# running -> `make down` stops them. Ports aren't pinned (another project may hold 5173/8000)
# so vite/live-server pick the first free port; the printed URLs reflect the actual ports.
# PIDs go to %APPDATA%\Protocol0\dev-up.json; outputs to logs/{agent,frontend,website}.log.
# Force the website port with `make up PORT=3000`.
up:
	@$(PY) scripts/up.py
.PHONY: up

# Stop the background stack started by `make up` (kills each process tree) and clean up
# any leftover agent as a safety net.
down:
	@$(PY) scripts/down.py
.PHONY: down

# Run the Vue 3 front (src/frontend) with Vite live-reload. Proxies /api and
# /status to the running agent on :9010. Run `make agent` in another terminal.
frontend:
	@cd src/frontend && npm run dev
.PHONY: frontend

# Rebuild the production SPA bundle (src/frontend/dist) that the agent serves on
# :9010. Run this then refresh the browser to see your changes in the real agent
# UI (no reinstall needed in dev — static_files reads dist/ from disk).
frontend-build:
	@cd src/frontend && npm run build
.PHONY: frontend-build

# Tail combine les logs Ableton (remote script, via Log.txt) et ceux de l'agent
# (%APPDATA%\Protocol0\logs\agent.log) dans un seul terminal. Stdlib pur, Windows-only.
logs:
	@$(PY) scripts/logs.py
.PHONY: logs

# Affiche les process agent en cours (exe gele + mode source) et les tue.
# Deux agents en parallele = un raccourci declenche plusieurs fois (cf.
# docs/debug-double-shortcut.md) : a lancer si un lancement source traine.
kill-agent:
	@$(PY) scripts/kill_agent.py
.PHONY: kill-agent

# Build and run the spike Ableton Extensions SDK extension (src/js-extension)
# in Live's Extension Host. Requires Node >= 24.14.1, Live 12.4.x Beta with
# Developer Mode ON, and an open Set. It serves an HTTP API (port 9005) and
# publishes its URL to runtime.json, like the Python script does.
extension:
	@cd src/js-extension && npm start
.PHONY: extension

# Serve src/website with live-reload for editing the landing page.
# Uses npx live-server (Node is already present in the repo); the first run
# downloads it, then it's cached. Override the port with `make website PORT=3000`.
website:
	npx --yes live-server src/website --port=$(or $(PORT),8000)
.PHONY: website

# Build the full Windows installer locally (same script CI runs on a tag):
# front Vue 3 -> agent exe (PyInstaller) -> stage remote script -> ISCC.
# Output: dist-installer/Protocol0-Setup-<version>.exe. Windows-only; needs
# Node, Poetry, and Inno Setup 6 (ISCC.exe). See scripts/windows/build_installer.ps1.
installer:
	@powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/build_installer.ps1
.PHONY: installer
