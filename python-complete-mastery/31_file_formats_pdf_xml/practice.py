"""
File Formats — Practice Problems
"""

import json
import csv
import xml.etree.ElementTree as ET
import pandas as pd
import io
import os


# ─────────────────────────────────────────────
# PROBLEM 1: JSON Parsing
# ─────────────────────────────────────────────
print("PROBLEM 1: JSON Parsing")

api_response = """
{
    "status": "success",
    "total": 3,
    "results": [
        {"id": 1, "name": "Alice", "score": 95, "metadata": {"level": "senior", "dept": "eng"}},
        {"id": 2, "name": "Bob",   "score": 87, "metadata": {"level": "mid",    "dept": "sales"}},
        {"id": 3, "name": "Carol", "score": 92, "metadata": {"level": "senior", "dept": "eng"}}
    ]
}
"""

data = json.loads(api_response)
print(f"Status: {data['status']}, Total: {data['total']}")
for r in data["results"]:
    print(f"  {r['name']}: score={r['score']}, dept={r['metadata']['dept']}")

# Flatten nested structure
df = pd.json_normalize(data["results"], sep=".")
print("\nNormalized DataFrame:")
print(df.to_string())


# ─────────────────────────────────────────────
# PROBLEM 2: CSV with edge cases
# ─────────────────────────────────────────────
print("\nPROBLEM 2: CSV Parsing")

# CSV with quoting and commas inside fields
csv_data = """name,price,description
Laptop,"$999.99","High-performance, 16GB RAM"
Mouse,"$29.99",Wireless mouse
Keyboard,"$49.99","Mechanical, RGB"
"""

df = pd.read_csv(io.StringIO(csv_data))
print(df)
print(f"\nData types: {df.dtypes.to_dict()}")

# Clean price column
df["price_num"] = df["price"].str.replace(r"[$,]", "", regex=True).astype(float)
print(f"\nCleaned prices: {df['price_num'].tolist()}")

# Write and re-read
df.to_csv("/tmp/products.csv", index=False)
df2 = pd.read_csv("/tmp/products.csv")
print(f"\nRe-read shape: {df2.shape}")


# ─────────────────────────────────────────────
# PROBLEM 3: XML Parsing
# ─────────────────────────────────────────────
print("\nPROBLEM 3: XML Parsing")

xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<orders>
    <order id="ORD001" date="2024-01-15">
        <customer>Alice</customer>
        <items>
            <item sku="LAP001" qty="1" price="999.99">Laptop Pro</item>
            <item sku="MOU001" qty="2" price="29.99">Wireless Mouse</item>
        </items>
        <total currency="USD">1059.97</total>
    </order>
    <order id="ORD002" date="2024-01-16">
        <customer>Bob</customer>
        <items>
            <item sku="KEY001" qty="1" price="49.99">Keyboard</item>
        </items>
        <total currency="USD">49.99</total>
    </order>
</orders>
"""

root = ET.fromstring(xml_data)

# Extract all orders
rows = []
for order in root.findall("order"):
    order_id = order.get("id")
    date     = order.get("date")
    customer = order.findtext("customer")
    total    = float(order.findtext("total"))
    currency = order.find("total").get("currency")
    n_items  = len(order.findall(".//item"))

    rows.append({
        "order_id": order_id, "date": date, "customer": customer,
        "total": total, "currency": currency, "n_items": n_items
    })

df = pd.DataFrame(rows)
print(df.to_string())
print(f"\nTotal revenue: ${df['total'].sum():.2f}")


# ─────────────────────────────────────────────
# PROBLEM 4: In-memory file operations
# ─────────────────────────────────────────────
print("\nPROBLEM 4: In-memory file operations")

# JSON round-trip
original = {"model": "sklearn", "accuracy": 0.923, "features": ["age", "income", "score"]}
json_bytes = json.dumps(original).encode("utf-8")
loaded = json.loads(json_bytes.decode("utf-8"))
assert loaded == original
print(f"JSON round-trip: {loaded}")

# CSV round-trip with StringIO
df_original = pd.DataFrame({"a": [1,2,3], "b": ["x","y","z"]})
buffer = io.StringIO()
df_original.to_csv(buffer, index=False)
buffer.seek(0)
df_loaded = pd.read_csv(buffer)
assert list(df_loaded.columns) == ["a", "b"]
print(f"CSV StringIO round-trip: shape={df_loaded.shape}")


# ─────────────────────────────────────────────
# PROBLEM 5: Multi-format pipeline
# ─────────────────────────────────────────────
print("\nPROBLEM 5: Multi-format pipeline")

# Simulate: read JSON → process → write CSV → read back → verify
source_data = [
    {"id": 1, "name": "Alice", "scores": {"q1": 88, "q2": 92}},
    {"id": 2, "name": "Bob",   "scores": {"q1": 75, "q2": 81}},
    {"id": 3, "name": "Carol", "scores": {"q1": 95, "q2": 98}},
]

# Step 1: Normalize JSON
df = pd.json_normalize(source_data, sep="_")
print("After normalize:")
print(df)

# Step 2: Compute average
df["avg_score"] = (df["scores_q1"] + df["scores_q2"]) / 2
df["grade"] = pd.cut(df["avg_score"], bins=[0,70,80,90,100], labels=["D","C","B","A"])

# Step 3: Save to CSV
df.to_csv("/tmp/grades.csv", index=False)

# Step 4: Read back
df_check = pd.read_csv("/tmp/grades.csv")
print(f"\nFinal grades:")
print(df_check[["name", "avg_score", "grade"]].to_string())


print("\n✅ File formats practice complete!")
