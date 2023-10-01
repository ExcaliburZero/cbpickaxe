.PHONY: test build

test:
	python -m black **/*.py
	python -m mypy **/*.py

build:
	python -m build --wheel