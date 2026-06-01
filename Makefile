backend:
	@cd src/backend && poetry run backend
.PHONY: backend

detector:
	@cd src/detector && poetry run detector
.PHONY: detector

install:
	@cd src/script && make install_script
.PHONY: install

reload:
	@powershell -NoProfile -ExecutionPolicy Bypass -File scripts/reload_p0_backend.ps1
.PHONY: reload

logs:
	@cd src/backend && poetry run logs
.PHONY: logs
