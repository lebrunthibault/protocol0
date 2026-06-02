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
