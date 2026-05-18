backend:
	@cd backend && poetry run backend
.PHONY: backend

reload:
	@powershell -NoProfile -ExecutionPolicy Bypass -File scripts/reload_p0_backend.ps1
.PHONY: reload

logs:
	@cd backend && poetry run logs
.PHONY: logs
