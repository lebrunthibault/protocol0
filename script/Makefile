REMOTE_SCRIPTS = C:\ProgramData\Ableton\Live 12 Suite\Resources\MIDI Remote Scripts

bootstrap:
	@pyenv local 3.11
	@poetry install
	@echo project bootstrapped
.PHONY: boostrap

install_script:
	@powershell -c 'cp -r -fo script_templates/p0 "$(REMOTE_SCRIPTS)"'
	@powershell -c '$$src = (Resolve-Path .).Path; (Get-Content "$(REMOTE_SCRIPTS)\p0\__init__.py") -replace "__P0_SOURCE_DIR__", $$src | Set-Content "$(REMOTE_SCRIPTS)\p0\__init__.py"'
	@powershell -c 'Get-ChildItem "$(REMOTE_SCRIPTS)\p0\.venv\Lib\site-packages" -Filter "protocol0*" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force'
	@powershell -c 'cd "$(REMOTE_SCRIPTS)\p0"; poetry lock; poetry install'
	@echo "p0 installed"
.PHONY: install_script
