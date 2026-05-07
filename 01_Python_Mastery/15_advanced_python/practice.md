# Practice — Advanced Python

| Q | Difficulty | Topic |
|---|-----------|-------|
| [Q1](#q1--repr-and-str) | 🟢 | `__repr__` and `__str__` |
| [Q2](#q2--len-and-bool) | 🟢 | `__len__` and `__bool__` |
| [Q3](#q3--eq-and-hash) | 🟡 | `__eq__` and `__hash__` |
| [Q4](#q4--total-ordering) | 🟡 | `__lt__` and `@total_ordering` |
| [Q5](#q5--contains-and-iter) | 🟡 | `__contains__` and `__iter__` |
| [Q6](#q6--add-and-radd) | 🟡 | `__add__` and `__radd__` |
| [Q7](#q7--mul-and-rmul) | 🟡 | `__mul__` and `__rmul__` |
| [Q8](#q8--call) | 🟡 | `__call__` with state |
| [Q9](#q9--enter-and-exit) | 🟡 | `__enter__` and `__exit__` |
| [Q10](#q10--getitem-and-setitem) | 🟡 | `__getitem__` and `__setitem__` |
| [Q11](#q11--descriptor-basics) | 🟡 | Basic descriptor with `__get__` and `__set__` |
| [Q12](#q12--set_name) | 🟡 | `__set_name__` auto-registration |
| [Q13](#q13--data-vs-non-data) | 🟡 | Data vs non-data descriptor priority |
| [Q14](#q14--property-internals) | 🟠 | `@property` as a descriptor |
| [Q15](#q15--dynamic-class-creation) | 🟡 | `type()` three-argument form |
| [Q16](#q16--metaclass-basics) | 🟡 | Custom metaclass with `__new__` |
| [Q17](#q17--singleton-metaclass) | 🟠 | Singleton via metaclass `__call__` |
| [Q18](#q18--init_subclass) | 🟡 | `__init_subclass__` for registration |
| [Q19](#q19--abcmeta) | 🟠 | ABCMeta and `@abstractmethod` |
| [Q20](#q20--basic-dataclass) | 🟢 | `@dataclass` basics |
| [Q21](#q21--frozen-dataclass) | 🟢 | `frozen=True` — immutable dataclass |
| [Q22](#q22--default-factory) | 🟡 | `field(default_factory=...)` |
| [Q23](#q23--post-init) | 🟡 | `__post_init__` for derived fields |
| [Q24](#q24--order) | 🟡 | `order=True` for sortable dataclasses |
| [Q25](#q25--slots-memory) | 🟡 | `__slots__` memory comparison |
| [Q26](#q26--slots-restriction) | 🟡 | `__slots__` attribute restriction |
| [Q27](#q27--slots-inheritance) | 🟠 | `__slots__` in subclasses |
| [Q28](#q28--dir-and-callable) | 🟡 | `dir()` + `callable()` introspection |
| [Q29](#q29--dynamic-attributes) | 🟡 | `getattr` / `setattr` / `hasattr` / `delattr` |
| [Q30](#q30--inspect-signature) | 🟠 | `inspect.signature` at runtime |
| [Q31](#q31--enum-basics) | 🟡 | `Enum` — named constants |
| [Q32](#q32--intenum) | 🟡 | `IntEnum` and `Flag` |
| [Q33](#q33--abc-interface) | 🟠 | ABC as interface contract |
| [Q34](#q34--protocol) | 🟠 | `typing.Protocol` structural typing |
| [Q35](#q35--capstone) | 🟠 | Capstone: ORM-style model using metaclass + descriptors |

---

### Q1 🟢 · representation — `__repr__` and `__str__`

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Create a `Book` class with `title`, `author`, and `year`. Implement `__repr__` so that `eval(repr(b))` recreates it, and `__str__` for human-readable display like `"The Hobbit by J.R.R. Tolkien (1937)"`.

<details>
<summary>💡 Hint</summary>
`__repr__` should look like `Book('The Hobbit', 'J.R.R. Tolkien', 1937)`. Use `!r` on string fields. `__str__` can be freely formatted.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Book:
    def __init__(self, title, author, year):
        self.title  = title
        self.author = author
        self.year   = year

    def __repr__(self):
        return f"Book({self.title!r}, {self.author!r}, {self.year!r})"

    def __str__(self):
        return f"{self.title} by {self.author} ({self.year})"

b = Book("The Hobbit", "J.R.R. Tolkien", 1937)
print(repr(b))   # Book('The Hobbit', 'J.R.R. Tolkien', 1937)
print(str(b))    # The Hobbit by J.R.R. Tolkien (1937)
print(b)         # The Hobbit by J.R.R. Tolkien (1937)
```

**Why:** `__repr__` is for developers — unambiguous, ideally `eval()`-able. `__str__` is for users — readable and concise. When `__str__` is missing, Python falls back to `__repr__`.
</details>

---

### Q2 🟢 · sizing — `__len__` and `__bool__`

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Create a `Bag` class wrapping a list of items. Implement `__len__` and `__bool__`. An empty bag should be falsy. A bag with items should be truthy regardless of item values.

<details>
<summary>💡 Hint</summary>
`__bool__` returns `bool(self.items)`. If you only implement `__len__`, Python uses `len(obj) != 0` as truth value — but explicit is cleaner.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Bag:
    def __init__(self, items=None):
        self.items = list(items or [])

    def __len__(self):
        return len(self.items)

    def __bool__(self):
        return bool(self.items)

    def __repr__(self):
        return f"Bag({self.items!r})"

b1 = Bag([1, 2, 3])
b2 = Bag()

print(len(b1))   # 3
print(bool(b1))  # True
print(bool(b2))  # False

if not b2:
    print("empty bag")   # this branch
```

**Why:** `__bool__` controls `if obj:`. Explicit `__bool__` is preferred over relying on `__len__` fallback because it communicates intent clearly.
</details>

---

### Q3 🟡 · equality — `__eq__` and `__hash__`

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Create a `Point` class with `x` and `y`. Implement `__eq__` (equal when same coordinates) and `__hash__` (so Points can be used in sets and as dict keys). Show both work.

<details>
<summary>💡 Hint</summary>
Return `NotImplemented` (not `False`) when comparing with an unknown type. Hash must be consistent with equality: `hash((self.x, self.y))` works well.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return NotImplemented   # not False!

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p1 = Point(1, 2)
p2 = Point(1, 2)
p3 = Point(3, 4)

print(p1 == p2)         # True
print(p1 == p3)         # False
seen = {p1, p2, p3}
print(len(seen))        # 2 — p1 and p2 deduplicated
labels = {p1: "A", p3: "B"}
print(labels[Point(1, 2)])  # A
```

**Why:** Defining `__eq__` without `__hash__` makes the class unhashable. The contract is: equal objects must have equal hashes.
</details>

---

### Q4 🟡 · ordering — `__lt__` and `@total_ordering`

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Create a `Version` class (`major.minor.patch`). Use `@total_ordering` to provide full comparison support from just `__eq__` and `__lt__`. Show that `sorted()` works.

<details>
<summary>💡 Hint</summary>
With `@functools.total_ordering`, define `__eq__` and ONE comparison method — all six are derived automatically. Compare as tuples: `(major, minor, patch)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __eq__(self, other):
        if isinstance(other, Version):
            return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Version):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
        return NotImplemented

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self):
        return f"Version({self.major}, {self.minor}, {self.patch})"

v1 = Version(1, 0, 0)
v2 = Version(0, 9, 5)
v3 = Version(1, 1, 0)

print(v1 > v2)                     # True
print(sorted([v1, v2, v3]))        # [0.9.5, 1.0.0, 1.1.0]
```

**Why:** `@total_ordering` derives the missing 4 comparison methods from `__eq__` + `__lt__`, saving you from writing all six manually.
</details>

---

### Q5 🟡 · container — `__contains__` and `__iter__`

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Create a `WordSet` class that stores unique lowercase words. Implement `__contains__` (case-insensitive `in` check) and `__iter__` (alphabetically sorted). Show that `for word in ws` and `"Hello" in ws` both work.

<details>
<summary>💡 Hint</summary>
Store words internally as lowercase. `__contains__` converts the search term to lowercase before checking. `__iter__` returns `iter(sorted(self._words))`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class WordSet:
    def __init__(self, words=None):
        self._words = {w.lower() for w in (words or [])}

    def add(self, word):
        self._words.add(word.lower())

    def __contains__(self, word):
        return word.lower() in self._words

    def __iter__(self):
        return iter(sorted(self._words))

    def __len__(self):
        return len(self._words)

ws = WordSet(["Python", "JAVA", "rust"])
print("python" in ws)    # True
print("Hello" in ws)     # False
print(list(ws))          # ['java', 'python', 'rust']
```

**Why:** `__contains__` powers the `in` operator. `__iter__` makes the object usable in `for` loops, `list()`, and any function expecting an iterable.
</details>

---

### Q6 🟡 · arithmetic — `__add__` and `__radd__`

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Create a `Vector2D` class. Implement `__add__` (Vector + Vector and Vector + scalar) and `__radd__` (so `5 + v` also works). Test all three cases.

<details>
<summary>💡 Hint</summary>
`__radd__` is called when the left operand's `__add__` returns `NotImplemented`. For commutative operations, `__radd__` can delegate to `__add__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x + other.x, self.y + other.y)
        if isinstance(other, (int, float)):
            return Vector2D(self.x + other, self.y + other)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __repr__(self):
        return f"Vector2D({self.x}, {self.y})"

v1 = Vector2D(1, 2)
v2 = Vector2D(3, 4)
print(v1 + v2)   # Vector2D(4, 6)
print(v1 + 10)   # Vector2D(11, 12)
print(10 + v1)   # Vector2D(11, 12)  — uses __radd__
```

**Why:** `__radd__` gives the right-hand operand a chance when the left operand doesn't know how to handle the operation. Without it, `5 + v` raises `TypeError`.
</details>

---

### Q7 🟡 · arithmetic — `__mul__` and `__rmul__`

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Add `__mul__` (scalar multiplication: `v * 3`) and `__rmul__` (`3 * v`) to `Vector2D`. Add `__abs__` for magnitude. Verify `3 * v == v * 3`.

<details>
<summary>💡 Hint</summary>
`__rmul__` is called when the scalar is on the left and doesn't know how to handle Vector. For commutative scalar multiplication, `__rmul__` delegates to `__mul__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import math

class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector2D(self.x * scalar, self.y * scalar)
        return NotImplemented

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __eq__(self, other):
        if isinstance(other, Vector2D):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __repr__(self):
        return f"Vector2D({self.x}, {self.y})"

v = Vector2D(3, 4)
print(v * 2)            # Vector2D(6, 8)
print(2 * v)            # Vector2D(6, 8) — uses __rmul__
print(v * 2 == 2 * v)   # True
print(abs(v))           # 5.0
```

**Why:** `__rmul__` allows `scalar * obj` even when the scalar's type has no knowledge of your class. Without it, `2 * v` would raise `TypeError`.
</details>

---

### Q8 🟡 · callable — `__call__` with state

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Create a `Counter` callable class that increments a tally each time it's called. It should track total calls, sum of all passed values, and support `.reset()`. Test it as a decorator.

<details>
<summary>💡 Hint</summary>
Store call count and sum as instance attributes. `__call__` receives whatever arguments the caller passes. The state persists between calls — that's what makes callable objects useful.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Counter:
    def __init__(self, func=None):
        self.func    = func
        self.calls   = 0
        self.total   = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        if args and isinstance(args[0], (int, float)):
            self.total += args[0]
        if self.func:
            return self.func(*args, **kwargs)

    def reset(self):
        self.calls = 0
        self.total = 0

    def __repr__(self):
        return f"Counter(calls={self.calls}, total={self.total})"

c = Counter()
c(10)
c(20)
c(30)
print(c.calls)   # 3
print(c.total)   # 60
c.reset()
print(c.calls)   # 0

@Counter
def process(x):
    return x * 2

process(5)
process(7)
print(process.calls)   # 2
```

**Why:** Callable objects maintain state between calls. A plain function or lambda has no memory — callable classes bridge the gap between configurable functions and stateful objects.
</details>

---

### Q9 🟡 · context manager — `__enter__` and `__exit__`

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Build a `Timer` context manager class. `__enter__` records the start time. `__exit__` records the end time and stores the elapsed duration as `.elapsed`. It should also suppress `ZeroDivisionError` and print a warning instead.

<details>
<summary>💡 Hint</summary>
`__exit__` receives `(exc_type, exc_val, exc_tb)`. Return `True` to suppress an exception, `False` or `None` to propagate it. Use `time.perf_counter()` for high-resolution timing.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time

class Timer:
    def __enter__(self):
        self._start  = time.perf_counter()
        self.elapsed = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self._start
        if exc_type is ZeroDivisionError:
            print(f"Warning: ZeroDivisionError suppressed (elapsed: {self.elapsed:.6f}s)")
            return True   # suppress
        return False      # propagate all other exceptions

with Timer() as t:
    total = sum(range(1_000_000))
print(f"Elapsed: {t.elapsed:.4f}s")

with Timer() as t2:
    result = 1 / 0   # suppressed, prints warning
print(f"Still running, elapsed: {t2.elapsed:.4f}s")
```

**Why:** `__enter__` sets up the resource, `__exit__` always runs (even if an exception occurs). Returning `True` suppresses the exception; returning `False` re-raises it.
</details>

---

### Q10 🟡 · subscript — `__getitem__` and `__setitem__`

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Create a `Matrix` class that supports `m[row, col]` reads and `m[row, col] = value` writes. Initialize all cells to `0`. Raise `IndexError` for out-of-bounds access.

<details>
<summary>💡 Hint</summary>
When you write `obj[row, col]`, Python passes `(row, col)` as a tuple to `__getitem__` and `__setitem__`. Unpack the key tuple in each method.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Matrix:
    def __init__(self, rows, cols):
        self.rows  = rows
        self.cols  = cols
        self._data = [[0] * cols for _ in range(rows)]

    def _check(self, row, col):
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError(f"({row}, {col}) out of range for {self.rows}x{self.cols} matrix")

    def __getitem__(self, key):
        row, col = key
        self._check(row, col)
        return self._data[row][col]

    def __setitem__(self, key, value):
        row, col = key
        self._check(row, col)
        self._data[row][col] = value

    def __repr__(self):
        return f"Matrix({self._data!r})"

m = Matrix(3, 3)
m[0, 0] = 1
m[1, 1] = 5
m[2, 2] = 9
print(m[1, 1])   # 5
```

**Why:** `obj[a, b]` passes `(a, b)` as a tuple to `__getitem__`. This is exactly how NumPy implements multi-dimensional indexing.
</details>

---

### Q11 🟡 · descriptors — basic descriptor with `__get__` and `__set__`

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

**Problem:** Write a `Positive` descriptor that raises `ValueError` if the value is set to zero or negative. Use it on a `Circle` class with a `radius` field.

<details>
<summary>💡 Hint</summary>
Store the value in `obj.__dict__` using a private key. In `__get__`, return `self` when `obj is None` (class access). In `__set__`, validate before storing.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Positive:
    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.private)

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.name} must be positive, got {value}")
        obj.__dict__[self.private] = value

class Circle:
    radius = Positive()

    def __init__(self, radius):
        self.radius = radius   # calls Positive.__set__

    def area(self):
        import math
        return math.pi * self.radius ** 2

c = Circle(5)
print(c.area())   # 78.54...

try:
    c.radius = -1   # ValueError
except ValueError as e:
    print(e)
```

**Why:** The descriptor acts as a smart attribute — every assignment goes through `__set__`, which enforces the constraint. Multiple classes can reuse the same descriptor.
</details>

---

### Q12 🟡 · descriptors — `__set_name__` auto-registration

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

**Problem:** Write a `Typed` descriptor that enforces a specific type. Use `__set_name__` so the descriptor knows its attribute name without being told explicitly. Apply it to a `Person` class with `name: str` and `age: int`.

<details>
<summary>💡 Hint</summary>
`__set_name__(self, owner, name)` is called at class-creation time with the attribute name. Store it so `__set__` can use it in error messages.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Typed:
    def __init__(self, expected_type):
        self.expected_type = expected_type

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.private)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        obj.__dict__[self.private] = value

class Person:
    name = Typed(str)
    age  = Typed(int)

    def __init__(self, name, age):
        self.name = name
        self.age  = age

p = Person("Alice", 30)
print(p.name)   # Alice

try:
    p.age = "thirty"   # TypeError
except TypeError as e:
    print(e)
```

**Why:** Before `__set_name__` (Python 3.6+), you had to pass the attribute name manually. `__set_name__` makes descriptors self-aware without metaclass tricks.
</details>

---

### Q13 🟡 · descriptors — data vs non-data descriptor priority

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

**Problem:** Demonstrate the difference between a data descriptor (has `__set__`) and a non-data descriptor (only `__get__`). Write directly to `obj.__dict__` and show which type wins.

<details>
<summary>💡 Hint</summary>
Data descriptor: define `__get__` + `__set__`. Non-data: define only `__get__`. Write `obj.__dict__['attr'] = 'override'` directly and observe which value `obj.attr` returns.
</details>

<details>
<summary>✅ Answer</summary>

```python
class DataDesc:
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return obj.__dict__.get('_d', 'from data descriptor')
    def __set__(self, obj, value):
        obj.__dict__['_d'] = value

class NonDataDesc:
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return 'from non-data descriptor'

class Demo:
    data    = DataDesc()
    nondata = NonDataDesc()

d = Demo()

# Data descriptor takes priority over instance __dict__:
d.__dict__['data'] = 'in dict'
print(d.data)      # 'from data descriptor' — descriptor wins

# Non-data descriptor loses to instance __dict__:
d.__dict__['nondata'] = 'in dict'
print(d.nondata)   # 'in dict' — instance __dict__ wins
```

**Why:** Lookup order: (1) data descriptors, (2) instance `__dict__`, (3) non-data descriptors. This is why `cached_property` works — it's a non-data descriptor that gets replaced by a `__dict__` entry on first access.
</details>

---

### Q14 🟠 · descriptors — `@property` as a descriptor

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

**Problem:** Implement `MyProperty` — a descriptor equivalent to Python's built-in `property`. Support getter, setter, and deleter via `.setter()` and `.deleter()` chaining. Test it on a `Circle.radius` attribute.

<details>
<summary>💡 Hint</summary>
Store `fget`, `fset`, `fdel` as instance attributes. Each of `.setter()` / `.deleter()` returns a new `MyProperty` with the updated function. In `__get__`, call `fget(obj)` when `obj is not None`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class MyProperty:
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or (fget.__doc__ if fget else None)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)

class Circle:
    def __init__(self, radius):
        self._radius = radius

    @MyProperty
    def radius(self):
        """The circle's radius."""
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

c = Circle(5)
print(c.radius)   # 5
c.radius = 10
print(c.radius)   # 10
```

**Why:** `@property` is just a descriptor with `fget`, `fset`, `fdel`. The `@radius.setter` syntax creates a new descriptor object with the setter added — the original is replaced.
</details>

---

### Q15 🟡 · metaclasses — `type()` three-argument form

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

**Problem:** Use `type(name, bases, namespace)` to create a `Rectangle` class dynamically — no `class` statement. Give it `width`, `height`, an `area()` method, and `__repr__`.

<details>
<summary>💡 Hint</summary>
`type(name, bases, namespace)` — `name` is a string, `bases` is a tuple of parent classes, `namespace` is a dict of attributes and methods.
</details>

<details>
<summary>✅ Answer</summary>

```python
def _rect_init(self, width, height):
    self.width  = width
    self.height = height

def _rect_area(self):
    return self.width * self.height

def _rect_repr(self):
    return f"Rectangle(width={self.width}, height={self.height})"

Rectangle = type(
    "Rectangle",
    (object,),
    {
        "__init__": _rect_init,
        "area":     _rect_area,
        "__repr__": _rect_repr,
    }
)

r = Rectangle(4, 5)
print(r)           # Rectangle(width=4, height=5)
print(r.area())    # 20
print(type(r))     # <class '__main__.Rectangle'>
print(type(Rectangle))   # <class 'type'>
```

**Why:** Every `class` statement calls `type(name, bases, namespace)` internally. Understanding this reveals that classes are just objects — instances of `type`.
</details>

---

### Q16 🟡 · metaclasses — custom metaclass with `__new__`

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

**Problem:** Write a `RegistryMeta` metaclass that auto-registers every concrete subclass by name in `RegistryMeta._registry`. The root class should NOT be registered. Show that subclasses appear automatically.

<details>
<summary>💡 Hint</summary>
In `__new__`, check if `bases` is non-empty to skip the root class. `cls = super().__new__(mcs, name, bases, namespace)` creates the class, then store it in the registry.
</details>

<details>
<summary>✅ Answer</summary>

```python
class RegistryMeta(type):
    _registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:   # skip root class
            mcs._registry[name] = cls
        return cls

class Command(metaclass=RegistryMeta):
    def execute(self): raise NotImplementedError

class StartCommand(Command):
    def execute(self): return "starting"

class StopCommand(Command):
    def execute(self): return "stopping"

print(RegistryMeta._registry)
# {'StartCommand': <class StartCommand>, 'StopCommand': <class StopCommand>}

# Dispatch by name:
name  = "StartCommand"
result = RegistryMeta._registry[name]().execute()
print(result)   # starting
```

**Why:** Auto-registration means adding a new subclass is the only step needed — no manual `registry.register()` calls. This is the foundation of plugin architectures.
</details>

---

### Q17 🟠 · metaclasses — singleton via metaclass `__call__`

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

**Problem:** Write a `SingletonMeta` metaclass. Calling `MyClass()` a second time returns the same instance, not a new one. Verify with `is`.

<details>
<summary>💡 Hint</summary>
Override `__call__` on the metaclass. `type.__call__` runs `cls.__new__` and `cls.__init__`. Store instances in a dict keyed by class so different classes have independent singletons.
</details>

<details>
<summary>✅ Answer</summary>

```python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(metaclass=SingletonMeta):
    def __init__(self, debug=False):
        self.debug = debug

c1 = Config(debug=True)
c2 = Config(debug=False)

print(c1 is c2)     # True — same instance
print(c1.debug)     # True — first __init__ wins
```

**Why:** Overriding `__call__` on the metaclass controls what happens when `cls()` is invoked — before `__new__` and `__init__` run. This is the cleanest singleton implementation.
</details>

---

### Q18 🟡 · metaclasses — `__init_subclass__` for registration

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

**Problem:** Implement a plugin registry using `__init_subclass__` instead of a metaclass. Each subclass declares a `plugin_name` keyword argument. Build a `dispatch(name, data)` classmethod.

<details>
<summary>💡 Hint</summary>
`__init_subclass__(cls, plugin_name="", **kwargs)` is called automatically when a subclass is defined. Always call `super().__init_subclass__(**kwargs)` to support multiple inheritance.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Processor:
    _registry = {}

    def __init_subclass__(cls, plugin_name="", **kwargs):
        super().__init_subclass__(**kwargs)
        if plugin_name:
            Processor._registry[plugin_name] = cls

    def process(self, data): raise NotImplementedError

    @classmethod
    def dispatch(cls, name, data):
        if name not in cls._registry:
            raise KeyError(f"No processor named {name!r}")
        return cls._registry[name]().process(data)

class JSONProcessor(Processor, plugin_name="json"):
    def process(self, data):
        import json; return json.dumps(data)

class CSVProcessor(Processor, plugin_name="csv"):
    def process(self, data):
        return ",".join(str(v) for v in data)

print(Processor.dispatch("json", {"x": 1}))   # {"x": 1}
print(Processor.dispatch("csv",  [1, 2, 3]))  # 1,2,3
```

**Why:** `__init_subclass__` is the modern preferred approach for registration — no metaclass needed, no metaclass conflict risk, and the syntax is clear.
</details>

---

### Q19 🟠 · ABCs — ABCMeta and `@abstractmethod`

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

**Problem:** Create an abstract `Shape` base class with abstract methods `area()` and `perimeter()` and a concrete `describe()` method. Create `Circle` and `Rectangle` subclasses. Show that `Shape()` raises `TypeError`.

<details>
<summary>💡 Hint</summary>
`from abc import ABC, abstractmethod`. Use `@abstractmethod` to mark required methods. Subclasses must implement all abstract methods before they can be instantiated.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod
import math

class Shape(ABC):
    """Abstract base — concrete shapes must implement area and perimeter."""

    @abstractmethod
    def area(self) -> float:
        """Return the area of the shape."""
        ...

    @abstractmethod
    def perimeter(self) -> float:
        """Return the perimeter of the shape."""
        ...

    def describe(self) -> str:
        return f"{type(self).__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"

# Can't instantiate:
try:
    Shape()
except TypeError as e:
    print(f"Caught: {e}")

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    def area(self):
        return math.pi * self.radius ** 2
    def perimeter(self):
        return 2 * math.pi * self.radius

class Rectangle(Shape):
    def __init__(self, w, h):
        self.w = w
        self.h = h
    def area(self):
        return self.w * self.h
    def perimeter(self):
        return 2 * (self.w + self.h)

print(Circle(5).describe())       # Circle: area=78.54, perimeter=31.42
print(Rectangle(4, 6).describe()) # Rectangle: area=24.00, perimeter=20.00
```

**Why:** ABCs enforce contracts at instantiation time. If you forget to implement a method, you get a clear `TypeError` rather than an `AttributeError` buried in a call stack.
</details>

---

### Q20 🟢 · dataclasses — `@dataclass` basics

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

**Problem:** Create a `Product` dataclass with `name: str`, `price: float`, and `in_stock: bool = True`. Show the auto-generated `__init__`, `__repr__`, and `__eq__`.

<details>
<summary>💡 Hint</summary>
Just add `@dataclass` and declare fields with type annotations. Fields with defaults must come after fields without defaults. You get `__init__`, `__repr__`, and `__eq__` for free.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass

@dataclass
class Product:
    name:     str
    price:    float
    in_stock: bool = True

p1 = Product("Widget", 9.99)
p2 = Product("Widget", 9.99)
p3 = Product("Gadget", 29.99, in_stock=False)

print(p1)           # Product(name='Widget', price=9.99, in_stock=True)
print(p1 == p2)     # True
print(p1 == p3)     # False
```

**Why:** `@dataclass` generates `__init__` from field declarations, `__repr__` showing all fields, and `__eq__` comparing fields in order. Without it, you'd write ~15 lines of boilerplate.
</details>

---

### Q21 🟢 · dataclasses — `frozen=True`

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

**Problem:** Create a frozen `Coordinate` dataclass with `lat: float` and `lon: float`. Show it's hashable (can be used in a set), and that attempting to modify it raises `FrozenInstanceError`.

<details>
<summary>💡 Hint</summary>
`frozen=True` generates `__setattr__` and `__delattr__` that raise `FrozenInstanceError`. It also generates `__hash__` from the fields.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Coordinate:
    lat: float
    lon: float

c1 = Coordinate(51.5074, -0.1278)   # London
c2 = Coordinate(48.8566,  2.3522)   # Paris

# Hashable — can use in set and as dict key:
visited = {c1, c2}
cache   = {c1: "London", c2: "Paris"}
print(cache[Coordinate(51.5074, -0.1278)])   # London

# Attempt to modify:
try:
    c1.lat = 0.0
except Exception as e:
    print(type(e).__name__, e)   # FrozenInstanceError
```

**Why:** `frozen=True` makes instances immutable and generates `__hash__`. Mutable dataclasses do NOT get `__hash__` because mutable objects shouldn't be hashable.
</details>

---

### Q22 🟡 · dataclasses — `field(default_factory=...)`

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

**Problem:** Create a `Task` dataclass with `title: str`, `tags: list[str]` defaulting to an empty list, and `metadata: dict` defaulting to an empty dict. Show that each instance gets its own list (not shared).

<details>
<summary>💡 Hint</summary>
Using `tags: list = []` raises `ValueError`. Use `field(default_factory=list)` — it calls `list()` for each new instance.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field

@dataclass
class Task:
    title:    str
    tags:     list[str] = field(default_factory=list)
    metadata: dict      = field(default_factory=dict)

t1 = Task("Build feature")
t2 = Task("Write tests")

t1.tags.append("backend")
t2.tags.append("testing")

print(t1.tags)         # ['backend']
print(t2.tags)         # ['testing'] — NOT shared!
print(t1.tags is t2.tags)  # False
```

**Why:** Python evaluates default values once at class definition time. A raw `[]` would be shared across all instances. `default_factory=list` creates a fresh list per instance.
</details>

---

### Q23 🟡 · dataclasses — `__post_init__`

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

**Problem:** Create a `Rectangle` dataclass with `width` and `height`. Use `__post_init__` to compute `area` as a derived field (`field(init=False)`) and validate that both dimensions are positive.

<details>
<summary>💡 Hint</summary>
`field(init=False)` means the field is NOT in `__init__` — set it in `__post_init__`. `__post_init__` runs at the end of the auto-generated `__init__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field

@dataclass
class Rectangle:
    width:  float
    height: float
    area:   float = field(init=False, repr=False)

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        self.area = self.width * self.height

r = Rectangle(4.0, 5.0)
print(r)        # Rectangle(width=4.0, height=5.0)  — area has repr=False
print(r.area)   # 20.0

try:
    Rectangle(-1, 5)
except ValueError as e:
    print(e)
```

**Why:** `field(init=False)` keeps derived values out of the constructor signature. `__post_init__` is the right place for computed fields and validation.
</details>

---

### Q24 🟡 · dataclasses — `order=True`

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

**Problem:** Create a `Task` dataclass with `priority: int`, `created_at: float`, and `title: str`. Use `order=True`. Mark `title` with `field(compare=False)` so sorting ignores it. Sort a list of tasks.

<details>
<summary>💡 Hint</summary>
`order=True` generates `__lt__`, `__le__`, `__gt__`, `__ge__` based on fields in declaration order. Fields with `compare=False` are excluded.
</details>

<details>
<summary>✅ Answer</summary>

```python
from dataclasses import dataclass, field

@dataclass(order=True)
class Task:
    priority:   int
    created_at: float
    title:      str = field(compare=False)

tasks = [
    Task(2, 1000.0, "Write docs"),
    Task(1, 2000.0, "Fix critical bug"),
    Task(2,  500.0, "Update config"),
    Task(1, 1500.0, "Deploy hotfix"),
]

for t in sorted(tasks):
    print(f"  [P{t.priority}] {t.title}")
# [P1] Deploy hotfix
# [P1] Fix critical bug
# [P2] Update config
# [P2] Write docs
```

**Why:** `order=True` makes instances work with `sorted()`, `min()`, `max()`, and `heapq`. Fields are compared left to right in declaration order — so field order matters.
</details>

---

### Q25 🟡 · slots — `__slots__` memory comparison

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

**Problem:** Create two versions of an `Event` class (with and without `__slots__`), each with `name: str`, `ts: float`, `value: float`. Compare memory using `sys.getsizeof`. Report percentage savings.

<details>
<summary>💡 Hint</summary>
For the dict version: total size = `sys.getsizeof(obj) + sys.getsizeof(obj.__dict__)`. For the slots version, there is no `__dict__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

class EventDict:
    def __init__(self, name, ts, value):
        self.name  = name
        self.ts    = ts
        self.value = value

class EventSlots:
    __slots__ = ("name", "ts", "value")

    def __init__(self, name, ts, value):
        self.name  = name
        self.ts    = ts
        self.value = value

e1 = EventDict("click", 1234567890.0, 1.0)
e2 = EventSlots("click", 1234567890.0, 1.0)

size_dict  = sys.getsizeof(e1) + sys.getsizeof(e1.__dict__)
size_slots = sys.getsizeof(e2)

print(f"With __dict__:  {size_dict} bytes")
print(f"With __slots__: {size_slots} bytes")
print(f"Savings: {size_dict - size_slots} bytes ({(size_dict - size_slots)/size_dict*100:.0f}%)")
```

**Why:** `__slots__` replaces the per-instance `__dict__` with a compact C-level array. For classes creating millions of instances (events, sensors, records), this saves 3-5x memory.
</details>

---

### Q26 🟡 · slots — `__slots__` attribute restriction

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)

**Problem:** Create a slotted `Config` class with slots `host`, `port`, `debug`. Show that reading and writing declared slots works normally, but trying to add an undeclared attribute raises `AttributeError`.

<details>
<summary>💡 Hint</summary>
`__slots__` prevents assigning any attribute not listed. The error is `AttributeError: 'Config' object has no attribute 'timeout'` (or similar).
</details>

<details>
<summary>✅ Answer</summary>

```python
class Config:
    __slots__ = ("host", "port", "debug")

    def __init__(self, host, port, debug=False):
        self.host  = host
        self.port  = port
        self.debug = debug

cfg = Config("localhost", 8080)
print(cfg.host)    # localhost
cfg.debug = True   # OK — declared slot

try:
    cfg.timeout = 30   # AttributeError
except AttributeError as e:
    print(e)

# No __dict__:
print(hasattr(cfg, "__dict__"))   # False

# Slot descriptors on the class:
print(type(Config.host))   # <class 'member_descriptor'>
```

**Why:** `__slots__` prevents dynamic attribute creation. This catches typos at runtime (`cfg.hots = ...` → error) and enforces a fixed schema on each instance.
</details>

---

### Q27 🟠 · slots — `__slots__` in subclasses

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)

**Problem:** Show how `__slots__` inheritance works. Create a slotted `Animal` base class and a slotted `Dog` subclass. Demonstrate that the subclass must also declare `__slots__` (even empty) to avoid a `__dict__` being added back.

<details>
<summary>💡 Hint</summary>
If a subclass does NOT declare `__slots__`, Python adds a `__dict__` to it — defeating the memory savings from the parent. An empty `__slots__ = ()` in the subclass prevents this.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

class Animal:
    __slots__ = ("name", "weight")

    def __init__(self, name, weight):
        self.name   = name
        self.weight = weight

class DogWithSlots(Animal):
    __slots__ = ("breed",)   # ← only NEW slots; inherits name, weight

    def __init__(self, name, weight, breed):
        super().__init__(name, weight)
        self.breed = breed

class DogWithoutSlots(Animal):
    # No __slots__ declared — Python adds __dict__ back!
    def __init__(self, name, weight, breed):
        super().__init__(name, weight)
        self.breed = breed

d1 = DogWithSlots("Rex", 30.0, "Husky")
d2 = DogWithoutSlots("Max", 25.0, "Lab")

print("DogWithSlots has __dict__:", hasattr(d1, "__dict__"))    # False
print("DogWithoutSlots has __dict__:", hasattr(d2, "__dict__")) # True

size1 = sys.getsizeof(d1)
size2 = sys.getsizeof(d2) + sys.getsizeof(d2.__dict__)
print(f"With slots: {size1}, Without: {size2}")
```

**Why:** Each class in the MRO that declares `__slots__` contributes its slots. A subclass without `__slots__` re-introduces `__dict__`, undoing the parent's memory savings.
</details>

---

### Q28 🟡 · introspection — `dir()` + `callable()`

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)

**Problem:** Write a `list_methods(obj)` function that returns all public, callable attributes (no dunder methods). Test it on a list, a dict, and a custom class.

<details>
<summary>💡 Hint</summary>
`dir(obj)` returns all names. Filter out names starting with `_`. Use `callable(getattr(obj, name))` to check. Wrap `getattr` in try/except in case a property raises.
</details>

<details>
<summary>✅ Answer</summary>

```python
def list_methods(obj):
    result = []
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            attr = getattr(obj, name)
        except Exception:
            continue
        if callable(attr):
            result.append(name)
    return result

print(list_methods([]))    # ['append', 'clear', 'copy', 'count', ...]
print(list_methods({}))    # ['clear', 'copy', 'fromkeys', 'get', ...]

class Service:
    def start(self): pass
    def stop(self): pass
    _private = lambda self: None

print(list_methods(Service()))   # ['start', 'stop']
```

**Why:** `dir()` + `callable()` is the standard pattern for discovering an object's interface at runtime. This is how tab-completion in interactive shells works.
</details>

---

### Q29 🟡 · introspection — dynamic attribute access

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)

**Problem:** Write a `Config` class that takes `**kwargs` in `__init__` and stores each key as an attribute using `setattr`. Add `get(name, default)`, `has(name)`, `remove(name)`, and `to_dict()` methods.

<details>
<summary>💡 Hint</summary>
`setattr(obj, name, value)` is identical to `obj.name = value` but works with dynamic names. `getattr(obj, name, default)` is `obj.name` with a fallback.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Config:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self, name, default=None):
        return getattr(self, name, default)

    def has(self, name):
        return hasattr(self, name)

    def remove(self, name):
        if hasattr(self, name):
            delattr(self, name)
        else:
            raise KeyError(f"Config key {name!r} not found")

    def to_dict(self):
        return dict(vars(self))

    def __repr__(self):
        return f"Config({vars(self)})"

cfg = Config(host="localhost", port=8080, debug=True)
print(cfg.host)                 # localhost
print(cfg.get("timeout", 30))   # 30 (default)
cfg.remove("debug")
print(cfg.to_dict())            # {'host': 'localhost', 'port': 8080}
```

**Why:** Dynamic attribute access powers config objects, proxy classes, and data loaders — anywhere the attribute names aren't known at class-definition time.
</details>

---

### Q30 🟠 · introspection — `inspect.signature` at runtime

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)

**Problem:** Write a `validate_call(func)` decorator that uses `inspect.signature` to check that all arguments match their type annotations at call time. Raise `TypeError` with a clear message if a type doesn't match.

<details>
<summary>💡 Hint</summary>
`inspect.signature(func).bind(*args, **kwargs)` binds actual call args to parameter names. `.apply_defaults()` fills in defaults. Then check each bound argument against its annotation.
</details>

<details>
<summary>✅ Answer</summary>

```python
import inspect
from functools import wraps

def validate_call(func):
    sig = inspect.signature(func)
    annotations = {
        name: param.annotation
        for name, param in sig.parameters.items()
        if param.annotation is not inspect.Parameter.empty
    }

    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for param_name, value in bound.arguments.items():
            if param_name in annotations:
                expected = annotations[param_name]
                if not isinstance(value, expected):
                    raise TypeError(
                        f"{param_name} must be {expected.__name__}, "
                        f"got {type(value).__name__}"
                    )
        return func(*args, **kwargs)

    return wrapper

@validate_call
def add(x: int, y: int) -> int:
    return x + y

print(add(1, 2))    # 3

try:
    add(1, "two")   # TypeError: y must be int, got str
except TypeError as e:
    print(e)
```

**Why:** `inspect.signature` gives you full parameter metadata at runtime. Combined with annotations, you can build runtime type checking, API validation, and documentation tools.
</details>

---

### Q31 🟡 · enums — `Enum` named constants

> 🛠️ **Solve locally:** [practice_local.py → Q31](./practice_local.py)

**Problem:** Create an `OrderStatus` enum with `PENDING`, `PROCESSING`, `SHIPPED`, `DELIVERED`, and `CANCELLED`. Show lookup by name and by value, membership testing, and iteration.

<details>
<summary>💡 Hint</summary>
`OrderStatus.PENDING` — name access. `OrderStatus("pending")` — value lookup. `OrderStatus["PENDING"]` — name string lookup. `for s in OrderStatus:` — iteration.
</details>

<details>
<summary>✅ Answer</summary>

```python
from enum import Enum

class OrderStatus(Enum):
    PENDING    = "pending"
    PROCESSING = "processing"
    SHIPPED    = "shipped"
    DELIVERED  = "delivered"
    CANCELLED  = "cancelled"

status = OrderStatus.PENDING
print(status.name)          # PENDING
print(status.value)         # pending

print(OrderStatus("shipped"))        # OrderStatus.SHIPPED
print(OrderStatus["DELIVERED"])      # OrderStatus.DELIVERED

print(list(OrderStatus))
# [<OrderStatus.PENDING: 'pending'>, ...]

# Membership:
print(OrderStatus.SHIPPED in list(OrderStatus))   # True
```

**Why:** Enums prevent magic strings and integers. They give you autocomplete, prevent typos (`status == "shiped"` is a bug; `status == OrderStatus.SHIPPED` is not), and support iteration.
</details>

---

### Q32 🟡 · enums — `IntEnum` and `Flag`

> 🛠️ **Solve locally:** [practice_local.py → Q32](./practice_local.py)

**Problem:** Create a `Priority` IntEnum and a `Permission` Flag enum. Show that `Priority.HIGH > Priority.LOW` works, and that `Permission.READ | Permission.WRITE` can be tested with `in`.

<details>
<summary>💡 Hint</summary>
`IntEnum` members compare with plain integers. `Flag` members support `|` (combine) and `in` (membership test). Use `auto()` for auto-assigned values.
</details>

<details>
<summary>✅ Answer</summary>

```python
from enum import IntEnum, Flag, auto

class Priority(IntEnum):
    LOW    = 1
    MEDIUM = 2
    HIGH   = 3

print(Priority.HIGH > Priority.LOW)    # True
print(Priority.HIGH > 2)               # True (compares with int)
print(sorted([Priority.HIGH, Priority.LOW, Priority.MEDIUM]))
# [<Priority.LOW: 1>, <Priority.MEDIUM: 2>, <Priority.HIGH: 3>]

class Permission(Flag):
    READ    = auto()   # 1
    WRITE   = auto()   # 2
    EXECUTE = auto()   # 4

user_perm = Permission.READ | Permission.WRITE
print(Permission.READ in user_perm)     # True
print(Permission.EXECUTE in user_perm)  # False
print(user_perm)                         # Permission.READ|WRITE
```

**Why:** `IntEnum` is ideal for priority levels and status codes where integer comparisons make sense. `Flag` is ideal for bitmask permissions where combinations are first-class.
</details>

---

### Q33 🟠 · ABCs — ABC as interface contract

> 🛠️ **Solve locally:** [practice_local.py → Q33](./practice_local.py)

**Problem:** Create an abstract `Repository` base class with abstract methods `save(entity)`, `find_by_id(id)`, and `delete(id)`. Add a concrete `find_all()` that calls `find_by_id` in a loop. Show partial implementation raises `TypeError`.

<details>
<summary>💡 Hint</summary>
A class that implements only SOME abstract methods is still abstract — it cannot be instantiated. All abstract methods must be implemented before the class becomes concrete.
</details>

<details>
<summary>✅ Answer</summary>

```python
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def save(self, entity): ...

    @abstractmethod
    def find_by_id(self, entity_id): ...

    @abstractmethod
    def delete(self, entity_id): ...

    def find_all(self, ids):
        return [self.find_by_id(i) for i in ids]

# Partial implementation — still abstract:
class PartialRepo(Repository):
    def save(self, entity): return entity

try:
    PartialRepo()   # TypeError
except TypeError as e:
    print(f"Caught: {e}")

# Full implementation:
class MemoryRepo(Repository):
    def __init__(self):
        self._store = {}
    def save(self, entity):
        self._store[id(entity)] = entity
        return entity
    def find_by_id(self, entity_id):
        return self._store.get(entity_id)
    def delete(self, entity_id):
        self._store.pop(entity_id, None)

repo = MemoryRepo()   # works
```

**Why:** ABCs enforce the full interface at instantiation time — not at first method call. This catches incomplete implementations early.
</details>

---

### Q34 🟠 · typing — `typing.Protocol` structural typing

> 🛠️ **Solve locally:** [practice_local.py → Q34](./practice_local.py)

**Problem:** Define a `Drawable` Protocol with a `draw() -> None` method. Write a `render_all(shapes)` function typed with `list[Drawable]`. Show that unrelated classes with a `draw()` method satisfy the protocol at runtime.

<details>
<summary>💡 Hint</summary>
`@runtime_checkable` makes `isinstance()` work with Protocols. Without it, Protocols are type-checker-only. A class satisfies the Protocol if it has the required methods — no inheritance needed.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self):
        print("Drawing circle ○")

class Square:
    def draw(self):
        print("Drawing square □")

class Label:
    def draw(self):
        print("Drawing label [text]")

class Invisible:
    def hide(self): pass   # no draw()

def render_all(shapes: list[Drawable]) -> None:
    for shape in shapes:
        shape.draw()

shapes = [Circle(), Square(), Label()]
render_all(shapes)

# Runtime check:
print(isinstance(Circle(), Drawable))     # True
print(isinstance(Invisible(), Drawable))  # False
```

**Why:** Protocol enables duck typing with type-safety. Unlike ABCs, classes don't need to inherit from Protocol — any class with the right methods qualifies. This is structural subtyping.
</details>

---

### Q35 🟠 · capstone — ORM-style model using metaclass + descriptors

> 🛠️ **Solve locally:** [practice_local.py → Q35](./practice_local.py)

**Problem:** Build a mini ORM model system where:
1. `Field` is a descriptor that enforces a type.
2. `ModelMeta` is a metaclass that collects all `Field` instances from the class namespace into `cls._fields`.
3. `ModelMeta` generates `__init__`, `__repr__`, and `__eq__` from `_fields`.
4. Subclassing `Model` and declaring `Field` attributes should give you a working data class.

<details>
<summary>💡 Hint</summary>
In the metaclass `__new__`, iterate the namespace and collect items that are `Field` instances. Generate `__init__` dynamically using `exec` or a helper that calls `setattr`. For `__repr__`, iterate `cls._fields`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Field:
    def __init__(self, field_type):
        self.field_type = field_type

    def __set_name__(self, owner, name):
        self.name    = name
        self.private = f"_field_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.private)

    def __set__(self, obj, value):
        if not isinstance(value, self.field_type):
            raise TypeError(
                f"{self.name}: expected {self.field_type.__name__}, "
                f"got {type(value).__name__}"
            )
        obj.__dict__[self.private] = value


class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        fields = {
            k: v for k, v in namespace.items()
            if isinstance(v, Field)
        }
        namespace["_fields"] = list(fields.keys())
        cls = super().__new__(mcs, name, bases, namespace)

        if fields:
            def __init__(self, **kwargs):
                for fname in self._fields:
                    if fname not in kwargs:
                        raise TypeError(f"Missing required field: {fname!r}")
                    setattr(self, fname, kwargs[fname])
            cls.__init__ = __init__

            def __repr__(self):
                parts = ", ".join(
                    f"{f}={getattr(self, f)!r}" for f in self._fields
                )
                return f"{type(self).__name__}({parts})"
            cls.__repr__ = __repr__

            def __eq__(self, other):
                if type(self) is not type(other):
                    return NotImplemented
                return all(
                    getattr(self, f) == getattr(other, f)
                    for f in self._fields
                )
            cls.__eq__ = __eq__

        return cls


class Model(metaclass=ModelMeta):
    pass


class User(Model):
    name  = Field(str)
    age   = Field(int)
    email = Field(str)


u1 = User(name="Alice", age=30, email="alice@example.com")
u2 = User(name="Alice", age=30, email="alice@example.com")
u3 = User(name="Bob",   age=25, email="bob@example.com")

print(u1)           # User(name='Alice', age=30, email='alice@example.com')
print(u1 == u2)     # True
print(u1 == u3)     # False

try:
    User(name="Alice", age="thirty", email="x@y.com")
except TypeError as e:
    print(e)        # age: expected int, got str
```

**Why:** This capstone combines descriptors (type-checked attributes) with a metaclass (automatic `__init__`/`__repr__`/`__eq__` generation) — the same pattern used by Django's ORM models.
</details>

---

## Navigation

| | |
|---|---|
| Root theory | [theory.md](./theory.md) |
| Root practice (local) | [practice_local.py](./practice_local.py) |
| Dunder methods | [01_dunder_methods/practice.md](./01_dunder_methods/practice.md) |
| Descriptors | [02_descriptors/practice.md](./02_descriptors/practice.md) |
| Metaclasses | [03_metaclasses/practice.md](./03_metaclasses/practice.md) |
| Dataclasses | [04_dataclasses/practice.md](./04_dataclasses/practice.md) |
| Advanced patterns | [05_advanced_patterns/practice.md](./05_advanced_patterns/practice.md) |
| Interview Q&A | [interview.md](./interview.md) |
| Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
