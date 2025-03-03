.env:
	powershell -Command "cp .env.dist .env"

bootstrap: .env
	@pyenv local 3.11.3
	@poetry install
	@echo project bootstrapped

.PHONY: boostrap

midi_server:
	@poetry run midi-server
.PHONY: midi_server

http_server:
	@poetry run http-server
.PHONY: http_server

logs:
	powershell -c "Get-Content -Path '${USERPROFILE}\AppData\Roaming\Ableton\Live $(abletonVersion)\Preferences\Log.txt' -Wait -Tail 50"
.PHONY: logs

test:
	@poetry run python p0_backend/scripts/cli.py test
.PHONY: test
