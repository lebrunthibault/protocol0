../.env:
	powershell -Command "cp ../.env.dist ../.env"

bootstrap: ../.env
	@pyenv local 3.11.3
	@poetry install
	@echo project bootstrapped

.PHONY: boostrap

backend:
	@poetry run backend
.PHONY: backend

logs:
	@poetry run logs
.PHONY: logs

logs-ableton:
	@poetry run logs-ableton
.PHONY: logs-ableton

test:
	@poetry run python p0_backend/scripts/cli.py test
.PHONY: test
