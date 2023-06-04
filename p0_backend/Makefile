.env:
	powershell -Command "cp .env.dist .env"

bootstrap: .env
	@pyenv local 3.11.3
	@poetry install
	@echo project bootstrapped

.PHONY: boostrap

http_server:
	@poetry run http-server
.PHONY: http_server

midi_server:
	@poetry run watchmedo auto-restart --directory=. --pattern="p0_backend/api/midi_server/*.py;p0_backend/api/midi_server/**/*.py;p0_backend/api/client/*.py;p0_backend/lib/*.py;p0_backend/lib/**/*.py;p0_backend/lib/**/**/*.py" --recursive --ignore-directories -- poetry run midi-server
.PHONY: midi_server

midi_server_api:
	@poetry run uvicorn p0_backend.api.midi_server.http_api:app --port 8001 --reload --workers 4
.PHONY: midi_server_api

celery:
	@poetry run celery -A p0_backend.celery.celery.celery_app worker --events --concurrency=10 --without-heartbeat --without-gossip --without-mingle --loglevel=INFO
.PHONY: celery

logs:
	@poetry run logs
.PHONY: logs

test:
	cls
	@poetry run python scripts/cli.py test
.PHONY: test

