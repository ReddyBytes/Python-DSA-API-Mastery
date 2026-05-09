# File Formats: PDF & XML — Practice

## Quick Index

| # | Chapter | Topic | Difficulty |
|---|---------|-------|------------|
| [Q1](#q1) | JSON | json.loads / json.dumps | 🟢 Basic |
| [Q2](#q2) | JSON | Nested JSON + pd.json_normalize | 🟡 Intermediate |
| [Q3](#q3) | JSON | json.JSONDecodeError handling | 🟢 Basic |
| [Q4](#q4) | JSON | json.dump to file + json.load | 🟢 Basic |
| [Q5](#q5) | CSV | csv.reader basics | 🟢 Basic |
| [Q6](#q6) | CSV | csv.DictReader row access | 🟢 Basic |
| [Q7](#q7) | CSV | csv.writer output | 🟡 Intermediate |
| [Q8](#q8) | CSV | Dialect and delimiter handling | 🟡 Intermediate |
| [Q9](#q9) | Excel | openpyxl read cells | 🟡 Intermediate |
| [Q10](#q10) | Excel | openpyxl write and style cells | 🟡 Intermediate |
| [Q11](#q11) | Excel | pandas read_excel with sheet_name | 🟢 Basic |
| [Q12](#q12) | Excel | pandas ExcelWriter multiple sheets | 🟡 Intermediate |
| [Q13](#q13) | PDF | pdfplumber text extraction | 🟡 Intermediate |
| [Q14](#q14) | PDF | pypdf page count | 🟢 Basic |
| [Q15](#q15) | PDF | pdfplumber table extraction | 🟠 Advanced |
| [Q16](#q16) | PDF | Scanned PDF — what to do | 🟡 Intermediate |
| [Q17](#q17) | XML | ElementTree parse from string | 🟢 Basic |
| [Q18](#q18) | XML | find / findall element navigation | 🟡 Intermediate |
| [Q19](#q19) | XML | XPath attribute filter | 🟠 Advanced |
| [Q20](#q20) | XML | Write XML with ElementTree | 🟡 Intermediate |
| [Q21](#q21) | High-Perf | Parquet read/write with pandas | 🟢 Basic |
| [Q22](#q22) | High-Perf | Feather vs Parquet use cases | 🟡 Intermediate |
| [Q23](#q23) | High-Perf | HDF5 key store with pandas | 🟡 Intermediate |
| [Q24](#q24) | High-Perf | CSV vs Parquet file size comparison | 🟠 Advanced |
| [Q25](#q25) | High-Perf | Pickle round-trip and security warning | 🟡 Intermediate |

---

<a id="q1"></a>

### Q1 · JSON — json.loads / json.dumps 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


You receive a JSON string from an API response. Parse it into a Python dict, then convert a Python dict back into a formatted JSON string with 2-space indentation.


<details><summary>💡 Hint</summary>Use json.loads() for string-to-dict and json.dumps(obj, indent=2) for dict-to-string.</details>

<details><summary>✅ Answer</summary>

```python
import json

# Parse JSON string → Python dict
raw = '{"name": "Alice", "score": 95, "tags": ["ai", "ml"]}'
data = json.loads(raw)          # ← string to dict
print(data["name"])             # Alice
print(data["tags"])             # ['ai', 'ml']

# Python dict → formatted JSON string
obj = {"model": "gpt-4", "temperature": 0.7, "tokens": 1024}
formatted = json.dumps(obj, indent=2)   # ← dict to string
print(formatted)
# {
#   "model": "gpt-4",
#   "temperature": 0.7,
#   "tokens": 1024
# }
```

**Why:** `json.loads` decodes a string; `json.dumps` encodes to a string. The `indent` argument makes the output human-readable.
</details>

---

<a id="q2"></a>

### Q2 · JSON — Nested JSON + pd.json_normalize 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


You have a list of records where each record contains a nested `metrics` dict. Flatten it into a DataFrame so that `metrics.accuracy` and `metrics.f1` become separate columns.


<details><summary>💡 Hint</summary>Use pd.json_normalize(records, sep=".") — the sep argument controls how nested keys are joined.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

records = [
    {"name": "Alice", "metrics": {"accuracy": 0.95, "f1": 0.93}},
    {"name": "Bob",   "metrics": {"accuracy": 0.88, "f1": 0.87}},
]

df = pd.json_normalize(records, sep=".")
# Columns: name, metrics.accuracy, metrics.f1
print(df.columns.tolist())      # ['name', 'metrics.accuracy', 'metrics.f1']
print(df)
```

**Why:** `pd.DataFrame(records)` would create a `metrics` column containing raw dicts — useless for analysis. `json_normalize` recurses into nested dicts and creates flat column names.
</details>

---

<a id="q3"></a>

### Q3 · JSON — json.JSONDecodeError handling 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Write a function `safe_parse(text)` that returns a Python object if the input is valid JSON, or `None` if it is not — without crashing the program.


<details><summary>💡 Hint</summary>Catch json.JSONDecodeError (which is a subclass of ValueError) inside a try/except block.</details>

<details><summary>✅ Answer</summary>

```python
import json

def safe_parse(text):
    try:
        return json.loads(text)         # ← attempt decode
    except json.JSONDecodeError:        # ← invalid JSON
        return None

print(safe_parse('{"key": 1}'))     # {'key': 1}
print(safe_parse("not json {{}"))   # None
print(safe_parse("42"))             # 42   ← valid JSON (bare number)
```

**Why:** `json.JSONDecodeError` is raised for malformed JSON. Catching it gracefully lets your pipeline continue when one record is corrupt.
</details>

---

<a id="q4"></a>

### Q4 · JSON — json.dump to file + json.load 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Write a config dict to a file called `config.json` using `json.dump`, then read it back with `json.load` and verify the round-trip.


<details><summary>💡 Hint</summary>Open the file in write mode ("w") for dump and read mode ("r") for load. Pass the file object, not the filename.</details>

<details><summary>✅ Answer</summary>

```python
import json

config = {"host": "localhost", "port": 5432, "debug": True}

# Write to file
with open("/tmp/config.json", "w") as f:
    json.dump(config, f, indent=2)      # ← file object, not filename

# Read back
with open("/tmp/config.json") as f:
    loaded = json.load(f)               # ← file object, not filename

assert loaded == config
print(loaded["host"])   # localhost
```

**Why:** `json.dump`/`json.load` work with file objects; `json.dumps`/`json.loads` work with strings. Mixing them up is a very common mistake.
</details>

---

<a id="q5"></a>

### Q5 · CSV — csv.reader basics 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Use `csv.reader` (not pandas) to read a CSV string and print each row as a list. The CSV has a header row.


<details><summary>💡 Hint</summary>Wrap the string in io.StringIO so csv.reader can iterate over it line by line.</details>

<details><summary>✅ Answer</summary>

```python
import csv, io

csv_text = "name,age,role\nAlice,25,Engineer\nBob,30,Manager"

reader = csv.reader(io.StringIO(csv_text))  # ← wrap string in StringIO
header = next(reader)                        # ← consume header
print("Header:", header)                     # ['name', 'age', 'role']

for row in reader:
    print(row)                               # ['Alice', '25', 'Engineer']
```

**Why:** `csv.reader` expects a file-like object that yields lines. `io.StringIO` turns a string into one. Every value comes out as a string — you must cast types yourself.
</details>

---

<a id="q6"></a>

### Q6 · CSV — csv.DictReader row access 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Use `csv.DictReader` to read the same CSV and access each row by column name instead of index.


<details><summary>💡 Hint</summary>DictReader uses the first row as keys automatically. Each row is an OrderedDict (Python 3.8+ just a dict).</details>

<details><summary>✅ Answer</summary>

```python
import csv, io

csv_text = "name,age,role\nAlice,25,Engineer\nBob,30,Manager"

reader = csv.DictReader(io.StringIO(csv_text))
for row in reader:
    print(f"{row['name']} is a {row['role']}, age {row['age']}")
# Alice is a Engineer, age 25
# Bob is a Manager, age 30
```

**Why:** `DictReader` maps each row to a dict using the header as keys — much cleaner than using column index numbers when the CSV has many columns.
</details>

---

<a id="q7"></a>

### Q7 · CSV — csv.writer output 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Write a list of employee records to a CSV file using `csv.writer`. Include a header row. Then verify the file content.


<details><summary>💡 Hint</summary>Always open the file with newline="" on Windows/Mac to prevent double newlines. Use writerow() for one row and writerows() for many.</details>

<details><summary>✅ Answer</summary>

```python
import csv, io

rows = [["Alice", 25, "Engineer"], ["Bob", 30, "Manager"]]

buffer = io.StringIO()
writer = csv.writer(buffer)
writer.writerow(["name", "age", "role"])    # ← header
writer.writerows(rows)                       # ← all data rows

print(buffer.getvalue())
# name,age,role
# Alice,25,Engineer
# Bob,30,Manager
```

**Why:** Use `newline=""` when opening real files with `csv.writer` — without it Python adds an extra blank line on Windows. `writerows()` is more efficient than looping `writerow()`.
</details>

---

<a id="q8"></a>

### Q8 · CSV — Dialect and delimiter handling 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Read a tab-separated values (TSV) file using pandas. Then register a custom CSV dialect with `csv.register_dialect` that uses semicolons as the delimiter.


<details><summary>💡 Hint</summary>pandas: use sep="\t". For custom dialect: csv.register_dialect("myformat", delimiter=";").</details>

<details><summary>✅ Answer</summary>

```python
import csv, io, pandas as pd

# pandas TSV read
tsv = "name\tage\nAlice\t25\nBob\t30"
df = pd.read_csv(io.StringIO(tsv), sep="\t")    # ← tab separator
print(df)

# Custom dialect with semicolon
csv.register_dialect("semicolon", delimiter=";", quoting=csv.QUOTE_MINIMAL)
data = "Alice;25;Engineer\nBob;30;Manager"
reader = csv.reader(io.StringIO(data), dialect="semicolon")
for row in reader:
    print(row)  # ['Alice', '25', 'Engineer']
```

**Why:** Different regions (especially Europe) use semicolons instead of commas to avoid conflicts with decimal numbers. Registering a dialect avoids repeating delimiter settings across many file reads.
</details>

---

<a id="q9"></a>

### Q9 · Excel — openpyxl read cells 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Use `openpyxl` to open a workbook and read a specific cell value, a full row, and iterate over all rows in a sheet.


<details><summary>💡 Hint</summary>ws["B2"].value reads a cell. ws[3] returns all cells in row 3. ws.iter_rows() iterates over row tuples.</details>

<details><summary>✅ Answer</summary>

```python
from openpyxl import Workbook, load_workbook

# Create a workbook to test with
wb = Workbook()
ws = wb.active
ws.append(["name", "score"])    # row 1 header
ws.append(["Alice", 95])        # row 2
ws.append(["Bob", 87])          # row 3
wb.save("/tmp/test.xlsx")

# Read it back
wb2 = load_workbook("/tmp/test.xlsx")
ws2 = wb2.active

# Single cell
print(ws2["A2"].value)              # Alice

# Entire row 1 (header)
header = [cell.value for cell in ws2[1]]
print(header)                       # ['name', 'score']

# All rows
for row in ws2.iter_rows(values_only=True):
    print(row)                      # ('name', 'score'), ('Alice', 95), ...
```

**Why:** `load_workbook` keeps all Excel formatting intact. `values_only=True` in `iter_rows` returns plain values instead of Cell objects — much faster for large sheets.
</details>

---

<a id="q10"></a>

### Q10 · Excel — openpyxl write and style cells 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Write a header cell to an Excel sheet, make it bold size-14, and fill the cell background yellow. Save the workbook.


<details><summary>💡 Hint</summary>Import Font and PatternFill from openpyxl.styles. Apply them via ws["A1"].font and ws["A1"].fill.</details>

<details><summary>✅ Answer</summary>

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

wb = Workbook()
ws = wb.active

ws["A1"] = "Quarterly Report"

# Bold + size 14
ws["A1"].font = Font(bold=True, size=14)

# Yellow background
ws["A1"].fill = PatternFill(fgColor="FFFF00", fill_type="solid")

wb.save("/tmp/styled.xlsx")
print("Saved styled.xlsx")
```

**Why:** `openpyxl.styles` gives you full control over fonts, fills, borders, and alignment — pandas `to_excel` can write data but cannot apply rich formatting like color fills.
</details>

---

<a id="q11"></a>

### Q11 · Excel — pandas read_excel with sheet_name 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Read a specific sheet by name from an Excel file using pandas. Then read ALL sheets at once as a dict of DataFrames.


<details><summary>💡 Hint</summary>sheet_name="Sales" reads one sheet; sheet_name=None reads all sheets and returns a dict keyed by sheet name.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd
from openpyxl import Workbook

# Create a test workbook with two sheets
wb = Workbook()
ws1 = wb.active
ws1.title = "Sales"
ws1.append(["product", "revenue"])
ws1.append(["Laptop", 1000])

ws2 = wb.create_sheet("Costs")
ws2.append(["item", "cost"])
ws2.append(["Server", 500])
wb.save("/tmp/multi.xlsx")

# Read one specific sheet
df_sales = pd.read_excel("/tmp/multi.xlsx", sheet_name="Sales")
print(df_sales)

# Read ALL sheets → dict of DataFrames
all_sheets = pd.read_excel("/tmp/multi.xlsx", sheet_name=None)
for name, df in all_sheets.items():
    print(f"{name}: {df.shape}")    # Sales: (1, 2), Costs: (1, 2)
```

**Why:** `sheet_name=None` is the fastest way to ingest a multi-sheet workbook — no need to know sheet names in advance.
</details>

---

<a id="q12"></a>

### Q12 · Excel — pandas ExcelWriter multiple sheets 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Write two DataFrames to separate sheets in the same Excel file using `pd.ExcelWriter`.


<details><summary>💡 Hint</summary>Use pd.ExcelWriter as a context manager with engine="openpyxl". Call df.to_excel(writer, sheet_name=...) for each DataFrame.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

df_sales = pd.DataFrame({"product": ["Laptop", "Mouse"], "revenue": [999, 29]})
df_costs = pd.DataFrame({"item": ["Hosting", "Support"], "cost": [500, 200]})

with pd.ExcelWriter("/tmp/report.xlsx", engine="openpyxl") as writer:
    df_sales.to_excel(writer, sheet_name="Sales", index=False)
    df_costs.to_excel(writer, sheet_name="Costs", index=False)

print("Written: Sales + Costs sheets")
```

**Why:** The context manager flushes and saves when the `with` block exits. Without it you must call `writer.save()` manually — and risk a partially written file on error.
</details>

---

<a id="q13"></a>

### Q13 · PDF — pdfplumber text extraction 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Use `pdfplumber` to open a PDF and extract all text from every page, concatenating page text with newlines between pages.


<details><summary>💡 Hint</summary>Use pdfplumber.open() as a context manager. page.extract_text() returns None for blank/image pages — guard with "if text".</details>

<details><summary>✅ Answer</summary>

```python
import pdfplumber

def extract_all_text(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        for page in pdf.pages:
            text = page.extract_text()      # ← returns None if no text layer
            if text:                         # ← guard against blank/image pages
                full_text += text + "\n"
    return full_text

# text = extract_all_text("report.pdf")
# print(text[:500])
```

**Why:** `pdfplumber` works best on native digital PDFs (text layer present). Always guard `extract_text()` with `if text` — scanned PDFs have no text layer and return `None`.
</details>

---

<a id="q14"></a>

### Q14 · PDF — pypdf page count 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


Use `pypdf` to open a PDF and print the total number of pages. Show how to access the text of the first page.


<details><summary>💡 Hint</summary>pypdf uses PdfReader. len(reader.pages) gives the page count. reader.pages[0].extract_text() gets the first page's text.</details>

<details><summary>✅ Answer</summary>

```python
from pypdf import PdfReader

def inspect_pdf(path):
    reader = PdfReader(path)
    page_count = len(reader.pages)          # ← total pages
    print(f"Pages: {page_count}")

    first_page_text = reader.pages[0].extract_text()
    print(f"First page preview:\n{first_page_text[:200]}")

# inspect_pdf("report.pdf")
```

**Why:** `pypdf` is lightweight and good for metadata and simple text extraction. For tables and complex layouts, switch to `pdfplumber` — it uses coordinate-aware parsing, which pypdf skips.
</details>

---

<a id="q15"></a>

### Q15 · PDF — pdfplumber table extraction 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


Use `pdfplumber` to extract the first table from the first page of a PDF and convert it into a pandas DataFrame.


<details><summary>💡 Hint</summary>page.extract_tables() returns a list of tables. Each table is a list of rows; each row is a list of cell strings. Use table[0] as the header and table[1:] as data rows.</details>

<details><summary>✅ Answer</summary>

```python
import pdfplumber
import pandas as pd

def extract_first_table(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()      # ← list of tables on this page
        if not tables:
            print("No tables found on page 1")
            return None
        first_table = tables[0]             # ← take the first table
        df = pd.DataFrame(
            first_table[1:],                # ← data rows (skip header)
            columns=first_table[0]          # ← first row = column names
        )
    return df

# df = extract_first_table("report.pdf")
# print(df)
```

**Why:** `extract_tables()` uses visual coordinate analysis to detect table boundaries — far more reliable than splitting raw text by whitespace. The output is a list-of-lists that maps cleanly to a DataFrame.
</details>

---

<a id="q16"></a>

### Q16 · PDF — Scanned PDF — what to do 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


Explain (in code comments) what happens when you call `pdfplumber.page.extract_text()` on a scanned PDF and what the correct approach is.


<details><summary>💡 Hint</summary>Scanned PDFs are images. No text layer = extract_text() returns None. You need OCR (pytesseract or a cloud service).</details>

<details><summary>✅ Answer</summary>

```python
import pdfplumber

# Scanned PDFs are photos of pages — they contain NO text layer.
# pdfplumber.extract_text() returns None because there is no text to extract.

# WRONG approach for scanned PDFs:
# with pdfplumber.open("scanned.pdf") as pdf:
#     text = pdf.pages[0].extract_text()   # → None, not an error

# CORRECT approach — OCR pipeline:
# 1. Convert PDF page to image (pdf2image library or PyMuPDF)
# 2. Run OCR on the image (pytesseract)
#
# import pytesseract
# from pdf2image import convert_from_path
# images = convert_from_path("scanned.pdf")
# for image in images:
#     text = pytesseract.image_to_string(image)
#     print(text)

# For production: AWS Textract or Google Document AI handle
# layout-aware OCR with table detection — far more accurate than tesseract.
print("Scanned PDFs require OCR — pdfplumber alone is not enough.")
```

**Why:** The single biggest PDF mistake is assuming all PDFs have a text layer. Always check `if page.extract_text()` returns something before processing — if it returns `None`, you have a scanned document.
</details>

---

<a id="q17"></a>

### Q17 · XML — ElementTree parse from string 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


Parse an XML string using `xml.etree.ElementTree` and print the root tag and all direct child tag names.


<details><summary>💡 Hint</summary>Use ET.fromstring(xml_string) for a string. root.tag gives the tag name. Iterate root directly to get direct children.</details>

<details><summary>✅ Answer</summary>

```python
import xml.etree.ElementTree as ET

xml_str = """
<catalog>
    <product id="001"><name>Laptop</name><price>999</price></product>
    <product id="002"><name>Mouse</name><price>29</price></product>
</catalog>
"""

root = ET.fromstring(xml_str)           # ← parse string to Element
print(f"Root tag: {root.tag}")          # catalog

for child in root:                      # ← direct children
    print(f"  Child: {child.tag}, id={child.get('id')}")
# Child: product, id=001
# Child: product, id=002
```

**Why:** `ET.fromstring` returns the root Element directly. For files, use `ET.parse("file.xml").getroot()`. Iterating the root only visits immediate children — not all descendants.
</details>

---

<a id="q18"></a>

### Q18 · XML — find / findall element navigation 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Given an XML catalog, use `findall` to get all products, then use `findtext` to get the name and `find().get()` to read an attribute from a child element.


<details><summary>💡 Hint</summary>product.findtext("name") reads element text. product.find("price").get("currency") reads an attribute of a child element.</details>

<details><summary>✅ Answer</summary>

```python
import xml.etree.ElementTree as ET

xml_str = """
<catalog>
    <product id="001">
        <name>Laptop Pro</name>
        <price currency="USD">999.99</price>
    </product>
    <product id="002">
        <name>Wireless Mouse</name>
        <price currency="USD">29.99</price>
    </product>
</catalog>
"""

root = ET.fromstring(xml_str)

for product in root.findall("product"):         # ← all <product> children
    prod_id  = product.get("id")                # ← attribute on <product>
    name     = product.findtext("name")         # ← text of <name> child
    price    = product.findtext("price")        # ← text of <price> child
    currency = product.find("price").get("currency")  # ← attribute on child
    print(f"{prod_id}: {name} = {currency} {price}")
```

**Why:** `findtext` is a shortcut for `find().text`. `get("attr")` reads XML attributes — not the same as element text. Confusing these two is the most common XML mistake.
</details>

---

<a id="q19"></a>

### Q19 · XML — XPath attribute filter 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


Use XPath inside `findall` to select only `<price>` elements where the `currency` attribute equals `"USD"`. Then use a more complex path to find all items inside orders.


<details><summary>💡 Hint</summary>XPath filter syntax: ".//element[@attr='value']". The "./" prefix means "anywhere in the tree".</details>

<details><summary>✅ Answer</summary>

```python
import xml.etree.ElementTree as ET

xml_str = """
<orders>
    <order id="O1">
        <item sku="A1" qty="2"><price currency="USD">99.99</price></item>
        <item sku="B1" qty="1"><price currency="EUR">49.99</price></item>
    </order>
    <order id="O2">
        <item sku="C1" qty="3"><price currency="USD">19.99</price></item>
    </order>
</orders>
"""

root = ET.fromstring(xml_str)

# All <price> elements with currency="USD" anywhere in the tree
usd_prices = root.findall(".//price[@currency='USD']")
for p in usd_prices:
    print(f"USD price: {p.text}")   # 99.99, 19.99

# All <item> elements inside any <order>
all_items = root.findall(".//order/item")
for item in all_items:
    print(f"SKU: {item.get('sku')}, qty: {item.get('qty')}")
```

**Why:** The `.//<tag>` prefix means "search all descendants" — without the `./` it only searches direct children. Attribute filters `[@attr='val']` avoid manual Python filtering in a loop.
</details>

---

<a id="q20"></a>

### Q20 · XML — Write XML with ElementTree 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


Build an XML document programmatically using `ElementTree`, add elements and attributes, then serialize it to a string and write it to a file.


<details><summary>💡 Hint</summary>Use ET.Element() for the root, ET.SubElement(parent, tag) for children. ET.tostring(root, encoding="unicode") converts to string. ET.indent() adds pretty-printing (Python 3.9+).</details>

<details><summary>✅ Answer</summary>

```python
import xml.etree.ElementTree as ET

# Build root
root = ET.Element("catalog")               # ← root element

# Add first product
p1 = ET.SubElement(root, "product")
p1.set("id", "001")                        # ← set attribute
name1 = ET.SubElement(p1, "name")
name1.text = "Laptop Pro"                  # ← set text content
price1 = ET.SubElement(p1, "price")
price1.set("currency", "USD")
price1.text = "999.99"

# Add second product
p2 = ET.SubElement(root, "product")
p2.set("id", "002")
ET.SubElement(p2, "name").text = "Mouse"
ET.SubElement(p2, "price").text = "29.99"

# Pretty-print and serialize
ET.indent(root, space="  ")                # ← Python 3.9+
xml_string = ET.tostring(root, encoding="unicode", xml_declaration=False)
print(xml_string)

tree = ET.ElementTree(root)
tree.write("/tmp/catalog.xml", encoding="unicode", xml_declaration=True)
```

**Why:** `ET.SubElement(parent, tag)` is cleaner than manually appending children. `ET.indent()` adds whitespace for human-readable output — without it everything is on one line.
</details>

---

<a id="q21"></a>

### Q21 · High-Performance — Parquet read/write with pandas 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


Write a DataFrame to a Parquet file with snappy compression, then read it back reading only specific columns.


<details><summary>💡 Hint</summary>df.to_parquet("file.parquet", compression="snappy", index=False). pd.read_parquet("file.parquet", columns=["col1"]) reads only the requested columns from disk.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "name":    ["Alice", "Bob", "Carol"],
    "score":   [95, 87, 92],
    "dept":    ["eng", "sales", "eng"],
    "salary":  [120000, 95000, 130000],
})

# Write with compression
df.to_parquet("/tmp/employees.parquet", compression="snappy", index=False)

# Read only specific columns — only those columns are read from disk
df_partial = pd.read_parquet("/tmp/employees.parquet", columns=["name", "score"])
print(df_partial)
# name  score
# Alice    95
# Bob      87
# Carol    92
```

**Why:** Parquet is columnar — `columns=["name", "score"]` reads ONLY those two columns off disk, skipping `dept` and `salary` entirely. With CSV you'd read the whole file then discard columns.
</details>

---

<a id="q22"></a>

### Q22 · High-Performance — Feather vs Parquet use cases 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


Show the feather read/write API with pandas. Explain in comments when you would choose feather over parquet.


<details><summary>💡 Hint</summary>df.to_feather() / pd.read_feather(). Feather is faster for in-process handoffs (Python to R or Python to Python); Parquet is better for long-term storage and cross-system portability.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({"x": range(1000), "y": [i * 2.5 for i in range(1000)]})

# Feather write/read
df.to_feather("/tmp/data.feather")
df2 = pd.read_feather("/tmp/data.feather")
print(df2.shape)    # (1000, 2)

# When to use feather vs parquet:
# FEATHER:
#   - Fastest possible read/write speed (minimal serialization overhead)
#   - Temporary in-process data handoff (Python → Python, Python → R)
#   - NOT compressed by default — file size is larger than parquet
#   - NOT suitable for long-term storage or cross-system exchange

# PARQUET:
#   - Compressed storage (snappy, gzip, zstd)
#   - Long-term archival, S3 data lakes, Spark/Hive compatibility
#   - Column pruning on read — only fetch needed columns
#   - Preferred for production data pipelines
```

**Why:** Feather skips compression for speed — it is an Apache Arrow IPC format designed for fast in-memory exchange. Parquet adds columnar compression and broad ecosystem support at the cost of slightly higher write/read overhead.
</details>

---

<a id="q23"></a>

### Q23 · High-Performance — HDF5 key store with pandas 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Write two DataFrames to different keys in the same HDF5 file using `pd.HDFStore`, then list all keys and read one back.


<details><summary>💡 Hint</summary>Use pd.HDFStore("file.h5") as a context manager. store["/key"] = df writes; store.keys() lists; store["/key"] reads.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

df_sales = pd.DataFrame({"product": ["Laptop", "Mouse"], "revenue": [999, 29]})
df_users = pd.DataFrame({"user": ["Alice", "Bob"], "age": [25, 30]})

# Write multiple DataFrames to one file under different keys
with pd.HDFStore("/tmp/data.h5", mode="w") as store:
    store["/sales"] = df_sales      # ← key like a file path
    store["/users"] = df_users

# Read back
with pd.HDFStore("/tmp/data.h5", mode="r") as store:
    print("Keys:", store.keys())    # ['/sales', '/users']
    df_read = store["/sales"]
    print(df_read)
```

**Why:** HDF5 acts like a filesystem within a file — one `.h5` file can hold many named datasets at different keys. Useful for storing model checkpoints, simulation results, or related tables together without a database.
</details>

---

<a id="q24"></a>

### Q24 · High-Performance — CSV vs Parquet file size comparison 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


Write the same 10,000-row DataFrame to CSV and Parquet, then compare their file sizes in bytes. Explain why the sizes differ.


<details><summary>💡 Hint</summary>Use os.path.getsize() to check file sizes. Parquet uses column-level compression; CSV stores everything as plain text with no compression.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd
import os
import random
import string

# Generate a realistic 10,000-row dataset
random.seed(42)
df = pd.DataFrame({
    "id":       range(10_000),
    "name":     ["Alice" if i % 2 == 0 else "Bob" for i in range(10_000)],
    "category": [random.choice(["A", "B", "C"]) for _ in range(10_000)],
    "score":    [round(random.uniform(60, 100), 2) for _ in range(10_000)],
})

csv_path     = "/tmp/compare.csv"
parquet_path = "/tmp/compare.parquet"

df.to_csv(csv_path, index=False)
df.to_parquet(parquet_path, compression="snappy", index=False)

csv_size     = os.path.getsize(csv_path)
parquet_size = os.path.getsize(parquet_path)

print(f"CSV:     {csv_size:>10,} bytes")
print(f"Parquet: {parquet_size:>10,} bytes")
print(f"Ratio:   {csv_size / parquet_size:.1f}x smaller as parquet")

# Expected: CSV ~400KB, Parquet ~30-80KB → parquet is 5-10x smaller
# Why: Parquet compresses column by column — repeated values like "Alice"/"Bob"
# or "A"/"B"/"C" compress extremely well with dictionary + RLE encoding.
# CSV stores every "Alice" and every "A" as repeated plain text characters.
```

**Why:** Columnar compression shines on low-cardinality columns (few unique values). In a column of 10,000 rows that only contains "A", "B", or "C", Parquet encodes this as a tiny dictionary. CSV writes the full character for every row.
</details>

---

<a id="q25"></a>

### Q25 · High-Performance — Pickle round-trip and security warning 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


Demonstrate pickling and unpickling a Python object. Add comments explaining when pickle is appropriate and when it is dangerous.


<details><summary>💡 Hint</summary>Open in "wb" (write binary) for pickle.dump, "rb" (read binary) for pickle.load. Never unpickle data from untrusted sources.</details>

<details><summary>✅ Answer</summary>

```python
import pickle

# Any Python object — including custom classes, sklearn models, etc.
model_state = {
    "weights": [0.1, 0.3, 0.7],
    "bias": 0.05,
    "n_features": 3,
    "label_map": {0: "cat", 1: "dog"},
}

# Save
with open("/tmp/model.pkl", "wb") as f:     # ← "wb" = write binary
    pickle.dump(model_state, f)

# Load
with open("/tmp/model.pkl", "rb") as f:     # ← "rb" = read binary
    loaded = pickle.load(f)

assert loaded == model_state
print("Round-trip OK:", loaded["label_map"])

# WHEN TO USE PICKLE:
#   - Saving trained sklearn/PyTorch models for reuse in the SAME Python env
#   - Short-term caching of Python objects between sessions
#   - Objects that cannot be serialized to JSON (custom classes, numpy arrays)

# WHEN NOT TO USE PICKLE:
#   - NEVER unpickle data from untrusted sources — pickle.load executes
#     arbitrary code. A malicious .pkl file can run any system command.
#   - Cross-language exchange → use JSON or Parquet
#   - Long-term storage → pickle format changes between Python versions
```

**Why:** Pickle is Python's native serialization — it can handle any Python object but carries a serious security risk. Unpickling is equivalent to running code — only load `.pkl` files you created yourself.
</details>

---

## 📂 Navigation

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
