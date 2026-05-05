"""
Streamlit and Flask — Practice Problems
Tests Flask API patterns (no browser needed).
Streamlit code is shown as examples only.
"""

from flask import Flask, request, jsonify
import json
import threading
import time
import requests as req


# ─────────────────────────────────────────────
# PROBLEM 1: Build a Flask REST API
# ─────────────────────────────────────────────
print("PROBLEM 1: Flask REST API")

app = Flask(__name__)

# In-memory data store
items_db = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "category": "electronics"},
    2: {"id": 2, "name": "Mouse",  "price": 29.99,  "category": "accessories"},
    3: {"id": 3, "name": "Keyboard", "price": 79.99, "category": "accessories"},
}
next_id = 4


@app.route("/health")
def health():
    return jsonify({"status": "ok", "items_count": len(items_db)})


@app.route("/items", methods=["GET"])
def list_items():
    category = request.args.get("category")
    if category:
        filtered = [v for v in items_db.values() if v["category"] == category]
    else:
        filtered = list(items_db.values())
    return jsonify({"items": filtered, "count": len(filtered)})


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = items_db.get(item_id)
    if not item:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify(item)


@app.route("/items", methods=["POST"])
def create_item():
    global next_id
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ["name", "price"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    if not isinstance(data["price"], (int, float)) or data["price"] < 0:
        return jsonify({"error": "Price must be a non-negative number"}), 422

    item = {
        "id": next_id,
        "name": data["name"],
        "price": data["price"],
        "category": data.get("category", "uncategorized"),
    }
    items_db[next_id] = item
    next_id += 1
    return jsonify(item), 201


@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    if item_id not in items_db:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    deleted = items_db.pop(item_id)
    return jsonify({"deleted": deleted})


@app.route("/predict", methods=["POST"])
def predict_price():
    """Fake ML model endpoint."""
    data = request.get_json()
    if not data or "features" not in data:
        return jsonify({"error": "Provide 'features' list"}), 400

    features = data["features"]
    if not isinstance(features, list) or len(features) != 3:
        return jsonify({"error": "features must be a list of 3 numbers"}), 422

    # Fake prediction formula
    prediction = sum(features[i] * [1.5, 2.3, 0.8][i] for i in range(3))
    return jsonify({
        "prediction": round(prediction, 2),
        "confidence": 0.87,
        "model": "LinearRegression_v1",
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


# ─────────────────────────────────────────────
# Run server in background thread and test it
# ─────────────────────────────────────────────
def run_server():
    app.run(port=5099, debug=False, use_reloader=False)

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
time.sleep(1)   # wait for server to start

BASE = "http://localhost:5099"

print("\n--- Testing Flask API ---")

# Test GET /health
r = req.get(f"{BASE}/health")
print(f"GET /health: {r.status_code} → {r.json()}")

# Test GET /items
r = req.get(f"{BASE}/items")
print(f"\nGET /items: {r.status_code} → count={r.json()['count']}")

# Test GET /items?category=accessories
r = req.get(f"{BASE}/items", params={"category": "accessories"})
print(f"GET /items?category=accessories: {r.status_code} → count={r.json()['count']}")

# Test GET /items/1
r = req.get(f"{BASE}/items/1")
print(f"\nGET /items/1: {r.status_code} → {r.json()['name']}")

# Test GET /items/999 (not found)
r = req.get(f"{BASE}/items/999")
print(f"GET /items/999: {r.status_code} → {r.json()['error']}")

# Test POST /items (create)
r = req.post(f"{BASE}/items", json={"name": "Monitor", "price": 349.99, "category": "electronics"})
print(f"\nPOST /items: {r.status_code} → id={r.json()['id']}, name={r.json()['name']}")

# Test POST /items (missing field)
r = req.post(f"{BASE}/items", json={"name": "Widget"})
print(f"POST /items (missing price): {r.status_code} → {r.json()['error']}")

# Test DELETE
r = req.delete(f"{BASE}/items/2")
print(f"\nDELETE /items/2: {r.status_code} → deleted={r.json()['deleted']['name']}")

# Test /predict
r = req.post(f"{BASE}/predict", json={"features": [10, 5, 8]})
print(f"\nPOST /predict: {r.status_code} → prediction={r.json()['prediction']}")

print("\n✅ Flask API practice complete!")


# ─────────────────────────────────────────────
# PROBLEM 2: Streamlit code examples (run separately)
# ─────────────────────────────────────────────
STREAMLIT_EXAMPLE = '''
# Save as streamlit_demo.py and run: streamlit run streamlit_demo.py

import streamlit as st
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="ML Demo", layout="wide")
st.title("Price Predictor Demo")

with st.sidebar:
    st.header("Features")
    f1 = st.slider("Feature 1", 0, 20, 10)
    f2 = st.slider("Feature 2", 0, 10, 5)
    f3 = st.slider("Feature 3", 0, 15, 8)
    predict_btn = st.button("Predict", type="primary")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Inputs")
    st.json({"features": [f1, f2, f3]})

with col2:
    if predict_btn:
        with st.spinner("Calling API..."):
            resp = requests.post(
                "http://localhost:5099/predict",
                json={"features": [f1, f2, f3]}
            )
            if resp.status_code == 200:
                result = resp.json()
                st.metric("Prediction", f"{result['prediction']:.2f}")
                st.metric("Confidence", f"{result['confidence']:.0%}")
            else:
                st.error(f"API error: {resp.status_code}")
    else:
        st.info("Click Predict to call the API")
'''

print("\nStreamlit example code (run in separate file):")
print(STREAMLIT_EXAMPLE[:200] + "...")
