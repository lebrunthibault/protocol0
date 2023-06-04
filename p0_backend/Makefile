.env:
	powershell -Command "cp .env.dist .env"

bootstrap: .env
	@pyenv local 3.11.3
	@poetry install
	@echo project bootstrapped

.PHONY: boostrap

http_server:
	@poetry run uvicorn p0_backend.api.http_server.main:app --port 8000 --reload --workers 4
.PHONY: http_server

midi_server:
	@poetry run watchmedo auto-restart --directory=. --pattern="p0_backend/api/midi_server/*.py;p0_backend/api/midi_server/**/*.py;p0_backend/api/client/*.py;p0_backend/lib/*.py;p0_backend/lib/**/*.py;p0_backend/lib/**/**/*.py" --recursive --ignore-directories -- poetry run python .\p0_backend\scripts\start_midi_server.py
.PHONY: midi_server

celery:
	@poetry run celery -A p0_backend.gui.celery.celery_app worker --events --concurrency=10 --without-heartbeat --without-gossip --without-mingle --loglevel=INFO
.PHONY: celery

logs:
	@poetry run python p0_backend/scripts/tail_protocol0_logs.py
.PHONY: logs

kill:
	poetry run python .\p0_backend\scripts\kill_old_processes.py

test:
	cls
	@poetry run python scripts/cli.py test
.PHONY: test

