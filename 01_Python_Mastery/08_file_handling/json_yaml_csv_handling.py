"""
08_file_handling/json_yaml_csv_handling.py
============================================
CONCEPT: Working with structured data formats — JSON, CSV, and YAML.
WHY THIS MATTERS: These three formats are the most common ways data moves
between systems. API responses (JSON), datasets (CSV), config files (YAML) —
every Python developer works with all three constantly.

Prerequisite: Modules 01–08 file_operations.py
"""

import json
import csv
import io
import tempfile
from pathlib import Path
from datetime import datetime, date
from dataclasses import dataclass, asdict
from typing import Any

# =============================================================================
# SECTION 1: JSON — the universal API exchange format
# =============================================================================

# CONCEPT: json.dumps converts Python objects → JSON string.
#          json.loads converts JSON string → Python objects.
#          json.dump/load work with file objects.
# Mapping: dict↔object, list↔array, str↔string, int/float↔number,
#          bool↔true/false, None↔null

print("=== Section 1: JSON ===")

# Basic serialization
data = {
    "user": {"id": 42, "name": "Alice", "active": True},
    "scores": [95, 87, 92, 88],
    "metadata": None,
    "ratio": 0.95,
}

json_str = json.dumps(data)
print(f"Compact: {json_str[:60]}...")

# Pretty printing (for config files, debug output, human-readable storage)
pretty = json.dumps(data, indent=2, sort_keys=True)
print(f"\nPretty:\n{pretty}")

# Parsing back
parsed = json.loads(json_str)
print(f"\nParsed user: {parsed['user']}")
print(f"Scores: {parsed['scores']}")

# File-based JSON (most common in production)
tmp = Path(tempfile.mkdtemp())
json_file = tmp / "data.json"

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

with open(json_file, "r", encoding="utf-8") as f:
    loaded = json.load(f)

print(f"\nFrom file: {loaded['user']['name']}")

# pathlib shortcut (small files)
json_file.write_text(json.dumps(data, indent=2))
loaded2 = json.loads(json_file.read_text())
print(f"Via pathlib: {loaded2['user']['active']}")


# =============================================================================
# SECTION 2: Custom JSON serialization — dates, decimals, dataclasses
# =============================================================================

# CONCEPT: json.dumps only handles Python's basic types. For dates, Decimals,
# custom objects — you need a custom encoder (subclass JSONEncoder or pass
# a `default` function).

print("\n=== Section 2: Custom JSON Serialization ===")

from decimal import Decimal

@dataclass
class Order:
    order_id: str
    amount: Decimal
    created_at: datetime
    tags: set   # sets aren't JSON serializable

def json_default(obj: Any) -> Any:
    """
    Fallback serializer for types json.dumps doesn't know.
    Called when obj is not serializable by default.
    Return a JSON-serializable object.
    """
    if isinstance(obj, Decimal):
        return float(obj)        # Decimal → float (watch precision!)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()   # datetime → ISO 8601 string
    if isinstance(obj, set):
        return sorted(list(obj))  # set → sorted list (deterministic)
    if hasattr(obj, "__dict__"):
        return obj.__dict__       # arbitrary objects → their dict
    raise TypeError(f"Not serializable: {type(obj)}")

order = Order(
    order_id="ORD-001",
    amount=Decimal("99.99"),
    created_at=datetime(2024, 1, 15, 10, 30, 0),
    tags={"premium", "express", "gift"},
)

# Use default= to handle non-standard types
json_order = json.dumps(asdict(order) | {"tags": order.tags}, default=json_default, indent=2)
print(f"Custom serialized order:\n{json_order}")

# Custom deserialization — convert ISO strings back to datetime
def parse_order_from_json(json_str: str) -> dict:
    def object_hook(d: dict) -> dict:
        """Called for every JSON object — can transform values on parse."""
        if "created_at" in d and isinstance(d["created_at"], str):
            d["created_at"] = datetime.fromisoformat(d["created_at"])
        if "amount" in d and isinstance(d["amount"], float):
            d["amount"] = Decimal(str(d["amount"]))
        return d
    return json.loads(json_str, object_pairs_hook=lambda pairs: object_hook(dict(pairs)))

round_tripped = parse_order_from_json(json_order)
print(f"\nRound-tripped amount: {round_tripped['amount']} (type: {type(round_tripped['amount']).__name__})")
print(f"Round-tripped datetime: {round_tripped['created_at']}")


# =============================================================================
# SECTION 3: CSV — tabular data exchange
# =============================================================================

# CONCEPT: csv module handles the tricky parts: quoting fields with commas,
# escaped quotes, different delimiters. NEVER manually split CSV on commas.
# Always use the csv module.

print("\n=== Section 3: CSV Reading and Writing ===")

# Sample data
employees = [
    {"id": 1, "name": "Alice Smith",   "department": "Engineering", "salary": 95000},
    {"id": 2, "name": "Bob O'Brien",   "department": "Marketing",   "salary": 75000},
    {"id": 3, "name": "Carol, Lee",    "department": "Engineering", "salary": 102000},
    {"id": 4, "name": "Diana \"Dee\"", "department": "Sales",       "salary": 80000},
]

csv_file = tmp / "employees.csv"

# Writing CSV (DictWriter writes dicts as rows)
fieldnames = ["id", "name", "department", "salary"]
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    # newline="" is required for csv module on all platforms!
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()   # write the header row
    writer.writerows(employees)

print(f"CSV content:\n{csv_file.read_text()}")

# Reading CSV (DictReader gives each row as a dict)
with open(csv_file, "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)   # convert iterator to list

print(f"Read {len(rows)} rows")
for row in rows:
    print(f"  {row['name']:20} | {row['department']:12} | ${int(row['salary']):,}")

# Reading with different delimiter (tab-separated values)
tsv_data = "name\tvalue\tstatus\nAlice\t100\tactive\nBob\t200\tinactive\n"
reader = csv.DictReader(io.StringIO(tsv_data), delimiter="\t")
tsv_rows = list(reader)
print(f"\nTSV rows: {[r['name'] for r in tsv_rows]}")


# =============================================================================
# SECTION 4: CSV data processing patterns
# =============================================================================

# CONCEPT: Common real-world CSV patterns: filtering, aggregating,
# type conversion (CSV is all strings!), handling missing values.

print("\n=== Section 4: CSV Processing ===")

# Generate a larger dataset
sales_csv = tmp / "sales.csv"
with open(sales_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "product", "quantity", "unit_price", "region"])
    for i in range(50):
        writer.writerow([
            f"2024-01-{(i%28)+1:02d}",
            ["Widget", "Gadget", "Doohickey"][i % 3],
            str((i % 10) + 1),
            str(round(9.99 + (i % 5) * 10, 2)),
            ["North", "South", "East", "West"][i % 4],
        ])

# Aggregate: total revenue by product
product_revenue = {}
with open(sales_csv, "r", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # CSV is ALL STRINGS — convert numeric fields explicitly
        product  = row["product"]
        quantity = int(row["quantity"])         # string → int
        price    = float(row["unit_price"])     # string → float
        revenue  = quantity * price

        if product not in product_revenue:
            product_revenue[product] = 0.0
        product_revenue[product] += revenue

print("Revenue by product:")
for product, revenue in sorted(product_revenue.items()):
    print(f"  {product:12}: ${revenue:,.2f}")


# =============================================================================
# SECTION 5: YAML — human-readable configuration
# =============================================================================

# CONCEPT: YAML (Yet Another Markup Language) is used for config files
# because it's very human-readable and supports comments (unlike JSON).
# Common in: Kubernetes, Docker Compose, CI/CD (GitHub Actions), Ansible.
# Python's yaml module (PyYAML) handles YAML. pyyaml must be installed.

print("\n=== Section 5: YAML ===")

try:
    import yaml

    # YAML config example
    config_yaml = """
# Application configuration
app:
  name: MyAPI
  version: 2.1.0
  debug: false

database:
  host: localhost
  port: 5432
  name: production_db
  pool_size: 10
  ssl: true

logging:
  level: INFO
  handlers:
    - console
    - file
  file_path: /var/log/myapp.log

feature_flags:
  new_dashboard: true
  beta_api: false
  max_users_per_batch: 1000
"""

    # Parse YAML → Python dict
    config = yaml.safe_load(config_yaml)   # ALWAYS use safe_load, not load!
    # WHY safe_load: yaml.load() can execute arbitrary Python — a security risk!

    print(f"App name: {config['app']['name']}")
    print(f"DB host:  {config['database']['host']}")
    print(f"Log level: {config['logging']['level']}")
    print(f"Handlers: {config['logging']['handlers']}")
    print(f"Feature flags: {config['feature_flags']}")

    # Serialize Python → YAML
    output_config = {
        "database": {"host": "prod-db.internal", "port": 5432},
        "workers": 4,
        "timeout": 30.5,
        "features": ["feature_a", "feature_b"],
    }
    yaml_str = yaml.dump(output_config, default_flow_style=False, sort_keys=True)
    print(f"\nSerialized YAML:\n{yaml_str}")

    # YAML file operations
    yaml_file = tmp / "config.yaml"
    with open(yaml_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    with open(yaml_file, "r") as f:
        reloaded = yaml.safe_load(f)
    print(f"Round-tripped app name: {reloaded['app']['name']}")

except ImportError:
    print("  PyYAML not installed. Install with: pip install pyyaml")
    print("  Showing YAML structure conceptually...")

    yaml_explanation = """
  YAML vs JSON comparison:
  JSON:  {"key": "value", "list": [1, 2, 3]}
  YAML:  key: value
         list:
           - 1
           - 2
           - 3

  YAML advantages: comments, no quotes for strings, cleaner syntax
  JSON advantages: strict, universally supported, no ambiguity
  Use YAML for: config files, CI/CD pipelines
  Use JSON for: API requests/responses, data storage
"""
    print(yaml_explanation)


# =============================================================================
# SECTION 6: Format comparison and selection guide
# =============================================================================

print("\n=== Section 6: Format Selection Guide ===")

comparison = """
┌─────────────────────────────────────────────────────────────────┐
│ Format Comparison                                               │
├──────────┬──────────────┬─────────────┬────────────────────────┤
│          │ JSON         │ CSV         │ YAML                   │
├──────────┼──────────────┼─────────────┼────────────────────────┤
│ Use for  │ APIs, nested │ Tabular     │ Config files           │
│          │ data, web    │ datasets,   │ Infrastructure as Code │
│          │              │ exports     │                        │
├──────────┼──────────────┼─────────────┼────────────────────────┤
│ Comments │ No           │ No          │ Yes                    │
├──────────┼──────────────┼─────────────┼────────────────────────┤
│ Nested   │ Yes          │ No (flat)   │ Yes                    │
│ data     │              │             │                        │
├──────────┼──────────────┼─────────────┼────────────────────────┤
│ Human    │ Moderate     │ Good        │ Excellent              │
│ readable │              │             │                        │
├──────────┼──────────────┼─────────────┼────────────────────────┤
│ stdlib   │ Yes (json)   │ Yes (csv)   │ No (pyyaml)            │
└──────────┴──────────────┴─────────────┴────────────────────────┘
"""
print(comparison)

print("Common pitfalls:")
print("  JSON: datetime/Decimal not serializable → use custom encoder")
print("  CSV:  all values are strings → always convert types on read")
print("  CSV:  commas in values → ALWAYS use csv module, not str.split(',')")
print("  YAML: yaml.load() has code execution risk → ALWAYS use yaml.safe_load()")
