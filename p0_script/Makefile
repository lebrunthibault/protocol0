publish:
	cls||clear
	del dist
	bump2version patch --allow-dirty
	python -m build
	twine upload dist/*
.PHONY: publish
