import requests
import sqlite3

def get_number_of_orders():
    conn = sqlite3.connect("ship.db")
    cursor = conn.cursor()
    sql = '''SELECT count(order_id) FROM orders'''
    cursor.execute(sql)
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else 0

def get_order_ids():
    conn = sqlite3.connect("ship.db")
    cursor = conn.cursor()
    sql = '''SELECT order_id FROM orders'''
    cursor.execute(sql)
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def scrape_qls(order_id):
    conn = sqlite3.connect("ship.db")
    cursor = conn.cursor()
    url = f"http://127.0.0.1:5000/api/order/{order_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        ql_count = data['ql_count']
        sql = '''UPDATE orders SET ql_count = ? WHERE order_id = ?'''
        cursor.execute(sql, (ql_count, order_id))
    conn.commit()
    conn.close()