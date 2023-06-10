REMOTE_SCRIPTS = "C:\ProgramData\Ableton\Live 11 Suite\Resources\MIDI Remote Scripts"

bootstrap:
	@pyenv local 3.7.3
	@poetry install
	@echo project bootstrapped
.PHONY: boostrap

install_scripts: \
	install_script_p0 \
	install_script_p0_midi
	@echo "remote scripts installed to $(REMOTE_SCRIPTS)"
.PHONY: install_scripts

install_script_p0:
	@powershell -c 'cp -r -fo script_templates/p0 $(REMOTE_SCRIPTS)'
	@cd $(REMOTE_SCRIPTS)/p0 && poetry install
	@echo "p0 installed"
.PHONY: install_script_p0

install_script_p0_midi:
	@powershell -c 'cp -r -fo script_templates/p0_midi $(REMOTE_SCRIPTS)'
	@cd $(REMOTE_SCRIPTS)/p0_midi && poetry install
	@echo "p0_midi installed"
.PHONY: install_script_p0_midi

logs:
	@cd ../p0_backend && poetry run logs
.PHONY: logs

publish:
	@del dist /F /Q
	@bump2version patch --allow-dirty
	@python -m build
	@twine upload dist/*
.PHONY: publish
