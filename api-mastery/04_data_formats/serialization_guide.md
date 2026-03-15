# Data Formats & Serialization

## The Language Problem

Your Python backend just built a `Product` object. It has a `price` field holding a
`Decimal("999.99")`. It has a `created_at` field holding a `datetime` object. It has a
`tags` field that is a Python `list`.

Now you need to send this to a JavaScript frontend.

JavaScript doesn't have a `Decimal` type. It doesn't have a Python `datetime`. Its
arrays are not Python lists — they're a different data structure entirely.

So how do you send a Python object over the wire to a JavaScript client? You don't.
You convert it to something both sides agree on first: a **serialized** representation.
Then the other side **deserializes** it back into whatever their language uses.

This is the entire job of data formats. They're the shared vocabulary that lets
different systems talk to each other.

---

## 1. JSON — The Web's Common Language

JSON (JavaScript Object Notation) won. It's not the most efficient format. It's not
the most expressive. But it's readable, universal, and supported by every language and
every HTTP client in existence. It became the de facto standard for web APIs around
2010 and has never looked back.

### The Six JSON Types

JSON has exactly six types. That's it. Six:

```
┌─────────────────────────────────────────────────────┐
│  JSON Type    Example                                │
├─────────────────────────────────────────────────────┤
│  string       "Hello, world"                        │
│  number       42  or  3.14  (no int/float split)    │
│  boolean      true  or  false  (lowercase)          │
│  null         null                                  │
│  array        [1, "two", true, null]                │
│  object       {"key": "value", "n": 42}             │
└─────────────────────────────────────────────────────┘
```

A JSON document is always one of these types at the root. Usually an object or array.

Notice what's missing: dates, integers vs floats, binary data, sets, tuples, bytes.
JSON doesn't know about any of these. This gap between "Python's type system" and
"JSON's type system" is where serialization bugs live.

### What JSON Can't Represent — And The Workarounds

**Dates and datetimes**

JSON has no date type. The most common convention is ISO 8601 strings:

```python
from datetime import datetime, timezone

# Python datetime → JSON string
dt = datetime(2024, 3, 8, 14, 30, 0, tzinfo=timezone.utc)
serialized = dt.isoformat()  # "2024-03-08T14:30:00+00:00"

# Or in UTC with Z suffix (common in APIs)
serialized = dt.strftime("%Y-%m-%dT%H:%M:%SZ")  # "2024-03-08T14:30:00Z"
```

Always include timezone information. A bare `"2024-03-08T14:30:00"` is ambiguous —
is that UTC? Local time? The server's timezone? Use `+00:00` or `Z` for UTC.

**Python Decimal — for money and precise numbers**

JSON numbers are IEEE 754 floating point under the hood. That means:

```python
>>> import json
>>> json.loads("0.1 + 0.2")  # conceptually
# 0.30000000000000004
```

Floating point arithmetic is not exact. For money, this matters. Never use JSON
numbers for currency amounts. Use strings:

```python
from decimal import Decimal
import json

price = Decimal("999.99")

# BAD: loses precision
json.dumps({"price": float(price)})  # "999.99" might become 999.9900000000001

# GOOD: exact
json.dumps({"price": str(price)})    # "999.99"

# On the receiving end, the client parses it as their exact decimal type
```

**Bytes and binary data**

JSON only knows strings, so binary data is typically base64-encoded:

```python
import base64
import json

# Encoding bytes → base64 string
image_bytes = b"\x89PNG\r\n..."
encoded = base64.b64encode(image_bytes).decode("utf-8")
json.dumps({"image": encoded})

# Decoding on the other side
data = json.loads(response_body)
image_bytes = base64.b64decode(data["image"])
```

Base64 increases the data size by about 33%. For large binary payloads, this is why
binary formats like MessagePack or Protobuf exist — more on those later.

### Python's json Module vs orjson

Python's standard library `json` module is correct but slow. For high-throughput APIs,
this matters.

```python
import json
import orjson   # pip install orjson
import ujson    # pip install ujson
import timeit

data = {"users": [{"id": i, "name": f"User {i}"} for i in range(1000)]}

# Standard library
timeit.timeit(lambda: json.dumps(data), number=10000)   # ~2.8s

# orjson (written in Rust)
timeit.timeit(lambda: orjson.dumps(data), number=10000)  # ~0.3s — ~10x faster

# ujson (written in C)
timeit.timeit(lambda: ujson.dumps(data), number=10000)   # ~0.7s — ~4x faster
```

`orjson` also natively handles `datetime`, `Decimal`, `uuid.UUID`, and numpy arrays
without custom serializers. For performance-sensitive APIs, it's worth the dependency.

```python
import orjson
from datetime import datetime
from decimal import Decimal

data = {
    "id": 1,
    "price": Decimal("999.99"),
    "created_at": datetime.now(),
}

# orjson serializes datetime and Decimal natively
orjson.dumps(data)
# b'{"id":1,"price":"999.99","created_at":"2024-03-08T14:30:00"}'
```

---

## 2. Pydantic for Validation & Serialization

Writing JSON serialization by hand gets tedious fast. You have to remember to convert
every `Decimal` to a string, every `datetime` to ISO 8601, every custom type to
something JSON understands. You have to validate that incoming data has the right types
and constraints. Miss one field and you get a `TypeError` or silent data corruption.

Pydantic solves this in one step: declare your data shape as a Python class. Validation
and serialization come for free.

```python
from pydantic import BaseModel, field_validator
from datetime import datetime
from decimal import Decimal

class Product(BaseModel):
    id: int
    name: str
    price: Decimal
    created_at: datetime
    tags: list[str] = []

# Creating and validating
product = Product(
    id=1,
    name="Laptop",
    price=Decimal("999.99"),
    created_at=datetime.now(),
    tags=["electronics", "computers"]
)

# Serializing to dict
product.model_dump()
# {'id': 1, 'name': 'Laptop', 'price': Decimal('999.99'), 'created_at': datetime(...), 'tags': [...]}

# Serializing to JSON string — handles Decimal and datetime automatically
product.model_dump_json()
# '{"id":1,"name":"Laptop","price":"999.99","created_at":"2024-03-08T14:30:00","tags":["electronics","computers"]}'

# Parsing from a dict (validates types)
raw = {"id": "1", "name": "Laptop", "price": "999.99", "created_at": "2024-03-08T14:00:00"}
product = Product.model_validate(raw)
print(product.id)     # 1 (int, coerced from string "1")
print(product.price)  # Decimal('999.99') (not a float)
```

Notice that `id` was passed as the string `"1"` but came out as `int`. Pydantic coerces
compatible types. If the coercion fails — say, you pass `"hello"` for an `int` field —
you get a clear `ValidationError` with the field name and what went wrong.

### Custom Validators

Sometimes type coercion isn't enough. You need business logic:

```python
from pydantic import BaseModel, field_validator, model_validator
from decimal import Decimal

class Order(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    discount: Decimal = Decimal("0")

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("quantity must be greater than 0")
        return v

    @field_validator("discount")
    @classmethod
    def discount_in_range(cls, v):
        if not (Decimal("0") <= v <= Decimal("1")):
            raise ValueError("discount must be between 0 and 1 (e.g. 0.10 = 10%)")
        return v

    @model_validator(mode="after")
    def total_makes_sense(self):
        total = self.unit_price * self.quantity * (1 - self.discount)
        if total < 0:
            raise ValueError("computed total cannot be negative")
        return self

# This will fail validation
Order(product_id=1, quantity=-5, unit_price=Decimal("10.00"))
# pydantic.ValidationError: 1 validation error for Order
# quantity
#   Value error, quantity must be greater than 0
```

### Controlling Serialization Output

Pydantic v2 gives you fine-grained control over how fields serialize:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

class Product(BaseModel):
    id: int
    internal_cost: Decimal = Field(exclude=True)  # never sent to clients
    price: Decimal
    created_at: datetime
    updated_at: datetime | None = None

product = Product(
    id=1,
    internal_cost=Decimal("450.00"),  # our cost — excluded from output
    price=Decimal("999.99"),
    created_at=datetime.now(),
)

product.model_dump_json()
# '{"id":1,"price":"999.99","created_at":"2024-03-08T14:30:00","updated_at":null}'
# Note: internal_cost is gone
```

---

## 3. Schema Validation in FastAPI

FastAPI uses Pydantic as its validation engine. When you declare a Pydantic model as
a request body type, FastAPI automatically:

1. Parses the JSON request body
2. Validates it against the model
3. Returns a `422 Unprocessable Entity` with detailed errors if validation fails
4. Passes the validated, typed object to your handler

```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal
from datetime import datetime

app = FastAPI()

class CreateProductRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: Decimal = Field(gt=0)
    category: str
    tags: list[str] = []

class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    category: str
    tags: list[str]
    created_at: datetime

@app.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(body: CreateProductRequest):
    # body is already validated — price is Decimal, name is non-empty, etc.
    product = save_to_database(body)
    return product  # FastAPI serializes this using ProductResponse
```

The `response_model=ProductResponse` declaration does two things:
- It filters the response to only include fields defined in `ProductResponse`
  (sensitive fields on your DB model won't leak out)
- It generates the OpenAPI schema for your docs automatically

If the request body is missing `name` or has an invalid `price`, FastAPI returns:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "name"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

This is FastAPI's default 422 format. You can customize it — that's covered in the
error handling module.

---

## 4. XML — The Enterprise Holdout

Before JSON, there was XML. Verbose, strict, but expressive. You'll encounter it in:

- **SOAP web services** — older enterprise APIs (banking, healthcare, government)
  that predate REST. If you're integrating with SAP, Oracle, or older payment
  processors, you're probably dealing with SOAP/XML.
- **RSS/Atom feeds** — still XML
- **SVG, XHTML** — structured document formats
- **Some government and financial APIs** that haven't been updated

```xml
<?xml version="1.0" encoding="UTF-8"?>
<product>
  <id>1</id>
  <name>Laptop</name>
  <price currency="USD">999.99</price>
  <tags>
    <tag>electronics</tag>
    <tag>computers</tag>
  </tags>
</product>
```

Python's standard library has `xml.etree.ElementTree` for parsing XML. For more
complex XML work, `lxml` is the go-to library.

**For new APIs: use JSON.** XML is verbose (the tags double or triple the payload size),
harder to work with in JavaScript, and adds no meaningful benefit over JSON for
standard REST APIs. You'll run into XML when integrating with legacy systems. You won't
choose it for something you're building from scratch.

---

## 5. Binary Formats — When JSON Is Too Slow

JSON is text. Converting a Python object to a JSON string takes CPU time. Sending
text takes more bytes than binary. For most APIs, this doesn't matter. For APIs
handling millions of requests per second or transmitting large datasets, it starts to.

### MessagePack

MessagePack is "JSON but binary." Same structure as JSON (strings, numbers, arrays,
objects), but stored as compact binary instead of text. Typically 20-50% smaller than
equivalent JSON, and faster to serialize and deserialize.

```python
import msgpack  # pip install msgpack

data = {"id": 1, "name": "Laptop", "price": 999.99, "tags": ["electronics"]}

# Encode to bytes
packed = msgpack.packb(data)
print(len(packed))          # ~40 bytes

import json
print(len(json.dumps(data).encode()))  # ~60 bytes

# Decode from bytes
unpacked = msgpack.unpackb(packed, raw=False)
```

MessagePack is a drop-in replacement for JSON in terms of data model. Easy to adopt
for internal service-to-service communication where you control both ends.

### Protocol Buffers (Protobuf)

Protobuf is Google's binary serialization format, used in gRPC. Unlike MessagePack,
Protobuf requires you to define a schema upfront in a `.proto` file:

```protobuf
// product.proto
syntax = "proto3";

message Product {
  int32 id = 1;
  string name = 2;
  string price = 3;
  repeated string tags = 4;
}
```

The schema is compiled to Python (or any other language) classes. Data is validated
against the schema at serialization/deserialization time. This is stricter than JSON
(no extra fields, no missing optional fields), and the payloads are much smaller —
often 60-80% smaller than equivalent JSON.

Use Protobuf when:
- You're building microservices with gRPC
- Bandwidth is genuinely constrained (IoT, mobile on slow networks)
- You need strict schema enforcement across many language boundaries
- Serialization/deserialization performance is a bottleneck

For public-facing REST APIs: stick with JSON. Developer experience matters, and
everyone knows how to debug JSON.

---

## 6. File Formats — When APIs Return Bulk Data

Sometimes an API doesn't return structured JSON — it returns a file. The two formats
you'll encounter most often for data APIs:

### CSV

The classic. Every spreadsheet tool, every data analysis library, every reporting
system can read CSV. Use it when:

```python
import csv
import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

@app.get("/reports/orders")
async def export_orders_csv():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "status", "total", "created_at"])
    writer.writeheader()

    orders = get_all_orders()  # fetch from DB
    for order in orders:
        writer.writerow({
            "id": order.id,
            "status": order.status,
            "total": str(order.total),
            "created_at": order.created_at.isoformat(),
        })

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders.csv"}
    )
```

CSV is great for: data exports, reports that users will open in Excel, bulk data that
a data team will import into a database.

CSV is bad for: nested data (it's flat by nature), binary data, anything requiring
schema enforcement.

### Parquet

Parquet is a columnar binary format used in data engineering. You'll encounter it in
data lake architectures, analytics pipelines, and APIs designed for data science teams.

```python
import pandas as pd
from fastapi.responses import Response

@app.get("/data/products")
async def export_products_parquet():
    df = pd.DataFrame(get_all_products())
    parquet_bytes = df.to_parquet(index=False)
    return Response(
        content=parquet_bytes,
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=products.parquet"}
    )
```

Parquet files are highly compressed, preserve data types (unlike CSV, where everything
becomes a string), and are designed for efficient column-level reads. A pandas
`DataFrame` or Spark job reading only the `price` column doesn't need to read the
entire file — just that column's data.

Use Parquet when your API is serving data to analytical workloads. Use CSV when
your API is serving data to humans with spreadsheets.

---

## Format Decision Guide

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  What are you building?                                       │
│                                                               │
│  Public REST API                → JSON (always)              │
│                                                               │
│  Internal microservices         → MessagePack or Protobuf    │
│  (high throughput, you own both    if performance matters;   │
│   ends)                            JSON otherwise            │
│                                                               │
│  gRPC services                  → Protobuf                   │
│                                                               │
│  Integrating with legacy system → XML/SOAP (no choice)       │
│                                                               │
│  Bulk data export for humans    → CSV                        │
│                                                               │
│  Bulk data for analytics        → Parquet                    │
│                                                               │
│  Large binary payload           → Multipart form data        │
│  (images, files)                   or pre-signed URLs        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

```
JSON:
  - 6 types: string, number, boolean, null, array, object
  - No native date → use ISO 8601 strings ("2024-03-08T14:30:00Z")
  - No native Decimal → use strings ("999.99") for money
  - No bytes → use base64-encoded strings
  - Standard library json is correct; orjson is ~10x faster for hot paths

Pydantic:
  - Declare your schema as a Python class
  - Validates, coerces types, and serializes in one step
  - model_dump_json() handles datetime + Decimal automatically
  - Use Field(exclude=True) to keep internal fields out of responses

FastAPI + Pydantic:
  - Declare request body as a Pydantic model → automatic validation
  - Declare response_model → automatic serialization + field filtering
  - Wrong input → 422 with exact field-level errors, before your code runs

XML:
  - Legacy/enterprise only (SOAP, government APIs)
  - Avoid for new APIs

Binary formats:
  - MessagePack: JSON-like, 20-50% smaller, same data model
  - Protobuf: schema-first, 60-80% smaller, use with gRPC

File formats:
  - CSV: human-readable bulk export (Excel, reporting)
  - Parquet: columnar binary, analytics and data engineering
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← REST Best Practices](../03_rest_best_practices/patterns.md) &nbsp;|&nbsp; **Next:** [Authentication & Authorization →](../05_authentication/securing_apis.md)

**Related Topics:** [REST Best Practices](../03_rest_best_practices/patterns.md) · [FastAPI Core Guide](../07_fastapi/core_guide.md) · [Testing APIs](../10_testing_documentation/testing_apis.md)
