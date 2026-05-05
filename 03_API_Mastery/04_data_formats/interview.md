# 🎯 Data Formats & Serialization — Interview Preparation

> This file prepares you to discuss data formats and serialization like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What are the 6 data types in JSON?**

<details>
<summary>💡 Show Answer</summary>

String (always double-quoted), number (integer or float — JSON makes no distinction), boolean (lowercase `true` or `false`, no quotes), null (lowercase, represents absence), array (ordered list in brackets), and object (key-value pairs in braces).

What JSON does NOT have: a date type, a decimal/money type, a bytes/binary type, or a distinction between integer and float. These are common interview follow-ups, and the answer is that you encode dates as ISO 8601 strings, money as strings, and binary as base64 strings.

</details>

<br>

**Q2: Why should you never use a JSON number (float) to represent money?**

<details>
<summary>💡 Show Answer</summary>

IEEE 754 floating-point arithmetic cannot represent all decimal values exactly. `0.1 + 0.2` in floating point equals `0.30000000000000004`, not `0.3`. For currency this is catastrophic — rounding errors compound over transactions and produce incorrect totals.

The correct approach: serialize money as a string (`"999.99"`) and deserialize into a `Decimal` type on both ends. In Python, use `from decimal import Decimal` and `Decimal("999.99")` — never `float(Decimal("999.99"))`. Libraries like Pydantic handle this automatically when you type a field as `Decimal`.

</details>

<br>

**Q3: How should dates and times be represented in a REST API response?**

<details>
<summary>💡 Show Answer</summary>

Always use ISO 8601 format with explicit timezone info. The safest format is UTC with a Z suffix: `"2024-03-08T14:30:00Z"`. You can also use `+00:00` offset notation. The key rule: never send a naive datetime without a timezone (`"2024-03-08T14:30:00"` is ambiguous and causes bugs when the client and server are in different timezones).

In Python: always create datetimes with `tzinfo=timezone.utc`. Use `datetime.isoformat()` or `strftime("%Y-%m-%dT%H:%M:%SZ")` for serialization. Libraries like Pydantic and orjson handle this automatically when the field is typed as `datetime`.

</details>

<br>

**Q4: What is the difference between JSON and Protocol Buffers (Protobuf)?**

<details>
<summary>💡 Show Answer</summary>

JSON is text-based and human-readable. Protobuf is binary and schema-defined. Protobuf messages are 60–80% smaller than equivalent JSON and serialize/deserialize significantly faster. The trade-off: Protobuf requires a `.proto` schema file and code generation on both client and server. You can't just read a Protobuf message in a browser dev console — you need the schema to decode it.

Use JSON for all public REST APIs — it's debuggable with zero tooling. Use Protobuf for gRPC and internal high-throughput services where performance and schema enforcement matter. Google, Netflix, and Uber use Protobuf/gRPC internally but expose JSON over HTTP for public APIs.

</details>

<br>

**Q5: What is Pydantic and what problem does it solve?**

<details>
<summary>💡 Show Answer</summary>

Pydantic is a Python data validation library that uses type annotations to validate and serialize data. You define a class inheriting from `BaseModel`, annotate fields with types, and Pydantic automatically validates input data, coerces types, and raises structured validation errors.

It solves the problem of manual validation boilerplate. Without Pydantic you'd write `if "email" not in data or not isinstance(data["email"], str)` for every field. With Pydantic: `class CreateUser(BaseModel): email: EmailStr`. FastAPI uses Pydantic as its validation layer — incoming request bodies are automatically validated against the model, and invalid data returns a structured 422 error response.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: How does Pydantic handle type coercion and what are the risks?**

<details>
<summary>💡 Show Answer</summary>

By default, Pydantic v2 coerces types in lax mode — it will convert `"1"` (string) to `1` (int) for a field typed as `int`. This is useful for query parameters which are always strings. The risk: it can silently accept malformed data. If a client sends `{"id": "abc"}` for an int field, Pydantic raises a `ValidationError`. But if it sends `{"id": "1"}`, Pydantic accepts it by converting the string.

Use `model_config = ConfigDict(strict=True)` to disable coercion when you need strict type enforcement — for example, when accepting data from untrusted sources. In FastAPI, path and query parameters are always strings and need coercion; request bodies should usually be strict.

</details>

<br>

**Q7: What does `model_dump(exclude_unset=True)` do in Pydantic and why is it important for PATCH endpoints?**

<details>
<summary>💡 Show Answer</summary>

`model_dump(exclude_unset=True)` returns only the fields that were explicitly provided in the input — fields that were not in the request are excluded entirely (not set to their defaults).

This is critical for PATCH endpoints. If you call `model_dump()` (without `exclude_unset=True`) on a PATCH body where the client only sent `{"status": "active"}`, Pydantic includes all other fields at their default values (e.g., `None`). Your update query then overwrites existing data with nulls. With `exclude_unset=True`, you get `{"status": "active"}` — only the fields to change — and build a safe partial update query.

</details>

<br>

**Q8: When would you use MessagePack instead of JSON for an API?**

<details>
<summary>💡 Show Answer</summary>

MessagePack is a binary serialization format with the same data model as JSON but 20–50% smaller and faster to parse. Use it for internal service-to-service communication where both sides are under your control and human-readability is not needed.

You would not use MessagePack for a public API — external developers can't inspect responses with browser tools, Postman, or curl without a decoder. The operational cost of losing debuggability usually outweighs the bandwidth savings unless you're at very high throughput. A practical middle ground: use orjson (a Rust-based JSON library that's 10x faster than the Python stdlib) — you keep the JSON format but eliminate most of the serialization overhead.

</details>

<br>

**Q9: How do you write a Pydantic cross-field validator and when do you need one?**

<details>
<summary>💡 Show Answer</summary>

Use a `@model_validator(mode="after")` when validity depends on multiple fields in combination. For example, an order model where the `discount` field must not make the `total` negative, or a date range model where `end_date` must be after `start_date`.

You decorate a method with `@model_validator(mode="after")`, and inside `self` is the fully-constructed model instance with all field values already validated individually. Raise `ValueError` with a message if the cross-field constraint fails. Pydantic converts this into the same structured `ValidationError` that single-field validators produce, so the error format is consistent across your entire API.

</details>

<br>

**Q10: What is the `exclude=True` field option in Pydantic and what is a typical use case?**

<details>
<summary>💡 Show Answer</summary>

`Field(exclude=True)` on a model field means that field is never included in serialized output from `model_dump()` or `model_dump_json()`. It can exist on the model and be used internally, but it never appears in API responses.

The canonical use case is an internal cost or margin field. The database model might have `internal_cost` that powers pricing logic, but you never want it in API responses. Without `exclude=True`, you'd need a separate response model. With it, the same model serves both purposes — it validates and stores the field but strips it from output automatically. Always prefer explicit response models for complex APIs, but `exclude=True` is useful for simpler cases.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: Describe how you would implement schema evolution for a binary format (Protobuf or Avro) without breaking existing consumers.**

<details>
<summary>💡 Show Answer</summary>

Protobuf supports schema evolution via field numbers. Rules: never reuse a field number (even after removing the field — use `reserved` to mark it), only add new optional fields (don't add required fields), and don't change a field's type. Old consumers see new fields as unknown and skip them. New consumers read old messages and get default values for missing new fields.

Avro requires a schema registry (Confluent Schema Registry is the standard for Kafka). Schemas are versioned; consumers can specify compatibility mode (BACKWARD, FORWARD, FULL). The registry validates that new schemas are compatible with previous versions before they're used in production. For REST APIs, JSON with Pydantic is simpler — just add new optional fields and don't remove existing ones.

</details>

<br>

**Q12: How do you handle Decimal serialization in a high-throughput financial API using orjson?**

<details>
<summary>💡 Show Answer</summary>

orjson natively serializes `Decimal` as a string without any custom serializer, which is exactly the right behavior for financial data. It also handles `datetime` as ISO 8601 automatically. At high throughput this matters — orjson is ~10x faster than Python's stdlib `json` module because it's implemented in Rust.

In FastAPI, switch the default response class: `app = FastAPI(default_response_class=ORJSONResponse)`. For Pydantic models, `model_dump_json()` can be configured to use orjson-compatible serialization. One gotcha: orjson serializes `Decimal` as a JSON string, which is correct. If a consumer expects a JSON number for a Decimal field, they'll break — document this in your API spec and enforce it with integration tests.

</details>

<br>

**Q13: A Pydantic model is used both as a database ORM model and an API response model. What are the risks and how do you avoid them?**

<details>
<summary>💡 Show Answer</summary>

Using a single model for both concerns couples the database schema directly to the API contract. Any database migration that adds, renames, or removes a column changes the API response — a breaking change for API consumers. Internal fields (hashed passwords, cost margins, audit columns) can accidentally leak into responses.

The solution is to use separate models: a database model (SQLAlchemy or similar ORM), an internal domain model, and one or more API response models. In FastAPI, specify `response_model=UserResponse` on the route decorator — FastAPI validates and filters the response through that model, so even if the handler returns an ORM object with extra fields, they're stripped at the boundary. This is the single most important architectural boundary in a production FastAPI app.

</details>

<br>

**Q14: Compare Parquet and JSON for a data export endpoint that serves 10 million rows to data engineers.**

<details>
<summary>💡 Show Answer</summary>

JSON is row-oriented and text-based. Serializing 10M rows to JSON produces a very large file (potentially gigabytes), requires loading all rows into memory or streaming them, and is slow to process in analytics tools — every row must be parsed even if only two columns are needed.

Parquet is a columnar binary format. It stores data column by column, which enables column pruning (read only the columns you need), predicate pushdown (skip row groups that don't match a filter), and very high compression ratios (often 5–10x vs JSON). A 1GB JSON export might be 100–200MB as Parquet.

For a data engineering export endpoint, return Parquet via a `StreamingResponse` or pre-generate files to S3/GCS with a signed URL. Never try to return 10M rows as JSON from an API — memory pressure and client parsing time make it impractical. CSV is acceptable for Excel users; Parquet for data pipelines.

</details>

<br>
