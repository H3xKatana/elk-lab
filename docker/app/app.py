#!/usr/bin/env python3

from flask import Flask, request, jsonify
import json
import time
import uuid
import random
from datetime import datetime

app = Flask(__name__)

LOG_FILE = "/var/log/app/requests.log"

USERS = ["user-001", "user-002", "user-003", "user-004", "user-005", "guest"]
ENDPOINTS = ["/api/health", "/api/products", "/api/cart", "/api/checkout", "/api/login", "/api/logout"]
METHODS = ["GET", "POST", "GET", "GET", "POST", "POST"]
PRODUCTS = ["prod-101", "prod-202", "prod-303", "prod-404"]

def log_request(request_id, method, endpoint, status_code, latency_ms, user_id=None):
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": "INFO",
        "request_id": request_id,
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "latency_ms": latency_ms,
        "user_id": user_id or random.choice(USERS),
        "service": "checkout-api",
        "message": f"{method} {endpoint} - {status_code} ({latency_ms}ms)"
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")
        f.flush()

@app.before_request
def before():
    request.start_time = time.time()

@app.after_request
def after(response):
    latency = int((time.time() - request.start_time) * 1000)
    request_id = f"req-{uuid.uuid4().hex[:12].upper()}"
    log_request(
        request_id,
        request.method,
        request.path,
        response.status_code,
        latency,
        request.headers.get("X-User-ID")
    )
    response.headers["X-Request-ID"] = request_id
    return response

@app.route("/api/health")
def health():
    return jsonify({"status": "healthy", "service": "checkout-api"})

@app.route("/api/products")
def products():
    return jsonify({
        "products": [
            {"id": "prod-101", "name": "Widget Pro", "price": 29.99},
            {"id": "prod-202", "name": "Gadget Plus", "price": 49.99},
            {"id": "prod-303", "name": "Tool Max", "price": 79.99}
        ]
    })

@app.route("/api/cart")
def cart():
    return jsonify({
        "items": [
            {"product_id": random.choice(PRODUCTS), "quantity": random.randint(1, 5)}
        ],
        "total": round(random.uniform(20, 200), 2)
    })

@app.route("/api/checkout", methods=["POST"])
def checkout():
    data = request.get_json() or {}
    return jsonify({
        "order_id": f"ord-{uuid.uuid4().hex[:8].upper()}",
        "status": "completed",
        "item": data.get("item", "unknown"),
        "total": round(random.uniform(20, 200), 2)
    })

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    user = data.get("username", "anonymous")
    return jsonify({
        "token": f"tok-{uuid.uuid4().hex[:16]}",
        "user_id": f"user-{user.lower()[:8]}",
        "expires_in": 3600
    })

@app.route("/api/logout", methods=["POST"])
def logout():
    return jsonify({"status": "logged_out"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
