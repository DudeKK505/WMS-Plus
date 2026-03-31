from flask import Flask, render_template, request, jsonify
import threading
import uuid
import main  # Twój plik z funkcją ship_ql_scraper

app = Flask(__name__)

# Przechowalnia wyników w pamięci RAM
tasks = {}

def background_worker(task_id, tour_id):
    try:
        # Wywołanie Twojej funkcji z main.py
        result = main.ship_ql_scraper(tour_id)
        tasks[task_id] = {'status': 'completed', 'result': result}
    except Exception as e:
        tasks[task_id] = {'status': 'error', 'result': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_scrape', methods=['POST'])
def start_scrape():
    tour_id = request.json.get('tour_id')
    if not tour_id:
        return jsonify({'error': 'Missing Tour ID'}), 400
    
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'processing', 'result': None}
    
    # Odpalamy scraper w tle
    thread = threading.Thread(target=background_worker, args=(task_id, tour_id))
    thread.start()
    
    return jsonify({'task_id': task_id})

@app.route('/check_status/<task_id>')
def check_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task)

if __name__ == '__main__':
    app.run(debug=True, port=5000)