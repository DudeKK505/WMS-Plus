import sqlite3
import logging
from concurrent.futures import ThreadPoolExecutor

def update_database_batch(data_list):
    """Zapisuje całą listę wyników w jednej transakcji"""
    if not data_list:
        return
        
    try:
        conn = sqlite3.connect("ship.db")
        cursor = conn.cursor()
        
        # Klucz do szybkości: WYŁĄCZAMY auto-commit i robimy to ręcznie
        cursor.execute("BEGIN TRANSACTION")
        
        # Używamy executemany - to jest rakieta w SQLite
        sql = "UPDATE orders SET ql_count = ?, is_processed = 1 WHERE order_id = ?"
        cursor.executemany(sql, data_list)
        
        conn.commit()
        conn.close()
        logging.info(f"Pomyślnie zapisano batch {len(data_list)} rekordów do bazy.")
    except Exception as e:
        logging.error(f"Błąd zapisu batcha do bazy: {e}")

def main_scrape_process(order_ids):
    all_results = []
    batch_size = 100 # Co tyle rekordów robimy zapis
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # executor.map zwraca wyniki w takiej kolejności, w jakiej były ID na liście
        # To idealnie pasuje do zbierania danych
        for result in executor.map(scraper_ql_worker, order_ids):
            if result: # result to np. (15, "ORD-123")
                all_results.append(result)
            
            # Jeśli uzbieraliśmy batch_size, zapisujemy i czyścimy listę
            if len(all_results) >= batch_size:
                update_database_batch(all_results)
                all_results = [] # Czyścimy worek na następną paczkę
                
    # Na koniec zapisujemy to, co zostało (np. ostatnie 40 sztuk)
    if all_results:
        update_database_batch(all_results)