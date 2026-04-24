# 🏷️ Type Hints & Pydantic — Theory

> *"Types are not a cage. They are a contract. They tell your teammates — and your future self — exactly what your code expects and what it promises to return."*

> 📝 **Practice:** [Q66 · type-hints](../python_practice_questions_100.md#q66--normal--type-hints)

---

## 🎬 The Problem: 2 AM, Production is Down

You're building an AI app. Your function takes a prompt, calls the OpenAI API, and returns a response. The code ships. The team is happy.

Three months later, a teammate passes an integer instead of a string. Your app crashes in production at 2 AM.

```python
# What your function expects:
def ask_llm(prompt: str, max_tokens: int) -> str:
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

# What your teammate wrote at 11 PM:
result = ask_llm(42, "gpt-4o")   # integer prompt, string where int expected
# → AttributeError: 'int' object has no attribute 'lower'  (somewhere deep in OpenAI SDK)
# → Stack trace 30 lines deep
# → No one knows where 42 came from
```

If you'd used type hints, your editor would have flagged this immediately. If you'd used Pydantic, the bad data would never have made it past the door.

This is why type hints and Pydantic matter — not just for correctness, but for team velocity and production reliability.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Basic annotations (`x: int`, `def f(x: int) -> str`) · `Optional` / `Union` · `List`, `Dict`, `Tuple`, `Set` · Pydantic `BaseModel` · `@field_validator`

**Should Learn** — Important for real projects, comes up regularly:
`TypeVar` · `Protocol` · `typing.Literal` · `TypedDict` · Pydantic v2 patterns · `dataclass` vs Pydantic

**Good to Know** — Useful in specific situations:
`typing.overload` · `typing.get_type_hints()` · Forward references · `TypeGuard`

**Reference** — Know it exists, look up when needed:
`typing.ParamSpec` · `typing.Concatenate` · Variance (covariant/contravariant) · `pyright` / `pyre` config

---

## 1️⃣ Why Type Hints Exist

Python is **dynamically typed** — variables have no declared type, and you can reassign anything to anything. This is great for quick scripts. It becomes a liability in large codebases.

```python
# Python without type hints — what does this function take? return?
def process(data, config, mode):
    ...

# You have to read the entire function body to find out.
# Six months later, even the author doesn't remember.
```

**Type hints** (introduced in Python 3.5 via PEP 484) let you annotate your code:

```python
def process(data: list[str], config: dict[str, int], mode: str) -> bool:
    ...
```

Now the contract is explicit. Tools like `mypy`, `pyright`, and your IDE can catch type errors before you run a single line of code.

**Key fact:** Python's type hints are NOT enforced at runtime by default. They are documentation + static analysis hints. Python runs the code regardless. Pydantic is the library that actually enforces types at runtime.

```python
# Python doesn't care at runtime:
def greet(name: str) -> str:
    return f"Hello, {name}"

greet(999)   # runs fine — Python ignores the hint
# → "Hello, 999"

# mypy WOULD catch this:
# error: Argument 1 to "greet" has incompatible type "int"; expected "str"
```

---

## 2️⃣ Basic Type Hints

The simplest annotations use Python's built-in types directly:

```python
# Variables
name: str = "Alice"
age: int = 30
score: float = 98.6
active: bool = True
nothing: None = None

# Function parameters and return types
def greet(name: str) -> str:
    return f"Hello, {name}"

def add(a: int, b: int) -> int:
    return a + b

def set_flag(value: bool) -> None:   # None return = no return value
    global FLAG
    FLAG = value

# A function that never returns (raises always):
def crash(message: str) -> None:
    raise RuntimeError(message)
```

**Why annotate variables?** Mostly for IDE support — autocomplete, hover docs, refactoring. It also makes the code self-documenting.

```python
# Without annotation — editor doesn't know what .split() is for:
result = fetch_data()

# With annotation — editor knows all str methods:
result: str = fetch_data()
result.split(",")   # IDE autocompletes correctly
```

---

## 3️⃣ Complex Types — List, Dict, Tuple, Optional, Union

For containers and compound types, Python has two syntaxes:

### The Old Way — `typing` Module (Python 3.5–3.8)

```python
from typing import List, Dict, Tuple, Set, Optional, Union, Any

def process_names(names: List[str]) -> Dict[str, int]:
    return {name: len(name) for name in names}

def get_coords() -> Tuple[float, float]:
    return (51.5, -0.1)

def find_user(user_id: int) -> Optional[str]:   # str or None
    ...

def parse(value: Union[str, int]) -> str:       # str or int
    return str(value)

def do_anything(data: Any) -> Any:              # opt-out of type checking
    return data
```

### The New Way — Python 3.10+ Built-in Syntax

```python
# Python 3.9+: use built-in types directly (no import needed):
def process_names(names: list[str]) -> dict[str, int]:
    return {name: len(name) for name in names}

def get_coords() -> tuple[float, float]:
    return (51.5, -0.1)

# Python 3.10+: use | for Union:
def find_user(user_id: int) -> str | None:      # replaces Optional[str]
    ...

def parse(value: str | int) -> str:             # replaces Union[str, int]
    return str(value)
```

### Nested Complex Types

```python
from typing import List, Dict

# List of dicts:
def get_messages() -> list[dict[str, str]]:
    return [{"role": "user", "content": "Hello"}]

# Dict with list values:
def group_by_role(messages: list[dict[str, str]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for msg in messages:
        result.setdefault(msg["role"], []).append(msg["content"])
    return result

# Optional with default:
def search(query: str, limit: int | None = None) -> list[str]:
    ...
```

---

## 4️⃣ Type Hints in Functions

### Parameters and Return Types

```python
def send_email(
    to: str,
    subject: str,
    body: str,
    cc: list[str] | None = None,
    html: bool = False,
) -> bool:
    """Returns True if sent successfully."""
    ...
```

### *args and **kwargs

```python
from typing import Any

# *args — variable positional arguments:
def log(*messages: str) -> None:
    for msg in messages:
        print(msg)

# **kwargs — variable keyword arguments:
def create_record(**fields: Any) -> dict[str, Any]:
    return dict(fields)

# Both together:
def format_output(*args: str, **kwargs: int) -> str:
    ...
```

### Callable Types

```python
from typing import Callable

# A function that takes a str and returns bool:
def filter_list(items: list[str], predicate: Callable[[str], bool]) -> list[str]:
    return [item for item in items if predicate(item)]

# A function with no args that returns str:
def run_later(callback: Callable[[], str]) -> None:
    result = callback()
    print(result)
```

### [Generator Types](../11_generators_iterators/theory.md#-chapter-3-generator-functions--yield)

```python
from typing import Generator, Iterator

def count_up(n: int) -> Generator[int, None, None]:
    for i in range(n):
        yield i

def read_lines(path: str) -> Iterator[str]:
    with open(path) as f:
        yield from f
```

---

## 5️⃣ TypedDict and dataclasses

Sometimes a plain dict or a class is the right structure — but you still want type safety.

### TypedDict — Typed Dictionaries

```python
from typing import TypedDict

class Message(TypedDict):
    role: str
    content: str

class MessageWithOptional(TypedDict, total=False):
    role: str
    content: str
    name: str   # optional — total=False means all keys are optional

# Usage:
msg: Message = {"role": "user", "content": "Hello"}
# msg["role"]  → str (IDE knows this)

# Function with TypedDict parameter:
def send(message: Message) -> None:
    print(f"{message['role']}: {message['content']}")
```

### [dataclasses](../05_oops/14_dataclasses.md#-the-basics) — Typed Classes Without Boilerplate

```python
from dataclasses import dataclass, field

@dataclass
class ChatMessage:
    role: str
    content: str
    tokens: int = 0
    metadata: dict = field(default_factory=dict)

msg = ChatMessage(role="user", content="What is Python?")
print(msg.role)     # "user"
print(msg.tokens)   # 0
print(msg)          # ChatMessage(role='user', content='What is Python?', tokens=0, metadata={})

# dataclass gives you: __init__, __repr__, __eq__ for free
# No runtime validation — just structure + type hints
```

---

## 🔤 `TypeVar` — Generic Functions

When a function should work on any type but return the SAME type it received, you need `TypeVar`.

Without it, type checkers can't track that `first([1,2,3])` returns `int`:

```python
from typing import TypeVar, List

T = TypeVar("T")   # T can be any type

def first(items: List[T]) -> T:
    return items[0]

result = first([1, 2, 3])     # type checker knows result is int
result = first(["a", "b"])    # type checker knows result is str
```

**The contract:** whatever type goes in, the same type comes back.

```python
from typing import TypeVar

T = TypeVar("T")

def identity(value: T) -> T:
    return value   # must return the same type

def swap(a: T, b: T) -> tuple[T, T]:
    return b, a    # a and b must be same type
```

**Constraining TypeVar to specific types:**

```python
from typing import TypeVar

# T can only be int or float (not str, list, etc.):
Number = TypeVar("Number", int, float)

def double(x: Number) -> Number:
    return x * 2

double(5)     # ✓ int
double(2.5)   # ✓ float
double("hi")  # ✗ type error — str not allowed
```

**Bound TypeVar — T must be a subtype of something:**

```python
from typing import TypeVar

class Animal:
    def speak(self) -> str: ...

A = TypeVar("A", bound=Animal)

def make_noise(animal: A) -> A:
    animal.speak()
    return animal   # returns same subtype, not just Animal
```

**When to use TypeVar:**
- When a function returns the same type it receives
- When two parameters must have the same type
- When building generic data structures

---

## 🦆 `typing.Protocol` — Duck Typing with Type Hints

Python has always used duck typing: "if it walks like a duck and quacks like a duck, it's a duck."
`Protocol` lets you express this in the type system — **without inheritance**.

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...
    def resize(self, factor: float) -> None: ...


# These classes DON'T inherit from Drawable:
class Circle:
    def draw(self) -> None:
        print("drawing circle")
    def resize(self, factor: float) -> None:
        self.radius *= factor

class Square:
    def draw(self) -> None:
        print("drawing square")
    def resize(self, factor: float) -> None:
        self.side *= factor

# But they SATISFY the Drawable protocol:
def render(shape: Drawable) -> None:
    shape.draw()

render(Circle())   # ✓  — no inheritance needed
render(Square())   # ✓  — structurally compatible
```

> 📝 **Practice:** [Q67 · protocol](../python_practice_questions_100.md#q67--thinking--protocol) · [Q83 · compare-abc-protocol](../python_practice_questions_100.md#q83--interview--compare-abc-protocol)


**Protocol vs ABC — the key difference:**

```python
# ABC — requires explicit inheritance:
from abc import ABC, abstractmethod

class Drawable(ABC):
    @abstractmethod
    def draw(self): ...

class Circle(Drawable):   # MUST inherit
    def draw(self): ...

# Protocol — no inheritance needed:
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:             # does NOT need to inherit
    def draw(self): ...   # just needs the method

# Both satisfy Drawable — checked structurally
```

**`runtime_checkable` — enable isinstance() checks:**

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Sized(Protocol):
    def __len__(self) -> int: ...

print(isinstance([1, 2, 3], Sized))   # True — list has __len__
print(isinstance("hello", Sized))     # True — str has __len__
print(isinstance(42, Sized))          # False — int has no __len__
```

**Real production use — accepting any "file-like" object:**

```python
from typing import Protocol

class Readable(Protocol):
    def read(self, n: int = -1) -> bytes: ...
    def seek(self, pos: int) -> int: ...

def parse_binary(source: Readable) -> dict:
    header = source.read(4)
    # works with real files, BytesIO, network streams — anything with read/seek
    ...
```

**When to use Protocol vs ABC:**
- Use `Protocol` when you want structural typing (duck typing + type safety)
- Use `ABC` when you want to enforce inheritance hierarchy
- Protocol is the modern Pythonic choice for "accepts anything with these methods"

---

## 6️⃣ What is Pydantic?

`dataclass` gives you structure. `TypedDict` gives you annotated dicts. But neither actually **validates** your data at runtime.

**Pydantic** is a data validation library. When you create a Pydantic model with `{"age": "thirty"}`, it will raise a `ValidationError` instead of silently storing a string where an int was expected.

```
Type hints  → documentation + static analysis (editor/mypy)
Pydantic    → runtime validation + parsing + serialization

The key difference:
  dataclass: ChatMessage(role=123)   → stores 123 as role (no validation)
  Pydantic:  ChatMessage(role=123)   → coerces 123 to "123" OR raises ValidationError
```

**Why Pydantic everywhere in AI engineering:**

- FastAPI uses Pydantic models for request/response validation
- LLM structured outputs (OpenAI, Anthropic) use Pydantic schemas
- `model_json_schema()` generates JSON Schema for function calling / tool use
- Configuration management (settings from env variables)
- Parsing external API responses into typed objects

```python
# Install:
# pip install pydantic   (gets v2 by default now)
```

---

## 7️⃣ Pydantic BaseModel — Defining Models

```python
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str
    tokens: int = 0


# Creating an instance — triggers validation:
msg = ChatMessage(role="user", content="Hello")
print(msg.role)      # "user"
print(msg.tokens)    # 0  (default)
print(msg)           # role='user' content='Hello' tokens=0

# Pydantic coerces compatible types:
msg2 = ChatMessage(role="user", content="Hi", tokens="42")
print(msg2.tokens)   # 42 (int) — Pydantic converted "42" → 42

# Pydantic raises on incompatible data:
try:
    bad = ChatMessage(role="user", content="Hi", tokens="not-a-number")
except Exception as e:
    print(e)
# → ValidationError: 1 validation error for ChatMessage
#   tokens: Input should be a valid integer, unable to parse string as an integer
```

> 📝 **Practice:** [Q68 · pydantic](../python_practice_questions_100.md#q68--normal--pydantic)


### Field Types and Defaults

```python
from pydantic import BaseModel
from typing import Optional

class LLMRequest(BaseModel):
    prompt: str
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: str | None = None   # optional, defaults to None
    stop_sequences: list[str] = []

# All these work:
req1 = LLMRequest(prompt="Hello")
req2 = LLMRequest(prompt="Hello", model="claude-3-5-sonnet-20241022", temperature=0.0)
req3 = LLMRequest(prompt="Hello", stop_sequences=["END", "STOP"])
```

---

## 8️⃣ Pydantic Validation — Field Constraints and Validators

### Field() with Constraints

```python
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    age: int = Field(gt=0, lt=150)         # gt = greater than, lt = less than
    score: float = Field(ge=0.0, le=1.0)   # ge = >=, le = <=
    bio: str = Field(default="", max_length=500)
    email: str = Field(pattern=r"^[\w.-]+@[\w.-]+\.\w{2,}$")

# Valid:
user = UserProfile(username="alice", age=25, score=0.9, email="alice@example.com")

# Invalid — raises ValidationError:
try:
    bad = UserProfile(username="ab", age=25, score=0.9, email="alice@example.com")
except Exception as e:
    print(e)
# → username: String should have at least 3 characters
```

### @field_validator

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
            raise ValueError(f"role must be one of {allowed}, got '{v}'")
        return v

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("content cannot be empty or whitespace")
        return v.strip()   # validators can also transform values

# Valid:
msg = ChatMessage(role="user", content="  Hello  ")
print(msg.content)   # "Hello" — stripped by validator

# Invalid:
try:
    bad = ChatMessage(role="admin", content="Hello")
except Exception as e:
    print(e)
# → role: Value error, role must be one of {'system', 'user', 'assistant'}, got 'admin'
```

### @model_validator — Cross-Field Validation

```python
from pydantic import BaseModel, model_validator

class LLMConfig(BaseModel):
    model: str
    temperature: float = 0.7
    top_p: float = 1.0

    @model_validator(mode="after")
    def check_temperature_and_top_p(self) -> "LLMConfig":
        # OpenAI recommends not using both temperature and top_p together:
        if self.temperature != 1.0 and self.top_p != 1.0:
            raise ValueError(
                "Use either temperature or top_p, not both. "
                "Set one to its default."
            )
        return self
```

---

## 9️⃣ Pydantic for LLM Structured Outputs

This is where Pydantic becomes essential in modern AI engineering.

OpenAI and Anthropic support **structured outputs** — you provide a JSON Schema and the LLM is forced to return data matching that schema exactly. Pydantic generates that schema automatically.

```python
from pydantic import BaseModel, Field
from openai import OpenAI

class SentimentResult(BaseModel):
    sentiment: str = Field(description="positive, negative, or neutral")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    reasoning: str = Field(description="One sentence explaining the classification")

client = OpenAI()

def classify_sentiment(text: str) -> SentimentResult:
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Classify the sentiment of the text."},
            {"role": "user", "content": text},
        ],
        response_format=SentimentResult,   # Pydantic model → JSON Schema
    )
    return response.choices[0].message.parsed   # already a SentimentResult object

result = classify_sentiment("I absolutely love this product!")
print(result.sentiment)    # "positive"
print(result.confidence)   # 0.97
print(result.reasoning)    # "The text expresses strong positive emotion."
print(type(result))        # <class 'SentimentResult'>
```

**Why this matters:** without structured outputs, you're parsing free-text JSON with `json.loads()` and hoping the LLM followed your instructions. With structured outputs + Pydantic, the output is guaranteed to match your schema, and you get a typed Python object back.

---

## 🔟 Pydantic v2 vs v1 Differences

Pydantic v2 (released June 2023) rewrote the core in Rust. Most APIs look the same but there are important changes:

```python
# v1 (old):
from pydantic import validator

class Model(BaseModel):
    name: str

    @validator("name")
    def name_valid(cls, v):
        return v.upper()

# v2 (current):
from pydantic import field_validator

class Model(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        return v.upper()
```

```python
# v1 dict/json methods:
model.dict()          # → use model.model_dump() in v2
model.json()          # → use model.model_dump_json() in v2
Model.parse_obj(d)    # → use Model.model_validate(d) in v2
Model.schema()        # → use Model.model_json_schema() in v2

# v2 performance: 5-50x faster validation than v1 (Rust core)
# v2 is the standard — use it for all new projects
```

---

## 1️⃣1️⃣ model_validate, model_dump, model_json_schema

These three methods are your main tools for working with Pydantic models in production.

### model_dump() — Export to Dict

```python
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str
    tokens: int = 0

msg = ChatMessage(role="user", content="Hello", tokens=42)

# Export to dict:
msg.model_dump()
# → {'role': 'user', 'content': 'Hello', 'tokens': 42}

# Exclude fields:
msg.model_dump(exclude={"tokens"})
# → {'role': 'user', 'content': 'Hello'}

# Include only specific fields:
msg.model_dump(include={"role", "content"})
# → {'role': 'user', 'content': 'Hello'}

# Exclude None values:
msg.model_dump(exclude_none=True)

# Export to JSON string:
msg.model_dump_json()
# → '{"role":"user","content":"Hello","tokens":42}'
```

### model_validate() — Import from Dict or JSON

```python
# From dict (e.g., after json.loads() or API response):
data = {"role": "assistant", "content": "I can help with that.", "tokens": 150}
msg = ChatMessage.model_validate(data)
print(msg.role)     # "assistant"

# From JSON string:
json_str = '{"role": "user", "content": "Hello"}'
msg = ChatMessage.model_validate_json(json_str)

# From object with attributes (e.g., ORM model):
msg = ChatMessage.model_validate(orm_object, from_attributes=True)
```

### model_json_schema() — Generate JSON Schema

```python
import json

print(json.dumps(ChatMessage.model_json_schema(), indent=2))
# {
#   "title": "ChatMessage",
#   "type": "object",
#   "properties": {
#     "role":    {"title": "Role",    "type": "string"},
#     "content": {"title": "Content", "type": "string"},
#     "tokens":  {"title": "Tokens",  "type": "integer", "default": 0}
#   },
#   "required": ["role", "content"]
# }
```

This JSON Schema is exactly what you pass to OpenAI function calling, Anthropic tool use, or any JSON Schema validator.

---

## 1️⃣2️⃣ Nested Models

Real-world data is hierarchical. Pydantic handles nested models cleanly:

```python
from pydantic import BaseModel, Field
from typing import Optional

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class Choice(BaseModel):
    index: int
    message: "ChatMessage"    # forward reference (or use TYPE_CHECKING)
    finish_reason: str

class LLMResponse(BaseModel):
    id: str
    model: str
    choices: list[Choice]
    usage: TokenUsage

# Creating nested models — plain dicts get auto-coerced:
response = LLMResponse(
    id="chatcmpl-abc123",
    model="gpt-4o",
    choices=[
        {
            "index": 0,
            "message": {"role": "assistant", "content": "Hello!"},
            "finish_reason": "stop",
        }
    ],
    usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
)

print(response.choices[0].message.content)   # "Hello!"
print(response.usage.total_tokens)           # 15
print(type(response.usage))                  # <class 'TokenUsage'>

# model_dump() works recursively:
response.model_dump()
# → {'id': 'chatcmpl-abc123', 'model': 'gpt-4o',
#    'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'Hello!'},
#                 'finish_reason': 'stop'}],
#    'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}}
```

---

## 1️⃣3️⃣ Real AI Engineering Example: ChatMessage, LLMResponse, RAGResult

Here is a realistic set of Pydantic models for an AI application with Retrieval-Augmented Generation (RAG):

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import datetime

# ── Message in a conversation ──────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]   # Literal = exact values only
    content: str
    timestamp: datetime | None = None

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message content cannot be empty")
        return v


# ── A document chunk retrieved from a vector store ─────────────────────────

class RAGDocument(BaseModel):
    doc_id: str
    content: str
    source: str                              # e.g. "docs/guide.pdf"
    page: int | None = None
    score: float = Field(ge=0.0, le=1.0)    # cosine similarity score


# ── Request to the LLM ─────────────────────────────────────────────────────

class LLMRequest(BaseModel):
    messages: list[ChatMessage]
    model: str = "gpt-4o"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
    context_documents: list[RAGDocument] = []


# ── Response from the LLM ──────────────────────────────────────────────────

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: TokenUsage
    finish_reason: str = "stop"
    latency_ms: float | None = None


# ── Full RAG pipeline result ───────────────────────────────────────────────

class RAGResult(BaseModel):
    query: str
    answer: str
    source_documents: list[RAGDocument]
    llm_response: LLMResponse
    total_tokens: int

    @property
    def top_source(self) -> RAGDocument | None:
        """Return highest-scoring source document."""
        if not self.source_documents:
            return None
        return max(self.source_documents, key=lambda d: d.score)


# ── Using the models together ─────────────────────────────────────────────

def build_rag_prompt(query: str, docs: list[RAGDocument]) -> list[ChatMessage]:
    context = "\n\n".join(f"[{d.source}]\n{d.content}" for d in docs)
    return [
        ChatMessage(role="system", content="Answer using the provided context."),
        ChatMessage(role="user", content=f"Context:\n{context}\n\nQuestion: {query}"),
    ]

# Parsing a real OpenAI API response into typed models:
def parse_openai_response(raw: dict, latency_ms: float) -> LLMResponse:
    return LLMResponse(
        content=raw["choices"][0]["message"]["content"],
        model=raw["model"],
        usage=raw["usage"],          # dict auto-coerced to TokenUsage
        finish_reason=raw["choices"][0]["finish_reason"],
        latency_ms=latency_ms,
    )
```

With this pattern, every piece of data in your AI pipeline is validated, typed, and serializable. You get IDE autocomplete everywhere, `ValidationError` when bad data enters the system, and `model_json_schema()` ready to pass to any LLM structured output feature.

---

## 🔥 Summary

```
TYPE HINTS:
  Not enforced at runtime (unless you use Pydantic)
  Used for: IDE support, mypy/pyright static analysis, documentation
  Syntax: str, int | None, list[str], dict[str, Any]

PYDANTIC:
  Runtime validation — raises ValidationError on bad data
  Coercion: "42" → 42 (if field type is int)
  BaseModel: the core class — define fields as class attributes
  Field(): add constraints — min_length, gt, lt, ge, le, pattern
  @field_validator: custom per-field validation logic
  @model_validator: cross-field validation (mode="after")
  model_dump(): export to dict
  model_validate(): import from dict or JSON
  model_json_schema(): export JSON Schema (for LLM function calling)

v2 vs v1:
  v1: .dict(), .json(), @validator, Model.parse_obj()
  v2: .model_dump(), .model_dump_json(), @field_validator, Model.model_validate()
  v2 is 5-50x faster (Rust core) — use v2 for all new projects

AI ENGINEERING USE CASES:
  Validate LLM inputs before sending to API (saves money + debugging time)
  Parse LLM API responses into typed objects
  model_json_schema() → JSON Schema for structured outputs / tool use
  Define ChatMessage, LLMRequest, LLMResponse, RAGDocument models
```

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Previous | [13 — Concurrency](../13_concurrency/theory.md) |
| ➡️ Next | [15 — Advanced Python](../15_advanced_python/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Concurrency — Interview Q&A](../13_concurrency/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
