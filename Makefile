.PHONY: install lint run fmt clean dev-setup docker-build docker-run help

# Default target
help:
	@echo "Доступные команды:"
	@echo "  install      - Установка зависимостей"
	@echo "  run          - Запуск бота"
	@echo "  lint         - Проверка кода"
	@echo "  fmt          - Форматирование кода"
	@echo "  clean        - Очистка временных файлов"
	@echo "  docker-build - Сборка Docker образа"
	@echo "  docker-run   - Запуск в Docker"

install:
	python3 -m venv .venv && . .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

dev-setup: install
	@echo "Среда разработки настроена!"
	@echo "Активируйте: source .venv/bin/activate"

lint:
	ruff check .
	black --check .
	isort --check-only .

fmt:
	ruff check --fix .
	black .
	isort .

run:
	. .venv/bin/activate && python3 bot.py

run-dev:
	. .venv/bin/activate && ENVIRONMENT=development python3 bot.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "Очистка завершена"

docker-build:
	docker build -t numbers_bot .

docker-run:
	docker run -d --name numbers_bot --env-file .env numbers_bot
