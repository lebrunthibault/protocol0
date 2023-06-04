bootstrap:
	@pyenv local 3.7.3
	@poetry install
	@echo project bootstrapped
.PHONY: boostrap

create_script:
	@pyenv local 3.11.3
	@poetry install
	@echo project bootstrapped
.PHONY: boostrap

publish:
	cls||clear
	@del dist
	@bump2version patch --allow-dirty
	@python -m build
	twine upload dist/*
.PHONY: publish
