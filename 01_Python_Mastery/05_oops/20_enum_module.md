# enum — Named Constants That the Type System Can Check

Picture a busy intersection. Traffic lights have three states: red, yellow, green. Now imagine the programmer who wrote the traffic controller used plain strings: `"red"`, `"green"`, `"yellow"`. Six months later, someone typos `"gren"` in a branch condition. The light stays green forever. No error is raised. The interpreter is happy. Cars are not.

An **Enum** is a traffic light where the only valid states are the ones you declared. `TrafficLight.GREEN` is not a string that could be mistyped. It is a named constant — a singleton with an identity the interpreter can verify.

Magic strings and magic numbers — `status = "activ"`, `priority = 2`, `env = "prod"` — are bugs waiting to happen. The typo passes through `if` checks silently because `"activ" != "active"` evaluates to `False` without complaint. An Enum turns a runtime surprise into an immediate `AttributeError` at the point of the typo.

---

## Learning Priority

**Must Know** — used constantly in production:
`Enum` · `.name` · `.value` · `auto()` · `@unique` · `IntEnum` · `StrEnum`

**Should Know** — important for real systems:
`Flag` · `IntFlag` · Enum with methods · Enum as dict key · Enum in dataclasses

**Good to Know** — advanced patterns:
`_generate_next_value_` · Pydantic integration · Enum with `__str__`

**Reference** — know it exists:
`EnumMeta` · `_missing_` hook · `_ignore_`

---

## Basic Enum

```python
from enum import Enum

class Color(Enum):
    RED   = 1
    GREEN = 2
    BLUE  = 3
```

Three ways to access a member:

```python
Color.RED          # ← by attribute name           → <Color.RED: 1>
Color["RED"]       # ← by name string (dict-style)  → <Color.RED: 1>
Color(1)           # ← by value                     → <Color.RED: 1>
```

### name and value

```python
c = Color.RED
c.name     # ← "RED"    (always a string)
c.value    # ← 1        (whatever you assigned)
```

### Iteration

```python
list(Color)
# [<Color.RED: 1>, <Color.GREEN: 2>, <Color.BLUE: 3>]

for c in Color:
    print(c.name, c.value)
```

### Membership

```python
Color.RED in Color      # ← True
"RED" in Color          # ← False  (string is not an Enum member)
```

### Comparison

```python
Color.RED == Color.RED    # ← True   (identity comparison)
Color.RED is Color.RED    # ← True   (same singleton)
Color.RED == 1            # ← False  (Enum is not an int unless you use IntEnum)
Color.RED == "RED"        # ← False  (same reason)
```

**Key rule:** base `Enum` members are not equal to their raw values. This is intentional — it prevents the accidental comparison that magic strings invite. Use `Color.RED.value == 1` if you need the raw comparison.

### Ordering

Base `Enum` does not support `<` or `>` — those comparisons raise `TypeError`. If you need ordering, use `IntEnum` or mix in `int` (see below).

---

## IntEnum — When Enum Values Are Integers

```python
from enum import IntEnum

class HTTPStatus(IntEnum):
    OK                  = 200
    CREATED             = 201
    BAD_REQUEST         = 400
    UNAUTHORIZED        = 401
    NOT_FOUND           = 404
    INTERNAL_ERROR      = 500
```

`IntEnum` members inherit from `int`. They behave like integers everywhere an integer is expected:

```python
HTTPStatus.OK == 200           # ← True  (because IntEnum inherits int)
HTTPStatus.OK < HTTPStatus.NOT_FOUND   # ← True  (integer comparison works)
HTTPStatus.OK + 1              # ← 201   (arithmetic works, returns plain int)

# Works with APIs that expect plain integers:
import http.client
status_code = HTTPStatus.OK
assert status_code == 200      # ← passes
```

Common use cases: HTTP status codes, OS signal numbers, database integer codes, priority levels.

**Trade-off:** Because `IntEnum` equals its integer value, you lose some of the protection that plain `Enum` provides. `HTTPStatus.OK == 200` is `True`, which means old code comparing against raw integers keeps working — useful for gradual migration.

---

## StrEnum and String Enums

### Python 3.11+ — StrEnum

```python
from enum import StrEnum

class OrderStatus(StrEnum):
    PENDING    = "pending"
    PROCESSING = "processing"
    SHIPPED    = "shipped"
    DELIVERED  = "delivered"
    CANCELLED  = "cancelled"
```

`StrEnum` members are strings. They work wherever a string is expected:

```python
OrderStatus.PENDING == "pending"     # ← True
f"Status is {OrderStatus.SHIPPED}"   # ← "Status is shipped"
json.dumps({"status": OrderStatus.PENDING})  # ← '{"status": "pending"}'
```

### Python < 3.11 — Manual str mixin

```python
class OrderStatus(str, Enum):
    PENDING    = "pending"
    PROCESSING = "processing"
    SHIPPED    = "shipped"
```

The `str` mixin achieves the same effect — members behave as strings in comparisons and serialization.

**Primary use case:** database status columns, JSON API fields, config values that must serialize cleanly without `.value`.

---

## auto() — Automatic Value Assignment

When the specific integer value does not matter, `auto()` generates one for you:

```python
from enum import Enum, auto

class Direction(Enum):
    NORTH = auto()   # ← 1
    SOUTH = auto()   # ← 2
    EAST  = auto()   # ← 3
    WEST  = auto()   # ← 4
```

Default behavior: sequential integers starting at 1.

### Custom auto() logic with _generate_next_value_

```python
class Severity(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()     # ← auto() returns the member name in lowercase

    LOW    = auto()   # ← "low"
    MEDIUM = auto()   # ← "medium"
    HIGH   = auto()   # ← "high"
```

This pattern is exactly how `StrEnum` works internally.

---

## Flag and IntFlag — Bitwise Combinations

Sometimes a value is not one state but a combination of states. Unix file permissions are the classic example: a file can be readable AND writable AND executable simultaneously. `Flag` handles this.

```
Permission
├── READ    = 4   (binary: 100)
├── WRITE   = 2   (binary: 010)
└── EXECUTE = 1   (binary: 001)

READ | WRITE = 6  (binary: 110)  ← both flags set
```

```python
from enum import Flag, auto

class Permission(Flag):
    READ    = auto()   # ← 1
    WRITE   = auto()   # ← 2
    EXECUTE = auto()   # ← 4

# Combine with |
rw = Permission.READ | Permission.WRITE

# Test membership with in
Permission.READ in rw      # ← True
Permission.EXECUTE in rw   # ← False

# Practical use
def check_access(user_perms: Permission, required: Permission) -> bool:
    return required in user_perms
```

### IntFlag — bitwise + integer compatible

```python
from enum import IntFlag

class LogLevel(IntFlag):
    DEBUG   = 1
    INFO    = 2
    WARNING = 4
    ERROR   = 8
    ALL     = DEBUG | INFO | WARNING | ERROR

active = LogLevel.INFO | LogLevel.ERROR
active & LogLevel.ERROR    # ← LogLevel.ERROR  (bitwise AND)
bool(active & LogLevel.DEBUG)   # ← False
```

`IntFlag` works with C-style bitmask APIs — pass the integer value to a C library, OS call, or any API expecting plain integers.

---

## @unique — Prevent Duplicate Values

By default, Enum allows aliases — two names with the same value:

```python
class Color(Enum):
    RED    = 1
    ROUGE  = 1    # ← alias for RED, not a separate member
```

`Color.ROUGE is Color.RED` is `True`. This is sometimes intentional (aliases), but often a mistake. Enforce uniqueness:

```python
from enum import Enum, unique

@unique
class Color(Enum):
    RED   = 1
    GREEN = 2
    BLUE  = 1    # ← raises ValueError: duplicate values found: BLUE -> RED
```

Use `@unique` whenever duplicate values would be a bug, which is most of the time.

---

## Enum Methods and Properties

Enums are classes. You can add methods, properties, and class methods.

### Instance methods

```python
from enum import Enum

class Planet(Enum):
    MERCURY = (3.303e+23, 2.4397e6)   # ← (mass_kg, radius_m)
    VENUS   = (4.869e+24, 6.0518e6)
    EARTH   = (5.976e+24, 6.37814e6)

    def __init__(self, mass, radius):
        self.mass   = mass
        self.radius = radius

    @property
    def gravity(self) -> float:
        G = 6.67430e-11
        return G * self.mass / (self.radius ** 2)

Planet.EARTH.gravity   # ← 9.802 m/s^2
```

### __str__ customization

```python
class Status(Enum):
    ACTIVE   = "active"
    INACTIVE = "inactive"

    def __str__(self):
        return self.value    # ← str(Status.ACTIVE) → "active" instead of "Status.ACTIVE"
```

### Class methods

```python
class Environment(Enum):
    DEV  = "dev"
    STAG = "staging"
    PROD = "production"

    @classmethod
    def from_env_var(cls) -> "Environment":
        import os
        val = os.environ.get("APP_ENV", "dev")
        return cls(val)    # ← looks up by value

Environment.from_env_var()   # ← reads $APP_ENV and returns the matching member
```

---

## Real-World Patterns

### HTTP status codes

```python
from enum import IntEnum

class HTTPStatus(IntEnum):
    OK           = 200
    CREATED      = 201
    NO_CONTENT   = 204
    BAD_REQUEST  = 400
    NOT_FOUND    = 404
    SERVER_ERROR = 500

    @property
    def is_success(self) -> bool:
        return 200 <= self.value < 300

    @property
    def is_error(self) -> bool:
        return self.value >= 400

def handle_response(status_code: int):
    status = HTTPStatus(status_code)
    if status.is_error:
        raise RuntimeError(f"Request failed: {status.name}")
```

### Order state machine

```python
from enum import Enum

class OrderStatus(Enum):
    PENDING    = "pending"
    CONFIRMED  = "confirmed"
    SHIPPED    = "shipped"
    DELIVERED  = "delivered"
    CANCELLED  = "cancelled"

    VALID_TRANSITIONS = {
        "PENDING":   {"CONFIRMED", "CANCELLED"},
        "CONFIRMED": {"SHIPPED", "CANCELLED"},
        "SHIPPED":   {"DELIVERED"},
        "DELIVERED": set(),
        "CANCELLED": set(),
    }

    def can_transition_to(self, next_status: "OrderStatus") -> bool:
        return next_status.name in self.VALID_TRANSITIONS.get(self.name, set())
```

### Config values

```python
from enum import Enum

class LogLevel(Enum):
    DEBUG   = "DEBUG"
    INFO    = "INFO"
    WARNING = "WARNING"
    ERROR   = "ERROR"

class AppConfig:
    log_level: LogLevel = LogLevel.INFO
```

### Enum with dataclasses

```python
from dataclasses import dataclass
from enum import Enum

class Priority(Enum):
    LOW    = 1
    MEDIUM = 2
    HIGH   = 3

@dataclass
class Task:
    name:     str
    priority: Priority = Priority.MEDIUM

t = Task(name="Deploy API", priority=Priority.HIGH)
t.priority          # ← Priority.HIGH
t.priority.value    # ← 3
```

### Enum with Pydantic

```python
from enum import Enum
from pydantic import BaseModel

class Status(str, Enum):    # ← str mixin ensures JSON serialization works
    ACTIVE   = "active"
    INACTIVE = "inactive"

class User(BaseModel):
    name:   str
    status: Status

u = User(name="Alice", status="active")   # ← Pydantic coerces string to Enum
u.status                                  # ← Status.ACTIVE
u.model_dump()                            # ← {"name": "Alice", "status": "active"}
u.model_dump_json()                       # ← '{"name":"Alice","status":"active"}'
```

If you use plain `Enum` (not `str, Enum` or `StrEnum`), `model_dump_json()` serializes the member object, not the value string. Always use `StrEnum` or `str, Enum` for Pydantic models that will be serialized.

### Enum as dict key

```python
from enum import Enum

class Season(Enum):
    SPRING = 1
    SUMMER = 2
    AUTUMN = 3
    WINTER = 4

avg_temp = {
    Season.SPRING: 15.2,
    Season.SUMMER: 27.8,
    Season.AUTUMN: 12.1,
    Season.WINTER: 3.4,
}

avg_temp[Season.SUMMER]   # ← 27.8
```

Enum members are hashable and make excellent dict keys — they are more explicit than integer or string keys and prevent key collisions from typos.

---

## Common Mistakes

```
Mistake                              | Effect                              | Fix
-------------------------------------|--------------------------------------|------------------------------
Comparing Enum to raw string         | Always False; silent logic bug       | Compare to Enum member, or use StrEnum
Forgetting .value when serializing   | JSON gets Enum object, not the value | Use StrEnum / str,Enum mixin
Mutable default values in Enum       | Shared state between members         | Use immutable types (str, int, tuple)
Not using @unique                    | Silent aliasing; member not found    | Add @unique to all Enums
Using plain Enum with Pydantic       | Serialization returns enum repr      | Use StrEnum or str,Enum mixin
Comparing IntEnum to float           | May work but is semantically wrong   | Explicit .value comparison
Assuming auto() starts at 0          | auto() starts at 1, not 0           | Check _generate_next_value_ if 0 needed
```

---

## Quick Enum Picker

```
Need                                       | Use
-------------------------------------------|------------------
Named constants, no int/str ops needed     | Enum
Integer-compatible (comparisons, C APIs)   | IntEnum
String-compatible (JSON, DB fields)        | StrEnum / str,Enum
Bitwise combinations (permissions, flags)  | Flag / IntFlag
Prevent duplicate values                   | @unique
Auto-generate values                       | auto()
```

---

## Navigation

- Previous: [14_dataclasses.md](14_dataclasses.md)
- Parent: [05_oops — Theory](theory_part1.md)
- Related: [14_dataclasses.md](14_dataclasses.md) | [14_type_hints_and_pydantic](../14_type_hints_and_pydantic/)
