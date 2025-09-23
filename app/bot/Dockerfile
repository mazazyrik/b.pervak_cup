FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV BOT_TOKEN=7149556054:AAFPIKcoj97DvflYdaCVlFtbNRJb4QKb87I
WORKDIR /app
RUN apt-get update 
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir aiogram httpx aiokafka
COPY app/bot ./app/bot
CMD python app/bot/main.py

