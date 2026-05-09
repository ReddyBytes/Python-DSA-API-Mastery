<a id="top"></a>
# 🏷️ Type Hints & Pydantic — Theory

> *"Types are not a cage. They are a contract. They tell your teammates — and your future self — exactly what your code expects and what it promises to return."*

## 📖 Table of Contents

- [1. Why Type Hints Exist](#1-why-type-hints-exist)
- [2. Basic Type Hints](#2-basic-type-hints)
- [3. Complex Types — List, Dict, Tuple, Optional, Union](#3-complex-types--list-dict-tuple-optional-union)
  - [The Old Way — `typing` Module (Python 3.5–3.8)](#the-old-way--typing-module-python-3538)
  - [The New Way — Python 3.9+ Built-in Syntax](#the-new-way--python-39-built-in-syntax)
  - [Nested Complex Types](#nested-complex-types)
- [4. Type Hints in Functions](#4-type-hints-in-functions)
  - [Parameters and Return Types](#parameters-and-return-types)
  - [*args and **kwargs](#args-and-kwargs)
  - [Callable Types](#callable-types)
  - [Generator Types](#generator-types)
- [5. Advanced Typing — TypedDict, dataclasses, TypeVar, Protocol](#5-advanced-typing--typeddict-dataclasses-typevar-protocol)
  - [TypedDict — Typed Dictionaries](#typeddict--typed-dictionaries)
  - [dataclasses — Typed Classes Without Boilerplate](#dataclasses--typed-classes-without-boilerplate)
  - [TypeVar — Generic Functions](#typevar--generic-functions)
  - [typing.Protocol — Duck Typing with Type Hints](#typingprotocol--duck-typing-with-type-hints)
- [6. What is Pydantic?](#6-what-is-pydantic)
- [7. Pydantic BaseModel — Defining Models](#7-pydantic-basemodel--defining-models)
  - [Field Types and Defaults](#field-types-and-defaults)
- [8. Pydantic Validation — Field Constraints and Validators](#8-pydantic-validation--field-constraints-and-validators)
  - [Field() with Constraints](#field-with-constraints)
  - [@field_validator](#field_validator)
  - [@model_validator — Cross-Field Validation](#model_validator--cross-field-validation)
- [9. Pydantic for LLM Structured Outputs](#9-pydantic-for-llm-structured-outputs)
- [10. Pydantic v2 vs v1 Differences](#10-pydantic-v2-vs-v1-differences)
- [11. model_validate, model_dump, model_json_schema](#11-model_validate-model_dump-model_json_schema)
  - [model_dump() — Export to Dict](#model_dump--export-to-dict)
  - [model_validate() — Import from Dict or JSON](#model_validate--import-from-dict-or-json)
  - [model_json_schema() — Generate JSON Schema](#model_json_schema--generate-json-schema)
- [12. Nested Models](#12-nested-models)
- [13. Real AI Engineering Example](#13-real-ai-engineering-example-chatmessage-llmresponse-ragresult)
  - [🔥 Summary](#-summary)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Basic annotations (`x: int`, `def f(x: int) -> str`) · `Optional` / `Union` · `list`, `dict`, `tuple` generics · Pydantic `BaseModel` · `@field_validator`

**Should Learn** — Important for real projects, comes up regularly:
`TypeVar` · `Protocol` · `typing.Literal` · `TypedDict` · Pydantic v2 patterns · `dataclass` vs Pydantic

**Good to Know** — Useful in specific situations:
`typing.overload` · `typing.get_type_hints()` · Forward references · `TypeGuard`

**Reference** — Know it exists, look up when needed:
`typing.ParamSpec` · `typing.Concatenate` · Variance (covariant/contravariant) · `pyright` / `pyre` config

---

<a id="the-problem-2-am-production-is-down"></a>
# 🎬 The Problem: 2 AM, Production is Down

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
# → AttributeError: 'int' object has no attribute 'lower'  (somewhere deep in SDK)
# → Stack trace 30 lines deep
# → No one knows where 42 came from
```

If you'd used type hints, your editor would have flagged this immediately. If you'd used Pydantic, the bad data would never have made it past the door.

---

<a id="1-why-type-hints-exist"></a>
# 1. Why Type Hints Exist

Imagine handing a form to a new employee with no field labels — just blank boxes. They fill it out, but in the wrong order, wrong format. Six months later you're trying to decode what they wrote in box 3. Type hints are the field labels: they tell anyone reading the code exactly what each input expects and what the output will be, without having to read the whole function body.

Python is **dynamically typed** — variables have no declared type, and you can reassign anything to anything. This is great for quick scripts. It becomes a liability in large codebases.

```python
# Without type hints — what does this function take? Return?
def process(data, config, mode):
    ...
# You must read the entire function body to find out.
# Six months later, even the author doesn't remember.

# With type hints — contract is explicit:
def process(data: list[str], config: dict[str, int], mode: str) -> bool:
    ...
# IDE autocompletes correctly. mypy catches wrong argument types.
```

**How the type hint ecosystem works:**

```
Your code:      def greet(name: str) -> str
                         ↑ annotation ↑ annotation
                         │              │
                         ▼              ▼
Static analysis:  mypy / pyright reads annotations, finds type mismatches
                  → runs BEFORE your code executes
                  → catches: wrong arg types, missing fields, None not handled

IDE support:    VS Code / PyCharm reads annotations
                  → autocomplete, hover docs, inline error highlights

Runtime:        Python IGNORES annotations by default
                  → greet(999) runs fine at runtime
                  → Pydantic is the tool that enforces types at runtime
```

**Key fact:** Python's type hints are NOT enforced at runtime by default. They are documentation + static analysis hints. Pydantic is what actually enforces types at runtime.

```python
# Python doesn't care at runtime:
def greet(name: str) -> str:
    return f"Hello, {name}"

greet(999)   # runs fine — Python ignores the hint
# → "Hello, 999"

# mypy WOULD catch this before you run it:
# error: Argument 1 to "greet" has incompatible type "int"; expected "str"
```

🔍 **Good to Know:** `🔍 [Visual: Python type hints mypy diagram](https://www.google.com/search?q=python+type+hints+mypy+static+analysis+diagram)`

📝 **Practice:** [Q1 — Why type hints exist — annotate a function](./practice.md#q1--why-type-hints-exist--annotate-a-function)

> [↑ Back to Top](#top)

---

<a id="2-basic-type-hints"></a>
# 2. Basic Type Hints

Think of labeling every jar in your kitchen: "sugar", "flour", "salt". You could tell them apart by taste — but why risk it? Labels are free and prevent the mistake that ruins the recipe. Type annotations are those labels: cheap to add, expensive to skip when something goes wrong.

The simplest annotations use Python's built-in types directly:

```python
# Variables
name:    str   = "Alice"
age:     int   = 30
score:   float = 98.6
active:  bool  = True
nothing: None  = None

# Function parameters and return types
def greet(name: str) -> str:
    return f"Hello, {name}"

def add(a: int, b: int) -> int:
    return a + b

def set_flag(value: bool) -> None:   # None return = no return value
    global FLAG
    FLAG = value

# A function that never returns normally (always raises):
from typing import NoReturn
def crash(message: str) -> NoReturn:
    raise RuntimeError(message)
```

**Why annotate variables?** Mostly for IDE support — autocomplete, hover docs, refactoring safety.

```python
# Without annotation — editor doesn't know what methods are available:
result = fetch_data()
result.  # ← IDE can't suggest anything useful

# With annotation — editor knows all str methods:
result: str = fetch_data()
result.split(",")   # ← IDE autocompletes correctly
result.upper()      # ← IDE suggests all str methods
```

⚠️ **Common mistake — annotating everything as `Any`:** `from typing import Any; def f(x: Any) -> Any` is valid but defeats the purpose. `Any` opts out of all type checking for that variable. Use it only at genuine system boundaries (deserializing JSON, calling untyped third-party code).

💡 **Hint:** In Python 3.10+, `None` as a return type can be written as `-> None`. A function with no return statement implicitly returns `None`. Always annotate it — it tells readers the function is used for side effects, not its return value.

📝 **Practice:** [Q2 — Basic type hints — primitive annotations](./practice.md#q2--basic-type-hints--primitive-annotations)

> [↑ Back to Top](#top)

---

<a id="3-complex-types--list-dict-tuple-optional-union"></a>
# 3. Complex Types — List, Dict, Tuple, Optional, Union

A basic type hint handles single values. Real code deals with lists of strings, dicts mapping strings to integers, or values that might be missing entirely. Python's type system has syntax for all of these — and it evolved from a verbose style (requiring imports from `typing`) to a clean built-in style in modern Python.

```
EVOLUTION OF TYPE SYNTAX:

Python 3.5–3.8:   from typing import List, Dict, Optional, Union
                   def f(names: List[str]) -> Dict[str, int]

Python 3.9:        built-in generics — no import needed
                   def f(names: list[str]) -> dict[str, int]

Python 3.10:       | operator for Union/Optional
                   def f(x: str | None) -> int | str
```

<a id="the-old-way--typing-module-python-3538"></a>
## The Old Way — `typing` Module (Python 3.5–3.8)

You'll see this in existing codebases — important to recognize it even if you write modern syntax.

```python
from typing import List, Dict, Tuple, Set, Optional, Union, Any

def process_names(names: List[str]) -> Dict[str, int]:
    return {name: len(name) for name in names}

def get_coords() -> Tuple[float, float]:
    return (51.5, -0.1)

def find_user(user_id: int) -> Optional[str]:   # str or None
    ...

def parse(value: Union[str, int]) -> str:        # str or int
    return str(value)

def do_anything(data: Any) -> Any:               # opt-out of type checking
    return data
```

<a id="the-new-way--python-39-built-in-syntax"></a>
## The New Way — Python 3.9+ Built-in Syntax

Cleaner, no imports needed for common types:

```python
# Python 3.9+: use built-in types directly:
def process_names(names: list[str]) -> dict[str, int]:
    return {name: len(name) for name in names}

def get_coords() -> tuple[float, float]:
    return (51.5, -0.1)

# Python 3.10+: use | for Union and Optional:
def find_user(user_id: int) -> str | None:       # replaces Optional[str]
    ...

def parse(value: str | int) -> str:              # replaces Union[str, int]
    return str(value)
```

💡 **Hint:** If your project supports Python 3.9+, prefer `list[str]` over `List[str]`. If you need to support 3.8, use `from __future__ import annotations` at the top of the file — it defers annotation evaluation and lets you use the new syntax even on older Python.

<a id="nested-complex-types"></a>
## Nested Complex Types

Real data structures nest multiple levels deep. Type hints can express this:

```python
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

# Tuple with fixed structure (each position has its own type):
def parse_point(s: str) -> tuple[float, float, str]:
    x, y, label = s.split(",")
    return float(x), float(y), label   # (float, float, str) exactly
```

⚠️ **Common mistake — `tuple[str]` vs `tuple[str, ...]`:** `tuple[str]` means a tuple with exactly ONE string. `tuple[str, ...]` means a tuple with any number of strings. These are different!

📝 **Practice:** [Q4 — Optional and Union — nullable fields](./practice.md#q4--optional-and-union--nullable-fields)

> [↑ Back to Top](#top)

---

<a id="4-type-hints-in-functions"></a>
# 4. Type Hints in Functions

A function is a contract: "give me these things, I'll return that thing." Type hints make that contract visible. Without them, the contract lives only in the author's head — invisible to IDEs, linters, and the next developer. With them, every caller knows exactly what to pass and what to expect back.

<a id="parameters-and-return-types"></a>
## Parameters and Return Types

Full function signature with all parameter styles annotated:

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

💡 **Hint:** Annotate ALL parameters and the return type. Partial annotation (some params but not others) confuses type checkers — they often skip checking unannotated functions entirely.

<a id="args-and-kwargs"></a>
## *args and **kwargs

For variadic functions, annotate the type of each individual element:

```python
from typing import Any

# *args — annotate the type of each individual argument:
def log(*messages: str) -> None:
    for msg in messages:
        print(msg)
# Each element of messages is str, not messages itself is tuple[str]

# **kwargs — annotate the value type:
def create_record(**fields: Any) -> dict[str, Any]:
    return dict(fields)
# Each value in fields is Any; keys are always str

# Both together:
def format_output(*args: str, **kwargs: int) -> str:
    ...
```

⚠️ **Common mistake — annotating `*args: tuple[str]`:** The annotation for `*args` applies to each individual argument, not to the tuple as a whole. `def f(*args: str)` means each arg is a `str`, not that args is `tuple[str]`.

<a id="callable-types"></a>
## Callable Types

When a function accepts another function as an argument (higher-order functions), use `Callable`:

```python
from typing import Callable

# Callable[[arg_types], return_type]:
def filter_list(items: list[str], predicate: Callable[[str], bool]) -> list[str]:
    return [item for item in items if predicate(item)]

# A function with no args that returns str:
def run_later(callback: Callable[[], str]) -> None:
    result = callback()
    print(result)

# A function accepting any callable (unknown signature):
from typing import Callable, Any
def timer(func: Callable[..., Any]) -> Callable[..., Any]:
    ...
```

🔍 **Good to Know:** For complex callable signatures (e.g., callbacks with keyword arguments), `typing.Protocol` with `__call__` defined is cleaner than `Callable`. See section 5.

<a id="generator-types"></a>
## Generator Types

Generator functions use `Generator[YieldType, SendType, ReturnType]` or the simpler `Iterator[YieldType]`:

```python
from typing import Generator, Iterator

# Full Generator type: what it yields, what .send() passes in, what return gives back
def count_up(n: int) -> Generator[int, None, None]:
    for i in range(n):
        yield i

# Iterator is simpler — use when you only need to iterate (most cases):
def read_lines(path: str) -> Iterator[str]:
    with open(path) as f:
        yield from f
```

💡 **Hint:** For most generator functions, use `Iterator[YieldType]` — it's simpler and covers 95% of use cases. Only use `Generator[Y, S, R]` when the send value or return value matters.

📝 **Practice:** [Q7 — Function type hints — parameters and return](./practice.md#q7--function-type-hints--parameters-and-return)

> [↑ Back to Top](#top)

---

<a id="5-advanced-typing--typeddict-dataclasses-typevar-protocol"></a>
# 5. Advanced Typing — TypedDict, dataclasses, TypeVar, Protocol

Beyond simple annotations, Python's type system has specialized tools for four scenarios: typed dictionaries (when your data lives in dicts but you want structure), dataclasses (when you want a typed class without boilerplate), generic functions (when the return type mirrors the input type), and structural interfaces (when you want duck typing with type safety). These four tools together cover nearly every advanced typing scenario.

<a id="typeddict--typed-dictionaries"></a>
## TypedDict — Typed Dictionaries

Sometimes data lives in dictionaries — API responses, config objects, message payloads. A plain `dict[str, Any]` loses all type information. `TypedDict` lets you declare exactly which keys a dictionary has and what type each key's value is, without converting to a class.

```python
from typing import TypedDict

class Message(TypedDict):
    role: str
    content: str

class MessageWithOptional(TypedDict, total=False):
    role: str
    content: str
    name: str   # optional — total=False makes all keys optional

# Usage:
msg: Message = {"role": "user", "content": "Hello"}
# msg["role"]  → IDE knows this is str

# Function with TypedDict parameter:
def send(message: Message) -> None:
    print(f"{message['role']}: {message['content']}")
```

⚠️ **Common mistake — using TypedDict when Pydantic is better:** TypedDict gives IDE hints but NO runtime validation. If you pass `{"role": 123, "content": "hi"}` to a `Message`-typed parameter, Python runs it happily. If you need runtime enforcement, use Pydantic BaseModel instead.

💡 **Hint:** `total=False` makes ALL keys optional. For a mix of required and optional keys, define two TypedDicts and inherit one from the other: one with required fields (`total=True`), one with optional fields (`total=False`).

<a id="dataclasses--typed-classes-without-boilerplate"></a>
## dataclasses — Typed Classes Without Boilerplate

Before dataclasses, typed classes required writing `__init__`, `__repr__`, and `__eq__` manually. The `@dataclass` decorator generates all of these automatically from the field annotations — structured, typed, and zero boilerplate.

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

**dataclass vs Pydantic BaseModel:**

```
┌──────────────────────┬─────────────────────────────────────────────┐
│ Feature              │ @dataclass          │ Pydantic BaseModel     │
├──────────────────────┼─────────────────────┼────────────────────────┤
│ Runtime validation   │ ✗ None              │ ✓ Always               │
│ Type coercion        │ ✗ No                │ ✓ "42" → 42            │
│ Field constraints    │ ✗ Manual            │ ✓ Field(gt=0)          │
│ JSON serialization   │ Manual (asdict)     │ model_dump_json()      │
│ JSON parsing         │ Manual              │ model_validate_json()  │
│ Performance          │ Faster              │ Slower (validation)    │
│ Use when             │ Internal data       │ External data (API)    │
└──────────────────────┴─────────────────────┴────────────────────────┘
```

<a id="typevar--generic-functions"></a>
## TypeVar — Generic Functions

Imagine a sorting machine: it takes 10 red boxes in and gives 10 red boxes out. It doesn't know or care what's inside — it just preserves the box type. A generic function has this same property: whatever type goes in, the same type comes back. `TypeVar` is how you express that contract to the type checker.

Without `TypeVar`, a function that "returns the first element of a list" would have to return `Any`, losing all type information:

```python
from typing import TypeVar

T = TypeVar("T")   # T can be any type

def first(items: list[T]) -> T:
    return items[0]

result = first([1, 2, 3])     # type checker knows result is int ✓
result = first(["a", "b"])    # type checker knows result is str ✓
result = first([1.0, 2.0])    # type checker knows result is float ✓
```

**Constraining TypeVar to specific types:**

```python
# T can only be int or float:
Number = TypeVar("Number", int, float)

def double(x: Number) -> Number:
    return x * 2

double(5)     # ✓ int
double(2.5)   # ✓ float
double("hi")  # ✗ type error — str not allowed
```

**Bound TypeVar — T must be a subtype of a class:**

```python
class Animal:
    def speak(self) -> str: ...

A = TypeVar("A", bound=Animal)

def make_noise(animal: A) -> A:
    animal.speak()
    return animal   # returns the exact subtype, not just Animal
```

💡 **Hint — when to use TypeVar:**
- Function returns the same type it receives (`first`, `identity`, `copy`)
- Two parameters must have the same type (`swap(a: T, b: T)`)
- Building generic data structures (typed containers)

<a id="typingprotocol--duck-typing-with-type-hints"></a>
## typing.Protocol — Duck Typing with Type Hints

You hire a delivery driver. You don't care if they trained on a Ford or a Toyota — as long as they can drive and navigate. `Protocol` is Python's way of saying "I don't care what class this is, as long as it has these specific methods." No inheritance required — pure structural matching.

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

render(Circle())   # ✓ — no inheritance needed
render(Square())   # ✓ — structurally compatible
```

**Protocol vs ABC:**

```
ABC (Abstract Base Class):           Protocol:
  requires explicit inheritance         no inheritance needed
  class Circle(Drawable): ...          class Circle: ...  # just has the methods
  enforced at class definition          checked structurally by type checker
  good for: is-a hierarchies           good for: duck typing + type safety
  isinstance() works naturally          need @runtime_checkable for isinstance()
```

**`@runtime_checkable` — enable isinstance() checks:**

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

📝 **Practice:** [Q10 — TypedDict](./practice.md#q10--typeddict--typed-dictionary-structure) · [Q13 — TypeVar](./practice.md#q13--typevar--generic-functions) · [Q14 — Protocol](./practice.md#q14--protocol--duck-typing-with-type-hints)

> [↑ Back to Top](#top)

---

<a id="6-what-is-pydantic"></a>
# 6. What is Pydantic?

Type hints are name tags on a door: they tell you what's supposed to enter, but they don't physically stop anyone from walking in without a badge. Pydantic is the security guard: it reads the data at the door, checks IDs, converts compatible formats (a string "42" gets converted to int 42), and physically blocks anything that doesn't match — raising a `ValidationError` with exact details about what failed and why.

**Type hints vs Pydantic — what each does:**

```
                    TYPE HINTS              PYDANTIC BASEMODEL
                    ──────────────────────  ──────────────────────────────
When checked:       Before runtime (IDE,    At runtime (when you create
                    mypy, pyright)          an instance)

Enforcement:        NOT enforced by Python  ALWAYS enforced
                    at runtime              

On bad data:        No error — runs         Raises ValidationError with
                    happily                 exact field + reason

Coercion:           Never — passes          "42" → 42 (if field is int)
                    data as-is              None → [] (if field is list)

Use case:           Documentation, IDE      External data: API inputs,
                    support, refactoring    config files, LLM outputs
```

**Why Pydantic is everywhere in AI engineering:**

```
FastAPI           → request/response body validated automatically via Pydantic models
LLM outputs       → structured outputs (OpenAI, Anthropic) use Pydantic schemas
Function calling  → model_json_schema() generates JSON Schema for tool definitions
Config management → settings from env variables, validated at startup
API responses     → parse raw dict from API into typed, validated Python object
```

🔍 `[Visual: Pydantic validation flow diagram](https://www.google.com/search?q=pydantic+validation+flow+diagram+basemodel)`

📝 **Practice:** [Q16 — Pydantic BaseModel — define a model](./practice.md#q16--pydantic-basemodel--define-a-model)

> [↑ Back to Top](#top)

---

<a id="7-pydantic-basemodel--defining-models"></a>
# 7. Pydantic BaseModel — Defining Models

When you define a Pydantic BaseModel, you're designing a stamp mold. Any data that comes in — a dict from an API, user input, a JSON payload — gets pressed through that mold. Missing fields with defaults get filled in. Compatible types get converted. Incompatible data is rejected with a clear error message. The output is always the exact shape you defined.

```python
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str
    tokens: int = 0

# Creating an instance — triggers validation:
msg = ChatMessage(role="user", content="Hello")
print(msg.role)      # "user"
print(msg.tokens)    # 0  (default applied)
print(msg)           # role='user' content='Hello' tokens=0

# Pydantic coerces compatible types:
msg2 = ChatMessage(role="user", content="Hi", tokens="42")
print(msg2.tokens)   # 42 (int) — Pydantic converted "42" → 42

# Pydantic raises on incompatible data:
try:
    bad = ChatMessage(role="user", content="Hi", tokens="not-a-number")
except Exception as e:
    print(e)
# ValidationError: 1 validation error for ChatMessage
#   tokens: Input should be a valid integer, unable to parse string as an integer
```

**What happens internally when you create a model:**

```
Input dict/kwargs
       │
       ▼
┌─────────────────────────────────────────┐
│  Pydantic validation pipeline           │
│                                         │
│  1. Check all required fields present   │
│  2. For each field:                     │
│     a. Try to coerce to declared type   │
│     b. Run any Field() constraints      │
│     c. Run @field_validators            │
│  3. Run @model_validators               │
│  4. Return validated model instance     │
└─────────────────────────────────────────┘
       │                    │
       ▼                    ▼
  Model instance       ValidationError
  (all fields typed)   (list of all errors)
```

<a id="field-types-and-defaults"></a>
## Field Types and Defaults

All standard Python default patterns work, plus Pydantic handles mutable defaults safely:

```python
from pydantic import BaseModel

class LLMRequest(BaseModel):
    prompt: str                              # required — no default
    model: str = "gpt-4o"                   # optional with default
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: str | None = None         # optional, defaults to None
    stop_sequences: list[str] = []           # Pydantic copies [] per instance (safe)

# All these work:
req1 = LLMRequest(prompt="Hello")
req2 = LLMRequest(prompt="Hello", model="claude-3-5-sonnet-20241022", temperature=0.0)
req3 = LLMRequest(prompt="Hello", stop_sequences=["END", "STOP"])
```

💡 **Hint:** Pydantic automatically handles the mutable default argument trap that plain Python classes have. `stop_sequences: list[str] = []` in a Pydantic model is safe — each instance gets its own fresh list. In a regular dataclass, you'd need `field(default_factory=list)`.

⚠️ **Common mistake — treating Pydantic models as mutable by default:** Pydantic v2 models are mutable by default, but you can make them immutable: `model_config = ConfigDict(frozen=True)`. Immutable models are hashable and safe to use as dict keys.

📝 **Practice:** [Q17 — Pydantic instantiation — coercion and validation](./practice.md#q17--pydantic-instantiation--coercion-and-validation)

> [↑ Back to Top](#top)

---

<a id="8-pydantic-validation--field-constraints-and-validators"></a>
# 8. Pydantic Validation — Field Constraints and Validators

Field constraints are the stamp mold's measurements: "username must be 3–50 characters, age must be positive, score must be between 0 and 1." `@field_validator` is a custom inspector who runs a specific check and optionally transforms the value after the basic type check passes. `@model_validator` is the final quality control that checks whether all fields work together correctly.

<a id="field-with-constraints"></a>
## Field() with Constraints

```python
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    username:  str   = Field(min_length=3, max_length=50)
    age:       int   = Field(gt=0, lt=150)          # gt = greater than, lt = less than
    score:     float = Field(ge=0.0, le=1.0)        # ge = >=, le = <=
    bio:       str   = Field(default="", max_length=500)
    email:     str   = Field(pattern=r"^[\w.-]+@[\w.-]+\.\w{2,}$")

# Valid:
user = UserProfile(username="alice", age=25, score=0.9, email="alice@example.com")

# Invalid — raises ValidationError:
try:
    bad = UserProfile(username="ab", age=25, score=0.9, email="alice@example.com")
except Exception as e:
    print(e)
# → username: String should have at least 3 characters
```

**Field constraint quick reference:**

```
Strings:   min_length, max_length, pattern (regex)
Numbers:   gt (>), ge (>=), lt (<), le (<=), multiple_of
Lists:     min_length (min items), max_length (max items)
General:   default, default_factory, title, description, examples
```

<a id="field_validator"></a>
## @field_validator

For validation logic more complex than simple constraints — checking against a whitelist, normalizing values, cross-checking with external data:

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
        return v.strip()   # validators can also TRANSFORM the value

# Valid — content gets stripped:
msg = ChatMessage(role="user", content="  Hello  ")
print(msg.content)   # "Hello"

# Invalid:
try:
    bad = ChatMessage(role="admin", content="Hello")
except Exception as e:
    print(e)
# → role: Value error, role must be one of {'system', 'user', 'assistant'}, got 'admin'
```

**`@field_validator` execution flow:**

```
Input value
     │
     ▼
Type coercion (str → int if needed)
     │
     ▼
@field_validator runs
     │
     ├── raise ValueError("...") → added to ValidationError
     │
     └── return value  ← this value gets stored in the model
                         (can be transformed/normalized)
```

⚠️ **Common mistake — forgetting `@classmethod`:** In Pydantic v2, `@field_validator` methods must also be decorated with `@classmethod`. Forgetting it raises a confusing error at class definition time.

<a id="model_validator--cross-field-validation"></a>
## @model_validator — Cross-Field Validation

When a validation rule involves multiple fields together — "you can't set both temperature and top_p at the same time" — use `@model_validator`:

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

🔍 **Good to Know:** `mode="before"` runs before type coercion (receives raw input). `mode="after"` runs after all field validation (receives the typed model instance). Use `mode="after"` for most cross-field logic.

📝 **Practice:** [Q19 — Field constraints](./practice.md#q19--field-constraints--gtltgele-min_length) · [Q20 — @field_validator](./practice.md#q20--field_validator--custom-validation-logic)

> [↑ Back to Top](#top)

---

<a id="9-pydantic-for-llm-structured-outputs"></a>
# 9. Pydantic for LLM Structured Outputs

Imagine you ask a friend a question and they answer in a completely different format every time — sometimes JSON, sometimes free text, sometimes a numbered list. Exhausting. LLMs have the same problem: without structure, you get raw text and you have to parse it yourself, which breaks constantly. Pydantic solves this by acting as the **translation layer** between your Python types and the JSON schema that LLMs understand.

When you send a Pydantic model to an LLM (via OpenAI's structured output feature, LangChain, or LlamaIndex), Pydantic automatically generates a JSON Schema that the LLM fills in. When the response comes back, Pydantic validates and parses it into a typed Python object. You never touch raw JSON.

```
┌─────────────────── LLM Structured Output Flow ────────────────────┐
│                                                                     │
│  You define:                                                        │
│  class MovieReview(BaseModel):                                      │
│      title: str                                                     │
│      rating: int                                                    │
│      summary: str                                                   │
│                                                                     │
│         │                                                           │
│         ▼                                                           │
│  Pydantic generates JSON Schema ──────────────────────────────►    │
│  {                                                                  │
│    "type": "object",                                                │
│    "properties": {                                                  │
│      "title":   {"type": "string"},                                 │
│      "rating":  {"type": "integer"},                                │
│      "summary": {"type": "string"}                                  │
│    },                                                               │
│    "required": ["title", "rating", "summary"]                       │
│  }                                                                  │
│         │                                                           │
│         ▼                                                           │
│  LLM receives schema + prompt ──► fills in values                  │
│         │                                                           │
│         ▼                                                           │
│  Raw JSON response:                                                 │
│  {"title": "Inception", "rating": 9, "summary": "Mind-bending..."}│
│         │                                                           │
│         ▼                                                           │
│  Pydantic validates + parses ──► MovieReview(title="Inception", ...)│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**OpenAI structured outputs** (Python SDK ≥ 1.14):

```python
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI()

class MovieReview(BaseModel):
    title: str
    rating: int          # 1–10
    summary: str
    pros: list[str]
    cons: list[str]

completion = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Review the movie Inception"}
    ],
    response_format=MovieReview,   # ← pass the Pydantic class directly
)

review = completion.choices[0].message.parsed  # ← already a MovieReview instance
print(review.rating)     # → 9
print(review.pros)       # → ['Complex narrative', 'Visual effects', ...]
```

⚠️ **Common Mistake:** Using `response_format={"type": "json_object"}` (old style) gives you a raw string you must parse manually. Use `response_format=ModelClass` with `.parse()` for automatic Pydantic validation.

**LangChain with `.with_structured_output()`:**

```python
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class ExtractedData(BaseModel):
    person_name: str
    company: str
    role: str

llm = ChatOpenAI(model="gpt-4o")
structured_llm = llm.with_structured_output(ExtractedData)

result = structured_llm.invoke(
    "Elon Musk is the CEO of SpaceX and Tesla."
)
# result is an ExtractedData instance — no JSON parsing needed
print(result.person_name)   # → "Elon Musk"
print(result.company)       # → "SpaceX" (or "Tesla" depending on model)
```

💡 **Hint:** `model_json_schema()` shows you exactly what schema Pydantic sends to the LLM. Use this for debugging when the LLM returns unexpected values.

```python
import json
print(json.dumps(MovieReview.model_json_schema(), indent=2))
```

🔍 **Good to Know:** Pydantic v2 is the preferred library for structured LLM outputs in production. OpenAI, Anthropic, and most LLM frameworks have first-class support for it.

🔍 [Visual: Pydantic LLM structured output workflow](https://www.google.com/search?q=pydantic+llm+structured+output+json+schema+diagram)

📝 **Practice:** [Q21 — LLM structured output](./practice.md#q21--pydantic-for-llm-structured-outputs)

> [↑ Back to Top](#top)

---

<a id="10-pydantic-v2-vs-v1-differences"></a>
# 10. Pydantic v2 vs v1 Differences

Think of Pydantic v1 as an original iPhone — great for its time. Pydantic v2 is the current model: rewritten in Rust (via `pydantic-core`), 5–50x faster, cleaner API. Most production code you'll encounter today uses v2, but legacy codebases still run v1. Knowing the differences saves you from cryptic errors when moving between them.

```
┌──────────────────────────────────────────────────────────────────────┐
│               Pydantic v1 vs v2 — Key Differences                   │
├─────────────────────────────┬────────────────────────────────────────┤
│ Feature                     │ v1                  → v2               │
├─────────────────────────────┼────────────────────────────────────────┤
│ Import path                 │ from pydantic       (same)             │
│ Model method — export dict  │ .dict()             → .model_dump()    │
│ Model method — export JSON  │ .json()             → .model_dump_json()│
│ Construct from dict         │ Model(**d)          → Model.model_validate(d)│
│ JSON schema                 │ .schema()           → .model_json_schema()│
│ Validator decorator         │ @validator          → @field_validator │
│ Root validator              │ @root_validator     → @model_validator │
│ Config class                │ class Config:       → model_config = ConfigDict()│
│ Strict mode                 │ not supported       → Field(strict=True)|
│ Performance                 │ Python (slower)     → Rust core (5–50x faster)|
└─────────────────────────────┴────────────────────────────────────────┘
```

**Detecting which version you have:**

```python
import pydantic
print(pydantic.VERSION)    # → "2.7.1" or "1.10.x"
```

**v1 → v2 migration: most common changes:**

```python
# ── EXPORT ────────────────────────────────────────────────────────────
# v1
user.dict()
user.json()
# v2
user.model_dump()
user.model_dump_json()

# ── CONSTRUCT ─────────────────────────────────────────────────────────
# v1
User(**raw_dict)           # ← validated on construction
User.parse_obj(raw_dict)   # ← explicit parse
# v2
User(**raw_dict)           # ← still works
User.model_validate(raw_dict)  # ← preferred in v2

# ── VALIDATORS ────────────────────────────────────────────────────────
# v1
from pydantic import validator

class User(BaseModel):
    name: str

    @validator("name")
    def name_must_be_non_empty(cls, v):
        if not v.strip():
            raise ValueError("name cannot be blank")
        return v.strip()

# v2
from pydantic import field_validator

class User(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_be_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be blank")
        return v.strip()

# ── CONFIG ────────────────────────────────────────────────────────────
# v1
class User(BaseModel):
    class Config:
        str_strip_whitespace = True
        validate_assignment = True

# v2
from pydantic import ConfigDict

class User(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
```

⚠️ **Common Mistake:** Calling `.dict()` on a v2 model doesn't raise an error immediately (there's a deprecation warning), but it returns the correct data. However, relying on `.dict()` means your code silently becomes incompatible when Pydantic finally removes the alias. Always use `.model_dump()` in new code.

💡 **Hint:** Run `python -c "import pydantic; print(pydantic.VERSION)"` in any environment before assuming v1 or v2 behavior.

📝 **Practice:** [Q22 — v1 vs v2 migration](./practice.md#q22--pydantic-v1-vs-v2-migration)

> [↑ Back to Top](#top)

---

<a id="11-model_validate-model_dump-model_json_schema"></a>
# 11. model_validate, model_dump, model_json_schema

These three methods are the **import/export/describe** toolkit for Pydantic models. Think of a Pydantic model like a customs officer: `model_validate` is arriving passengers being checked (raw data → typed object), `model_dump` is departing passengers showing their passport (typed object → raw dict), and `model_json_schema` is the official document describing exactly what the customs officer accepts (typed model → JSON Schema). You'll use all three constantly in production.

<a id="model_dump--export-to-dict"></a>
## model_dump() — Export to Dict

```python
from pydantic import BaseModel
from datetime import datetime

class Order(BaseModel):
    id: int
    item: str
    quantity: int
    created_at: datetime

order = Order(id=1, item="laptop", quantity=2, created_at=datetime(2024, 1, 15))

# Basic export
order.model_dump()
# {'id': 1, 'item': 'laptop', 'quantity': 2, 'created_at': datetime(2024, 1, 15, 0, 0)}

# Include only specific fields
order.model_dump(include={"id", "item"})
# {'id': 1, 'item': 'laptop'}

# Exclude specific fields
order.model_dump(exclude={"created_at"})
# {'id': 1, 'item': 'laptop', 'quantity': 2}

# Serialize datetime as string (useful for JSON APIs)
order.model_dump(mode="json")
# {'id': 1, 'item': 'laptop', 'quantity': 2, 'created_at': '2024-01-15T00:00:00'}

# Exclude fields that are None
order.model_dump(exclude_none=True)

# Exclude fields at their default value
order.model_dump(exclude_defaults=True)

# Serialize to JSON string directly
order.model_dump_json()
# '{"id":1,"item":"laptop","quantity":2,"created_at":"2024-01-15T00:00:00"}'
```

💡 **Hint:** Use `mode="json"` when feeding the output to `json.dumps()` or an HTTP response — it converts `datetime`, `UUID`, `Decimal`, and other non-JSON-native types automatically.

<a id="model_validate--import-from-dict-or-json"></a>
## model_validate() — Import from Dict or JSON

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool

# From dict (most common — API responses, DB rows)
raw = {"name": "headphones", "price": "79.99", "in_stock": "true"}
product = Product.model_validate(raw)
# price coerced: "79.99" → 79.99
# in_stock coerced: "true" → True

# From JSON string
json_str = '{"name": "keyboard", "price": 49.99, "in_stock": false}'
product2 = Product.model_validate_json(json_str)  # ← direct from JSON string

# Strict mode — no coercion, types must match exactly
from pydantic import ValidationError

try:
    Product.model_validate(raw, strict=True)
except ValidationError as e:
    print(e)
    # price: Input should be a valid number [input_value='79.99', ...]
```

⚠️ **Common Mistake:** Using `Product(**raw_dict)` when the dict has extra keys. By default Pydantic v2 ignores extra fields (they're just dropped). If you want to catch extra keys, set `model_config = ConfigDict(extra="forbid")`.

<a id="model_json_schema--generate-json-schema"></a>
## model_json_schema() — Generate JSON Schema

```python
import json
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Max results")
    filters: list[str] = Field(default_factory=list, description="Tag filters")

schema = SearchRequest.model_json_schema()
print(json.dumps(schema, indent=2))
# {
#   "title": "SearchRequest",
#   "type": "object",
#   "properties": {
#     "query": {
#       "title": "Query",
#       "description": "Search query",
#       "minLength": 1,
#       "maxLength": 500,
#       "type": "string"
#     },
#     "limit": {
#       "title": "Limit",
#       "description": "Max results",
#       "default": 10,
#       "minimum": 1,
#       "maximum": 100,
#       "type": "integer"
#     },
#     ...
#   },
#   "required": ["query"]
# }
```

🔍 **Good to Know:** `model_json_schema()` is what OpenAI, LangChain, and other LLM frameworks call internally when you pass a Pydantic model as `response_format`. Understanding the schema helps you debug why an LLM returns unexpected values.

📝 **Practice:** [Q23 — model_dump and model_validate](./practice.md#q23--model_dump-and-model_validate)

> [↑ Back to Top](#top)

---

<a id="12-nested-models"></a>
# 12. Nested Models

Think of nested models like Russian dolls — each model can contain other models inside it, all the way down. A `BlogPost` has an `Author`, the `Author` has an `Address`, and each layer validates itself independently. You don't write nested validation logic by hand; you just compose models together and Pydantic handles the rest automatically.

This is one of Pydantic's most powerful features for real-world APIs — a single nested model can represent a complex JSON document with full validation at every level.

```
┌──────────────────────── Nested Model Hierarchy ────────────────────┐
│                                                                     │
│  BlogPost                                                           │
│  ├── title: str                                                     │
│  ├── content: str                                                   │
│  ├── author: Author          ← nested model                        │
│  │   ├── name: str                                                  │
│  │   ├── email: str                                                 │
│  │   └── address: Address    ← doubly nested model                 │
│  │       ├── city: str                                              │
│  │       └── country: str                                           │
│  └── tags: list[Tag]         ← list of nested models               │
│      └── Tag                                                        │
│          ├── name: str                                              │
│          └── color: str                                             │
│                                                                     │
│  All levels validated simultaneously on BlogPost(**data)            │
└─────────────────────────────────────────────────────────────────────┘
```

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

class Author(BaseModel):
    name: str
    email: EmailStr
    address: Address          # ← nested model as field type

class Tag(BaseModel):
    name: str
    color: str = "#000000"

class BlogPost(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str
    author: Author            # ← nested Author
    tags: list[Tag] = []      # ← list of nested models
    related_posts: list["BlogPost"] = []   # ← self-referencing

# Pydantic auto-validates all nested levels
raw_data = {
    "title": "Getting Started with Pydantic",
    "content": "Pydantic is amazing...",
    "author": {
        "name": "Alice",
        "email": "alice@example.com",
        "address": {
            "street": "123 Main St",
            "city": "San Francisco",
            "country": "US",
            "postal_code": "94105"
        }
    },
    "tags": [
        {"name": "python", "color": "#3776AB"},
        {"name": "tutorial"}         # ← missing color → uses default
    ]
}

post = BlogPost.model_validate(raw_data)
print(post.author.address.city)       # → "San Francisco"
print(post.tags[1].color)             # → "#000000"  (default applied)
```

**Exporting nested models:**

```python
# model_dump() recursively converts all nested models to dicts
post_dict = post.model_dump()
print(type(post_dict["author"]))           # → <class 'dict'>
print(type(post_dict["author"]["address"])) # → <class 'dict'>

# With mode="json" — all types (datetime, UUID, etc.) become JSON-safe
post.model_dump(mode="json")

# Exclude nested field
post.model_dump(exclude={"author": {"address": {"street"}}})
```

**Optional nested models:**

```python
from typing import Optional

class UserProfile(BaseModel):
    username: str
    address: Optional[Address] = None    # ← nested model is optional

# Works with or without address
UserProfile(username="bob")                          # address = None
UserProfile(username="bob", address={"city": "NY", "street": "5th Ave", "country": "US", "postal_code": "10001"})
```

⚠️ **Common Mistake:** Trying to pass a nested model instance where a raw dict is expected in JSON serialization. Always use `model_dump(mode="json")` when building API responses — it recursively converts everything to JSON-safe types.

💡 **Hint:** For deeply nested models with shared structures, define base models (e.g., `BaseAddress`) and inherit from them. Pydantic supports full inheritance with field overrides.

🔍 [Visual: Pydantic nested models JSON validation](https://www.google.com/search?q=pydantic+nested+models+json+validation+diagram)

📝 **Practice:** [Q24 — Nested models](./practice.md#q24--nested-models)

> [↑ Back to Top](#top)

---

<a id="13-real-ai-engineering-example-chatmessage-llmresponse-ragresult"></a>
# 13. Real AI Engineering Example — ChatMessage → LLMResponse → RAGResult

In a real AI application, data flows through several layers — user input → LLM call → structured response → retrieved documents → final answer. Each layer is a potential source of bugs if types are loose. Pydantic locks down every layer so bugs surface at validation time, not at 2am when your production app crashes on unexpected data.

This section builds a full RAG (Retrieval-Augmented Generation) pipeline using Pydantic — the same pattern used in production AI systems at scale.

```
┌──────────────── RAG Pipeline Architecture ─────────────────────────┐
│                                                                     │
│  User Input                                                         │
│  ChatMessage(role="user", content="What is RAG?")                  │
│       │                                                             │
│       ▼                                                             │
│  LLMRequest                                                         │
│  (model, messages: list[ChatMessage], temperature, max_tokens)     │
│       │                                                             │
│       ▼                                                             │
│  LLM API Call ──────────────────────────────────── (OpenAI / etc.) │
│       │                                                             │
│       ▼                                                             │
│  LLMResponse (validated)                                            │
│  (content: str, model: str, usage: TokenUsage, finish_reason)      │
│       │                                                             │
│       ▼                                                             │
│  Document Retrieval                                                 │
│  RetrievedDoc(content, source, score, metadata)                    │
│       │                                                             │
│       ▼                                                             │
│  RAGResult (final)                                                  │
│  (answer: str, sources: list[RetrievedDoc], confidence_score)      │
│       │                                                             │
│       ▼                                                             │
│  API Response (serialized via model_dump(mode="json"))             │
└─────────────────────────────────────────────────────────────────────┘
```

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional
from datetime import datetime
import uuid

# ── Layer 1: Chat Messages ────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]  # ← only 3 valid roles
    content: str = Field(..., min_length=1, max_length=32_000)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("content")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

# ── Layer 2: LLM Request ─────────────────────────────────────────────
class LLMRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model: str = "gpt-4o"
    messages: list[ChatMessage] = Field(..., min_length=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=128_000)
    stream: bool = False

    @model_validator(mode="after")
    def validate_system_message(self) -> "LLMRequest":
        # System message must be first if present
        roles = [m.role for m in self.messages]
        if "system" in roles and roles[0] != "system":
            raise ValueError("System message must be the first message")
        return self

# ── Layer 3: LLM Response ────────────────────────────────────────────
class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: TokenUsage
    finish_reason: Literal["stop", "length", "content_filter", "tool_calls"]
    response_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ── Layer 4: Retrieved Document ──────────────────────────────────────
class RetrievedDoc(BaseModel):
    doc_id: str
    content: str
    source: str                              # URL or file path
    relevance_score: float = Field(ge=0.0, le=1.0)
    metadata: dict = Field(default_factory=dict)

# ── Layer 5: Final RAG Result ────────────────────────────────────────
class RAGResult(BaseModel):
    query: str
    answer: str
    sources: list[RetrievedDoc]
    confidence_score: float = Field(ge=0.0, le=1.0)
    llm_usage: TokenUsage
    processing_time_ms: float

    @field_validator("sources")
    @classmethod
    def sort_by_relevance(cls, docs: list[RetrievedDoc]) -> list[RetrievedDoc]:
        # Always return sources sorted by relevance, highest first
        return sorted(docs, key=lambda d: d.relevance_score, reverse=True)

# ── Usage ─────────────────────────────────────────────────────────────
request = LLMRequest(
    model="gpt-4o",
    messages=[
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="What is RAG?"),
    ],
    temperature=0.3,
)

# Serialize to send to LLM API
payload = request.model_dump(mode="json", exclude={"request_id"})

# After LLM response comes back, parse it
raw_response = {
    "content": "RAG stands for Retrieval-Augmented Generation...",
    "model": "gpt-4o",
    "usage": {"prompt_tokens": 45, "completion_tokens": 120, "total_tokens": 165},
    "finish_reason": "stop",
    "response_id": "chatcmpl-abc123",
}
response = LLMResponse.model_validate(raw_response)

# Build final result
result = RAGResult(
    query="What is RAG?",
    answer=response.content,
    sources=[
        RetrievedDoc(
            doc_id="doc_001",
            content="RAG is a technique that combines...",
            source="https://docs.example.com/rag",
            relevance_score=0.95,
        )
    ],
    confidence_score=0.88,
    llm_usage=response.usage,
    processing_time_ms=230.5,
)

# Export for API response
api_payload = result.model_dump(mode="json")
```

⚠️ **Common Mistake:** Using plain `dict` or untyped JSON throughout an AI pipeline. The moment an LLM returns an unexpected field or a retrieval score is `null` instead of `0.0`, a typed Pydantic model catches it instantly. With raw dicts, you find out at runtime — in production.

💡 **Hint:** Add `model_config = ConfigDict(frozen=True)` to models that should never be mutated after creation (e.g., `LLMResponse`, `RetrievedDoc`). This gives you immutable value objects — like namedtuples but with full validation.

🔍 **Good to Know:** LangChain, LlamaIndex, and most AI frameworks use Pydantic internally for their own message/response types. Learning Pydantic well means you understand these frameworks' internals, not just how to use them.

🔍 [Visual: RAG pipeline architecture diagram](https://www.google.com/search?q=rag+pipeline+architecture+diagram+retrieval+augmented+generation)

📝 **Practice:** [Q25 — Full RAG pipeline models](./practice.md#q25--full-rag-pipeline-models)

> [↑ Back to Top](#top)

---

<a id="-summary"></a>
## 🔥 Summary

```
┌──────────────────── Type Hints & Pydantic — Mental Model ──────────┐
│                                                                     │
│  TYPE HINTS (static analysis tool):                                 │
│  ─────────────────────────────────                                  │
│  def greet(name: str) -> str: ...                                   │
│  • Zero runtime cost                                                │
│  • mypy / pyright validate at CI time                               │
│  • Use typing module for complex types                              │
│  • Python 3.9+ allows built-in generics: list[str], dict[str, int] │
│                                                                     │
│  PYDANTIC (runtime validation library):                             │
│  ──────────────────────────────────────                             │
│  class User(BaseModel):                                             │
│      name: str                                                      │
│      age: int                                                       │
│  • Validates data at runtime                                        │
│  • Coerces compatible types ("42" → 42)                             │
│  • Raises ValidationError on invalid data                           │
│  • First-class LLM structured output support                        │
│                                                                     │
│  WHEN TO USE WHICH:                                                 │
│  ──────────────────                                                 │
│  Internal functions between modules  → Type hints only             │
│  API request/response bodies         → Pydantic BaseModel          │
│  Config / env var parsing            → Pydantic Settings (v2)      │
│  LLM structured outputs              → Pydantic + OpenAI/.parse()  │
│  Database rows                       → SQLModel (Pydantic + SQLAlchemy)│
└─────────────────────────────────────────────────────────────────────┘
```

**Key takeaways:**
- Type hints = contracts for your IDE and static analysis. Zero cost.
- Pydantic = runtime validation. Use at system boundaries (API, config, LLM).
- `Optional[X]` is `Union[X, None]` — always set a default or `...` (required).
- Pydantic v2: `.model_dump()`, `.model_validate()`, `@field_validator`, `ConfigDict`.
- Nested models: compose freely — Pydantic validates all levels simultaneously.

---

<a id="-navigation"></a>
## 🔁 Navigation

**This folder:**
[theory.md](./theory.md) · [cheetsheet.md](./cheetsheet.md) · [interview.md](./interview.md) · [practice.md](./practice.md)

**Related modules:**
[15 — Advanced Python (metaclasses, descriptors)](../15_advanced_python/theory.md) · [13 — Concurrency](../13_concurrency/theory.md) · [07 — FastAPI (type hints in APIs)](../../03_API_Mastery/07_fastapi/theory.md)

**Jump to specific topics:**
[Why Type Hints Exist](#1-why-type-hints-exist) · [Pydantic BaseModel](#7-pydantic-basemodel--defining-models) · [field_validator](#field_validator) · [model_dump](#model_dump--export-to-dict) · [LLM Structured Outputs](#9-pydantic-for-llm-structured-outputs) · [Nested Models](#12-nested-models)

---

| | |
|---|---|
| ⬅ Prev Module | [13 — Concurrency](../13_concurrency/theory.md) |
| ➡ Next Module | [15 — Advanced Python](../15_advanced_python/theory.md) |

**[🏠 Back to README](../../README.md)**
