# Используем базовый образ Python
FROM python:3.12

# Устанавливаем рабочую директорию в /app
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Копируем все файлы из текущего каталога в контейнер
COPY . .

# Команда для запуска приложения (в данном случае можно оставить пустой, так как сенсоры будут генерировать данные автоматически)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
