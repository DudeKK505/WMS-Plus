import time
import random
def ship_ql_scraper(tour):
    time.sleep(30)
    #return 100
    return {
        "ql_total": random.randint(900, 1000),
        "orders_count": random.randint(200, 400)
    }