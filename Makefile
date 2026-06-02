# One-command local setup for a fresh checkout: installs both Python
# environments (remote script + detector) and deploys the remote script into
# Ableton. After this, `make detector` is all you need to run.
bootstrap:
	@cd src/script && make bootstrap
	@cd src/detector && poetry install
	@$(MAKE) install
	@echo "Bootstrap complete — run 'make detector' to start."
.PHONY: bootstrap

detector:
	@cd src/detector && poetry run detector
.PHONY: detector

install:
	@cd src/script && make install_script
.PHONY: install
