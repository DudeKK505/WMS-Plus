from flask import Flask, jsonify, render_template_string
import time
import random

app = Flask(__name__)

# --- SYMULACJA DANYCH ---
MOCK_ORDERS = [{"id": f"ORD-{i:04d}", "ql": random.randint(1, 15)} for i in range(1, 101)]

# --- WIDOK DLA CZŁOWIEKA (HTML) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>WMS PRO Alpha</title>
    <style>
        body { font-family: sans-serif; background: #222; color: #eee; padding: 20px; }
        .truck-box { border: 2px solid #ffa500; padding: 15px; border-radius: 8px; }
        button { background: #ffa500; border: none; padding: 10px; cursor: pointer; font-weight: bold; }
        #order-list { margin-top: 20px; }
        .order-item { background: #333; margin: 5px 0; padding: 10px; border-left: 5px solid #ffa500; }
    </style>
</head>
<body>
    <h1>System Zarządzania Transportem (WMS)</h1>
    <div class="truck-box">
        <h2>Truck: HERMES-V7</h2>
        <button onclick="loadOrders()">POBIERZ LISTĘ ZAMÓWIEŃ (SHIP)</button>
    </div>
    <div id="order-list">
        </div>

    <script>
        function loadOrders() {
            console.log("Inicjuję pobieranie z API...");
            fetch('/api/shipments')
                .then(response => response.json())
                .then(data => {
                    const list = document.getElementById('order-list');
                    list.innerHTML = '<h3>Lista zamówień:</h3>';
                    data.orders.forEach(order => {
                        list.innerHTML += `<div class="order-item">
                            ID: ${order.id} | <button onclick="loadDetails('${order.id}')">Pokaż szczegóły QL</button>
                            <span id="details-${order.id}"></span>
                        </div>`;
                    });
                });
        }

        function loadDetails(id) {
            const span = document.getElementById('details-'+id);
            span.innerText = " Ładowanie...";
            fetch('/api/order/' + id)
                .then(response => response.json())
                .then(data => {
                    span.innerHTML = ` <b>[QL: ${data.ql_count}]</b> - Status: ${data.status}`;
                });
        }
    </script>
</body>
</html>
"""

# --- ENDPOINTY API (DLA TWOJEGO SCRAPERA) ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/shipments')
def get_shipments():
    # Udajemy, że serwer myśli...
    time.sleep(0.5)
    # Zwracamy tylko ID (Moduł 1)
    return jsonify({"truck": "Hermes", "orders": [{"id": o["id"]} for o in MOCK_ORDERS]})

@app.route('/api/order/<order_id>')
def get_order_details(order_id):
    # Udajemy wolny WMS (Moduł 2)
    time.sleep(0.3)
    order = next((o for o in MOCK_ORDERS if o["id"] == order_id), None)
    if order:
        return jsonify({"order_id": order["id"], "ql_count": order["ql"], "status": "Packed"})
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)