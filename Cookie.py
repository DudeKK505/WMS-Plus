from playwright.sync_api import sync_playwright
import json
import time

def refresh_session():
    with sync_playwright() as p:
        # Odpalamy Chrome (używamy zainstalowanego u Tomka, żeby widział sesje)
        browser = p.chromium.launch(headless=False) # Na początku False, żeby Tomek widział okno
        context = browser.new_context()
        page = context.new_page()

        print("Czekam na przechwycenie requestu do WMS...")
        
        captured_data = {}

        # Magia: podsłuchujemy każdy request wychodzący ze strony
        def handle_request(request):
            # Tu wpisz fragment URL-a, który scrapujesz (np. 'api/shipping')
            if "nazwa_twojego_systemu_wms" in request.url:
                captured_data['headers'] = request.headers
                # Ciastka są w headerach, ale Playwright ma je też osobno
                captured_data['cookies'] = context.cookies()
                print("ZŁAPANO SESJĘ!")

        page.on("request", handle_request)

        # Wchodzimy na stronę główną WMS
        page.goto("https://wms.twoja_firma.pl/login")
        
        # Dajemy Tomkowi 30 sekund na zalogowanie się (jeśli trzeba)
        # Lub czekamy, aż captured_data się zapełni
        timeout = 0
        while not captured_data and timeout < 60:
            time.sleep(1)
            timeout += 1

        if captured_data:
            with open("config.json", "w") as f:
                json.dump(captured_data, f, indent=4)
            print("Plik config.json zaktualizowany!")
        
        browser.close()

if __name__ == "__main__":
    refresh_session()
