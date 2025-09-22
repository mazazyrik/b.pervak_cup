FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update 

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir aiogram fastapi[all] tortoise-orm httpx asyncpg aiokafka

COPY app ./app
RUN mkdir -p /app/media

EXPOSE 8000

CMD uvicorn app.src.main:app --host 0.0.0.0 --port 8000

