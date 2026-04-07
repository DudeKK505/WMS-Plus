import os
import sys
import webview
import threading
import uuid
import logging
import requests
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect
from playwright.sync_api import sync_playwright 
import main
import ql_scraper

# ... Twoja konfiguracja logów i Flask (bez zmian) ...
if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
    app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'), static_folder=os.path.join(basedir, 'static'))
else:
    app = Flask(__name__)

tasks = {}
user_name = 'Nieznany'

@app.route('/')
def root():
    file_path = 'config.json'
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Test sesji
            response = requests.post('https://zalos-lodz-frontend-live.logistics.zalan.do/frontend/rpc/secure/orderManagementService', 
                                    cookies=config_data['cookies'], headers=config_data['headers'], 
                                    data='''7|0|9|...''', timeout=10)
            
            if response.status_code == 200:
                return render_template('index.html', user_name=config_data.get("user_name", "Nieznajomy"))
        except Exception: pass
    return render_template('login.html')

# --- NOWY ENDPOINT CPT2 ---
@app.route('/start_cpt_scrape', methods=['POST'])
def start_cpt_scrape():
    data = request.json
    schedule = data.get('schedule') # Lista [{'date': '...', 'time': '...'}, ...]
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'processing', 'result': None}
    
    thread = threading.Thread(target=cpt_worker, args=(task_id, schedule))
    thread.daemon = True
    thread.start()
    return jsonify({'task_id': task_id})

def cpt_worker(task_id, schedule):
    try:
        results_details = []
        grand_total = 0
        for item in schedule:
            # Tutaj wywołujesz swoją funkcję Playwrighta
            # count = main.scrape_orders_by_time(item['date'], item['time'])
            count = 100 # Mockup do testów
            results_details.append({"time": item['time'], "count": count})
            grand_total += count
            
        tasks[task_id] = {
            'status': 'completed', 
            'result': {'type': 'cpt', 'details': results_details, 'total': grand_total}
        }
    except Exception as e:
        tasks[task_id] = {'status': 'error', 'result': str(e)}

# ... Reszta Twoich metod (start_scrape dla TourID, check_status) zostaje bez zmian ...

if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(port=5000, threaded=True, use_reloader=False), daemon=True)
    flask_thread.start()
    webview.create_window('SHIP Tool', 'http://127.0.0.1:5000', width=350, height=550, resizable=False)
    webview.start()
