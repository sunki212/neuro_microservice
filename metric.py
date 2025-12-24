'''Анализ метрик. Получаем данные, считаем разницу и логируем в CSV'''

import pika
import json
import pandas as pd
import os

# Путь к лог-файлу
log_file = './logs/metric_log.csv'

# Инициализируем CSV с заголовками, если файла нет
if not os.path.exists(log_file):
    with open(log_file, 'w') as f:
        f.write('id,y_true,y_pred,absolute_error\n')

# Буфер для хранения неполных данных {id: {'y_true': ..., 'y_pred': ...}}
buffer = {}

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue='y_true')
channel.queue_declare(queue='y_pred')

def callback(ch, method, properties, body):
    message = json.loads(body)
    msg_id = message['id']
    value = message['body']
    queue_name = method.routing_key

    # Добавляем в буфер
    if msg_id not in buffer:
        buffer[msg_id] = {}
    
    buffer[msg_id][queue_name] = value

    # Проверяем, есть ли оба значения
    if 'y_true' in buffer[msg_id] and 'y_pred' in buffer[msg_id]:
        y_true = buffer[msg_id]['y_true']
        y_pred = buffer[msg_id]['y_pred']
        abs_error = abs(y_true - y_pred)

        # Записываем в CSV
        with open(log_file, 'a') as f:
            f.write(f'{msg_id},{y_true},{y_pred},{abs_error}\n')
        
        print(f"Записана метрика для ID {msg_id}")
        
        # Удаляем из буфера, чтобы не занимать память
        del buffer[msg_id]

# Подписываемся на обе очереди
channel.basic_consume(queue='y_true', on_message_callback=callback, auto_ack=True)
channel.basic_consume(queue='y_pred', on_message_callback=callback, auto_ack=True)

print('Ожидание данных...')
channel.start_consuming()