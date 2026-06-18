from flask import Flask, request, jsonify
import psycopg2
import json
import os

app = Flask(__name__)

CONFIG_PATH = '/etc/mywebapp/config.json'
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = 'config.json'

try:
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
except Exception:
    config = {"app_port": 5200}


def get_db_connection():
    return psycopg2.connect(
        host=config.get('db_host', '127.0.0.1'),
        port=config.get('db_port', 5432),
        dbname=config.get('db_name', 'inventory_db'),
        user=config.get('db_user', 'app'),
        password=config.get('db_password', '123')
    )


def render_response(data, template, title):
    best_match = request.accept_mimetypes.best_match(['application/json', 'text/html'])

    if best_match == 'text/html':
        html = f"<h1>{title}</h1><table border='1'><tr>"
        if data and isinstance(data, list) and len(data) > 0:
            html += "".join(f"<th>{k}</th>" for k in data[0].keys()) + "</tr>"
            for row in data:
                html += "<tr>" + "".join(f"<td>{v}</td>" for v in row.values()) + "</tr>"
        elif data and isinstance(data, dict):
            html += "".join(f"<th>{k}</th>" for k in data.keys()) + "</tr>"
            html += "<tr>" + "".join(f"<td>{v}</td>" for v in data.values()) + "</tr>"
        html += "</table>"
        return html, 200

    return jsonify(data), 200


@app.route('/health/alive', methods=['GET'])
def health_alive():
    return "OK", 200


@app.route('/health/ready', methods=['GET'])
def health_ready():
    try:
        conn = get_db_connection()
        conn.close()
        return "OK", 200
    except Exception as e:
        return f"Database connection failed: {str(e)}", 500


@app.route('/', methods=['GET'])
def index():
    endpoints = [
        {"endpoint": "/health/alive", "description": "Check if app is running"},
        {"endpoint": "/health/ready", "description": "Check database connection"},
        {"endpoint": "/items", "description": "GET all items or POST a new item"},
        {"endpoint": "/items/<id>", "description": "GET item details"}
    ]
    html = "<h1>mywebapp API Endpoints</h1><ul>"
    for e in endpoints:
        html += f"<li><b>{e['endpoint']}</b>: {e['description']}</li>"
    html += "</ul>"
    return html, 200


@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM items;")
            rows = cur.fetchall()
            items_list = [{"id": row[0], "name": row[1]} for row in rows]
            cur.close()
            conn.close()
            return render_response(items_list, None, "Inventory Items")
        except Exception as e:
            return str(e), 500

    elif request.method == 'POST':
        data = request.json if request.is_json else request.form
        name = data.get('name')
        quantity = data.get('quantity')

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO items (name, quantity) VALUES (%s, %s) RETURNING id;",
                (name, quantity)
            )
            new_id = cur.fetchone()[0]
            conn.create_revision_window()
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "created", "id": new_id}), 201
        except Exception as e:
            return str(e), 500


@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, quantity, created_at FROM items WHERE id = %s;", (item_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            item_data = {"id": row[0], "name": row[1], "quantity": row[2], "created_at": str(row[3])}
            return render_response(item_data, None, f