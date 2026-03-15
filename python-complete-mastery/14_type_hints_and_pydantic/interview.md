# 🎯 Type Hints & Pydantic — Interview Questions

> *"Type hints and Pydantic questions reveal whether you write Python that works only for you, or Python that works for a whole team — six months from now."*

---

## 📊 Question Map

```
LEVEL 1 — Beginner
  • What are type hints and why use them?
  • Are type hints enforced at runtime?
  • What is Pydantic and why do people use it?
  • What is the difference between Optional and str | None?

LEVEL 2 — Intermediate
  • Pydantic vs dataclass vs TypedDict — when to use each?
  • How does Pydantic validate data? What happens with wrong types?
  • How do you add constraints to a Pydantic field?
  • What is @field_validator and when do you use it?
  • What is model_dump() and when would you use it?

LEVEL 3 — Advanced
  • Pydantic v2 performance improvements and breaking changes
  • Using Pydantic with FastAPI for request/response validation
  • Using Pydantic for LLM structured outputs
  • model_json_schema() for OpenAI function calling / tool use
  • model_validator for cross-field validation
```

---

## 🟢 Level 1 — Beginner Questions

---

### Q1: What are type hints in Python and why would you use them?

**Weak answer:** "They tell Python what type a variable is."

**Strong answer:**

> Type hints are annotations that describe what types a function expects as inputs and what it returns. They were added in Python 3.5 (PEP 484).

```python
# Without type hints — reader has to guess:
def send_message(recipient, content, priority):
    ...

# With type hints — contract is explicit:
def send_message(recipient: str, content: str, priority: int = 1) -> bool:
    ...
```

> **Why use them:**
> 1. **IDE support** — autocomplete, hover documentation, navigation work correctly
> 2. **Static analysis** — tools like `mypy` and `pyright` catch type errors before runtime
> 3. **Documentation** — the function signature tells you exactly what it needs
> 4. **Refactoring** — renaming a type? Your IDE can find all the places it's used

> Type hints are especially valuable in large teams and codebases where you don't hold all the context in your head.

---

### Q2: Are type hints enforced at runtime in Python?

**Weak answer:** "Yes, Python will raise a TypeError if you pass the wrong type."

**Strong answer:**

> No. Python completely ignores type hints at runtime. You can pass the wrong type and Python will run the code fine:

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

greet(999)      # Python runs this — no error
# → "Hello, 999"

greet([1, 2, 3])  # Python runs this too
# → "Hello, [1, 2, 3]"
```

> Type hints are hints to tools (mypy, pyright, your IDE) and to humans reading the code. They are not runtime contracts.
>
> **If you want runtime enforcement**, you use Pydantic. Pydantic reads the type annotations and actually validates the data when you create a model instance.

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

User(name="Alice", age="not-a-number")   # raises ValidationError at runtime
```

---

### Q3: What is Pydantic and why do AI engineers use it so much?

**Strong answer:**

> Pydantic is a Python library for **data validation and parsing**. It uses type annotations to validate that data matches your expected schema at runtime, automatically coerce compatible types (e.g. `"42"` → `42`), and raise a detailed `ValidationError` when data is invalid.

```python
from pydantic import BaseModel

class LLMRequest(BaseModel):
    prompt: str
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 1000

# Valid — works fine:
req = LLMRequest(prompt="What is Python?")
print(req.temperature)   # 0.7

# Invalid — raises immediately with a clear error:
try:
    bad = LLMRequest(prompt="Hello", temperature="very hot")
except Exception as e:
    print(e)
# temperature: Input should be a valid number
```

> **Why AI engineers use it:**
> - **FastAPI** (the most popular Python web framework for AI apps) uses Pydantic for all request/response models
> - **OpenAI and Anthropic structured outputs** — `model_json_schema()` generates the JSON Schema you pass to the API to force structured responses
> - **Parsing LLM responses** — after calling an LLM, you validate and type the result with Pydantic
> - **Configuration** — Pydantic Settings reads environment variables and validates them

---

### Q4: What is the difference between `Optional[str]` and `str | None`?

**Strong answer:**

> They are identical in meaning — both say "this value is either a string or None."

```python
from typing import Optional

# These two are equivalent:
def find_user(user_id: int) -> Optional[str]:
    ...

def find_user(user_id: int) -> str | None:
    ...
```

> `Optional[str]` is from the `typing` module (Python 3.5+). It was the original syntax.
>
> `str | None` uses the union operator `|` introduced in Python 3.10 (PEP 604). It requires no imports and is cleaner to read.
>
> In modern code (Python 3.10+), prefer `str | None`. In code that must support older Python, use `Optional[str]`.
>
> **Common mistake:** forgetting to set a default of `None` when using Optional:

```python
# This means the parameter IS optional (can be None):
def greet(name: str | None = None) -> str:
    return f"Hello, {name or 'stranger'}"

# This means the caller MUST provide name, but it can be None:
def greet(name: str | None) -> str:   # still required!
    ...
```

---

## 🔵 Level 2 — Intermediate Questions

---

### Q5: When would you use Pydantic vs dataclass vs TypedDict?

**Strong answer:**

```
TypedDict:
  Use when: working with dicts that have a known structure (e.g., JSON from an API)
  Validates: nothing (type hints only)
  Runtime: plain dict — lowest overhead
  Example: annotating dict shapes for IDE support, internal function contracts

dataclass:
  Use when: you want a class with typed attributes and no boilerplate
  Validates: nothing (type hints only)
  Runtime: creates a class instance with __init__, __repr__, __eq__
  Example: internal data transfer objects, config structures

Pydantic BaseModel:
  Use when: data comes from outside your code (API request, user input, file, LLM)
  Validates: at runtime — raises ValidationError on bad data
  Runtime: slightly more overhead, but gets type coercion and JSON serialization
  Example: FastAPI models, LLM request/response, environment config
```

```python
from typing import TypedDict
from dataclasses import dataclass
from pydantic import BaseModel

# TypedDict — dict with type hints (no validation, no class instance):
class MessageDict(TypedDict):
    role: str
    content: str

# dataclass — class with type hints (no validation):
@dataclass
class MessageDC:
    role: str
    content: str

# Pydantic — class with runtime validation:
class MessagePydantic(BaseModel):
    role: str
    content: str

# The difference:
MessageDC(role=123, content="Hi")         # stores 123 — no error
MessagePydantic(role=123, content="Hi")   # coerces 123 → "123" (or raises)
```

---

### Q6: How does Pydantic validate data? What happens when you pass the wrong type?

**Strong answer:**

> When you call `Model(field=value)`, Pydantic:
> 1. Iterates over the model fields
> 2. For each field, attempts to **coerce** the value to the declared type
> 3. If coercion succeeds, stores the coerced value
> 4. If coercion fails, records a validation error
> 5. After checking all fields, if any errors exist, raises `ValidationError` with full detail

```python
from pydantic import BaseModel

class Order(BaseModel):
    item: str
    quantity: int
    price: float

# Coercion — compatible types are converted:
o = Order(item="book", quantity="3", price="9.99")
print(o.quantity)   # 3     (str "3" → int 3)
print(o.price)      # 9.99  (str "9.99" → float 9.99)
print(type(o.quantity))   # <class 'int'>

# Validation error — incompatible types:
try:
    bad = Order(item="book", quantity="three", price=10.0)
except Exception as e:
    print(e)
# → 1 validation error for Order
#   quantity
#     Input should be a valid integer, unable to parse string as an integer [...]
```

> **Key point:** Pydantic is lenient about compatible types (string digits → int) but strict about incompatible ones. This is called "lax mode" in v2. You can enable strict mode if you need exact type matching.

---

### Q7: How do you add constraints to a Pydantic field? Show examples.

**Strong answer:**

> Use `Field()` from pydantic with constraint parameters:

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name:     str   = Field(min_length=1, max_length=100)
    price:    float = Field(gt=0)                         # must be > 0
    quantity: int   = Field(ge=0)                         # must be >= 0
    discount: float = Field(ge=0.0, le=1.0)               # 0.0 to 1.0
    sku:      str   = Field(pattern=r"^[A-Z]{2}\d{6}$")  # e.g. "AB123456"
    tags:     list[str] = Field(default_factory=list, max_length=10)  # max 10 tags

# All these constraints are checked at instantiation AND in model_json_schema():
try:
    bad = Product(name="Widget", price=-5.0, quantity=10, discount=0.1, sku="AB123456")
except Exception as e:
    print(e)
# price: Input should be greater than 0
```

> **Constraint summary:**
> - `min_length` / `max_length` → string or list length
> - `gt` / `lt` → strictly greater / less than (numbers)
> - `ge` / `le` → greater or equal / less or equal (numbers)
> - `pattern` → regex (strings only)
> - `default_factory` → callable for mutable defaults (list, dict)
> - `description` → included in JSON Schema output

---

### Q8: What is `@field_validator` and when do you use it instead of `Field()`?

**Strong answer:**

> `Field()` constraints handle simple numeric and string rules (bounds, length, regex). For anything more complex — custom logic, cross-referencing other data, calling a function — you need `@field_validator`:

```python
from pydantic import BaseModel, field_validator

class ChatMessage(BaseModel):
    role: str
    content: str

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        allowed = {"system", "user", "assistant"}
        if v not in allowed:
            raise ValueError(f"role must be one of {allowed}")
        return v   # you can also transform the value here

    @field_validator("content")
    @classmethod
    def strip_content(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("content cannot be blank")
        return stripped   # transformed: whitespace stripped

msg = ChatMessage(role="user", content="  Hello  ")
print(msg.content)   # "Hello" — transformed by validator
```

> **Rules for `@field_validator`:**
> - Must be a `@classmethod`
> - Receives the raw value as second argument
> - Must return the value (possibly transformed)
> - Raise `ValueError` (not `ValidationError`) to signal failure

---

### Q9: What does `model_dump()` do and when would you use it?

**Strong answer:**

> `model_dump()` converts a Pydantic model instance to a plain Python dictionary. It recursively converts nested models too.

```python
from pydantic import BaseModel

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int

class Response(BaseModel):
    content: str
    model: str
    usage: Usage

resp = Response(
    content="Hello!",
    model="gpt-4o",
    usage=Usage(prompt_tokens=10, completion_tokens=5),
)

resp.model_dump()
# → {'content': 'Hello!', 'model': 'gpt-4o',
#    'usage': {'prompt_tokens': 10, 'completion_tokens': 5}}

resp.model_dump_json()
# → '{"content":"Hello!","model":"gpt-4o","usage":{"prompt_tokens":10,...}}'
```

> **When to use it:**
> - Serializing to JSON to store in a database or return from an API
> - Logging a model's contents
> - Passing data to a function that expects a dict
> - Selective export: `model_dump(exclude={"internal_field"})`

---

## 🔴 Level 3 — Advanced Questions

---

### Q10: What are the main improvements in Pydantic v2 compared to v1?

**Strong answer:**

> Pydantic v2 (June 2023) rewrote the validation core in **Rust** (via the `pydantic-core` library). The key improvements:

```
PERFORMANCE: 5–50x faster validation than v1 for typical models.
             Measurable in high-throughput FastAPI services.

NEW API:
  v1                          v2
  ─────────────────────────────────────────────────────
  model.dict()                model.model_dump()
  model.json()                model.model_dump_json()
  Model.parse_obj(d)          Model.model_validate(d)
  Model.schema()              Model.model_json_schema()
  @validator                  @field_validator (requires @classmethod)
  @root_validator             @model_validator(mode="before"|"after")

STRICT MODE: v2 adds model_config = ConfigDict(strict=True)
             which disables coercion ("3" does NOT become 3)

DISCRIMINATED UNIONS: better support for polymorphic models

model_config: replaces v1's inner Config class:
```

```python
from pydantic import BaseModel
from pydantic.config import ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)  # no coercion
    age: int

StrictModel(age="30")   # raises in strict mode — "30" is not an int
```

---

### Q11: How does Pydantic integrate with FastAPI?

**Strong answer:**

> FastAPI uses Pydantic models for **automatic request validation, response serialization, and OpenAPI documentation generation** — all without any extra code.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class ChatRequest(BaseModel):
    messages: list[dict]
    model: str = "gpt-4o"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

class ChatResponse(BaseModel):
    content: str
    model: str
    tokens_used: int

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    # 'request' is already a validated ChatRequest object
    # FastAPI auto-parsed and validated the JSON body
    # If validation failed, FastAPI returned 422 before this ran

    result = await call_llm(request.messages, request.model, request.temperature)

    return ChatResponse(
        content=result["content"],
        model=request.model,
        tokens_used=result["usage"]["total_tokens"],
    )
    # FastAPI calls response.model_dump() and returns JSON
```

> **What FastAPI does automatically:**
> - Parses the JSON request body into the Pydantic model
> - Returns `422 Unprocessable Entity` with error details if validation fails
> - Serializes the response model to JSON
> - Generates `/docs` (Swagger UI) from the Pydantic model schemas

---

### Q12: How do you use Pydantic for LLM structured outputs?

**Strong answer:**

> LLM providers (OpenAI, Anthropic) support **structured output mode** — you provide a JSON Schema and the model is constrained to return data matching that schema exactly. Pydantic generates this schema automatically via `model_json_schema()`.

```python
from pydantic import BaseModel, Field
from typing import Literal
from openai import OpenAI

# Define the schema using a Pydantic model:
class ExtractedEntity(BaseModel):
    name: str
    entity_type: Literal["person", "organization", "location", "product"]
    confidence: float = Field(ge=0.0, le=1.0)

class ExtractionResult(BaseModel):
    entities: list[ExtractedEntity]
    summary: str

client = OpenAI()

def extract_entities(text: str) -> ExtractionResult:
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Extract all named entities from the text."},
            {"role": "user", "content": text},
        ],
        response_format=ExtractionResult,  # Pydantic model → OpenAI uses its schema
    )
    # response.choices[0].message.parsed is already a validated ExtractionResult
    return response.choices[0].message.parsed

result = extract_entities("Apple Inc. was founded by Steve Jobs in Cupertino.")
for entity in result.entities:
    print(f"{entity.name}: {entity.entity_type} ({entity.confidence:.0%})")
# Apple Inc.: organization (99%)
# Steve Jobs: person (99%)
# Cupertino: location (97%)
```

> **Why it matters:** without structured outputs you parse free-text JSON and hope the LLM followed your prompt. With structured outputs + Pydantic, the output is **guaranteed** to match your schema, and you get a fully typed Python object back automatically.

---

### Q13: How does `model_json_schema()` work for OpenAI function calling?

**Strong answer:**

> OpenAI's function calling (and tool use) requires a JSON Schema that describes the parameters your function accepts. `model_json_schema()` generates this automatically from a Pydantic model.

```python
from pydantic import BaseModel, Field
from typing import Literal
import json

class WeatherQuery(BaseModel):
    location: str = Field(description="City and country, e.g. 'London, UK'")
    unit: Literal["celsius", "fahrenheit"] = "celsius"
    days: int = Field(default=1, ge=1, le=7, description="Forecast days (1-7)")

schema = WeatherQuery.model_json_schema()
print(json.dumps(schema, indent=2))
# {
#   "title": "WeatherQuery",
#   "type": "object",
#   "properties": {
#     "location": {"title": "Location", "type": "string",
#                  "description": "City and country, e.g. 'London, UK'"},
#     "unit":     {"default": "celsius", "enum": ["celsius", "fahrenheit"], ...},
#     "days":     {"default": 1, "minimum": 1, "maximum": 7, "type": "integer", ...}
#   },
#   "required": ["location"]
# }

# Use in OpenAI function calling:
tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather forecast",
        "parameters": WeatherQuery.model_json_schema(),
    },
}

# When OpenAI calls the function and returns arguments, validate them:
raw_args = {"location": "London, UK", "unit": "celsius", "days": 3}
query = WeatherQuery.model_validate(raw_args)   # validated + typed
result = get_weather(query.location, query.unit, query.days)
```

> **The loop:** define schema with Pydantic → generate JSON Schema → pass to OpenAI → validate returned args back through Pydantic. Type safety at every step.

---

## ⚠️ Trap Questions

---

### Trap 1 — Mutable default with `[]` instead of `default_factory`

```python
# ❌ WRONG — all instances share the same list:
class Request(BaseModel):
    tags: list[str] = []   # Pydantic actually handles this safely...

# Wait — Pydantic v2 DOES handle mutable defaults safely (unlike dataclasses).
# But for clarity and consistency, use default_factory:

# ✅ Explicit and clear:
from pydantic import Field
class Request(BaseModel):
    tags: list[str] = Field(default_factory=list)

# ❌ In DATACLASSES, mutable defaults DO break things:
from dataclasses import dataclass
@dataclass
class BadConfig:
    tags: list = []   # ALL instances share one list — classic Python gotcha!

from dataclasses import dataclass, field
@dataclass
class GoodConfig:
    tags: list = field(default_factory=list)
```

---

### Trap 2 — Forgetting `@classmethod` on field_validator in v2

```python
# ❌ WRONG — will raise a TypeError in Pydantic v2:
from pydantic import BaseModel, field_validator

class Model(BaseModel):
    name: str

    @field_validator("name")
    def validate_name(cls, v: str) -> str:   # missing @classmethod!
        return v.upper()

# ✅ CORRECT:
class Model(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.upper()
```

---

### Trap 3 — Using v1 API in v2

```python
# ❌ Will raise AttributeError or DeprecationWarning in Pydantic v2:
model.dict()
model.json()
Model.parse_obj(data)
Model.schema()

# ✅ v2 equivalents:
model.model_dump()
model.model_dump_json()
Model.model_validate(data)
Model.model_json_schema()
```

---

## 🔥 Rapid-Fire Revision

```
Q: Type hints enforced at runtime?
A: No. Python ignores them. Only static analysis tools (mypy, pyright) use them.
   Pydantic enforces them at runtime.

Q: Optional[str] vs str | None?
A: Identical. str | None is the modern Python 3.10+ syntax.

Q: What does Pydantic do that dataclass doesn't?
A: Runtime validation — coerces compatible types, raises ValidationError on bad data.

Q: What does Field(gt=0) mean?
A: Value must be strictly greater than 0. ge=0 means >= 0.

Q: How do you get a dict from a Pydantic model?
A: model.model_dump() — returns a plain Python dict, nested models included.

Q: How do you create a Pydantic model from a dict?
A: Model.model_validate(my_dict)

Q: What does model_json_schema() return?
A: A dict in JSON Schema format — used for OpenAI function calling / structured outputs.

Q: Pydantic v1 vs v2 key change?
A: v2 is 5-50x faster (Rust core). API changed: .dict() → .model_dump(),
   @validator → @field_validator (requires @classmethod), etc.

Q: How does FastAPI use Pydantic?
A: Request bodies are Pydantic models — auto-validated, 422 on failure.
   Response models serialized with model_dump(). Schemas power /docs.

Q: Can nested models accept plain dicts?
A: Yes — Pydantic auto-coerces {"prompt_tokens": 5} into a TokenUsage instance.
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Previous | [13 — Concurrency](../13_concurrency/theory.md) |
| ➡️ Next | [15 — Advanced Python](../15_advanced_python/theory.md) |
