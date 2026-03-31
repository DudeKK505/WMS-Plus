import sqlite3
import logging
from concurrent.futures import ThreadPoolExecutor

def update_database_batch(data_list):
    """Zrzuca całą listę wyników do bazy w JEDNEJ transakcji"""
    if not data_list:
        return
        
    try:
        conn = sqlite3.connect("ship.db")
        cursor = conn.cursor()
        
        # Otwieramy bramę dla danych
        cursor.execute("BEGIN TRANSACTION")
        
        # To jest ten moment, gdzie 400-4000 rekordów zapisuje się w mgnieniu oka
        sql = "UPDATE orders SET ql_count = ?, is_processed = 1 WHERE order_id = ?"
        cursor.executemany(sql, data_list)
        
        conn.commit()
        conn.close()
        logging.info(f"FINISH: Jednorazowo zapisano {len(data_list)} rekordów w transakcji.")
    except Exception as e:
        logging.error(f"KRYTYCZNY BŁĄD BAZY: {e}")

def main_scrape_process(order_ids):
    """Główny procesor: sieje wątki, zbiera wyniki do RAM, na koniec strzela do bazy"""
    logging.info(f"START: Rozpoczynam scrapowanie dla {len(order_ids)} zamówień.")

    # 1. Scrapowanie do RAM (wszystko trafia do final_data)
    with ThreadPoolExecutor(max_workers=10) as executor:
        # list() wymusza, by program poczekał na wszystkich pracowników
        final_data = list(executor.map(scraper_ql_worker, order_ids))

    # 2. Filtracja śmieci (wywalamy None, jeśli pracownik uderzył w ścianę/timeout)
    clean_data = [r for r in final_data if r is not None]
    
    # 3. JEDEN WIELKI COMMIT
    update_database_batch(clean_data)
    
    logging.info("PROCES ZAKOŃCZONY: Dane w bazie, połączenia zamknięte.")