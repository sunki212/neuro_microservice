FROM python:3.9
WORKDIR /app
# Копируем список библиотек и устанавливаем их
COPY requirements.txt .
RUN pip install -r requirements.txt
# Копируем весь наш код внутрь контейнера
COPY . .
# Команда по умолчанию 
CMD ["python", "features.py"]