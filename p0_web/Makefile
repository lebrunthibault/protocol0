.env:
	powershell -Command "cp .env.dist .env"

bootstrap: .env
	@pyenv local 3.11.3
	@poetry install
	@echo project bootstrapped

.PHONY: boostrap

up:
	@docker compose -f docker-compose-dev.yml up --build
.PHONY: up

logs:
	@docker compose -f docker-compose-dev.yml logs -f
.PHONY: logs

publish:
	@docker compose build
	@docker compose push