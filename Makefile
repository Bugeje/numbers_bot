.PHONY: install lint test run fmt

install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

lint:
	ruff check .
	black --check .
	isort --check-only .

fmt:
	ruff check --fix .
	black .
	isort .

run:
	python -m bot
