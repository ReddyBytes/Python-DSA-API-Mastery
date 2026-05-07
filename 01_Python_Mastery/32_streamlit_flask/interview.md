# 🖥️ Streamlit and Flask — Interview Questions

---

**Q: What is the difference between Streamlit and Flask, and when would you use each?**

Streamlit is a Python library that turns a script into a web app automatically — no HTML, CSS, or JavaScript required. Every time a user interacts with a widget, the entire script reruns from top to bottom. It's ideal for ML demos, internal dashboards, and data exploration tools where the primary user is a non-technical stakeholder or where speed of development matters more than customization. Flask is a WSGI web framework that gives you full control over routes, HTTP methods, request handling, and response formatting. It's ideal for building REST APIs, backend services, and production web applications. When another service (a mobile app, frontend, or pipeline) needs to call your ML model programmatically, Flask (or FastAPI) is the right choice.

---

**Q: What is `st.cache_data` vs `st.cache_resource` and when do you use each?**

`st.cache_data` caches functions that return data — DataFrames, lists, dicts, numpy arrays. The return value is serialized (pickled) and stored; each call with the same arguments returns the cached copy. It's safe to use for any data-returning function. `st.cache_resource` caches shared resources — models, database connections, API clients. The resource is NOT serialized; it lives in the process as a singleton, shared across all users and sessions. Use `st.cache_data` for data loading functions (`pd.read_csv`, API calls). Use `st.cache_resource` for model loading (`joblib.load`, `torch.load`) and connection objects. Without caching, Streamlit reruns the full script (including model loading) on every user interaction — making the app unusably slow.

---

**Q: How do you handle request validation in Flask?**

Validate at the route function level before doing any business logic. Check required fields, types, and ranges: `data = request.get_json()` returns None if the body is not valid JSON. Then check for required keys: `if "field" not in data: return jsonify({"error": "missing field"}), 400`. For production, use a validation library: marshmallow or pydantic for schema-based validation. Return 400 Bad Request for invalid input, 422 Unprocessable Entity for semantically wrong input, and 500 only for unexpected server errors. Always return JSON responses for API endpoints — never let Flask return its default HTML error pages from a JSON API.

---

**Q: How would you deploy a Streamlit app for others to use?**

Options by complexity: (1) **Streamlit Community Cloud** (free) — push your app to GitHub, connect at share.streamlit.io, deployed in minutes with no infrastructure; (2) **Hugging Face Spaces** (free) — upload app.py + requirements.txt, runs on HF's servers with a public URL; (3) **Docker + cloud** — `streamlit run app.py` inside a Docker container, deploy to AWS ECS, Google Cloud Run, or Azure Container Apps; (4) **Render/Railway** — connect GitHub repo, configure start command, auto-deploy. For production: set secrets via environment variables (never in code), use `st.cache_resource` for models, add `requirements.txt` with pinned versions.

---

**Q: How do you structure a large Flask application using blueprints and the app factory pattern?**

For anything beyond a small script, Flask's recommended architecture is the **app factory pattern** combined with **blueprints**. A blueprint is a collection of routes, error handlers, and templates that belong to one domain (e.g., `auth`, `items`, `predictions`). You define a blueprint in a submodule: `auth_bp = Blueprint("auth", __name__)`, attach routes to it with `@auth_bp.route(...)`, then register it on the app at startup: `app.register_blueprint(auth_bp, url_prefix="/auth")`. The app factory is a `create_app(config="production")` function that constructs and returns the Flask app, loading config and registering all blueprints inside. Benefits: (1) testable — `create_app("testing")` returns a fresh app per test with test config; (2) no circular imports — each blueprint imports nothing from the main app; (3) separation of concerns — each domain's code is entirely self-contained. The standard folder layout is one subfolder per domain, each with its own `__init__.py` (defining the blueprint) and `routes.py`.

---

**Q: How does `st.session_state` work and what are the common pitfalls?**

`st.session_state` is a dictionary-like namespace that Streamlit preserves across reruns within a single browser session. It resets when the user closes or refreshes the tab. The core pattern: always initialize with a guard — `if "key" not in st.session_state: st.session_state.key = default_value`. Without the guard, the value resets to the default on every rerun, defeating the purpose. Common pitfalls: (1) **forgetting the guard** — the most common mistake, causes the counter/chat history/flag to reset on every widget interaction; (2) **mutating complex objects in-place** — assigning `st.session_state.list = []` works, but `st.session_state.list.append(x)` may not trigger a rerun — use `st.rerun()` explicitly if the UI doesn't update; (3) **sharing state across users** — `st.session_state` is per-user, per-session, never shared; use a database or Redis for cross-user state.

---

**Q: How do you build a multipage Streamlit app?**

Streamlit supports multipage apps natively. Create a `pages/` directory alongside your main `app.py`. Any `.py` file in `pages/` becomes a page — Streamlit auto-generates a sidebar navigation entry for each one. File name determines the page name: `pages/1_Dashboard.py` → "Dashboard", `pages/2_Settings.py` → "Settings". The number prefix controls ordering. Each page is a full independent Streamlit script — `st.session_state` is shared across all pages within the same session. For programmatic navigation (redirect from one page to another via code), use `st.switch_page("pages/target.py")`. This pattern scales well for ML apps: one page for data upload, one for model training, one for results visualization.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⬅️ Prev Module | [../31_file_formats_pdf_xml/theory.md](../31_file_formats_pdf_xml/theory.md) |
| ➡️ Next Module | [../33_regular_expressions/theory.md](../33_regular_expressions/theory.md) |

---

**[🏠 Back to README](../README.md)**
