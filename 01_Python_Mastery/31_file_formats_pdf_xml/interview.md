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

---

**Q: What is the difference between pdfplumber and pypdf, and when would you use each?**

Both libraries extract text from PDFs, but they take different approaches. `pypdf` is lightweight and fast — it reads the raw text stream embedded in each PDF page. It handles page metadata, encryption, and simple text extraction well, but has no layout awareness: whitespace between columns and table borders is lost. `pdfplumber` sits on top of `pdfminer.six` and parses PDFs using character coordinates. It knows where each character sits on the page, which lets it reconstruct tables and detect column boundaries. Use `pypdf` when you only need raw text and page count. Use `pdfplumber` when you need tables or need to preserve the visual structure of the content.

---

**Q: When would you choose Parquet over CSV in a data pipeline?**

Always prefer Parquet when you control both the writer and the reader. Parquet is columnar — data is stored column by column rather than row by row. This means a query that reads only two columns out of fifty only touches those two columns on disk: 10-50x faster for analytical workloads. Parquet also stores type metadata (integers stay integers, dates stay dates) so there is no silent type coercion on read the way there is with CSV. Parquet files are 5-10x smaller due to column-level compression (snappy, gzip, zstd). Use CSV only for human-readable interchange, when the consumer cannot read Parquet, or for tiny files where the overhead difference does not matter.

---

**Q: What is the feather format and when is it the right choice?**

Feather is the Apache Arrow IPC file format — essentially a memory-mapped snapshot of an Arrow table. Writing and reading feather involves almost no serialization work: the in-memory layout and the on-disk layout are nearly identical. This makes feather the fastest possible format for temporary data exchange between two Python processes or between Python and R (both use Arrow natively). The tradeoff: feather files are not compressed by default and are not designed for long-term storage. They may also be larger than CSV for sparse data. Choose feather when you need maximum throughput for an intermediate step in a local pipeline. Choose Parquet for storage, S3, Spark, or any cross-system use.

---

**Q: What is the XPath syntax supported by Python's ElementTree, and what are its limits?**

ElementTree supports a subset of XPath called "ElementPath". Key patterns:

- `root.findall("child")` — direct children named `child`
- `root.findall(".//child")` — all descendants named `child`
- `root.findall(".//child[@attr='val']")` — descendants with a specific attribute value
- `root.findall(".//parent/child")` — children of a named parent
- `root.findtext("child")` — text of first matching child element

Limits: ElementTree does not support the full XPath 1.0 spec. No `contains()`, no `text()` node selectors, no `|` union operator, no axes like `parent::` or `following-sibling::`. For full XPath support use `lxml`, which implements the complete XPath 1.0 standard and is much faster on large documents.

---

**Q: How do you apply cell formatting in openpyxl?**

openpyxl uses style objects from `openpyxl.styles`. The main ones are `Font` (bold, size, color, italic), `PatternFill` (background color), `Border` (cell borders), and `Alignment` (text alignment, wrap). You set them as attributes on a `Cell` object:

```python
from openpyxl.styles import Font, PatternFill, Alignment

ws["A1"].font      = Font(bold=True, size=14, color="FF0000")
ws["A1"].fill      = PatternFill(fgColor="FFFF00", fill_type="solid")
ws["A1"].alignment = Alignment(horizontal="center", wrap_text=True)
```

pandas `to_excel` cannot apply these styles — it writes data only. Use `pd.ExcelWriter` with `engine="openpyxl"` to write data, then load the workbook with `load_workbook` to apply formatting as a second pass.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⬅️ Prev Module | [../30_sql_with_python/theory.md](../30_sql_with_python/theory.md) |
| ➡️ Next Module | [../32_streamlit_flask/theory.md](../32_streamlit_flask/theory.md) |

---

**[🏠 Back to README](../README.md)**
