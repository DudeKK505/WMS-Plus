import asyncio
from playwright.async_api import async_playwright

def cpt_worker(task_id, schedule):
    try:
        # Uruchamiamy asynchroniczną pętlę wewnątrz synchronicznego wątku
        result = asyncio.run(run_async_cpt_scrape(schedule))
        
        tasks[task_id] = {
            'status': 'completed', 
            'result': {
                'type': 'cpt', 
                'details': result['details'], 
                'total': result['total']
            }
        }
    except Exception as e:
        logger.error(f"Błąd CPT Worker: {e}", exc_info=True)
        tasks[task_id] = {'status': 'error', 'result': str(e)}

async def run_async_cpt_scrape(schedule):
    async with async_playwright() as p:
        # Uruchamiamy Chrome raz, ale stworzymy osobne zadania dla każdej tury
        browser = await p.chromium.launch(headless=True, channel="chrome")
        
        # Wczytujemy ciastka z config.json raz dla całego kontekstu
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        context = await browser.new_context()
        await context.add_cookies([{'name': k, 'value': v, 'domain': '.zalan.do', 'path': '/'} 
                                 for k, v in config['cookies'].items()])

        # Tworzymy listę zadań (Tasks) do wykonania równolegle
        tasks_list = []
        for item in schedule:
            tasks_list.append(scrape_single_wave(context, item['date'], item['time']))

        # ODPAŁ: Wszystkie tury sprawdzane są w tym samym czasie!
        results_list = await asyncio.gather(*tasks_list)

        total_sum = sum(r['count'] for r in results_list)
        await browser.close()
        
        return {
            'details': results_list,
            'total': total_sum
        }

async def scrape_single_wave(context, date, time):
    page = await context.new_page()
    try:
        # TWOJA LOGIKA KLIKANIA (Przykład)
        await page.goto('https://zalos-lodz-frontend-live.logistics.zalan.do/#ordermanagement-orderoverview-module')
        
        # Tutaj wpisujesz datę i godzinę do filtrów WMS
        # np. await page.fill("#date-input", date)
        # np. await page.fill("#time-input", time)
        # await page.click("text=Suchen")
        
        # Czekasz na wynik i parsowanie
        # res_text = await page.locator(".total-count").inner_text()
        # count = int(res_text)
        count = 120 # Mock
        
        return {"time": time, "count": count}
    finally:
        await page.close()
