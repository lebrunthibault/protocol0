sdk:
	@java -jar openapi-generator-cli.jar generate -i http://localhost:8000/openapi.json -g python-legacy -c openapi_config.json -o p0_sdk -t openapi_templates
	@cd ..\p0_script && poetry install
.PHONY: sdk
