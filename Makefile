# Thin cross-platform dispatcher. All per-OS logic lives in the stdlib-only
# scripts/*.py (no PowerShell, no pyenv). Override PY on a fresh machine where
# `python` isn't a 3.x, e.g. `make PY=python3 bootstrap`.
PY ?= python

# One-command local setup for a fresh checkout: both poetry envs + deploy the
# remote script into Ableton. After this, `make detector` is all you need.
bootstrap:
	@$(PY) scripts/bootstrap.py
.PHONY: bootstrap

# Redeploy just the remote script into Ableton (after editing it).
install:
	@$(PY) scripts/install_remote_script.py
.PHONY: install

detector:
	@cd src/detector && poetry run detector
.PHONY: detector

# Affiche les process detector en cours (exe gele + mode source) et les tue.
# Deux detectors en parallele = un raccourci declenche plusieurs fois (cf.
# docs/debug-double-shortcut.md) : a lancer si un lancement source traine.
kill-detector:
	@$(PY) scripts/kill_detector.py
.PHONY: kill-detector

# Serve src/website with live-reload for editing the landing page.
# Uses npx live-server (Node is already present in the repo); the first run
# downloads it, then it's cached. Override the port with `make website PORT=3000`.
website:
	npx --yes live-server src/website --port=$(or $(PORT),8000)
.PHONY: website
