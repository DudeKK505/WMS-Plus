import logging
from datetime import datetime

# Główna konfiguracja - wykonaj ją TYLKO RAZ w głównym pliku
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"log_{timestamp}.txt"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s', # Dodaliśmy %(name)s
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Stwórz główny logger
logger = logging.getLogger("WMS_App")
logger.info("System wystartował.")
