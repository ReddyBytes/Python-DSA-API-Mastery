# 💻 Type Hints & Pydantic — Practice

> 30 questions covering all sections of theory.md — from basic annotations to full AI engineering models.

---

## Quick Index

| # | Difficulty | Topic |
|---|---|---|
| [Q1](#q1) | 🟢 Easy | Why type hints exist — annotate a function |
| [Q2](#q2) | 🟢 Easy | Basic type hints — primitive annotations |
| [Q3](#q3) | 🟢 Easy | Runtime enforcement — the Pydantic difference |
| [Q4](#q4) | 🟢 Easy | Optional and Union — nullable fields |
| [Q5](#q5) | 🟢 Easy | Complex container types — list/dict |
| [Q6](#q6) | 🟡 Medium | Nested complex types — list[dict[str, str]] |
| [Q7](#q7) | 🟢 Easy | Function type hints — parameters and return |
| [Q8](#q8) | 🟡 Medium | Callable types — function as argument |
| [Q9](#q9) | 🟡 Medium | *args and **kwargs with type hints |
| [Q10](#q10) | 🟡 Medium | TypedDict — typed dictionary structure |
| [Q11](#q11) | 🟡 Medium | dataclass — typed class without boilerplate |
| [Q12](#q12) | 🟡 Medium | TypedDict vs dataclass vs Pydantic |
| [Q13](#q13) | 🟡 Medium | TypeVar — generic functions |
| [Q14](#q14) | 🟡 Medium | Protocol — duck typing with type hints |
| [Q15](#q15) | 🟠 Hard | Protocol vs ABC |
| [Q16](#q16) | 🟢 Easy | Pydantic BaseModel — define a model |
| [Q17](#q17) | 🟡 Medium | Pydantic instantiation — coercion and validation |
| [Q18](#q18) | 🟡 Medium | ValidationError — catching and inspecting |
| [Q19](#q19) | 🟡 Medium | Field constraints — gt/lt/ge/le/min_length |
| [Q20](#q20) | 🟡 Medium | @field_validator — custom validation logic |
| [Q21](#q21) | 🟠 Hard | @model_validator — cross-field validation |
| [Q22](#q22) | 🟡 Medium | Pydantic for LLM outputs — SentimentResult |
| [Q23](#q23) | 🟠 Hard | model_json_schema — for OpenAI function calling |
| [Q24](#q24) | 🟡 Medium | Pydantic v1 vs v2 — API differences |
| [Q25](#q25) | 🟠 Hard | Pydantic v2 strict mode |
| [Q26](#q26) | 🟡 Medium | model_validate — import from dict and JSON |
| [Q27](#q27) | 🟡 Medium | model_dump — selective export |
| [Q28](#q28) | 🟠 Hard | Nested Pydantic models — dict auto-coercion |
| [Q29](#q29) | 🟠 Hard | Nested model_dump — recursive serialization |
| [Q30](#q30) | 🟠 Hard | Capstone — ChatMessage, TokenUsage, LLMResponse |

---

<a id="q1"></a>

### Q1 🟢 · Why type hints exist — annotate a function

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** Write a function `send_message(recipient, content, priority)` without type hints, then rewrite it with type hints where `recipient` is a `str`, `content` is a `str`, `priority` is an `int` with a default of `1`, and the function returns `bool`. Show why the annotated version is better.

<details>
<summary>💡 Hint</summary>

The annotated version makes the contract explicit. Neither version enforces types at runtime — the value is in IDE support and static analysis tools like mypy.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Without type hints — reader must guess:
def send_message(recipient, content, priority):
    ...

# With type hints — contract is explicit:
def send_message(recipient: str, content: str, priority: int = 1) -> bool:
    ...
```

**Why:** Type hints give your IDE full autocomplete, let mypy catch errors before runtime, and document intent without prose. Python itself ignores them — `send_message(123, 456, "high")` still runs without error.
</details>

---

<a id="q2"></a>

### Q2 🟢 · Basic type hints — primitive annotations

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** Annotate each of these four functions with the correct return type: `greet(name: str)` returns a greeting string, `add(a: int, b: int)` returns their sum, `set_flag(value: bool)` returns nothing, `crash(message: str)` always raises and never returns.

<details>
<summary>💡 Hint</summary>

"Returns nothing" is `-> None`. "Never returns" is `-> NoReturn` from typing (or just `-> None` is acceptable in most codebases).
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import NoReturn

def greet(name: str) -> str:
    return f"Hello, {name}"

def add(a: int, b: int) -> int:
    return a + b

def set_flag(value: bool) -> None:
    pass

def crash(message: str) -> NoReturn:
    raise RuntimeError(message)
```

**Why:** `None` means "this function runs, completes, returns nothing." `NoReturn` means "this function never completes normally" — it always raises or loops forever. Both are correct for `crash`, but `NoReturn` is more precise.
</details>

---

<a id="q3"></a>

### Q3 🟢 · Runtime enforcement — the Pydantic difference

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** Show that Python does NOT enforce type hints at runtime by calling `greet(999)` where `greet` expects a `str`. Then show that Pydantic DOES enforce types by creating a `User` model with `name: str` and `age: int` and trying to pass `age="not-a-number"`.

<details>
<summary>💡 Hint</summary>

Python runs `greet(999)` fine. Pydantic raises `ValidationError` — catch it and print the error.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel, ValidationError

def greet(name: str) -> str:
    return f"Hello, {name}"

print(greet(999))   # → "Hello, 999" — Python runs it fine

class User(BaseModel):
    name: str
    age: int

try:
    User(name="Alice", age="not-a-number")
except ValidationError as e:
    print(e)
# → 1 validation error for User
#   age: Input should be a valid integer, unable to parse string as an integer
```

**Why:** Type hints are documentation and static-analysis hints — Python's runtime ignores them. Pydantic reads those same annotations and enforces them when you construct the model.
</details>

---

<a id="q4"></a>

### Q4 🟢 · Optional and Union — nullable fields

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** Write two equivalent function signatures for `find_user(user_id: int)` that returns a `str` or `None` — one using the old `Optional[str]` syntax and one using the modern `str | None` syntax. Then write `parse(value)` that accepts either `str` or `int` using both `Union` and `|` syntax.

<details>
<summary>💡 Hint</summary>

`Optional[str]` and `str | None` are exactly identical in meaning. The `|` syntax requires Python 3.10+.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import Optional, Union

# Optional — old syntax:
def find_user_old(user_id: int) -> Optional[str]:
    return "Alice" if user_id == 1 else None

# Optional — new syntax:
def find_user(user_id: int) -> str | None:
    return "Alice" if user_id == 1 else None

# Union — old syntax:
def parse_old(value: Union[str, int]) -> str:
    return str(value)

# Union — new syntax:
def parse(value: str | int) -> str:
    return str(value)
```

**Why:** `Optional[X]` is shorthand for `Union[X, None]`. The `|` operator was introduced in Python 3.10 (PEP 604) and removes the need for imports. For new code targeting Python 3.10+, prefer `str | None`.
</details>

---

<a id="q5"></a>

### Q5 🟢 · Complex container types — list/dict

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Write `process_names(names)` that takes a list of strings and returns a dict mapping each name to its length. Write `get_coords()` that returns a tuple of two floats. Use the modern (no-import) syntax.

<details>
<summary>💡 Hint</summary>

Python 3.9+ allows `list[str]`, `dict[str, int]`, `tuple[float, float]` directly without importing from `typing`.
</details>

<details>
<summary>✅ Answer</summary>

```python
def process_names(names: list[str]) -> dict[str, int]:
    return {name: len(name) for name in names}

def get_coords() -> tuple[float, float]:
    return (51.5, -0.1)
```

**Why:** Python 3.9+ subscripted built-in types — no `from typing import List, Dict` needed. This is cleaner and is the preferred modern style.
</details>

---

<a id="q6"></a>

### Q6 🟡 · Nested complex types — list[dict[str, str]]

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Write `get_messages()` that returns a `list` of dicts with `str` keys and `str` values. Write `group_by_role(messages)` that takes that same list and returns a `dict` mapping `str` role keys to `list[str]` content values.

<details>
<summary>💡 Hint</summary>

Nest the type hints: `list[dict[str, str]]` for a list of string-to-string dicts. `dict[str, list[str]]` for a dict with list values.
</details>

<details>
<summary>✅ Answer</summary>

```python
def get_messages() -> list[dict[str, str]]:
    return [{"role": "user", "content": "Hello"}]

def group_by_role(messages: list[dict[str, str]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for msg in messages:
        result.setdefault(msg["role"], []).append(msg["content"])
    return result
```

**Why:** Nesting type hints mirrors the actual data shape. Your IDE can now infer that `result["user"]` is a `list[str]`, enabling correct autocomplete for list methods.
</details>

---

<a id="q7"></a>

### Q7 🟢 · Function type hints — parameters and return

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Write `send_email(to, subject, body, cc, html)` with full type hints: `to` and `subject` and `body` are `str`, `cc` is an optional list of strings defaulting to `None`, `html` is a `bool` defaulting to `False`, return type is `bool`.

<details>
<summary>💡 Hint</summary>

An optional list is `list[str] | None`. Set `= None` as the default for optional parameters.
</details>

<details>
<summary>✅ Answer</summary>

```python
def send_email(
    to: str,
    subject: str,
    body: str,
    cc: list[str] | None = None,
    html: bool = False,
) -> bool:
    ...
```

**Why:** Multi-line parameter style is cleaner for long signatures. `list[str] | None = None` means "caller may omit this; if omitted it is None; if provided it must be a list of strings."
</details>

---

<a id="q8"></a>

### Q8 🟡 · Callable types — function as argument

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Write `filter_list(items, predicate)` where `items` is a `list[str]` and `predicate` is a callable that takes a `str` and returns `bool`. The function returns `list[str]`. Then write `run_later(callback)` where `callback` takes no arguments and returns `str`.

<details>
<summary>💡 Hint</summary>

`Callable[[ArgType], ReturnType]` — the list contains arg types, the second element is the return type. `Callable[[], str]` means no arguments.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import Callable

def filter_list(items: list[str], predicate: Callable[[str], bool]) -> list[str]:
    return [item for item in items if predicate(item)]

def run_later(callback: Callable[[], str]) -> None:
    result = callback()
    print(result)
```

**Why:** `Callable[[str], bool]` documents that `predicate` must accept one `str` and return `bool`. Your IDE will flag it if you pass `len` (which returns `int`) where `bool` is expected.
</details>

---

<a id="q9"></a>

### Q9 🟡 · *args and **kwargs with type hints

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:** Write `log_messages(*messages)` that accepts any number of strings and prints each one. Write `create_record(**fields)` that accepts any keyword arguments of any type and returns a `dict[str, Any]`.

<details>
<summary>💡 Hint</summary>

For `*args: str`, the hint applies to each individual argument (not to the tuple). `**kwargs: Any` means each value can be any type.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import Any

def log_messages(*messages: str) -> None:
    for msg in messages:
        print(f"[LOG] {msg}")

def create_record(**fields: Any) -> dict[str, Any]:
    return dict(fields)
```

**Why:** `*messages: str` tells the type checker that every positional argument must be a `str`. `**fields: Any` opts out of per-value type checking while still documenting that keys are strings.
</details>

---

<a id="q10"></a>

### Q10 🟡 · TypedDict — typed dictionary structure

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:** Define a `Message` TypedDict with `role: str` and `content: str`. Then define a `PartialMessage` TypedDict where all keys are optional (`total=False`). Create an instance of each and access a field.

<details>
<summary>💡 Hint</summary>

`TypedDict` is from `typing`. `total=False` makes all keys optional at the type-checker level — the dict can still exist without them at runtime.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import TypedDict

class Message(TypedDict):
    role: str
    content: str

class PartialMessage(TypedDict, total=False):
    role: str
    content: str
    name: str

msg: Message = {"role": "user", "content": "Hello"}
print(msg["role"])   # IDE knows this is str

partial: PartialMessage = {"role": "assistant"}   # content not required
```

**Why:** `TypedDict` gives IDE type awareness for dict access without creating a class instance. `total=False` is useful for partial updates or optional data blobs.
</details>

---

<a id="q11"></a>

### Q11 🟡 · dataclass — typed class without boilerplate

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



**Problem:** Define a `Config` dataclass with `model: str`, `temperature: float = 0.7`, `max_tokens: int = 1000`, and `stop_sequences: list[str]` using `field(default_factory=list)`. Create an instance with just `model="gpt-4o"` and print it.

<details>
<summary>💡 Hint</summary>

Use `field(default_factory=list)` for the mutable default — never `stop_sequences: list[str] = []` in a dataclass, as that shares one list across all instances.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    stop_sequences: list[str] = field(default_factory=list)

cfg = Config(model="gpt-4o")
print(cfg)
# → Config(model='gpt-4o', temperature=0.7, max_tokens=1000, stop_sequences=[])
```

**Why:** `@dataclass` auto-generates `__init__`, `__repr__`, and `__eq__`. `field(default_factory=list)` ensures each instance gets its own list instead of sharing one mutable default.
</details>

---

<a id="q12"></a>

### Q12 🟡 · TypedDict vs dataclass vs Pydantic

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



**Problem:** Create the same structure — `role: str`, `content: str` — three ways: as a `TypedDict`, a `@dataclass`, and a Pydantic `BaseModel`. Then demonstrate the key difference: show that the dataclass stores a bad value silently, while Pydantic raises.

<details>
<summary>💡 Hint</summary>

Pass `role=123` (an int) to both the dataclass and the Pydantic model. The dataclass stores it quietly; Pydantic coerces it to `"123"` or raises.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import TypedDict
from dataclasses import dataclass
from pydantic import BaseModel

class MessageDict(TypedDict):
    role: str
    content: str

@dataclass
class MessageDC:
    role: str
    content: str

class MessageModel(BaseModel):
    role: str
    content: str

# TypedDict — no validation, just a plain dict:
d: MessageDict = {"role": "user", "content": "Hi"}

# dataclass — no validation, stores wrong type silently:
dc = MessageDC(role=123, content="Hi")
print(dc.role)   # 123 — stored without complaint

# Pydantic — coerces 123 to "123":
m = MessageModel(role=123, content="Hi")
print(m.role)    # "123" — coerced to str
```

**Why:** `TypedDict` is a plain dict with IDE hints. `@dataclass` is a class with no runtime validation. Pydantic is the only one that actually enforces types at runtime.
</details>

---

<a id="q13"></a>

### Q13 🟡 · TypeVar — generic functions

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



**Problem:** Write a generic function `first(items)` that returns the first element of a list. The return type should be the same type as the list elements — so `first([1, 2, 3])` returns `int`, and `first(["a", "b"])` returns `str`. Use `TypeVar`.

<details>
<summary>💡 Hint</summary>

`T = TypeVar("T")` — then annotate the function as `first(items: list[T]) -> T`. The `T` in and `T` out tells the type checker they're the same type.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]

n = first([1, 2, 3])     # type checker knows n is int
s = first(["a", "b"])    # type checker knows s is str
```

**Why:** Without `TypeVar`, you'd annotate the return as `Any`, losing all type information. `TypeVar` preserves the relationship: "whatever type goes in, the same type comes out."
</details>

---

<a id="q14"></a>

### Q14 🟡 · Protocol — duck typing with type hints

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



**Problem:** Define a `Drawable` Protocol with a `draw() -> None` method. Write two classes `Circle` and `Square` that each implement `draw()` but do NOT inherit from `Drawable`. Write a `render(shape: Drawable)` function that calls `draw()`. Show that both classes satisfy the protocol.

<details>
<summary>💡 Hint</summary>

Protocols use structural typing — a class satisfies a Protocol by having the right methods, not by inheriting from it. No `isinstance` check or registration needed.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("drawing circle")

class Square:
    def draw(self) -> None:
        print("drawing square")

def render(shape: Drawable) -> None:
    shape.draw()

render(Circle())   # works — Circle satisfies Drawable structurally
render(Square())   # works — Square satisfies Drawable structurally
```

**Why:** Protocol captures Python's native duck typing in the type system. Neither `Circle` nor `Square` needs to know `Drawable` exists — they just need the right methods.
</details>

---

<a id="q15"></a>

### Q15 🟠 · Protocol vs ABC

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



**Problem:** Show the same `Drawable` interface implemented as an ABC and as a Protocol. Explain the key difference. Then add `@runtime_checkable` to the Protocol and demonstrate `isinstance()` checking.

<details>
<summary>💡 Hint</summary>

ABC requires inheritance — `class Circle(DrawableABC)`. Protocol does not. `@runtime_checkable` enables `isinstance(obj, SomeProtocol)` checks at runtime.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

# ABC — requires explicit inheritance:
class DrawableABC(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class CircleABC(DrawableABC):   # MUST inherit
    def draw(self) -> None:
        print("circle")

# Protocol — no inheritance needed:
@runtime_checkable
class DrawableProto(Protocol):
    def draw(self) -> None: ...

class CircleProto:              # does NOT inherit
    def draw(self) -> None:
        print("circle")

# isinstance works with runtime_checkable Protocol:
print(isinstance(CircleProto(), DrawableProto))   # True
print(isinstance(42, DrawableProto))              # False — int has no draw()
```

**Why:** Use Protocol when you want structural typing (duck typing + type safety) — ideal for accepting third-party objects you can't modify. Use ABC when you want to enforce an inheritance hierarchy within your own codebase.
</details>

---

<a id="q16"></a>

### Q16 🟢 · Pydantic BaseModel — define a model

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)



**Problem:** Define a `ChatMessage` Pydantic model with `role: str`, `content: str`, and `tokens: int = 0`. Create an instance with `role="user"` and `content="Hello"`. Access each field and print the model.

<details>
<summary>💡 Hint</summary>

Inherit from `BaseModel`. Field defaults work the same as regular Python defaults. Access fields as attributes, not dict keys.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str
    tokens: int = 0

msg = ChatMessage(role="user", content="Hello")
print(msg.role)      # "user"
print(msg.content)   # "Hello"
print(msg.tokens)    # 0
print(msg)           # role='user' content='Hello' tokens=0
```

**Why:** Pydantic `BaseModel` generates `__init__`, `__repr__`, and validation logic from the class annotations. You use dot notation to access fields, not `msg["role"]` like a dict.
</details>

---

<a id="q17"></a>

### Q17 🟡 · Pydantic instantiation — coercion and validation

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)



**Problem:** Using the `ChatMessage` model from Q16, show that Pydantic coerces `"42"` to `42` for the `tokens` field. Then show that passing `tokens="not-a-number"` raises a `ValidationError`.

<details>
<summary>💡 Hint</summary>

Pydantic is lenient: `"42"` can be parsed as an integer, so it coerces silently. `"not-a-number"` cannot, so it raises. Catch `ValidationError` from `pydantic`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel, ValidationError

class ChatMessage(BaseModel):
    role: str
    content: str
    tokens: int = 0

# Coercion — "42" → 42:
msg = ChatMessage(role="user", content="Hi", tokens="42")
print(msg.tokens)          # 42
print(type(msg.tokens))    # <class 'int'>

# Validation error — "not-a-number" cannot be an int:
try:
    bad = ChatMessage(role="user", content="Hi", tokens="not-a-number")
except ValidationError as e:
    print(e.error_count(), "error(s)")
    print(e)
```

**Why:** Pydantic's default mode ("lax") coerces compatible types automatically. This is useful in practice — JSON fields often arrive as strings even when they should be numbers.
</details>

---

<a id="q18"></a>

### Q18 🟡 · ValidationError — catching and inspecting

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)



**Problem:** Create a `UserProfile` model with `username: str` and `age: int`. Pass `age="not-a-number"` to trigger a `ValidationError`. Catch it and print the number of errors and each error's `loc`, `msg`, and `input` fields.

<details>
<summary>💡 Hint</summary>

`e.errors()` returns a list of dicts. Each dict has `loc` (field location tuple), `msg` (error message), and `input` (the bad value that was passed).
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel, ValidationError

class UserProfile(BaseModel):
    username: str
    age: int

try:
    UserProfile(username="alice", age="not-a-number")
except ValidationError as e:
    print(f"Total errors: {e.error_count()}")
    for err in e.errors():
        print(f"  Field : {err['loc']}")
        print(f"  Error : {err['msg']}")
        print(f"  Input : {err['input']}")
```

**Why:** `ValidationError` is structured — you can iterate errors programmatically. This is how FastAPI constructs its 422 response body and how you build user-facing error messages.
</details>

---

<a id="q19"></a>

### Q19 🟡 · Field constraints — gt/lt/ge/le/min_length

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)



**Problem:** Define a `UserProfile` model using `Field()` constraints: `username` must be 3–50 chars, `age` must be > 0 and < 150, `score` must be between 0.0 and 1.0 inclusive, `email` must match a basic email regex pattern. Show a valid instance and show that a constraint violation raises `ValidationError`.

<details>
<summary>💡 Hint</summary>

`min_length`/`max_length` for strings, `gt`/`lt` for strict bounds, `ge`/`le` for inclusive bounds, `pattern` for regex. All live in `Field(...)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel, Field, ValidationError

class UserProfile(BaseModel):
    username: str   = Field(min_length=3, max_length=50)
    age:      int   = Field(gt=0, lt=150)
    score:    float = Field(ge=0.0, le=1.0)
    email:    str   = Field(pattern=r"^[\w.-]+@[\w.-]+\.\w{2,}$")

# Valid:
user = UserProfile(username="alice", age=25, score=0.9, email="alice@example.com")
print(user)

# Invalid — username too short:
try:
    bad = UserProfile(username="ab", age=25, score=0.9, email="alice@example.com")
except ValidationError as e:
    print(e)
# → username: String should have at least 3 characters
```

**Why:** `Field()` constraints are enforced both at runtime (when creating the model) and encoded in `model_json_schema()` — so they flow through automatically to OpenAI structured outputs.
</details>

---

<a id="q20"></a>

### Q20 🟡 · @field_validator — custom validation logic

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)



**Problem:** Add a `@field_validator("role")` to a `ChatMessage` model that raises `ValueError` if role is not `"system"`, `"user"`, or `"assistant"`. Add a second `@field_validator("content")` that strips whitespace and raises if the stripped string is empty.

<details>
<summary>💡 Hint</summary>

Both validators must be decorated with `@classmethod` (Pydantic v2 requirement). They receive the raw value, must return the value (possibly transformed), and raise `ValueError` to signal failure.
</details>

<details>
<summary>✅ Answer</summary>

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
        return v.strip()

msg = ChatMessage(role="user", content="  Hello  ")
print(msg.content)   # "Hello" — stripped by validator
```

**Why:** Validators can both validate AND transform values. Stripping whitespace in the validator means callers never need to remember to strip before passing data in.
</details>

---

<a id="q21"></a>

### Q21 🟠 · @model_validator — cross-field validation

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)



**Problem:** Define an `LLMConfig` model with `temperature: float = 1.0` and `top_p: float = 1.0`. Add a `@model_validator(mode="after")` that raises if both `temperature` and `top_p` are set to non-default values simultaneously (OpenAI recommends using one or the other, not both).

<details>
<summary>💡 Hint</summary>

`mode="after"` means the validator runs after all individual fields are validated and set. `self` is the model instance with all fields accessible.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel, model_validator

class LLMConfig(BaseModel):
    model: str = "gpt-4o"
    temperature: float = 1.0
    top_p: float = 1.0

    @model_validator(mode="after")
    def check_sampling_params(self) -> "LLMConfig":
        if self.temperature != 1.0 and self.top_p != 1.0:
            raise ValueError(
                "Use either temperature or top_p, not both. "
                "Set one to its default value."
            )
        return self

# Valid — only temperature changed:
cfg = LLMConfig(model="gpt-4o", temperature=0.7)

# Invalid — both changed:
try:
    bad = LLMConfig(model="gpt-4o", temperature=0.7, top_p=0.9)
except Exception as e:
    print(e)
```

**Why:** `@field_validator` can only see one field at a time. For rules involving multiple fields together, `@model_validator(mode="after")` is the right tool — it runs once all fields are set.
</details>

---

<a id="q22"></a>

### Q22 🟡 · Pydantic for LLM outputs — SentimentResult

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)



**Problem:** Define a `SentimentResult` Pydantic model for structured LLM output with: `sentiment` as a `Literal["positive", "negative", "neutral"]`, `confidence` as a `float` constrained to 0.0–1.0 with a description, `reasoning` as a `str` with a description. Show how you'd use it as `response_format` in an OpenAI call (code comment is fine).

<details>
<summary>💡 Hint</summary>

`Literal` enforces exact allowed values. `Field(description=...)` adds the description to the JSON Schema output, which the LLM sees as instructions.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel, Field
from typing import Literal

class SentimentResult(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0–1")
    reasoning: str = Field(description="One sentence explaining the classification")

# How you'd use it with OpenAI structured outputs:
# response = client.beta.chat.completions.parse(
#     model="gpt-4o",
#     messages=[
#         {"role": "system", "content": "Classify the sentiment."},
#         {"role": "user", "content": text},
#     ],
#     response_format=SentimentResult,
# )
# result = response.choices[0].message.parsed  # already a SentimentResult
```

**Why:** The `description` fields become part of `model_json_schema()` output — OpenAI's structured outputs feature passes that schema to the model, so the descriptions serve as per-field instructions to the LLM.
</details>

---

<a id="q23"></a>

### Q23 🟠 · model_json_schema — for OpenAI function calling

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)



**Problem:** Define a `WeatherQuery` model with `location: str` (with description), `unit: Literal["celsius", "fahrenheit"]` defaulting to `"celsius"`, and `days: int` constrained 1–7 with a description. Print the JSON Schema. Then show how you'd build the OpenAI tool definition dict using the schema.

<details>
<summary>💡 Hint</summary>

`model_json_schema()` returns a plain Python dict. JSON-dump it with `indent=2` for readability. The tool definition dict has `"type": "function"` and `"function"` with `"parameters"` set to the schema.
</details>

<details>
<summary>✅ Answer</summary>

```python
import json
from pydantic import BaseModel, Field
from typing import Literal

class WeatherQuery(BaseModel):
    location: str = Field(description="City and country, e.g. 'London, UK'")
    unit: Literal["celsius", "fahrenheit"] = "celsius"
    days: int = Field(default=1, ge=1, le=7, description="Forecast days (1–7)")

print(json.dumps(WeatherQuery.model_json_schema(), indent=2))

tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather forecast",
        "parameters": WeatherQuery.model_json_schema(),
    },
}

# When OpenAI returns the args, validate them back through Pydantic:
raw_args = {"location": "London, UK", "unit": "celsius", "days": 3}
query = WeatherQuery.model_validate(raw_args)
print(query.days)   # 3 — validated int
```

**Why:** `model_json_schema()` auto-encodes all `Field()` constraints as JSON Schema properties (`minimum`, `maximum`, `enum`, etc.) — no manual schema writing required.
</details>

---

<a id="q24"></a>

### Q24 🟡 · Pydantic v1 vs v2 — API differences

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)



**Problem:** Write the v1 version of a model with `@validator` and then the v2 equivalent with `@field_validator`. Show the equivalent methods: `dict()`/`model_dump()`, `json()`/`model_dump_json()`, `parse_obj()`/`model_validate()`, `schema()`/`model_json_schema()`.

<details>
<summary>💡 Hint</summary>

The v1 methods (`dict()`, `json()`, etc.) still exist in Pydantic v2 but are deprecated. Always use the `model_` prefixed versions for new code.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel, field_validator

# v2 model (current standard):
class Model(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def upper_name(cls, v: str) -> str:
        return v.upper()

obj = Model(name="alice")

# v2 methods (use these):
obj.model_dump()                        # → {'name': 'ALICE'}
obj.model_dump_json()                   # → '{"name":"ALICE"}'
Model.model_validate({"name": "bob"})   # import from dict
Model.model_json_schema()               # JSON Schema dict

# v1 equivalents (deprecated — avoid):
# obj.dict()
# obj.json()
# Model.parse_obj({"name": "bob"})
# Model.schema()
```

**Why:** v2 added the `model_` prefix to all class and instance methods to avoid name collisions with user-defined fields. If your model has a field called `dict`, v1's `.dict()` would break — the new `model_dump()` never clashes.
</details>

---

<a id="q25"></a>

### Q25 🟠 · Pydantic v2 strict mode

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)



**Problem:** Create a `StrictUser` model using `model_config = ConfigDict(strict=True)` with `name: str` and `age: int`. Show that passing `age="30"` (a string digit) raises a `ValidationError` in strict mode, even though it would normally coerce fine.

<details>
<summary>💡 Hint</summary>

Import `ConfigDict` from `pydantic`. In strict mode, no coercion happens — `"30"` is a string, not an int, and Pydantic refuses to convert it.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel, ValidationError
from pydantic import ConfigDict

class StrictUser(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str
    age: int

# Normal (non-strict) would coerce "30" → 30. Strict refuses:
try:
    StrictUser(name="Alice", age="30")
except ValidationError as e:
    print(e)
# → age: Input should be a valid integer [type=int_type, ...]

# This works fine in strict mode — age is already an int:
user = StrictUser(name="Alice", age=30)
print(user)
```

**Why:** Strict mode is useful when you want to guarantee no silent type coercion — e.g., in internal APIs where you control all callers and want exact type matching rather than lenient parsing.
</details>

---

<a id="q26"></a>

### Q26 🟡 · model_validate — import from dict and JSON

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)



**Problem:** Using a `ChatMessage` model (role, content, tokens), use `model_validate()` to create an instance from a plain dict. Use `model_validate_json()` to create an instance from a JSON string. Show that the result is a typed `ChatMessage` object in both cases.

<details>
<summary>💡 Hint</summary>

`model_validate(dict)` is the v2 replacement for `parse_obj()`. `model_validate_json(json_str)` parses the JSON string directly without needing `json.loads()` first.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str
    tokens: int = 0

# From dict:
data = {"role": "assistant", "content": "I can help.", "tokens": 150}
msg = ChatMessage.model_validate(data)
print(msg.role)     # "assistant"
print(type(msg))    # <class 'ChatMessage'>

# From JSON string:
json_str = '{"role": "user", "content": "Hello"}'
msg2 = ChatMessage.model_validate_json(json_str)
print(msg2.content)   # "Hello"
print(type(msg2))     # <class 'ChatMessage'>
```

**Why:** `model_validate` is the standard entry point when receiving data from an API, database, or file. It runs the same validation pipeline as the constructor — you get a fully validated typed object.
</details>

---

<a id="q27"></a>

### Q27 🟡 · model_dump — selective export

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)



**Problem:** Create a `ChatMessage` with `role="user"`, `content="Hello"`, `tokens=42`. Use `model_dump()` to export all fields, then with `exclude={"tokens"}`, then with `include={"role", "content"}`, then with `exclude_none=True` on a model that has a `None` field.

<details>
<summary>💡 Hint</summary>

`exclude` and `include` take sets of field name strings. `exclude_none=True` skips any field whose value is `None` — useful for optional fields.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str
    tokens: int = 0
    name: str | None = None

msg = ChatMessage(role="user", content="Hello", tokens=42)

print(msg.model_dump())
# → {'role': 'user', 'content': 'Hello', 'tokens': 42, 'name': None}

print(msg.model_dump(exclude={"tokens"}))
# → {'role': 'user', 'content': 'Hello', 'name': None}

print(msg.model_dump(include={"role", "content"}))
# → {'role': 'user', 'content': 'Hello'}

print(msg.model_dump(exclude_none=True))
# → {'role': 'user', 'content': 'Hello', 'tokens': 42}
```

**Why:** `exclude_none=True` is essential when sending data to APIs that don't accept null fields. `include` and `exclude` give surgical control over what gets serialized.
</details>

---

<a id="q28"></a>

### Q28 🟠 · Nested Pydantic models — dict auto-coercion

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)



**Problem:** Define `TokenUsage` with `prompt_tokens: int`, `completion_tokens: int`, `total_tokens: int`. Define `LLMResponse` with `content: str`, `model: str`, and `usage: TokenUsage`. Create an `LLMResponse` passing `usage` as a plain dict (not a `TokenUsage` instance). Verify the `usage` field is a `TokenUsage` object.

<details>
<summary>💡 Hint</summary>

Pydantic auto-coerces nested dicts into the declared nested model type. The dict `{"prompt_tokens": 10, ...}` becomes a `TokenUsage` instance automatically.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: TokenUsage

# Pass usage as a plain dict — Pydantic coerces it to TokenUsage:
response = LLMResponse(
    content="Python was created by Guido van Rossum.",
    model="gpt-4o",
    usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
)

print(type(response.usage))               # <class 'TokenUsage'>
print(response.usage.total_tokens)        # 15
print(response.usage.prompt_tokens)       # 10
```

**Why:** This dict-to-model coercion is critical for parsing real API responses — you receive a raw JSON dict and Pydantic turns the nested objects into proper typed models automatically, with full validation.
</details>

---

<a id="q29"></a>

### Q29 🟠 · Nested model_dump — recursive serialization

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)



**Problem:** Using the `LLMResponse` and `TokenUsage` models from Q28, call `model_dump()` on a response instance. Show that the result is a plain dict with the nested `TokenUsage` also serialized as a dict (not as a `TokenUsage` object). Then round-trip it: call `LLMResponse.model_validate()` on the dict to recreate the model.

<details>
<summary>💡 Hint</summary>

`model_dump()` recursively converts all nested models to dicts. `model_validate()` recursively reconstructs all nested models from dicts.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: TokenUsage

response = LLMResponse(
    content="Hello!",
    model="gpt-4o",
    usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
)

# model_dump() — recursive to plain dict:
d = response.model_dump()
print(d)
# → {'content': 'Hello!', 'model': 'gpt-4o',
#    'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}}
print(type(d["usage"]))   # <class 'dict'> — not TokenUsage

# Round-trip — reconstruct from dict:
reloaded = LLMResponse.model_validate(d)
print(type(reloaded.usage))          # <class 'TokenUsage'>
print(reloaded.usage.total_tokens)   # 15
```

**Why:** The serialize-then-validate round-trip is a common pattern for storing data in a database or Redis cache (store as JSON, reload as typed model). It works seamlessly across nested structures.
</details>

---

<a id="q30"></a>

### Q30 🟠 · Capstone — ChatMessage, TokenUsage, LLMResponse

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)



**Problem:** Build a realistic AI engineering model set from scratch:

1. `ChatMessage`: `role` as `Literal["system", "user", "assistant"]`, `content: str` with a `@field_validator` that strips whitespace and rejects empty strings
2. `TokenUsage`: `prompt_tokens: int`, `completion_tokens: int`, `total_tokens: int`
3. `LLMResponse`: `content: str`, `model: str`, `usage: TokenUsage`, `finish_reason: str = "stop"`, `latency_ms: float | None = None`, and a `@property` that estimates cost

Then instantiate an `LLMResponse` passing `usage` as a plain dict, call `model_dump(exclude_none=True)`, and round-trip through `model_validate`.

<details>
<summary>💡 Hint</summary>

Properties on Pydantic models work exactly like regular Python `@property`. For cost estimate: GPT-4o is roughly $2.50/M input tokens and $10.00/M output tokens.
</details>

<details>
<summary>✅ Answer</summary>

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("content cannot be empty")
        return stripped

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

    @property
    def cost_estimate_usd(self) -> float:
        input_cost  = (self.usage.prompt_tokens / 1_000_000) * 2.50
        output_cost = (self.usage.completion_tokens / 1_000_000) * 10.00
        return round(input_cost + output_cost, 6)

# Create — passing usage as a plain dict:
response = LLMResponse(
    content="Python was created by Guido van Rossum.",
    model="gpt-4o",
    usage={"prompt_tokens": 120, "completion_tokens": 25, "total_tokens": 145},
    finish_reason="stop",
)

print(type(response.usage))         # <class 'TokenUsage'>
print(response.usage.total_tokens)  # 145
print(response.cost_estimate_usd)   # ~0.00055

# Serialize — exclude latency_ms (it's None):
d = response.model_dump(exclude_none=True)
print(list(d.keys()))   # ['content', 'model', 'usage', 'finish_reason']

# Round-trip:
reloaded = LLMResponse.model_validate(d)
print(reloaded.model)                        # "gpt-4o"
print(reloaded.usage.prompt_tokens)          # 120
```

**Why:** This pattern — define typed models, validate at entry points, serialize for storage, round-trip back — is the backbone of every production AI engineering system. Getting comfortable with it end-to-end is the goal of this module.
</details>

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |
| ⬅️ Back to Module | [../13_concurrency/theory.md](../13_concurrency/theory.md) |
| ➡️ Next Module | [../15_advanced_python/theory.md](../15_advanced_python/theory.md) |
