import requests
import sqlite3
import time

def scrape_id():
    url = "http://127.0.0.1:5000/api/shipments"
    conn = sqlite3.connect("ship.db")
    cursor = conn.cursor()
    sql = '''INSERT INTO orders (order_id, is_processed, timestamp) VALUES (?, ?, ?)'''
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS "orders" (
        "key" INTEGER PRIMARY KEY,
        "order_id" TEXT,
        "tour" TEXT,
        "ql_count" INTEGER,
        "is_processed" INTEGER,
        "timestamp" INTEGER
    )
    ''')

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        for orders in data["orders"]:
            order_temp = orders["id"]
            teraz = int(time.time())
            cursor.execute(sql, (order_temp, 0, teraz))
            conn.commit()
    conn.close()


