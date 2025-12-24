'''Файл-скрипт. Считывает изменения в CSV и обновляет график'''

import pandas as pd
import matplotlib.pyplot as plt
import time
import os

while True:
    try:
        if os.path.exists('./logs/metric_log.csv'):
            df = pd.read_csv('./logs/metric_log.csv')
            if not df.empty:
                plt.figure(figsize=(10, 6))
                plt.hist(df['absolute_error'], bins=20, color='skyblue', edgecolor='black')
                plt.title('Распределение абсолютных ошибок')
                plt.xlabel('Ошибка')
                plt.ylabel('Количество')
                plt.savefig('./logs/error_distribution.png')
                plt.close()
                print("График обновлен")
    except Exception as e:
        print(f"Ошибка построения графика: {e}")
    
    time.sleep(5) # Обновляем раз в 5 секунд