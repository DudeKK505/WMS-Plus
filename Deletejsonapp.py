if __name__ == '__main__':
    logger.info("System wystartował.")
    
    # Start Flaska w tle
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start okna
    webview.create_window('SHIP Tool', 'http://127.0.0.1:5000', width=350, height=500)
    webview.start()

    # --- TUTAJ DZIEJE SIĘ MAGIA SPRZĄTANIA ---
    logger.info("Zamykanie aplikacji, usuwanie sesji...")
    if os.path.exists("config.json"):
        try:
            os.remove("config.json")
            logger.info("Plik config.json został usunięty pomyślnie.")
        except Exception as e:
            logger.error(f"Nie udało się usunąć pliku sesji: {e}")
