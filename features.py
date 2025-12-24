'''Генерация данных'''

import pika
import numpy as np
import json
import time
from datetime import datetime
from sklearn.datasets import load_diabetes

# Загружаем датасет о диабете
X, y = load_diabetes(return_X_y=True)

# Бесконечный цикл для отправки сообщений
while True:
    try:
        # Случайный индекс строки
        random_row = np.random.randint(0, X.shape[0])
        
        # Создаем уникальный идентификатор (timestamp)
        message_id = datetime.timestamp(datetime.now())

        # Формируем сообщение с истинным ответом (для metric)
        message_y_true = {
            'id': message_id,
            'body': y[random_row]
        }

        # Формируем сообщение с признаками (для model)
        message_features = {
            'id': message_id,
            'body': list(X[random_row])
        }

        # Подключение к RabbitMQ
        # rabbitmq — имя сервиса в docker-compose
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Объявляем очереди (и создаем, если их нет)
        channel.queue_declare(queue='y_true')
        channel.queue_declare(queue='features')

        # Публикуем сообщения
        # Истинный ответ отправляем в очередь y_true
        channel.basic_publish(exchange='',
                              routing_key='y_true',
                              body=json.dumps(message_y_true))
        
        # Признаки отправляем в очередь features
        channel.basic_publish(exchange='',
                              routing_key='features',
                              body=json.dumps(message_features))

        print(f"Sent message with ID {message_id}")

        # Закрываем соединение 
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")
        # Если RabbitMQ не поднялся, ждем немного перед повторной попыткой
        time.sleep(5)
        continue

    # Задержка, чтобы было удобно наблюдать за логами 
    time.sleep(2)