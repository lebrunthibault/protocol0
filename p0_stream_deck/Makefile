help:
	@echo "commands: bootstrap, log, dev, icon, build"

bootstrap:
	@yarn install
.PHONY: bootstrap

log:
	@tail -f C:\Users\thiba\AppData\Roaming\Elgato\StreamDeck\logs\StreamDeck0.log
.PHONY: logs

dev:
	@cls && yarn watch
.PHONY: dev

icon:
	@cls
	@powershell ./scripts/make_icon.ps1 $(filter-out $@, $(MAKECMDGOALS))
	"Success !"
.PHONY: icon

build:
	@cls
	@powershell ./scripts/build.ps1
.PHONY: build
