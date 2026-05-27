../../.env:
	powershell -Command "cp ../../.env.dist ../../.env"

bootstrap: ../../.env
	@pyenv local 3.11.3
	@poetry install
	@echo project bootstrapped

.PHONY: bootstrap

backend:
	@poetry run backend
.PHONY: backend

reload:
	@powershell -NoProfile -ExecutionPolicy Bypass -File ../../scripts/reload_p0_backend.ps1
.PHONY: reload

test:
	@poetry run python backend/scripts/cli.py test
.PHONY: test
