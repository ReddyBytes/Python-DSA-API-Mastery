# 📄 File Formats — Interview Questions

---

**Q: What is the difference between CSV and Parquet, and when would you use each?**

CSV is a plain-text row-oriented format: every row is a line, fields are comma-separated. It's universally readable by any tool, but has no type information (everything is a string until parsed), no compression, and poor performance for column-selective reads — to get one column you read the entire file. Parquet is a columnar binary format: data is stored column by column, with type metadata embedded and compression per column. To get one column from a 50-column Parquet file, you only read that column's bytes. For analytics workloads (read a few columns from millions of rows), Parquet is 5-10x smaller and 10-50x faster. Use CSV for human-readable interchange, tool compatibility, and small files. Use Parquet for data pipelines, analytics, and any file you read more than once.

---

**Q: How do you handle character encoding issues when reading CSV files?**

If `pd.read_csv("file.csv")` raises a `UnicodeDecodeError`, the file uses an encoding other than UTF-8. Common alternatives: `latin-1` (Western European), `cp1252` (Windows), `iso-8859-1`, `utf-8-sig` (UTF-8 with BOM). Strategy: (1) try `encoding="latin-1"` first — it rarely fails since it's a superset of ASCII; (2) use `chardet.detect()` to identify the encoding automatically; (3) if the source is a Windows Excel export, try `encoding="cp1252"`. Always specify encoding explicitly in production code — don't rely on system default which varies by OS.

---

**Q: How would you extract structured data from a PDF?**

PDFs are designed for visual layout, not data extraction. Strategy depends on PDF type: (1) **Text PDFs** (not scanned): use `pdfplumber` or `PyMuPDF` to extract text or tables. `pdfplumber` is better for tables; `PyMuPDF` (fitz) is faster for bulk text extraction. (2) **Scanned PDFs**: text is embedded as images — need OCR. Use `pytesseract` (wrapper for Tesseract) or cloud services (AWS Textract, Google Document AI). (3) **Tables in PDFs**: `pdfplumber.page.extract_tables()` returns table data as lists of lists. `camelot-py` is better for complex multi-line table cells. The biggest challenge is that PDFs have no semantic structure — "this is a table cell" is not encoded; you're inferring structure from visual coordinates.

---

**Q: What is `pd.json_normalize` and when do you need it?**

`pd.json_normalize` flattens nested JSON objects into a flat DataFrame. Standard `pd.DataFrame(records)` fails or creates columns containing dicts when records have nested structure. Example: `{"name": "Alice", "metrics": {"accuracy": 0.95, "f1": 0.93}}` — calling `pd.DataFrame([record])` creates a column `metrics` containing a dict, which is useless for analysis. `pd.json_normalize([record], sep=".")` creates `name`, `metrics.accuracy`, `metrics.f1` columns. The `record_path` parameter expands nested lists into rows. Use it whenever your JSON has more than one level of nesting.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Prev Module | [../30_sql_with_python/theory.md](../30_sql_with_python/theory.md) |
| ➡️ Next Module | [../32_streamlit_flask/theory.md](../32_streamlit_flask/theory.md) |

---

**[🏠 Back to README](../README.md)**
