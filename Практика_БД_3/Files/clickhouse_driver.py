import mysql.connector
import time
from datetime import datetime
import requests

# Настройки подключения к базе данных MySQL
mysql_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port':'3307',
    'database': 'mydatabase',
}

#ClickHouse
clickhouse_url = 'http://localhost:8123'
clickhouse_table = 'message'

def fetch_data():
    # Подключение к MySQL
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()

    # Выполнение запроса
    cursor.execute("SELECT * FROM messages")  
    data = cursor.fetchall()

    # Закрытие соединения
    cursor.close()
    conn.close()

    return data

def save_to_clickhouse(data):
    for row in data:
        #формируем запрос для вставки данных в ClickHouse
        insert_query = f"INSERT INTO {clickhouse_table} (id, timestamp, message) VALUES ({row[0]}, '{row[1]}', '{row[2]}')"
        try:
            requests.post(clickhouse_url, data=insert_query, timeout=5)
        except Exception as e:
            print(f"Error while sending data to ClickHouse: {e}")

if __name__ == "__main__":
    while True:
        print("Fetching data from MySQL...")
        data = fetch_data()
        print("Data fetched, now saving to ClickHouse...")
        save_to_clickhouse(data)
        time.sleep(100)  