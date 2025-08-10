# Slim образ с системными зависимостями для WeasyPrint
FROM python:3.11-slim

ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libcairo2 \
    pango1.0-tools \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    fonts-dejavu-core \
    wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY numbers_bot/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY numbers_bot /app
CMD ["python", "-m", "bot"]
