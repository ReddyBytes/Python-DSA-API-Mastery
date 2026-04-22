# 📄 File Formats — PDF, XML, JSON, CSV, Excel

---

A government regulatory body sends you their annual compliance report as a 400-page PDF. A healthcare system exports patient records as XML. Your financial data vendor delivers daily feeds as CSV with unusual encodings. Your trading partner sends orders in Excel with merged cells and color-coded rows.

None of this data is in a clean pandas DataFrame yet. Getting it there is the job.

Real-world data arrives in dozens of formats, each with its own parsing quirks, encoding gotchas, and structural surprises. The ability to handle any format Python can touch is a core data engineering skill.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`json` module · `csv` module · `pd.read_csv()` · `pd.read_excel()` · `pd.read_json()` · File encoding (`utf-8`, `latin-1`)

**Should Learn** — Important for real projects, comes up regularly:
`pymupdf` / `pdfplumber` for PDF extraction · `xml.etree.ElementTree` · `lxml` · `openpyxl` for Excel manipulation · `pickle` · `parquet` with pandas/pyarrow

**Good to Know** — Useful in specific situations:
`pdfminer` · `camelot` for PDF tables · `xmltodict` · YAML with `pyyaml` · `msgpack` · `feather` format

**Reference** — Know it exists, look up when needed:
`zarr` · HDF5 with `h5py` · Apache Arrow IPC format · `orjson` (faster JSON)

---

## 1️⃣ JSON — JavaScript Object Notation

JSON is the universal format for APIs, configs, and semi-structured data.

```python
import json

# Parse JSON string → Python object
data = json.loads('{"name": "Alice", "score": 95, "tags": ["ai", "ml"]}')
print(data["name"])   # Alice
print(data["tags"])   # ['ai', 'ml']

# Python object → JSON string
obj = {"model": "gpt-4", "temperature": 0.7, "tokens": 1024}
json_string = json.dumps(obj, indent=2)   # indent for pretty-print
print(json_string)

# Read JSON file
with open("config.json") as f:
    config = json.load(f)

# Write JSON file
with open("output.json", "w") as f:
    json.dump({"results": [1, 2, 3]}, f, indent=2)

# Handle nested JSON → DataFrame
import pandas as pd
nested = [
    {"name": "Alice", "metrics": {"accuracy": 0.95, "f1": 0.93}},
    {"name": "Bob",   "metrics": {"accuracy": 0.88, "f1": 0.87}},
]
df = pd.json_normalize(nested, sep=".")
# Columns: name, metrics.accuracy, metrics.f1
print(df)
```

---

## 2️⃣ CSV — Comma-Separated Values

```python
import csv
import pandas as pd

# Read with csv module
with open("data.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)   # dict per row
    for row in reader:
        print(row["name"], row["price"])

# Write with csv module
rows = [["Alice", 25, "Engineer"], ["Bob", 30, "Manager"]]
with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age", "role"])   # header
    writer.writerows(rows)

# Pandas (faster and more ergonomic)
df = pd.read_csv("data.csv",
    encoding="utf-8",           # try "latin-1" if utf-8 fails
    sep=",",                    # or "\t" for TSV
    skiprows=2,                 # skip first 2 rows
    usecols=["name", "price"],  # only load needed columns (memory efficient)
    dtype={"price": float},     # specify types upfront
    na_values=["N/A", "NULL", ""],  # treat these as NaN
    parse_dates=["date_col"],   # parse strings as datetime
    nrows=1000,                 # only read first 1000 rows (for testing)
)

df.to_csv("output.csv", index=False, encoding="utf-8")
```

---

## 3️⃣ Excel Files

```python
import pandas as pd

# Read Excel
df = pd.read_excel("report.xlsx",
    sheet_name="Sales",       # sheet name or index (0-based)
    header=0,                  # row to use as column names
    skiprows=2,                # skip preamble rows
    usecols="A:E",             # columns A through E
    dtype={"Revenue": float},
)

# Read all sheets as dict of DataFrames
all_sheets = pd.read_excel("report.xlsx", sheet_name=None)
for sheet_name, df in all_sheets.items():
    print(f"{sheet_name}: {df.shape}")

# Write to Excel
with pd.ExcelWriter("output.xlsx", engine="openpyxl") as writer:
    df_sales.to_excel(writer, sheet_name="Sales", index=False)
    df_costs.to_excel(writer, sheet_name="Costs", index=False)

# openpyxl — fine-grained Excel manipulation
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

wb = load_workbook("report.xlsx")
ws = wb.active

# Read cells
value = ws["B2"].value
row_data = [cell.value for cell in ws[3]]   # row 3

# Write and style
ws["A1"] = "Updated Header"
ws["A1"].font = Font(bold=True, size=14)
ws["A1"].fill = PatternFill(fgColor="FFFF00", fill_type="solid")

wb.save("styled_output.xlsx")
```

---

## 4️⃣ PDF Extraction

PDFs are the hardest format. They have no inherent structure — text can be anywhere.

```python
# pdfplumber — best for text and tables
# pip install pdfplumber
import pdfplumber

with pdfplumber.open("report.pdf") as pdf:
    print(f"Pages: {len(pdf.pages)}")

    # Extract text from all pages
    full_text = ""
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    # Extract tables (returns list of lists)
    page = pdf.pages[0]
    tables = page.extract_tables()
    for table in tables:
        import pandas as pd
        df = pd.DataFrame(table[1:], columns=table[0])
        print(df)


# PyMuPDF — fast, good for text-heavy PDFs
# pip install pymupdf
import fitz   # PyMuPDF import name

doc = fitz.open("report.pdf")
for page_num, page in enumerate(doc):
    text = page.get_text()
    print(f"Page {page_num + 1}:\n{text[:200]}\n")

doc.close()
```

---

## 5️⃣ XML Parsing

```python
import xml.etree.ElementTree as ET

xml_string = """
<catalog>
    <product id="001">
        <name>Laptop Pro</name>
        <price currency="USD">999.99</price>
        <category>Electronics</category>
    </product>
    <product id="002">
        <name>Wireless Mouse</name>
        <price currency="USD">29.99</price>
        <category>Accessories</category>
    </product>
</catalog>
"""

# Parse from string
root = ET.fromstring(xml_string)

# Parse from file
# tree = ET.parse("catalog.xml"); root = tree.getroot()

# Navigate and extract
print(f"Root tag: {root.tag}")   # catalog

for product in root.findall("product"):
    prod_id = product.get("id")            # attribute
    name    = product.findtext("name")     # child element text
    price   = product.findtext("price")
    currency = product.find("price").get("currency")   # child attribute
    print(f"{prod_id}: {name} = {currency} {price}")

# XPath for complex queries
prices = root.findall(".//price[@currency='USD']")

# xmltodict — treat XML like JSON (simpler for simple cases)
# pip install xmltodict
import xmltodict
data = xmltodict.parse(xml_string)
products = data["catalog"]["product"]
print(products[0]["name"])
```

---

## 6️⃣ High-Performance Formats

```python
import pandas as pd

# Parquet — columnar format, fast for analytics
df.to_parquet("data.parquet", index=False, compression="snappy")
df = pd.read_parquet("data.parquet", columns=["name", "price"])  # read specific columns

# Pickle — Python-specific binary, preserves all Python types
import pickle
with open("model.pkl", "wb") as f:
    pickle.dump(trained_model, f)

with open("model.pkl", "rb") as f:
    loaded_model = pickle.load(f)
# Warning: never unpickle untrusted files — security risk

# Feather — fast R/Python interchange
df.to_feather("data.feather")
df = pd.read_feather("data.feather")
```

---

## Common Mistakes to Avoid ⚠️

- **Wrong encoding**: if CSV has accented characters and `utf-8` fails, try `latin-1` or `cp1252`. Always specify encoding explicitly.
- **Forgetting `index=False` in `to_csv`/`to_excel`**: default writes the index as an extra column, creating an unnamed column on re-read.
- **Trying to parse PDFs like structured data**: PDFs are page layout, not data. Scanned PDFs need OCR (tesseract). Always inspect the raw text before writing extraction logic.
- **Treating XML attributes and elements the same**: XML has both child elements (`<name>value</name>`) and attributes (`<tag attr="value">`). Use `.get("attr")` for attributes and `.findtext("element")` for element text.

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
