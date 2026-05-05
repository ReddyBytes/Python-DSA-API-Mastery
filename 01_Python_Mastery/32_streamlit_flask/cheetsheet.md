# 🖥️ Streamlit and Flask — Cheatsheet

## Streamlit Quick Reference

```bash
pip install streamlit
streamlit run app.py             # run on localhost:8501
streamlit run app.py --server.port 8080
```

---

## Streamlit Page Structure

```python
import streamlit as st

# Page config (must be first st call)
st.set_page_config(
    page_title="App Name",
    page_icon="🤖",
    layout="wide",            # or "centered"
    initial_sidebar_state="expanded"
)

# Title hierarchy
st.title("Main Title")
st.header("Section Header")
st.subheader("Subsection")
st.caption("Small caption text")
st.markdown("**Bold** and `code` and [link](url)")

# Layout
col1, col2, col3 = st.columns([2, 1, 1])  # ratio 2:1:1
with col1:
    st.write("Wide column")

tab1, tab2 = st.tabs(["Tab A", "Tab B"])
with tab1:
    st.write("Content A")

with st.expander("Click to expand"):
    st.write("Hidden content")

with st.sidebar:
    st.header("Sidebar")
```

---

## Streamlit Widgets

```python
# Input widgets — all return current value
name        = st.text_input("Label", value="default", placeholder="hint")
text        = st.text_area("Label", height=200)
num         = st.number_input("Label", min_value=0, max_value=100, value=50, step=1)
date        = st.date_input("Pick date")
time_val    = st.time_input("Pick time")

slider      = st.slider("Label", 0.0, 1.0, 0.5)
range_val   = st.slider("Range", 0, 100, (20, 80))  # range slider

clicked     = st.button("Click me", type="primary")  # or "secondary"
checked     = st.checkbox("Enable", value=True)
toggle      = st.toggle("Active")
radio       = st.radio("Choose", ["A", "B", "C"])
select      = st.selectbox("Pick one", options, index=0)
multisel    = st.multiselect("Pick many", options, default=[])
color       = st.color_picker("Color", "#00AAFF")

uploaded    = st.file_uploader("Upload", type=["csv", "xlsx", "json"])
```

---

## Streamlit Display

```python
st.write(anything)                    # auto-detect: text, df, dict, chart
st.dataframe(df, use_container_width=True)   # interactive sortable table
st.table(df)                          # static table
st.json(dict_or_json)
st.code("code here", language="python")
st.metric("Label", "95%", delta="+2%")  # KPI metric with optional delta

# Images and media
st.image("path/or/url", caption="caption", width=400)
st.video("video.mp4")
st.audio("audio.mp3")

# Charts (quick)
st.line_chart(df); st.bar_chart(df); st.area_chart(df); st.scatter_chart(df)

# Matplotlib
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1,2,3])
st.pyplot(fig)

# Plotly
import plotly.express as px
fig = px.scatter(df, x="col1", y="col2")
st.plotly_chart(fig, use_container_width=True)

# Status
st.success("Done!"); st.error("Failed!"); st.warning("Careful!"); st.info("Note:")
bar = st.progress(0)                  # update with bar.progress(50)
with st.spinner("Loading..."):
    do_work()
```

---

## Streamlit Session State and Caching

```python
# Session state
if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Increment"):
    st.session_state.count += 1

st.write(f"Count: {st.session_state.count}")

# Caching
@st.cache_data(ttl=3600)          # cache for 1 hour; invalidate on argument change
def load_data(path: str):
    return pd.read_csv(path)

@st.cache_resource                 # for models, DB connections (not serialized)
def load_model():
    return joblib.load("model.pkl")
```

---

## Flask Quick Reference

```bash
pip install flask
python app.py                      # run with app.run()
flask run --debug --port 5001      # use FLASK_APP=app.py env var
```

---

## Flask App Structure

```python
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"status": "ok"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()          # parse JSON body
    if not data:
        return jsonify({"error": "No JSON body"}), 400
    # process...
    return jsonify({"result": 42})

@app.route("/items/<int:item_id>", methods=["GET", "DELETE"])
def item(item_id):
    if request.method == "GET":
        return jsonify({"id": item_id, "name": "Widget"})
    elif request.method == "DELETE":
        return jsonify({"deleted": item_id})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

---

## Flask Request Object

```python
request.method           # "GET", "POST", etc.
request.json             # parsed JSON body (alias: request.get_json())
request.form             # form POST data
request.args             # URL query params: /search?q=hello → request.args["q"]
request.headers          # request headers
request.files            # uploaded files
request.get_data()       # raw request body
```

---

## Flask Response Patterns

```python
# JSON response
return jsonify({"key": "value"}), 200      # default 200
return jsonify({"error": "msg"}), 400      # 400 Bad Request
return jsonify({"error": "not found"}), 404

# Headers
from flask import make_response
resp = make_response(jsonify(data), 200)
resp.headers["X-Custom-Header"] = "value"
return resp
```

---

## Calling a Flask API

```python
import requests

# POST with JSON
r = requests.post("http://localhost:5000/predict",
                  json={"bedrooms": 3, "sqft": 2000})
r.raise_for_status()
print(r.json())

# GET with query params
r = requests.get("http://localhost:5000/search", params={"q": "laptop"})
```

---

## Golden Rules

1. Always use `@st.cache_resource` for models — without caching, the model reloads on every user interaction
2. Use `st.session_state` for any data that must persist across reruns (chat history, user state)
3. Never use `debug=True` in Flask production — it exposes an interactive debugger
4. Always read secrets from environment variables in Flask — never hardcode
5. Use FastAPI over Flask for new projects — it's faster, has automatic docs, and type safety via Pydantic
