REMOTE_SCRIPTS = C:\ProgramData\Ableton\Live 12 Suite\Resources\MIDI Remote Scripts

bootstrap:
	@pyenv local 3.11
	@poetry install
	@echo project bootstrapped
.PHONY: boostrap

install_script:
	@powershell -c 'cp -r -fo script_templates/p0 "$(REMOTE_SCRIPTS)"'
	@powershell -c 'cd "$(REMOTE_SCRIPTS)\p0"; poetry install'
	@echo "p0 installed"
.PHONY: install_script

publish:
	@del dist /F /Q
	@bump2version patch --allow-dirty
	@python -m build
	@twine upload dist/*
.PHONY: publish
