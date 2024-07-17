# Используем базовый образ Python с Alpine Linux
FROM python:3.9-alpine

# Установка пакетов системы
RUN apk update && \
    apk add --no-cache \
        tesseract-ocr \
        tesseract-ocr-dev \
        build-base \
        gcc \
        jpeg-dev \
        zlib-dev \
        linux-headers

# Установка зависимостей Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копирование исходного кода приложения
COPY . /app
WORKDIR /app

# Запуск бота
CMD ["python", "discord_bot.py"]