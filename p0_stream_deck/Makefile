#!make

.PHONY: log dev lint icons build test check

log:
	cls && tail -f C:\Users\thiba\AppData\Roaming\Elgato\StreamDeck\logs\StreamDeck0.log

dev:
	cls && yarn watch

lint:
	cls && npm run lint-fix

icon:
	cls
	powershell ./scripts/make_icon.ps1 $(filter-out $@, $(MAKECMDGOALS))
	"Success !"

check:
	cls
	make lint
	make test

build:
	cls && powershell ./scripts/build.ps1

test:
	cls && yarn test