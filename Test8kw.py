import asyncio
import json
from playwright.async_api import async_playwright
import re
import aiosqlite
import logging

# --- KONFIGURACJA LOGGERA ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("test_playwright")

# Funkcja wykonująca zadanie dla pojedynczej daty/godziny
async def procesuj_pojedynczy_wpis(browser, item, formatted_cookies, headers, domena):
    d = item['date']
    t = item['time']
    
    # Tworzymy nowy kontekst (izolacja sesji/kart)
    context = await browser.new_context(extra_http_headers=headers)
    if formatted_cookies:
        await context.add_cookies(formatted_cookies)
    
    page = await context.new_page()
    liczba = 0 # Domyślna wartość w razie błędu
    domena_pelna = "zalos-lodz-frontend-live.logistics.zalan.do/#ordermanagement-orderoverview-module" 

    try:
        await page.goto(f"https://{domena_pelna}")
        
        # Twoje selektory
        selector_data = 'input[name="isc_TextDateItem_1_dateTextField"]'
        selector_godzina = 'input[name="isc_TextTimeItem_0"]'

        await page.wait_for_selector(selector_data, timeout=10000)
        
        # Wypełnianie pól
        await page.click(selector_data)
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        await page.type(selector_data, d, delay=30)

        await page.click(selector_godzina)
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        await page.type(selector_godzina, t, delay=30)
        await page.keyboard.press("Enter")
        logger.info(f"Dane wpisane do formularza: {d} {t}")

        selector_rodzaj = 'td.formTitle:has-text("Ordertyp:") >> .. >> div.selectItemText'

        try:
            await page.wait_for_selector(selector_rodzaj, timeout=5000)
            await page.click(selector_rodzaj)
            cos = [0, 6, 7, 8, 12]
            for x in cos:
                row = page.locator(f'tr[aria-posinset="{x}"]')
                await row.locator('img[src*="checked.png"]').click()
        except Exception as e:
            logger.warning(f"[{d} {t}] Nie udało się kliknąć w Rodzaj zamówienia: {e}")
            
        await page.keyboard.press("Escape")
        selector_land = 'td.formTitle:has-text("Land:") + td div.selectItemText'
        
        try:
            await page.wait_for_selector(selector_land, timeout=5000)
            await page.click(selector_land)
            row = page.locator('tr[aria-posinset="6"]')
            await row.locator('img[src*="DE.png"]').click()
            await page.keyboard.press("Escape")
        except Exception as e:
            logger.warning(f"[{d} {t}] Nie udało się kliknąć w Land: {e}")
            
        selector_status = 'td.formTitle:text-is("Status:") + td div.selectItemText'
        
        try:
            await page.wait_for_selector(selector_status, timeout=5000)
            await page.click(selector_status)
            status_indeksy = [3, 8]
            for x in status_indeksy:
                row = page.locator(f'tr[aria-posinset="{x}"]')
                await row.locator('img[src*="checked.png"]').click()
            await page.keyboard.press("Escape")
        except Exception as e:
            logger.warning(f"[{d} {t}] Nie udało się kliknąć w Status: {e}")
            
        selector_rodzaj_versand = 'td.formTitle:text-is("Versandart:") + td div.selectItemText'
        
        try:
            await page.wait_for_selector(selector_rodzaj_versand, timeout=5000)
            await page.click(selector_rodzaj_versand)
            row = page.locator('tr[aria-posinset="12"]')
            await row.locator('div').filter(has_text='HMS').click()
            await page.keyboard.press("Escape")
        except Exception as e:
            logger.warning(f"[{d} {t}] Nie udało się kliknąć w Versandart: {e}")
            
    except Exception as e:
        logger.error(f"[{d} {t}] Krytyczny błąd interakcji z UI: {e}")

    # Pobieranie danych
    try:
        # Kliknięcie Suchen i czekanie na odpowiedź
        async with page.expect_response(lambda response: response.url == "https://zalos-lodz-frontend-live.logistics.zalan.do/frontend/rpc/secure/orderManagementService" and response.status == 200, timeout=15000):
            await page.get_by_text("Suchen", exact=True).click()

        # Pobranie wyniku
        raw_text = await page.locator('td.normal:has-text("Records:")').inner_text(timeout=5000)
        match = re.search(r"Records:\s*(\d+)", raw_text)
        if match:
            liczba = int(match.group(1))
            logger.info(f"[{d} {t}] Sukces! Znaleziona liczba: {liczba}")
        else:
            logger.warning(f"[{d} {t}] Regex nie znalazł liczby w tekście: {raw_text}")
            
    except Exception as e:
        logger.error(f"[{d} {t}] Błąd pobierania wyniku (Timeout/Suchen): {e}")
    finally:
        await page.close()
        await context.close()
    
    wynik = {"time": t, "date": d, "count": liczba}
    await zapisz_do_bazy(wynik)
    return wynik

# Główna funkcja sterująca
async def uruchom_tpt_rownolegle(lista_dat):
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error("Brak pliku config.json! Użytkownik prawdopodobnie niezalogowany.")
        return []

    raw_cookies = config.get("cookies", {})
    headers = config.get("headers", {}).copy()
    if "cookie" in headers: del headers["cookie"]

    domena = "zalos-lodz-frontend-live.logistics.zalan.do" 
    
    formatted_cookies = [{
        "name": n, "value": str(v), "domain": domena, "path": "/"
    } for n, v in raw_cookies.items()]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel='chrome') # Headless=True do tła
        
        zadania = [
            procesuj_pojedynczy_wpis(browser, item, formatted_cookies, headers, domena) 
            for item in lista_dat
        ]
        
        wyniki = await asyncio.gather(*zadania)
        await browser.close()
        return wyniki
    
async def zapisz_do_bazy(wynik):
    # Dodany timeout żeby baza mogła 'oddychać' przy równoległych zapisach
    async with aiosqlite.connect("ship.db", timeout=30) as db:
        await db.execute('PRAGMA journal_mode=WAL;') # Tryb WAL
        try:
            await db.execute(
                "INSERT INTO tpt (date, time, count) VALUES (?, ?, ?)",
                (wynik['date'], wynik['time'], wynik['count'])
            )
            await db.commit()
            logger.info(f"Zapisano db: {wynik['date']} {wynik['time']} = {wynik['count']}")
        except Exception as e:
            logger.warning(f"Błąd INSERT (baza zajęta?), próba UPDATE: {e}")
            try:
                # POPRAWKA: Było tps, jest tpt!
                await db.execute(
                    "UPDATE tpt SET count = ? WHERE date = ? AND time = ?;", 
                    (wynik['count'], wynik['date'], wynik['time'])
                )
                await db.commit()
            except Exception as update_err:
                logger.error(f"Krytyczny błąd zapisu DB: {update_err}")
