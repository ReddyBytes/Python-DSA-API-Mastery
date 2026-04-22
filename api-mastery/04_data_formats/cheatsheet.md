# ⚡ Data Formats & Serialization — Cheatsheet

## Learning Priority

| Priority | Topics |
|---|---|
| Must Learn | JSON types and limitations · ISO 8601 dates · Decimal as string · Pydantic basics |
| Should Learn | Protocol Buffers · MessagePack · CSV/Parquet for data export |
| Good to Know | binary format size/speed comparison · CBOR |
| Reference | Avro · wire format internals · schema evolution |

---

## Format Comparison Table

| Format | Type | Size vs JSON | Speed | Human-readable | Best for |
|---|---|---|---|---|---|
| JSON | Text | Baseline | Medium | Yes | All public REST APIs |
| XML | Text | +50–200% larger | Slow | Yes (verbose) | SOAP/legacy/enterprise |
| MessagePack | Binary | 20–50% smaller | Fast | No | Internal services, drop-in JSON replacement |
| Protobuf | Binary | 60–80% smaller | Very fast | No | gRPC, strict schema, microservices |
| CSV | Text | Varies | Medium | Yes | Bulk human export (Excel/reports) |
| Parquet | Binary columnar | Very small | Very fast for reads | No | Analytics, data engineering |

**Decision rule:** Public REST API → JSON always. Internal high-throughput → MessagePack or Protobuf.

---

## JSON — 6 Types Only

```json
{
  "name":       "Alice",          // string — always double-quoted
  "age":        30,               // number — no quotes (int or float, no distinction)
  "is_admin":   true,             // boolean — true/false lowercase, no quotes
  "middle_name": null,            // null — means "nothing"
  "scores":     [95, 87, 92],     // array — ordered, mixed types allowed
  "address": {                    // object — key-value pairs
    "city": "Austin"
  }
}
```

### What JSON Cannot Represent (and workarounds)

| Missing type | Workaround | Example |
|---|---|---|
| Date / datetime | ISO 8601 string | `"2024-03-08T14:30:00Z"` |
| Decimal / money | String | `"999.99"` (never float) |
| Bytes / binary | base64 string | `"iVBORw0KGgo..."` |
| Set | Array (dedup manually) | `[1, 2, 3]` |
| Tuple | Array | `[1, 2, 3]` |
| Integer vs float | Both use `number` type | No distinction in JSON |

---

## Date/Time Rules

```python
from datetime import datetime, timezone

# ALWAYS include timezone info
dt = datetime(2024, 3, 8, 14, 30, 0, tzinfo=timezone.utc)

# ISO 8601 formats (both acceptable)
dt.isoformat()                      # "2024-03-08T14:30:00+00:00"
dt.strftime("%Y-%m-%dT%H:%M:%SZ")   # "2024-03-08T14:30:00Z"  (Z = UTC)
```

**Never send a bare `"2024-03-08T14:30:00"` — timezone is ambiguous.**

---

## Decimal / Money Rules

```python
from decimal import Decimal
import json

# BAD — float loses precision
json.dumps({"price": float(Decimal("999.99"))})   # might become 999.9900000001

# GOOD — serialize as string
json.dumps({"price": str(Decimal("999.99"))})     # "999.99"

# On receive: parse back to Decimal
price = Decimal(response_data["price"])
```

**Rule: never use JSON numbers for currency. Always string.**

---

## Pydantic Model Syntax

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional

class Product(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=200)
    price: Decimal = Field(gt=0)                       # gt = greater than
    category: str
    tags: list[str] = []                               # default empty list
    internal_cost: Decimal = Field(exclude=True)       # never in output
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v):
        if not v.strip():
            raise ValueError("name cannot be blank")
        return v.strip()
```

### Field Constraint Reference

| Constraint | Meaning | Example |
|---|---|---|
| `gt=0` | greater than | `Field(gt=0)` |
| `ge=1` | greater than or equal | `Field(ge=1)` |
| `lt=100` | less than | `Field(lt=100)` |
| `le=100` | less than or equal | `Field(le=100)` |
| `min_length=3` | string min chars | `Field(min_length=3)` |
| `max_length=255` | string max chars | `Field(max_length=255)` |
| `pattern=r"..."` | regex match | `Field(pattern=r"^[a-z]+")`|
| `exclude=True` | hide from output | `Field(exclude=True)` |

---

## Pydantic Serialization / Deserialization

```python
# Creating (validate on input)
product = Product(id=1, name="Laptop", price=Decimal("999.99"), ...)

# Serialize to dict (Python types preserved)
product.model_dump()
# {"id": 1, "name": "Laptop", "price": Decimal("999.99"), ...}

# Serialize to JSON string (Decimal → string, datetime → ISO 8601)
product.model_dump_json()
# '{"id":1,"name":"Laptop","price":"999.99","created_at":"2024-03-08T14:30:00"}'

# Deserialize from dict (validates + coerces types)
raw = {"id": "1", "name": "Laptop", "price": "999.99", "created_at": "2024-03-08T14:00:00"}
product = Product.model_validate(raw)
product.id      # 1 (int, coerced from "1")
product.price   # Decimal("999.99") (not float)

# Serialize to dict, excluding unset optional fields
product.model_dump(exclude_unset=True)

# Serialize, excluding None values
product.model_dump(exclude_none=True)
```

---

## Field Validators

```python
from pydantic import BaseModel, field_validator, model_validator

class Order(BaseModel):
    quantity: int
    unit_price: Decimal
    discount: Decimal = Decimal("0")

    @field_validator("quantity")                   # single field
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("quantity must be > 0")
        return v

    @field_validator("discount")
    @classmethod
    def discount_in_range(cls, v):
        if not (Decimal("0") <= v <= Decimal("1")):
            raise ValueError("discount must be 0.0–1.0")
        return v

    @model_validator(mode="after")                 # cross-field validation
    def check_total(self):
        total = self.unit_price * self.quantity * (1 - self.discount)
        if total < 0:
            raise ValueError("total cannot be negative")
        return self
```

---

## Common Type Annotations

```python
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from decimal import Decimal

# Basic
name: str
count: int
price: Decimal
flag: bool
timestamp: datetime

# Optional (can be None)
middle_name: Optional[str] = None
updated_at: Optional[datetime] = None

# Collections
tags: list[str] = []
scores: list[int]
metadata: dict[str, Any] = {}

# Union types (Python 3.10+)
value: str | int | None
```

---

## JSON Library Performance

```python
import json       # stdlib — correct, slow
import orjson     # Rust-based — ~10x faster, native datetime/Decimal
import ujson      # C-based — ~4x faster

# orjson handles datetime/Decimal natively
import orjson
from datetime import datetime
from decimal import Decimal

data = {"price": Decimal("999.99"), "ts": datetime.now()}
orjson.dumps(data)   # b'{"price":"999.99","ts":"2024-03-08T14:30:00"}'
```

**For hot-path APIs: use orjson. For most APIs: stdlib is fine.**

---

## MessagePack vs JSON

```python
import msgpack   # pip install msgpack
import json

data = {"id": 1, "name": "Laptop", "price": 999.99}

packed = msgpack.packb(data)
print(len(packed))                        # ~35 bytes
print(len(json.dumps(data).encode()))     # ~45 bytes

unpacked = msgpack.unpackb(packed, raw=False)
```

Same data model as JSON. Drop-in for internal services.

---

## Navigation

**[Back to README](../README.md)**

**Theory:** [serialization_guide.md](./serialization_guide.md)

**Prev:** [← REST Best Practices](../03_rest_best_practices/cheatsheet.md) &nbsp;|&nbsp; **Next:** [Authentication →](../05_authentication/cheatsheet.md)

**Related:** [05 Authentication](../05_authentication/cheatsheet.md) · [07 FastAPI](../07_fastapi/cheatsheet.md) · [10 Testing](../10_testing_documentation/cheatsheet.md)
