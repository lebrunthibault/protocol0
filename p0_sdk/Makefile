API_URL          ?= http://localhost:8000/openapi.json

.env:
	@powershell -Command "cp .env.dist .env"
	@echo Please edit your .env

bootstrap: .env
	@npm install
	@echo project bootstrapped

sdk:
	@openapi-generator-cli generate -i $(API_URL) -g python -c openapi_config.json -o ../p0_script/protocol0/domain/shared/backend -t openapi_templates --global-property apis --global-property apiTests=false,apiDocs=false
.PHONY: sdk
