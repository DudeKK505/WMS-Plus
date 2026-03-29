import scraper_id
import scraper_ql
from concurrent.futures import ThreadPoolExecutor

print("Pobieranie zamówień, prosze czekać")
scraper_id.scrape_id()

print("Procesor sie poci by pobrac QL, czekaj")
orders = scraper_ql.get_order_ids()

with ThreadPoolExecutor(max_workers=20) as executor:
    executor.map(scraper_ql.scrape_qls, orders)

print("Pobrane :D")
