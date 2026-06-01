REMOTE_SCRIPTS = C:\ProgramData\Ableton\Live 12 Suite\Resources\MIDI Remote Scripts

bootstrap:
	@pyenv local 3.11
	@poetry install
	@echo project bootstrapped
.PHONY: bootstrap

install_script:
	@powershell -c 'cp -r -fo script_templates/Protocol_0 "$(REMOTE_SCRIPTS)"'
	@powershell -c '$$src = (Resolve-Path .).Path; (Get-Content "$(REMOTE_SCRIPTS)\Protocol_0\__init__.py") -replace "__P0_SOURCE_DIR__", $$src | Set-Content "$(REMOTE_SCRIPTS)\Protocol_0\__init__.py"'
	@echo "Protocol 0 installed"
.PHONY: install_script
