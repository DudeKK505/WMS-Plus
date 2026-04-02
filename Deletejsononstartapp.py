def cleanup_on_start():
    # Usuwamy stare śmieci przed startem nowej sesji
    files_to_clean = ["config.json", "state.json"]
    for f in files_to_clean:
        if os.path.exists(f):
            os.remove(f)

if __name__ == '__main__':
    cleanup_on_start() # <--- Wywołaj to jako pierwszą rzecz
    # ... reszta kodu ...
