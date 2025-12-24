import pika
import pickle
import numpy as np
import json
from sklearn.linear_model import LinearRegression

# Создаем простую модель для примера, сохраняем её и обучаем
X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6, 8])
reg = LinearRegression().fit(X, y)

# Подключаемся к RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

# Объявляем очереди
channel.queue_declare(queue='features')
channel.queue_declare(queue='y_pred')

def callback(ch, method, properties, body):
    message = json.loads(body)
    features = message['body']
    msg_id = message['id']
    
    # Предсказание 
    pred = reg.predict(np.array(features[0]).reshape(-1, 1))[0]

    message_y_pred = {
        'id': msg_id,
        'body': float(pred) # Ответ модели
    }
    
    # Отправляем ответ в очередь y_pred
    channel.basic_publish(exchange='',
                          routing_key='y_pred',
                          body=json.dumps(message_y_pred))
    print(f"Предсказание отправлено для ID {msg_id}")

# Начинаем слушать очередь features
channel.basic_consume(queue='features', on_message_callback=callback, auto_ack=True)
print('Ожидание сообщений...')
channel.start_consuming()