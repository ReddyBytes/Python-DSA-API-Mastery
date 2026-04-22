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
