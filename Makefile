# Protocol0 development commands

PY ?= python

-include .env
export FRONTEND_PORT


# fresh checkout: remote-script poetry env + deploy into Ableton
bootstrap:
	@$(PY) scripts/bootstrap.py
.PHONY: bootstrap

# Redeploy just the remote script into Ableton (after editing it)
install:
	@$(PY) scripts/install_remote_script.py
.PHONY: install

# Build the Rust agent (src/agent) and run the produced Protocol0.exe (kills stale agents first)
agent: kill-agent
	@cd src/agent && cargo build --release && "target/release/Protocol0.exe"
.PHONY: agent

# Run the whole dev stack (agent + frontend + website) detached
up:
	@$(PY) scripts/up.py
.PHONY: up

# Stop the background stack started by `make up`
down:
	@$(PY) scripts/down.py
.PHONY: down

# Run the Vue frontend (src/frontend) with Vite live-reload, proxying to the agent on :9010
frontend:
	@cd src/frontend && npm run dev
.PHONY: frontend

# Tail combined Ableton (remote script) and agent logs in one terminal
logs:
	@$(PY) scripts/logs.py
.PHONY: logs

# Show running agent processes (frozen exe + source mode) and kill them
kill-agent:
	@$(PY) scripts/kill_agent.py
.PHONY: kill-agent

# Build and run the test Ableton Extensions SDK extension (src/js-extension) in Live's Extension Host
extension:
	@cd src/js-extension && npm start
.PHONY: extension

# Serve src/website with live-reload for editing the landing page (PORT overrides the port)
# Absolute path: scripts/up.py reaps stale servers by spotting the repo path in their cmdline
website:
	npx --yes live-server $(CURDIR)/src/website --port=$(or $(PORT),8000)
.PHONY: website

# Build the full Windows installer locally (same script CI runs on a tag) -> dist-installer/Protocol0-Setup-<version>.exe
installer:
	@powershell -NoProfile -ExecutionPolicy Bypass -File installer/windows/build_installer.ps1
.PHONY: installer
