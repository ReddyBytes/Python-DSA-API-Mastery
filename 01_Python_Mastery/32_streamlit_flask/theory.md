# 🖥️ Streamlit and Flask — Building AI Apps

---

You trained a model that predicts house prices. It works beautifully in your Jupyter notebook. Your manager says: "Great, can other people use it?"

You could give them the notebook — but non-technical users don't run notebooks. You could expose it as an API — but then they need to write code to call it. What you need is a **web interface**: a form where someone enters bedrooms, square footage, and zip code, clicks a button, and sees the predicted price.

That's what Streamlit and Flask do.

**Streamlit** turns a Python script into a shareable web app in minutes — no HTML, no CSS, no JavaScript. Perfect for ML demos, dashboards, and internal tools.

**Flask** is a lightweight web framework for building REST APIs and web applications. It gives you full control — ideal for production APIs, microservices, and backend services.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Streamlit widgets (`st.text_input`, `st.button`, `st.selectbox`) · `st.write` / `st.dataframe` · Flask `@app.route` · Flask `request` object · JSON responses · `jsonify`

**Should Learn** — Important for real projects, comes up regularly:
Streamlit `st.session_state` · `st.cache_data` · Streamlit file upload · Flask `request.json` · Flask error handling · Environment variables for secrets

**Good to Know** — Useful in specific situations:
Streamlit `st.columns` / `st.tabs` · Multi-page Streamlit apps · Flask blueprints · Flask-CORS · Streamlit deployment on Hugging Face Spaces

**Reference** — Know it exists, look up when needed:
FastAPI (better Flask alternative for modern APIs) · Gradio (alternative to Streamlit for ML demos) · Streamlit `st.experimental_fragment`

---

## 1️⃣ Streamlit — ML App in Minutes

```python
# app.py — run with: streamlit run app.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ── Page config ─────────────────────────────
st.set_page_config(page_title="House Price Predictor", page_icon="🏠", layout="wide")

# ── Title and description ───────────────────
st.title("🏠 House Price Predictor")
st.markdown("Enter house details to get a price estimate.")

# ── Sidebar inputs ──────────────────────────
with st.sidebar:
    st.header("Input Features")
    bedrooms   = st.slider("Bedrooms", 1, 8, 3)
    bathrooms  = st.slider("Bathrooms", 1, 5, 2)
    sqft       = st.number_input("Square Footage", 500, 10000, 2000, step=100)
    zip_code   = st.selectbox("ZIP Code", ["10001", "90210", "60601"])
    predict_btn = st.button("Predict Price", type="primary")

# ── Main content ────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Your Inputs")
    st.json({"bedrooms": bedrooms, "bathrooms": bathrooms,
             "sqft": sqft, "zip": zip_code})

with col2:
    if predict_btn:
        # Fake prediction for demo
        predicted = 200000 + sqft * 150 + bedrooms * 20000 + bathrooms * 15000
        st.metric("Predicted Price", f"${predicted:,.0f}", delta="+2.3% from last month")
        st.success("Prediction complete!")
    else:
        st.info("Click 'Predict Price' to get an estimate")
```

---

## 2️⃣ Streamlit Key Widgets

```python
import streamlit as st
import pandas as pd

# Text inputs
name    = st.text_input("Your name", placeholder="Enter name...")
text    = st.text_area("Long text", height=150)
number  = st.number_input("Pick a number", min_value=0, max_value=100, value=50)

# Selection
option  = st.selectbox("Choose model", ["Linear Regression", "Random Forest", "XGBoost"])
options = st.multiselect("Choose features", ["age", "income", "score"], default=["age"])
slider  = st.slider("Confidence threshold", 0.0, 1.0, 0.5, step=0.05)

# Buttons and toggles
clicked  = st.button("Run analysis")
checked  = st.checkbox("Include outliers", value=True)
toggled  = st.toggle("Advanced mode")

# Display elements
st.write("Markdown **bold** and `code`")      # auto-renders markdown
st.dataframe(df, use_container_width=True)    # interactive table
st.table(df)                                  # static table
st.json({"key": "value"})                     # formatted JSON
st.code("print('hello')", language="python")  # syntax-highlighted code

# Charts
st.line_chart(df[["col1", "col2"]])           # quick interactive line chart
st.bar_chart(df["col"])
st.area_chart(df)

# Matplotlib/Seaborn figures
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.scatter([1,2,3], [4,5,6])
st.pyplot(fig)                                # render matplotlib in Streamlit

# File upload
uploaded = st.file_uploader("Upload CSV", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
    st.dataframe(df)

# Progress and status
with st.spinner("Processing..."):
    import time; time.sleep(2)
st.success("Done!"); st.error("Error!"); st.warning("Warning!")
progress = st.progress(0)
for i in range(100):
    progress.progress(i + 1)
```

---

## 3️⃣ Streamlit Session State and Caching

```python
import streamlit as st

# Session state — persists across reruns within a session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat-like interface
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = f"Echo: {prompt}"   # replace with LLM call
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Caching — avoid re-running expensive operations on each rerun
@st.cache_data   # cache data-returning functions
def load_dataset(path: str):
    return pd.read_csv(path)   # only runs once; result cached by (path,)

@st.cache_resource   # cache resources like models (not serialized, lives in process)
def load_model():
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return model

df    = load_dataset("large_file.csv")   # cached after first call
model = load_model()                     # cached after first load
```

---

## 4️⃣ Flask — REST API

```python
# api.py — run with: python api.py (or flask run)
from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

# Load model at startup (not per request)
# model = joblib.load("model.pkl")

@app.route("/")
def health():
    return jsonify({"status": "ok", "service": "Price Predictor API"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    # Validate input
    required = ["bedrooms", "sqft"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    # Fake prediction
    bedrooms = data["bedrooms"]
    sqft     = data["sqft"]
    prediction = 200000 + sqft * 150 + bedrooms * 20000

    return jsonify({
        "prediction": round(prediction, 2),
        "currency": "USD",
        "model_version": "v1.2",
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

**Calling the Flask API:**
```python
import requests

response = requests.post(
    "http://localhost:5000/predict",
    json={"bedrooms": 3, "sqft": 2000}
)
print(response.json())   # {"prediction": 800000, "currency": "USD", ...}
```

---

## 5️⃣ Flask with Environment Config

```python
import os
from flask import Flask

app = Flask(__name__)

# Configuration from environment variables (never hardcode secrets)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-key")
API_KEY = os.environ.get("API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///dev.db")

@app.route("/secure-endpoint")
def secure():
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"data": "secret"})
```

---

## Streamlit vs Flask Decision Guide

```
Use Streamlit when:
  ✓ Building ML demos and dashboards quickly
  ✓ Internal tools for non-technical users
  ✓ Prototyping an AI-powered interface
  ✓ Need charts, file uploads, interactive widgets
  ✓ Solo data scientist / small team

Use Flask when:
  ✓ Building a REST API for other services to consume
  ✓ Need fine-grained URL routing and HTTP method control
  ✓ Building production backend services
  ✓ Integrating with frontend frameworks (React, Vue)
  ✓ Need authentication, sessions, middleware

Use FastAPI (instead of Flask) when:
  ✓ Same as Flask but want: automatic OpenAPI docs,
    async support, type validation (Pydantic)
```

---

## Common Mistakes to Avoid ⚠️

- **Not using `st.cache_data`**: loading a large model on every rerun (triggered by any user interaction) will make your app painfully slow.
- **Hardcoding secrets in Flask**: never hardcode API keys or passwords. Use environment variables + `python-dotenv` for local dev.
- **Running Flask in debug mode in production**: `debug=True` exposes the interactive debugger and is a security vulnerability.
- **Forgetting CORS in Flask APIs**: if a JavaScript frontend calls your Flask API from a different domain, you need `flask-cors` or the browser will block the requests.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Prev Module | [../31_file_formats_pdf_xml/theory.md](../31_file_formats_pdf_xml/theory.md) |
| ➡️ Next Module | [../33_regular_expressions/theory.md](../33_regular_expressions/theory.md) |

---

**[🏠 Back to README](../README.md)**
