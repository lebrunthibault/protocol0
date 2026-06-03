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

agent:
	@cd src/agent && poetry run agent
.PHONY: agent

# Run the Vue 3 front (src/frontend) with Vite live-reload. Proxies /api and
# /status to the running agent on :9010. Run `make agent` in another terminal.
frontend:
	@cd src/frontend && npm run dev
.PHONY: frontend

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
