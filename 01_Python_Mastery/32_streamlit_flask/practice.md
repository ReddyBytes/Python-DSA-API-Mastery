# Streamlit & Flask — Practice

## Quick Index

| # | Topic | Difficulty |
|---|-------|-----------|
| [Q1](#q1) | Streamlit basics — `st.write` and `st.markdown` | 🟢 Basic |
| [Q2](#q2) | Streamlit basics — `st.dataframe` and `st.table` | 🟢 Basic |
| [Q3](#q3) | Streamlit basics — `st.pyplot` matplotlib figure | 🟢 Basic |
| [Q4](#q4) | Streamlit basics — run command and page config | 🟢 Basic |
| [Q5](#q5) | Widgets — `st.slider` and `st.number_input` | 🟢 Basic |
| [Q6](#q6) | Widgets — `st.selectbox` and `st.multiselect` | 🟢 Basic |
| [Q7](#q7) | Widgets — `st.file_uploader` CSV parsing | 🟡 Intermediate |
| [Q8](#q8) | Widgets — `st.button` conditional display | 🟡 Intermediate |
| [Q9](#q9) | Session state — counter across reruns | 🟡 Intermediate |
| [Q10](#q10) | Session state — chat history list | 🟡 Intermediate |
| [Q11](#q11) | Caching — `@st.cache_data` for data loading | 🟡 Intermediate |
| [Q12](#q12) | Caching — `@st.cache_resource` for model loading | 🟡 Intermediate |
| [Q13](#q13) | Flask REST API — app factory and health route | 🟢 Basic |
| [Q14](#q14) | Flask REST API — GET route with path variable | 🟢 Basic |
| [Q15](#q15) | Flask REST API — POST route with `request.json` | 🟡 Intermediate |
| [Q16](#q16) | Flask REST API — `jsonify` and status codes | 🟡 Intermediate |
| [Q17](#q17) | Flask REST API — error handlers | 🟡 Intermediate |
| [Q18](#q18) | Flask config — `os.environ` secrets | 🟡 Intermediate |
| [Q19](#q19) | Flask config — `.env` with `python-dotenv` | 🟡 Intermediate |
| [Q20](#q20) | Flask config — blueprints | 🟠 Advanced |
| [Q21](#q21) | Flask config — app context and `g` | 🟠 Advanced |
| [Q22](#q22) | Decision guide — Streamlit vs Flask | 🟢 Basic |
| [Q23](#q23) | Common mistakes — re-run model on every interaction | 🟡 Intermediate |
| [Q24](#q24) | Common mistakes — Flask thread safety | 🟠 Advanced |
| [Q25](#q25) | Decision guide — blueprint structure for large apps | 🟠 Advanced |

---

<a id="q1"></a>

### Q1 · Streamlit basics — `st.write` and `st.markdown` 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Write a minimal Streamlit page that shows a title, a markdown sentence with bold text, and a Python dict displayed with `st.write`. No widgets needed.


<details><summary>💡 Hint</summary>`st.title`, `st.markdown`, and `st.write` all accept strings; `st.write` auto-renders dicts as formatted JSON.</details>

<details><summary>✅ Answer</summary>

```python
import streamlit as st

st.title("My First Streamlit App")
st.markdown("This app demonstrates **Streamlit basics** with `st.write`.")
st.write({"model": "LinearRegression", "version": "v1.0", "accuracy": 0.93})
```

**Why:** `st.write` is the Swiss-army knife — it detects the type and renders appropriately (dict as JSON, DataFrame as table, string as markdown).
</details>

---

<a id="q2"></a>

### Q2 · Streamlit basics — `st.dataframe` and `st.table` 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Create a small DataFrame with three columns (`name`, `score`, `grade`) and display it both as an interactive table and a static table. Explain the difference.


<details><summary>💡 Hint</summary>`st.dataframe` is interactive (sortable, scrollable); `st.table` is static HTML — use `use_container_width=True` on `st.dataframe`.</details>

<details><summary>✅ Answer</summary>

```python
import streamlit as st
import pandas as pd

df = pd.DataFrame({
    "name":  ["Alice", "Bob", "Carol"],
    "score": [92, 87, 95],
    "grade": ["A", "B", "A"],
})

st.subheader("Interactive table (sortable)")
st.dataframe(df, use_container_width=True)   # ← user can sort columns

st.subheader("Static table")
st.table(df)                                  # ← no sorting, pure HTML
```

**Why:** Use `st.dataframe` for exploration; use `st.table` when you want a clean static display (e.g., a summary at the bottom of a report).
</details>

---

<a id="q3"></a>

### Q3 · Streamlit basics — `st.pyplot` matplotlib figure 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Generate a simple scatter plot with matplotlib (x = [1,2,3,4,5], y = squares) and render it inside a Streamlit app using `st.pyplot`.


<details><summary>💡 Hint</summary>Create the figure with `fig, ax = plt.subplots()`, draw on `ax`, then pass `fig` to `st.pyplot(fig)`.</details>

<details><summary>✅ Answer</summary>

```python
import streamlit as st
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [v**2 for v in x]

fig, ax = plt.subplots()
ax.scatter(x, y, color="steelblue", s=80)   # ← draw on ax
ax.set_title("Squares")
ax.set_xlabel("x"); ax.set_ylabel("x²")

st.pyplot(fig)                               # ← render matplotlib figure
```

**Why:** Streamlit can't display raw matplotlib figures — you must create a `Figure` object and pass it to `st.pyplot(fig)`.
</details>

---

<a id="q4"></a>

### Q4 · Streamlit basics — run command and page config 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Write the correct terminal command to run a Streamlit file called `app.py` on port 8080. Also write the `st.set_page_config` call that sets the title to "ML Dashboard", icon to "🤖", and layout to wide.


<details><summary>💡 Hint</summary>`st.set_page_config` must be the very first Streamlit call in the script — before any other `st.*` call.</details>

<details><summary>✅ Answer</summary>

```python
# Terminal command:
# streamlit run app.py --server.port 8080

import streamlit as st

# Must be FIRST st call — before any other st.* function
st.set_page_config(
    page_title="ML Dashboard",   # ← browser tab title
    page_icon="🤖",
    layout="wide",               # ← uses full browser width
)

st.title("ML Dashboard")
```

**Why:** `st.set_page_config` must come first because Streamlit sends page headers to the browser before rendering any content.
</details>

---

<a id="q5"></a>

### Q5 · Widgets — `st.slider` and `st.number_input` 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Build a mini BMI calculator: use `st.slider` for height (150–210 cm) and `st.number_input` for weight (40–200 kg), then display the computed BMI with `st.metric`.


<details><summary>💡 Hint</summary>BMI = weight / (height_m ** 2). `st.slider` returns the current value immediately — no button needed.</details>

<details><summary>✅ Answer</summary>

```python
import streamlit as st

height_cm = st.slider("Height (cm)", 150, 210, 170)     # ← slider
weight_kg = st.number_input("Weight (kg)", 40, 200, 70)  # ← number input

height_m = height_cm / 100
bmi = weight_kg / (height_m ** 2)

st.metric("BMI", f"{bmi:.1f}")    # ← KPI display widget
```

**Why:** Streamlit reruns on every widget change, so BMI updates instantly — no submit button required.
</details>

---

<a id="q6"></a>

### Q6 · Widgets — `st.selectbox` and `st.multiselect` 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Show a `st.selectbox` for choosing a single ML model (Linear Regression, Random Forest, XGBoost) and a `st.multiselect` for choosing feature columns from `["age", "income", "score", "region"]` with `"age"` and `"income"` pre-selected. Print the selections with `st.write`.


<details><summary>💡 Hint</summary>Use the `default` parameter on `st.multiselect` for pre-selected values.</details>

<details><summary>✅ Answer</summary>

```python
import streamlit as st

model = st.selectbox(
    "Choose model",
    ["Linear Regression", "Random Forest", "XGBoost"]   # ← single choice
)

features = st.multiselect(
    "Choose features",
    ["age", "income", "score", "region"],
    default=["age", "income"]   # ← pre-selected
)

st.write(f"Model: **{model}**")
st.write(f"Features: {features}")
```

**Why:** `st.selectbox` returns one string; `st.multiselect` returns a list — use the list directly with your model's feature pipeline.
</details>

---

<a id="q7"></a>

### Q7 · Widgets — `st.file_uploader` CSV parsing 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Write a Streamlit snippet that lets the user upload a CSV file. If a file is uploaded, read it into a DataFrame and display it. If not, show an `st.info` message asking them to upload a file.


<details><summary>💡 Hint</summary>`st.file_uploader` returns `None` until a file is chosen — always check before calling `pd.read_csv`.</details>

<details><summary>✅ Answer</summary>

```python
import streamlit as st
import pandas as pd

uploaded = st.file_uploader("Upload a CSV file", type=["csv"])  # ← None until chosen

if uploaded is not None:
    df = pd.read_csv(uploaded)       # ← file-like object, pandas handles it
    st.success(f"Loaded {len(df)} rows")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Upload a CSV file to get started")
```

**Why:** The uploaded file object behaves like a Python file handle — `pd.read_csv` accepts it directly without saving to disk.
</details>

---

<a id="q8"></a>

### Q8 · Widgets — `st.button` conditional display 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Create a Streamlit form with a text input for a user's name and a "Greet" button. When the button is clicked, show `st.success("Hello, {name}!")`. Before clicking, show `st.info("Enter your name and click Greet")`.


<details><summary>💡 Hint</summary>`st.button` returns `True` only on the rerun triggered by the click — wrap your display logic in `if clicked:`.</details>

<details><summary>✅ Answer</summary>

```python
import streamlit as st

name    = st.text_input("Your name", placeholder="Enter name...")
clicked = st.button("Greet", type="primary")

if clicked and name:
    st.success(f"Hello, {name}!")          # ← shown after button click
elif clicked and not name:
    st.warning("Please enter a name first")
else:
    st.info("Enter your name and click Greet")  # ← default state
```

**Why:** `st.button` returns `True` on the rerun immediately after the click, then returns `False` on all subsequent reruns — that's why you test `if clicked`.
</details>

---

<a id="q9"></a>

### Q9 · Session state — counter across reruns 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Build a click counter with two buttons: "+" and "−". The count should persist across reruns. Display the current count between the two buttons.


<details><summary>💡 Hint</summary>Initialize `st.session_state.count = 0` inside an `if "count" not in st.session_state:` guard — without this guard it resets on every rerun.</details>

<details><summary>✅ Answer</summary>

```python
import streamlit as st

# Initialize once — guard prevents reset on every rerun
if "count" not in st.session_state:
    st.session_state.count = 0

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("−"):
        st.session_state.count -= 1   # ← mutate session state

with col2:
    st.metric("Count", st.session_state.count)   # ← read session state

with col3:
    if st.button("+"):
        st.session_state.count += 1
```

**Why:** Without `st.session_state`, a variable like `count = 0` resets to 0 on every rerun — session state is the only way to persist data within a user session.
</details>

---

<a id="q10"></a>

### Q10 · Session state — chat history list 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Implement a minimal chat interface: store messages in `st.session_state.messages`. On each submission, append the user message and an echo reply, then display all messages in order.


<details><summary>💡 Hint</summary>Use `st.chat_input` for the input box and `st.chat_message` for display; call `st.rerun()` after appending to refresh the view.</details>

<details><summary>✅ Answer</summary>

```python
import streamlit as st

if "messages" not in st.session_state:
    st.session_state.messages = []   # ← list of {"role": ..., "content": ...}

# Render existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Accept new input
if prompt := st.chat_input("Say something"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    reply = f"Echo: {prompt}"
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()   # ← re-render with new messages
```

**Why:** Appending to `st.session_state.messages` persists across reruns — each new prompt extends the list rather than replacing it.
</details>

---

<a id="q11"></a>

### Q11 · Caching — `@st.cache_data` for data loading 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Write a cached function `load_csv(path: str)` that reads a CSV. Demonstrate that calling it twice with the same path skips the second file read. Also show how to set a 1-hour TTL.


<details><summary>💡 Hint</summary>`@st.cache_data` caches by function arguments — the same `path` returns the cached DataFrame without re-reading the file.</details>

<details><summary>✅ Answer</summary>

```python
import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600)   # ← cache result for 1 hour; re-run after TTL expires
def load_csv(path: str) -> pd.DataFrame:
    st.write(f"Reading file: {path}")   # ← this line only runs on cache miss
    return pd.read_csv(path)

df1 = load_csv("data.csv")   # ← reads file, caches result
df2 = load_csv("data.csv")   # ← returns cached copy, no file read

st.write("DataFrames are identical:", df1.equals(df2))
```

**Why:** `@st.cache_data` serializes (pickles) the return value and stores it keyed by `(function, arguments)` — safe for data because each call gets its own copy.
</details>

---

<a id="q12"></a>

### Q12 · Caching — `@st.cache_resource` for model loading 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Write a cached function `get_model()` that loads a scikit-learn model from disk. Explain why you use `@st.cache_resource` instead of `@st.cache_data` here. Show what happens without caching.


<details><summary>💡 Hint</summary>`@st.cache_resource` stores the object as a shared singleton (not pickled) — all users share the same model object in memory.</details>

<details><summary>✅ Answer</summary>

```python
import streamlit as st

# WITHOUT caching — model reloads from disk on EVERY widget interaction!
# def get_model():
#     return joblib.load("model.pkl")   # ← called 100x per session = very slow

@st.cache_resource   # ← load once, share across all users and reruns
def get_model():
    import joblib
    return joblib.load("model.pkl")   # ← only runs once per process

model = get_model()   # ← fast on all subsequent calls
st.write("Model loaded:", type(model).__name__)
```

**Why:** Unlike `@st.cache_data`, `@st.cache_resource` does NOT copy the return value — all callers share one model object. This is correct for models (immutable inference objects) but dangerous for mutable data.
</details>

---

<a id="q13"></a>

### Q13 · Flask REST API — app factory and health route 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Write the minimal Flask app setup with a `GET /health` endpoint that returns `{"status": "ok"}` as JSON. Include the `if __name__ == "__main__"` block to run on port 5000.


<details><summary>💡 Hint</summary>`Flask(__name__)` creates the app; `@app.route("/health")` registers the route; `jsonify` serializes the dict to a JSON response.</details>

<details><summary>✅ Answer</summary>

```python
from flask import Flask, jsonify

app = Flask(__name__)   # ← __name__ tells Flask where to find templates/static

@app.route("/health")   # ← GET by default
def health():
    return jsonify({"status": "ok", "service": "my-api"})   # ← JSON response

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

**Why:** `jsonify` sets `Content-Type: application/json` automatically — returning a raw dict would not set the correct header.
</details>

---

<a id="q14"></a>

### Q14 · Flask REST API — GET route with path variable 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


Add a `GET /items/<int:item_id>` route to a Flask app. If the item exists in a dict, return it. If not, return a 404 JSON error.


<details><summary>💡 Hint</summary>Flask converts `<int:item_id>` to a Python int automatically — use `.get(item_id)` on the dict and check for `None`.</details>

<details><summary>✅ Answer</summary>

```python
from flask import Flask, jsonify

app = Flask(__name__)

items = {1: {"id": 1, "name": "Laptop"}, 2: {"id": 2, "name": "Mouse"}}

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):                    # ← Flask passes item_id as int
    item = items.get(item_id)             # ← dict lookup
    if item is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404  # ← 404
    return jsonify(item)                  # ← 200 by default
```

**Why:** The `<int:item_id>` converter handles the string-to-int conversion — without it, `item_id` would be a string and `items.get("1")` would fail.
</details>

---

<a id="q15"></a>

### Q15 · Flask REST API — POST route with `request.json` 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


Write a `POST /items` route that reads `name` and `price` from the JSON body. Validate both fields are present and `price` is a positive number. Return the created item with status 201.


<details><summary>💡 Hint</summary>`request.get_json()` returns `None` if the body is not valid JSON or `Content-Type` is not `application/json` — always check before accessing fields.</details>

<details><summary>✅ Answer</summary>

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
items, next_id = {}, 1

@app.route("/items", methods=["POST"])
def create_item():
    global next_id
    data = request.get_json()              # ← None if body is not JSON
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    missing = [f for f in ["name", "price"] if f not in data]
    if missing:
        return jsonify({"error": f"Missing: {missing}"}), 400

    if not isinstance(data["price"], (int, float)) or data["price"] <= 0:
        return jsonify({"error": "price must be a positive number"}), 422

    item = {"id": next_id, "name": data["name"], "price": data["price"]}
    items[next_id] = item
    next_id += 1
    return jsonify(item), 201              # ← 201 Created
```

**Why:** Return 400 for missing/malformed fields, 422 for semantically invalid values (negative price), and 201 (not 200) when a new resource is created.
</details>

---

<a id="q16"></a>

### Q16 · Flask REST API — `jsonify` and status codes 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


Explain the difference between returning `jsonify(data)` and `jsonify(data), 200`. Write a route that returns different status codes: 200 for success, 400 for bad input, and 404 for not found.


<details><summary>💡 Hint</summary>`jsonify(data)` alone defaults to 200 — the two-element tuple `(response, status_code)` overrides the status.</details>

<details><summary>✅ Answer</summary>

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/demo", methods=["GET"])
def demo():
    action = request.args.get("action")

    if action == "success":
        return jsonify({"result": "ok"})           # ← 200 (default)

    if action == "bad":
        return jsonify({"error": "bad input"}), 400  # ← 400 Bad Request

    if action == "missing":
        return jsonify({"error": "not found"}), 404  # ← 404 Not Found

    return jsonify({"help": "use ?action=success|bad|missing"}), 200
```

**Why:** Flask's `jsonify` always sets `Content-Type: application/json`. The status code is always the second element of the returned tuple — Flask's default is 200 when omitted.
</details>

---

<a id="q17"></a>

### Q17 · Flask REST API — error handlers 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


Register global error handlers for 404 and 500 errors that return JSON instead of Flask's default HTML error pages.


<details><summary>💡 Hint</summary>Use `@app.errorhandler(404)` and `@app.errorhandler(500)` — the decorated function receives the error object as its first argument.</details>

<details><summary>✅ Answer</summary>

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found", "code": 404}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed", "code": 405}), 405

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "code": 500}), 500

# Without these handlers, Flask returns HTML — breaks JSON API clients
```

**Why:** JSON API clients (mobile apps, other services) expect JSON for all responses including errors — without these handlers, a 404 returns an HTML page that `response.json()` will fail to parse.
</details>

---

<a id="q18"></a>

### Q18 · Flask config — `os.environ` secrets 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Show how to load three config values from environment variables: `SECRET_KEY`, `API_KEY`, and `DATABASE_URL`. Use a fallback default only for non-sensitive values. Demonstrate an auth check using `API_KEY`.


<details><summary>💡 Hint</summary>Sensitive values (API keys) should have no fallback — `os.environ.get("API_KEY")` returns `None` if unset, which you then guard against at startup.</details>

<details><summary>✅ Answer</summary>

```python
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Non-sensitive: safe to have a dev default
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-insecure-key")

# Sensitive: no fallback — must be set in environment
API_KEY      = os.environ.get("API_KEY")          # ← None if unset
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///dev.db")

@app.route("/secure")
def secure():
    key = request.headers.get("X-API-Key")        # ← read from header
    if not API_KEY or key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"data": "secret payload"})
```

**Why:** Never hardcode secrets in source code — they end up in git history. `os.environ` reads from the shell environment or a `.env` file loaded by `python-dotenv`.
</details>

---

<a id="q19"></a>

### Q19 · Flask config — `.env` with `python-dotenv` 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


Show the complete setup for loading a `.env` file in a Flask app using `python-dotenv`. Include the `.env` file contents, the Python code to load it, and the correct `.gitignore` entry.


<details><summary>💡 Hint</summary>Call `load_dotenv()` before reading `os.environ` — it injects the `.env` file variables into the process environment.</details>

<details><summary>✅ Answer</summary>

```python
# .env file (NEVER commit this to git):
# SECRET_KEY=my-super-secret-key-12345
# API_KEY=sk-prod-abc123
# DATABASE_URL=postgresql://user:pass@localhost/mydb

# .gitignore:
# .env

# app.py
import os
from dotenv import load_dotenv   # pip install python-dotenv
from flask import Flask

load_dotenv()   # ← reads .env file, injects into os.environ

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]   # ← raises KeyError if missing
```

**Why:** `load_dotenv()` is a local-dev convenience — in production (Docker, K8s), environment variables are injected directly by the platform, so the `.env` file is not needed.
</details>

---

<a id="q20"></a>

### Q20 · Flask config — blueprints 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


Split a Flask app into two blueprints: `items_bp` (routes under `/items`) and `users_bp` (routes under `/users`). Show the blueprint definition, route registration, and how to register them on the main app.


<details><summary>💡 Hint</summary>Create a `Blueprint("name", __name__)` in each module, add routes to it with `@bp.route(...)`, then `app.register_blueprint(bp, url_prefix="/prefix")` in the factory.</details>

<details><summary>✅ Answer</summary>

```python
# items.py
from flask import Blueprint, jsonify

items_bp = Blueprint("items", __name__)   # ← blueprint object

@items_bp.route("/")
def list_items():
    return jsonify({"items": ["Laptop", "Mouse"]})

@items_bp.route("/<int:item_id>")
def get_item(item_id):
    return jsonify({"id": item_id})

# users.py
from flask import Blueprint, jsonify

users_bp = Blueprint("users", __name__)

@users_bp.route("/")
def list_users():
    return jsonify({"users": ["Alice", "Bob"]})

# app.py
from flask import Flask
from items import items_bp
from users import users_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(items_bp, url_prefix="/items")  # ← /items/, /items/1
    app.register_blueprint(users_bp, url_prefix="/users")  # ← /users/
    return app

app = create_app()
```

**Why:** Blueprints let you split a large Flask app into logical modules — each blueprint owns its routes, error handlers, and templates independently.
</details>

---

<a id="q21"></a>

### Q21 · Flask config — app context and `g` 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


Explain Flask's application context. Show how to use `flask.g` to store per-request data (e.g., a database connection) and clean it up after the request with `@app.teardown_appcontext`.


<details><summary>💡 Hint</summary>`flask.g` is a namespace object that lives for one request — fresh for each request, automatically discarded after the response is sent.</details>

<details><summary>✅ Answer</summary>

```python
from flask import Flask, g, jsonify

app = Flask(__name__)

def get_db():
    """Return the request-scoped DB connection, creating it if needed."""
    if "db" not in g:
        # In real code: g.db = sqlite3.connect("dev.db")
        g.db = {"connection": "fake-db-connection"}   # ← stored on g
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)           # ← clean up after each request
    if db is not None:
        pass   # db.close() in real code

@app.route("/data")
def get_data():
    db = get_db()                    # ← same connection reused within request
    return jsonify({"connection": str(db)})
```

**Why:** `g` ensures each request gets its own DB connection — storing it on `g` avoids opening multiple connections per request and lets the teardown handler close it reliably.
</details>

---

<a id="q22"></a>

### Q22 · Decision guide — Streamlit vs Flask 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


A data scientist wants to build a tool where teammates can upload a CSV, choose columns, and see a chart. A backend team wants to expose a trained model for a mobile app to call. Which framework fits each case? Give three reasons each.


<details><summary>💡 Hint</summary>Think about the consumer: is it a human clicking widgets (Streamlit) or a machine calling an endpoint (Flask)?</details>

<details><summary>✅ Answer</summary>

```
Data scientist tool → Streamlit
  1. File upload, dropdowns, and charts are built-in widgets — no frontend code
  2. No HTTP knowledge needed — the data scientist writes pure Python
  3. Deployed in minutes via Streamlit Community Cloud or Hugging Face Spaces

Mobile app backend → Flask (or FastAPI)
  1. Exposes a REST endpoint the mobile app calls programmatically
  2. Full control over HTTP methods, status codes, and JSON schema
  3. Supports authentication, rate limiting, and middleware

Rule of thumb:
  Human uses it interactively → Streamlit
  Another service calls it programmatically → Flask / FastAPI
```

**Why:** Streamlit's re-run model is designed for human interaction loops; Flask's request/response model is designed for machine-to-machine communication.
</details>

---

<a id="q23"></a>

### Q23 · Common mistakes — re-run model on every interaction 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


A Streamlit app loads a 500 MB model with `joblib.load("model.pkl")` at the top of the script. It becomes unbearably slow. Diagnose and fix the problem.


<details><summary>💡 Hint</summary>Streamlit reruns the entire script on every widget interaction — any code at the top level runs on every click.</details>

<details><summary>✅ Answer</summary>

```python
import streamlit as st

# BROKEN: model reloads from disk on every slider move, button click, etc.
# model = joblib.load("model.pkl")   # ← 500 MB, runs 100x per session

# FIXED: load once, share across all reruns and all users
@st.cache_resource
def load_model():
    import joblib
    return joblib.load("model.pkl")   # ← runs ONCE per process lifetime

model = load_model()   # ← instant on all subsequent calls

threshold = st.slider("Confidence threshold", 0.0, 1.0, 0.5)
st.write(f"Model: {type(model).__name__}, threshold: {threshold}")
```

**Why:** Without `@st.cache_resource`, Streamlit loads 500 MB from disk on every widget interaction (slider move, button click, text input). With caching, the model is loaded once and reused.
</details>

---

<a id="q24"></a>

### Q24 · Common mistakes — Flask thread safety 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


A Flask app stores a prediction counter in a global Python variable and increments it on every `/predict` request. Under concurrent load, the counter gives wrong results. Explain why and show the fix.


<details><summary>💡 Hint</summary>Flask's development server is single-threaded, but production WSGI servers (Gunicorn) run multiple threads or workers — a plain `counter += 1` is a read-modify-write race condition.</details>

<details><summary>✅ Answer</summary>

```python
# BROKEN: race condition with multiple threads
# prediction_count = 0
# @app.route("/predict", methods=["POST"])
# def predict():
#     global prediction_count
#     prediction_count += 1   # ← read-modify-write: not atomic under threads

# FIX 1: threading.Lock for in-process thread safety
import threading
from flask import Flask, jsonify

app = Flask(__name__)
_count = 0
_lock = threading.Lock()

@app.route("/predict", methods=["POST"])
def predict():
    global _count
    with _lock:           # ← only one thread increments at a time
        _count += 1
        current = _count
    return jsonify({"prediction": 42, "total_requests": current})

# FIX 2 (production): use Redis INCR — atomic across multiple processes/workers
# import redis; r = redis.Redis(); count = r.incr("prediction_count")
```

**Why:** In production, Gunicorn runs 4–8 worker threads per process. Without a lock, two threads can read the same value simultaneously, both increment, and one write is lost.
</details>

---

<a id="q25"></a>

### Q25 · Decision guide — blueprint structure for large apps 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


Sketch the folder structure for a production Flask API with three domains: `auth`, `items`, and `predictions`. Show where blueprints live, how the app factory assembles them, and where configuration is loaded.


<details><summary>💡 Hint</summary>The app factory pattern (`create_app()`) is the standard Flask pattern for large apps — it enables testing with different configs and avoids circular imports.</details>

<details><summary>✅ Answer</summary>

```
myapi/
├── app.py              ← entry point: from myapi import create_app; app = create_app()
├── myapi/
│   ├── __init__.py     ← create_app() factory
│   ├── config.py       ← Config classes (DevConfig, ProdConfig)
│   ├── auth/
│   │   ├── __init__.py ← auth_bp = Blueprint("auth", __name__)
│   │   └── routes.py   ← @auth_bp.route("/login"), @auth_bp.route("/logout")
│   ├── items/
│   │   ├── __init__.py ← items_bp = Blueprint("items", __name__)
│   │   └── routes.py   ← @items_bp.route("/"), @items_bp.route("/<int:id>")
│   └── predictions/
│       ├── __init__.py ← predictions_bp = Blueprint("predictions", __name__)
│       └── routes.py   ← @predictions_bp.route("/predict", methods=["POST"])
└── .env                ← local secrets (gitignored)
```

```python
# myapi/__init__.py
from flask import Flask
from .config import config_map
from .auth import auth_bp
from .items import items_bp
from .predictions import predictions_bp

def create_app(env="production"):
    app = Flask(__name__)
    app.config.from_object(config_map[env])   # ← load config class
    app.register_blueprint(auth_bp,        url_prefix="/auth")
    app.register_blueprint(items_bp,       url_prefix="/items")
    app.register_blueprint(predictions_bp, url_prefix="/predictions")
    return app
```

**Why:** The app factory pattern + blueprints is the standard Flask architecture for anything beyond a toy project — it supports multiple configs (dev/prod/test), avoids circular imports, and keeps each domain's code isolated.
</details>

---

## Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| ⬅️ Prev Module | [../31_file_formats_pdf_xml/theory.md](../31_file_formats_pdf_xml/theory.md) |
| ➡️ Next Module | [../33_regular_expressions/theory.md](../33_regular_expressions/theory.md) |

---

**[Back to README](../README.md)**
