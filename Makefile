.PHONY: install lint test run fmt

install:
	python -m venv .venv && . .venv/bin/activate && pip install -r numbers_bot/requirements.txt
	pre-commit install || true

lint:
	ruff check numbers_bot
	black --check numbers_bot
	isort --check-only numbers_bot

fmt:
	ruff check --fix numbers_bot
	black numbers_bot
	isort numbers_bot

test:
	pytest -q

run:
	python -m numbers_bot.bot
