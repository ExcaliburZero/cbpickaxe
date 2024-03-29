.PHONY: test regression_test build

test:
	python -m black .
	python -m mypy .
	python -m pylint cbpickaxe/*.py cbpickaxe_scripts/*.py

regression_test:
	python -m pytest regression_tests/test_*.py

build:
	python -m build