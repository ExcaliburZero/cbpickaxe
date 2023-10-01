test:
	python -m black *.py **/*.py
	python -m mypy *.py **/*.py