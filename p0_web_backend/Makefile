.env:
	powershell -Command "cp .env.dist .env"

bootstrap: .env
	@pyenv local 3.11.3
	@poetry install
	@echo project bootstrapped

.PHONY: boostrap

build:
	@docker compose build
.PHONY: build

up:
	@docker compose up
.PHONY: up

publish:
	@docker tag docker/welcome-to-docker thibaultlebrun/p0_web_backend