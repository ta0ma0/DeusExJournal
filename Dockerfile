# Dockerfile

# Используем официальный образ Python как базовый
# Выбирайте версию Python, соответствующую вашему окружению разработки
FROM python:3.13.2


# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
# Это делается отдельно, чтобы Docker мог кэшировать слои,
# если requirements.txt не меняется
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальное содержимое вашего приложения в рабочую директорию
COPY . .

EXPOSE 5000

ENV FLASK_APP=app
ENV FLASK_DEBUG=0

# Копируем файл конфигурации .env в контейнер
COPY .env .
RUN flask db migrate -m "Initial migration"
RUN flask db upgrade

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]