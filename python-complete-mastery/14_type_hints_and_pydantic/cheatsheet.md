# ⚡ Type Hints & Pydantic — Cheatsheet

> Quick reference: type hint syntax, Pydantic models, validators, serialization, AI engineering patterns.

---

## 🏷️ Type Hint Syntax — Old vs New

```python
# OLD (typing module — Python 3.5–3.8):
from typing import List, Dict, Tuple, Set, Optional, Union, Any, Callable

def f(names: List[str]) -> Dict[str, int]: ...
def g(x: Optional[str]) -> None: ...          # Optional[X] = X | None
def h(x: Union[str, int]) -> str: ...

# NEW (Python 3.9+ built-ins, 3.10+ | syntax):
def f(names: list[str]) -> dict[str, int]: ...
def g(x: str | None) -> None: ...             # replaces Optional[str]
def h(x: str | int) -> str: ...               # replaces Union[str, int]

# Python 3.9+: use list, dict, tuple, set directly (no import)
# Python 3.10+: use | for union/optional (no import)
```

---

## 🔑 Common Type Hint Patterns

```python
from typing import Any, Callable, Literal, TypeVar

# Literals — exact allowed values:
def set_role(role: Literal["user", "assistant", "system"]) -> None: ...

# Any — opt out of type checking:
def process(data: Any) -> Any: ...

# Callable — function as argument:
def apply(fn: Callable[[str], int], value: str) -> int: ...
def run(callback: Callable[[], None]) -> None: ...

# TypeVar — generic types:
T = TypeVar("T")
def first(items: list[T]) -> T:
    return items[0]

# Annotating variables:
name: str = "Alice"
items: list[int] = []
lookup: dict[str, float] = {}

# Return None explicitly:
def side_effect() -> None: ...

# Never returns (always raises):
from typing import NoReturn
def crash(msg: str) -> NoReturn:
    raise RuntimeError(msg)
```

---

## 📦 TypedDict and dataclass

```python
from typing import TypedDict
from dataclasses import dataclass, field

# TypedDict — typed dict structure:
class Message(TypedDict):
    role: str
    content: str

class PartialMessage(TypedDict, total=False):   # all keys optional
    role: str
    content: str

# dataclass — typed class, no boilerplate:
@dataclass
class Config:
    model: str
    temperature: float = 0.7
    tags: list[str] = field(default_factory=list)

# Neither validates at runtime — just type hints + IDE support
```

---

## 🏗️ Pydantic BaseModel Patterns

```python
from pydantic import BaseModel, Field
from typing import Literal

# Basic model:
class ChatMessage(BaseModel):
    role: str
    content: str
    tokens: int = 0              # default value

# Literal field — only specific values allowed:
class StrictMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

# Optional field:
class LLMRequest(BaseModel):
    prompt: str
    model: str = "gpt-4o"
    system_prompt: str | None = None   # optional, defaults to None

# Nested model:
class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: TokenUsage                  # nested — dict auto-coerced

# List of models:
class Conversation(BaseModel):
    messages: list[ChatMessage]
    metadata: dict[str, str] = {}

# Creating instances:
msg  = ChatMessage(role="user", content="Hello")
resp = LLMResponse(
    content="Hi there!",
    model="gpt-4o",
    usage={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
)
```

---

## 🔒 Field() with Constraints

```python
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    username: str  = Field(min_length=3, max_length=50)
    age:      int  = Field(gt=0, lt=150)              # gt=>, lt=<
    score:    float = Field(ge=0.0, le=1.0)           # ge=>=, le=<=
    bio:      str  = Field(default="", max_length=500)
    email:    str  = Field(pattern=r"^[\w.-]+@[\w.-]+\.\w{2,}$")
    tags:     list[str] = Field(default_factory=list)

# Field constraints:
# min_length / max_length  → string length
# gt / lt                  → strictly greater/less than (numbers)
# ge / le                  → greater/less than or equal (numbers)
# pattern                  → regex pattern (strings)
# default                  → default value
# default_factory          → callable that returns default (for mutable types)
# description              → shows up in JSON Schema
```

---

## ✅ Validators

```python
from pydantic import BaseModel, field_validator, model_validator

class ChatMessage(BaseModel):
    role: str
    content: str

    # Single field validator:
    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        if v not in {"system", "user", "assistant"}:
            raise ValueError(f"invalid role: {v}")
        return v   # can transform the value

    # Multiple fields in one validator:
    @field_validator("content", "role")
    @classmethod
    def no_empty_strings(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("field cannot be empty")
        return v.strip()

class LLMConfig(BaseModel):
    temperature: float = 1.0
    top_p: float = 1.0

    # Cross-field validator (runs after all fields set):
    @model_validator(mode="after")
    def check_sampling_params(self) -> "LLMConfig":
        if self.temperature != 1.0 and self.top_p != 1.0:
            raise ValueError("use temperature OR top_p, not both")
        return self
```

---

## 🔄 model_dump(), model_validate(), model_json_schema()

```python
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str
    tokens: int = 0

msg = ChatMessage(role="user", content="Hello", tokens=42)

# ── Export ──────────────────────────────────────────────────────────────────

msg.model_dump()
# → {'role': 'user', 'content': 'Hello', 'tokens': 42}

msg.model_dump(exclude={"tokens"})
# → {'role': 'user', 'content': 'Hello'}

msg.model_dump(include={"role"})
# → {'role': 'user'}

msg.model_dump(exclude_none=True)    # skip fields that are None
msg.model_dump(exclude_defaults=True) # skip fields at their default value

msg.model_dump_json()
# → '{"role":"user","content":"Hello","tokens":42}'

# ── Import ──────────────────────────────────────────────────────────────────

data = {"role": "assistant", "content": "Sure!", "tokens": 100}
ChatMessage.model_validate(data)           # from dict

ChatMessage.model_validate_json('{"role":"user","content":"Hi"}')  # from JSON string

ChatMessage.model_validate(orm_obj, from_attributes=True)   # from ORM object

# ── JSON Schema (for LLM structured output / function calling) ──────────────

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

---

## 🤖 Common AI Engineering Pydantic Models

```python
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

# Chat message:
class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
    timestamp: datetime | None = None

# LLM request:
class LLMRequest(BaseModel):
    messages: list[ChatMessage]
    model: str = "gpt-4o"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
    stream: bool = False

# LLM response:
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

# RAG document chunk:
class RAGDocument(BaseModel):
    doc_id: str
    content: str
    source: str
    page: int | None = None
    score: float = Field(ge=0.0, le=1.0)

# Full RAG result:
class RAGResult(BaseModel):
    query: str
    answer: str
    source_documents: list[RAGDocument]
    llm_response: LLMResponse

# Structured LLM output (for function calling / structured response):
class SentimentResult(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
```

---

## 🆚 Pydantic v1 vs v2 Migration

```python
# v1 (old — avoid for new projects):
from pydantic import validator

class OldModel(BaseModel):
    name: str

    @validator("name")
    def validate_name(cls, v):
        return v.upper()

obj = OldModel(name="alice")
obj.dict()                      # export
obj.json()                      # JSON string
OldModel.parse_obj({"name": "alice"})  # import
OldModel.schema()               # JSON Schema

# v2 (current):
from pydantic import field_validator

class NewModel(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.upper()

obj = NewModel(name="alice")
obj.model_dump()                # export
obj.model_dump_json()           # JSON string
NewModel.model_validate({"name": "alice"})  # import
NewModel.model_json_schema()    # JSON Schema
```

---

## 🔥 Rapid-Fire

```
Q: Are type hints enforced at runtime?
A: No — Python ignores them. Pydantic enforces them.

Q: Optional[str] vs str | None?
A: Identical — str | None is the modern syntax (Python 3.10+).

Q: Pydantic vs dataclass?
A: dataclass: structure + no validation. Pydantic: structure + runtime validation.

Q: What does Field(gt=0) mean?
A: Value must be greater than 0 (strict). ge=0 means >= 0.

Q: How does Pydantic help with OpenAI structured outputs?
A: model_json_schema() generates the JSON Schema you pass to response_format.
   OpenAI returns data guaranteed to match that schema.

Q: model_dump vs model_dump_json?
A: model_dump() → Python dict. model_dump_json() → JSON string.

Q: Can nested models accept plain dicts?
A: Yes — Pydantic auto-coerces dicts into the nested model type.

Q: @field_validator vs @model_validator?
A: field_validator: validates one field in isolation.
   model_validator: validates the whole model (cross-field logic).
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 🎯 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Previous | [13 — Concurrency](../13_concurrency/theory.md) |
| ➡️ Next | [15 — Advanced Python](../15_advanced_python/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Interview Q&A](./interview.md)
