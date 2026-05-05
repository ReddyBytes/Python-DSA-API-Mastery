# 📄 File Formats — Cheatsheet

## Format Selection Guide

| Format | Use When | Library |
|---|---|---|
| CSV | Tabular data, universal exchange | `pandas`, `csv` |
| JSON | APIs, config, semi-structured | `json`, `pandas` |
| Excel | Business reports, multi-sheet | `pandas`, `openpyxl` |
| Parquet | Large analytical datasets | `pandas`, `pyarrow` |
| XML | Enterprise data exchange | `xml.etree`, `lxml`, `xmltodict` |
| PDF | Documents, reports | `pdfplumber`, `pymupdf` |
| Pickle | Python-specific serialization | `pickle` |
| Feather | Fast R↔Python data exchange | `pandas` |

---

## JSON

```python
import json

# String → Python
data = json.loads('{"key": "value", "list": [1,2,3]}')

# Python → String
s = json.dumps(data, indent=2, ensure_ascii=False)

# File → Python
with open("file.json") as f:
    data = json.load(f)

# Python → File
with open("file.json", "w") as f:
    json.dump(data, f, indent=2)

# Nested JSON → DataFrame
pd.json_normalize(records, sep=".")            # flatten nested dicts
pd.json_normalize(records, record_path="items")  # expand nested lists
```

---

## CSV

```python
# Read
df = pd.read_csv("file.csv",
    encoding="utf-8",        # or "latin-1", "cp1252"
    sep=",",                 # or "\t", ";"
    header=0,                # row index for header
    usecols=["a","b"],       # load specific columns only
    dtype={"col": str},      # force string type
    parse_dates=["date"],    # parse as datetime
    na_values=["N/A",""],    # treat as NaN
    nrows=1000,              # limit rows (for testing)
)

# Write
df.to_csv("out.csv", index=False, encoding="utf-8")

# Large files — chunked reading
for chunk in pd.read_csv("large.csv", chunksize=10000):
    process(chunk)
```

---

## Excel

```python
# Read
df = pd.read_excel("file.xlsx", sheet_name="Sheet1", header=0)
all_sheets = pd.read_excel("file.xlsx", sheet_name=None)  # dict of DFs

# Write multiple sheets
with pd.ExcelWriter("out.xlsx", engine="openpyxl") as writer:
    df1.to_excel(writer, sheet_name="Sales", index=False)
    df2.to_excel(writer, sheet_name="Costs", index=False)

# Direct openpyxl manipulation
from openpyxl import load_workbook
wb = load_workbook("file.xlsx")
ws = wb["Sheet1"]
ws["A1"].value          # read cell
ws["A1"] = "new value"  # write cell
wb.save("modified.xlsx")
```

---

## XML

```python
import xml.etree.ElementTree as ET

# Parse
root = ET.parse("file.xml").getroot()   # from file
root = ET.fromstring(xml_string)         # from string

# Find elements
root.findall("child")                    # direct children named "child"
root.findall(".//child")                 # all descendants named "child"
root.findall(".//child[@attr='val']")    # with attribute filter
root.find("child")                       # first match
root.findtext("child")                   # text content of first match
el.get("attr")                           # element attribute
el.text                                  # element text content
el.tag                                   # element tag name

# xmltodict (simpler for shallow XML)
import xmltodict
data = xmltodict.parse(xml_string)       # XML → dict
xml  = xmltodict.unparse(data)           # dict → XML
```

---

## PDF Extraction

```python
# pdfplumber — best for text + tables
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    # Text
    for page in pdf.pages:
        print(page.extract_text())

    # Tables (returns list of lists)
    for page in pdf.pages:
        for table in page.extract_tables():
            df = pd.DataFrame(table[1:], columns=table[0])

# PyMuPDF — fast text extraction
import fitz
doc = fitz.open("file.pdf")
text = "".join(page.get_text() for page in doc)
doc.close()
```

---

## Parquet and High-Performance Formats

```python
# Parquet (columnar, compressed, fast)
df.to_parquet("data.parquet", compression="snappy", index=False)
df = pd.read_parquet("data.parquet", columns=["col1", "col2"])

# Pickle (Python-only, preserves complex types)
import pickle
with open("obj.pkl", "wb") as f: pickle.dump(obj, f)
with open("obj.pkl", "rb") as f: obj = pickle.load(f)
# NEVER unpickle files from untrusted sources

# CSV vs Parquet performance
# Parquet: 5-10x smaller, 10-50x faster for column-selective reads
```

---

## Encoding Troubleshooting

```python
# Detect encoding
import chardet
with open("file.csv", "rb") as f:
    result = chardet.detect(f.read(10000))
print(result["encoding"])   # e.g., "latin-1", "utf-8-sig"

# Common encodings to try
encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
for enc in encodings:
    try:
        df = pd.read_csv("file.csv", encoding=enc)
        print(f"Works: {enc}")
        break
    except UnicodeDecodeError:
        continue
```

---

## Golden Rules

1. Always specify `encoding=` in `read_csv` — silent wrong encoding causes invisible garbled data
2. Always write `index=False` when saving DataFrames to CSV/Excel — default index creates mystery columns
3. For large CSVs, use `usecols` and `dtype` upfront — don't load then filter in memory
4. Parquet is almost always better than CSV for analytics — use it whenever you control both reader and writer
5. Never pickle untrusted data — use JSON or parquet for portable serialization
