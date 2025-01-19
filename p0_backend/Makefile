.env:
	powershell -Command "cp .env.dist .env"

bootstrap: .env
	@pyenv local 3.11.3
	@poetry install
	@echo project bootstrapped

.PHONY: boostrap

midi_server:
	@poetry run watchmedo auto-restart --directory=. --pattern="p0_backend/api/midi_server/*.py;p0_backend/api/midi_server/**/*.py;p0_backend/api/client/*.py;p0_backend/lib/*.py;p0_backend/lib/**/*.py;p0_backend/lib/**/**/*.py" --recursive --ignore-directories -- poetry run midi-server
.PHONY: midi_server

http_server:
	@poetry run http-server
.PHONY: http_server

logs:
	powershell -c "Get-Content -Path 'C:\Users\thiba\AppData\Roaming\Ableton\Live 12.1.5\Preferences\Log.txt' -Wait -Tail 50"
.PHONY: logs

test:
	@poetry run python p0_backend/scripts/cli.py test
.PHONY: test
