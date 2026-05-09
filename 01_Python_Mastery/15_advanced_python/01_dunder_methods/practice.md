# Practice — Dunder Methods

| Q | Difficulty | Topic |
|---|-----------|-------|
| [Q1](#q1) | 🟢 | `__str__` and `__repr__` |
| [Q2](#q2) | 🟢 | `__len__` and `__bool__` |
| [Q3](#q3) | 🟡 | `__eq__` and `__hash__` |
| [Q4](#q4) | 🟡 | `__lt__`, `__le__`, `@total_ordering` |
| [Q5](#q5) | 🟡 | `__add__` and `__radd__` |
| [Q6](#q6) | 🟡 | `__getitem__` and `__setitem__` |
| [Q7](#q7) | 🟡 | `__iter__` and `__next__` |
| [Q8](#q8) | 🟡 | `__contains__` |
| [Q9](#q9) | 🟡 | `__enter__` and `__exit__` |
| [Q10](#q10) | 🟠 | `__mul__` and `__rmul__` |
| [Q11](#q11) | 🟠 | `__call__` |
| [Q12](#q12) | 🟠 | Operator overloading capstone |

---

<a id="q1"></a>

### Q1 🟢 · representation — implement `__str__` and `__repr__`

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** Create a `Book` class with `title`, `author`, and `year`. Implement `__repr__` so that `eval(repr(b))` would recreate it, and `__str__` for a human-readable display like `"The Hobbit by J.R.R. Tolkien (1937)"`.

<details>
<summary>💡 Hint</summary>
`__repr__` should look like `Book('The Hobbit', 'J.R.R. Tolkien', 1937)`. Use `!r` on string fields to include quotes. `__str__` can be freely formatted for readability.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Book:
    def __init__(self, title, author, year):
        self.title, self.author, self.year = title, author, year

    def __repr__(self):
        return f"Book({self.title!r}, {self.author!r}, {self.year!r})"

    def __str__(self):
        return f"{self.title} by {self.author} ({self.year})"

b = Book("The Hobbit", "J.R.R. Tolkien", 1937)
print(repr(b))  # Book('The Hobbit', 'J.R.R. Tolkien', 1937)
print(str(b))   # The Hobbit by J.R.R. Tolkien (1937)
print(b)        # The Hobbit by J.R.R. Tolkien (1937)
```

**Why:** `__repr__` is for developers — unambiguous, ideally reconstructable with `eval()`. `__str__` is for users — readable and concise. `print()` calls `__str__`; the REPL calls `__repr__`.
</details>

---

<a id="q2"></a>

### Q2 🟢 · sizing — implement `__len__` and `__bool__`

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** Create a `Playlist` class that wraps a list of song titles. Implement `__len__` and `__bool__`. A playlist with no songs should be falsy.

<details>
<summary>💡 Hint</summary>
`__bool__` should return `bool(self.songs)`. If you only implement `__len__`, Python uses `len(obj) != 0` as the truth value — but explicit is better.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Playlist:
    def __init__(self, songs=None):
        self.songs = list(songs or [])

    def __len__(self):
        return len(self.songs)

    def __bool__(self):
        return bool(self.songs)

    def __repr__(self):
        return f"Playlist({self.songs!r})"

p1 = Playlist(["Song A", "Song B"])
p2 = Playlist()

print(len(p1))  # 2
print(bool(p1)) # True
print(bool(p2)) # False

if p2:
    print("has songs")
else:
    print("empty")   # this branch
```

**Why:** `__bool__` controls `if obj:`. Without it, Python falls back to `__len__` (empty = falsy). Being explicit with `__bool__` is clearer about intent.
</details>

---

<a id="q3"></a>

### Q3 🟡 · equality — `__eq__` and `__hash__`

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** Create a `Point` class with `x` and `y`. Implement `__eq__` (two Points are equal if their coordinates are equal) and `__hash__` (so Points can be used in sets and as dict keys). Demonstrate both work correctly.

<details>
<summary>💡 Hint</summary>
Return `NotImplemented` (not `False`) when comparing with an unknown type. Hash must be consistent with equality: if `a == b` then `hash(a) == hash(b)`. Tuple hash works well: `hash((self.x, self.y))`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return NotImplemented   # not False!

    def __hash__(self):
        return hash((self.x, self.y))   # consistent with __eq__

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p1 = Point(1, 2)
p2 = Point(1, 2)
p3 = Point(3, 4)

print(p1 == p2)         # True
print(p1 == p3)         # False
print(p1 == "other")    # False  (NotImplemented → reflected → False)

# Can be used in set and dict:
seen = {p1, p2, p3}
print(len(seen))        # 2  (p1 and p2 are equal → deduplicated)
labels = {p1: "origin area", p3: "far"}
print(labels[Point(1, 2)])  # "origin area"  (same hash + equal)
```

**Why:** Defining `__eq__` without `__hash__` makes the class unhashable — Python sets `__hash__ = None`. The contract is: equal objects must have equal hashes.
</details>

---

<a id="q4"></a>

### Q4 🟡 · ordering — `__lt__`, `__le__` with `@total_ordering`

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** Create a `Version` class representing a semantic version (`major.minor.patch`). Use `@total_ordering` to provide full comparison support from just `__eq__` and `__lt__`. Demonstrate that `sorted()` works.

<details>
<summary>💡 Hint</summary>
With `@functools.total_ordering`, define `__eq__` and ONE of `__lt__/__le__/__gt__/__ge__` and you get all six comparison methods derived automatically.
</details>

<details>
<summary>✅ Answer</summary>

```python
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, major, minor, patch):
        self.major, self.minor, self.patch = major, minor, patch

    def __eq__(self, other):
        if isinstance(other, Version):
            return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Version):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
        return NotImplemented

    def __repr__(self):
        return f"Version({self.major}, {self.minor}, {self.patch})"

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

v1, v2, v3 = Version(1, 0, 0), Version(0, 9, 5), Version(1, 1, 0)
print(v1 > v2)    # True   (derived from __lt__ and __eq__)
print(v1 <= v2)   # False  (derived)
print(sorted([v1, v2, v3]))   # [0.9.5, 1.0.0, 1.1.0]
```

**Why:** `@total_ordering` fills in the missing 4 comparison methods by combining `__eq__` and `__lt__`. Without it, you'd have to write all six manually.
</details>

---

<a id="q5"></a>

### Q5 🟡 · arithmetic — `__add__` and `__radd__` for a Vector

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Create a `Vector2D` class. Implement `__add__` (Vector + Vector and Vector + scalar) and `__radd__` (so that `5 + v` also works). Test all three cases.

<details>
<summary>💡 Hint</summary>
`__radd__` is called when the left operand's `__add__` returns `NotImplemented`. For commutative operations like addition, `__radd__` can simply delegate to `__add__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Vector2D:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x + other.x, self.y + other.y)
        if isinstance(other, (int, float)):
            return Vector2D(self.x + other, self.y + other)
        return NotImplemented

    def __radd__(self, other):
        # Called when: other + self (and other.__add__(self) → NotImplemented)
        return self.__add__(other)   # commutative — delegate

    def __repr__(self):
        return f"Vector2D({self.x}, {self.y})"

v1 = Vector2D(1, 2)
v2 = Vector2D(3, 4)
print(v1 + v2)   # Vector2D(4, 6)
print(v1 + 10)   # Vector2D(11, 12)
print(10 + v1)   # Vector2D(11, 12)  — uses __radd__
```

**Why:** `__radd__` exists so the right-hand operand gets a chance when the left-hand operand doesn't know how to handle the operation.
</details>

---

<a id="q6"></a>

### Q6 🟡 · subscript — `__getitem__` and `__setitem__`

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Create a `Grid` class representing a 2D grid. Support `grid[row, col]` for reading and `grid[row, col] = value` for writing. Initialize all cells to `0`.

<details>
<summary>💡 Hint</summary>
When you write `obj[row, col]`, Python passes `(row, col)` as a tuple to `__getitem__` and `__setitem__`. Unpack the tuple in the method.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Grid:
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self._data = [[0] * cols for _ in range(rows)]

    def __getitem__(self, key):
        row, col = key   # key is a tuple (row, col) from grid[r, c]
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError(f"({row}, {col}) out of bounds")
        return self._data[row][col]

    def __setitem__(self, key, value):
        row, col = key
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError(f"({row}, {col}) out of bounds")
        self._data[row][col] = value

    def __repr__(self):
        return f"Grid({self._data!r})"

g = Grid(3, 3)
g[0, 0] = 1
g[1, 1] = 5
g[2, 2] = 9
print(g[1, 1])   # 5
```

**Why:** `obj[a, b]` passes `(a, b)` as a tuple to `__getitem__`. This is how NumPy arrays support multi-dimensional indexing.
</details>

---

<a id="q7"></a>

### Q7 🟡 · iteration — `__iter__` and `__next__`

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Create a `FibSequence` class that generates Fibonacci numbers up to a limit. Make it iterable by implementing `__iter__` and `__next__`. It should be re-usable (looping twice should yield the same results).

<details>
<summary>💡 Hint</summary>
For re-usable iteration, `__iter__` should return a new iterator object, not `self`. Create a separate `FibIterator` class, or make `__iter__` return a fresh instance.
</details>

<details>
<summary>✅ Answer</summary>

```python
class FibSequence:
    def __init__(self, limit):
        self.limit = limit

    def __iter__(self):
        # Return a NEW iterator each time — makes this re-usable
        return FibIterator(self.limit)

class FibIterator:
    def __init__(self, limit):
        self.limit = limit
        self.a, self.b = 0, 1

    def __iter__(self):
        return self   # iterators return self

    def __next__(self):
        if self.a > self.limit:
            raise StopIteration
        result = self.a
        self.a, self.b = self.b, self.a + self.b
        return result

fibs = FibSequence(50)
print(list(fibs))   # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
print(list(fibs))   # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]  — works again!
```

**Why:** If `__iter__` returns `self`, the object is exhausted after one loop. Returning a new iterator object each time allows re-use.
</details>

---

<a id="q8"></a>

### Q8 🟡 · membership — `__contains__`

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Create an `IPRange` class representing a range of IP addresses (given as a start and end integer). Implement `__contains__` so that `"192.168.1.5" in ip_range` works, converting the string to an integer first.

<details>
<summary>💡 Hint</summary>
Python's `socket.inet_aton()` or manual parsing converts IP strings to integers. For simplicity, parse `"a.b.c.d"` as `a*16777216 + b*65536 + c*256 + d`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class IPRange:
    def __init__(self, start: str, end: str):
        self.start = self._to_int(start)
        self.end   = self._to_int(end)

    @staticmethod
    def _to_int(ip: str) -> int:
        parts = [int(p) for p in ip.split(".")]
        return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]

    def __contains__(self, ip: str) -> bool:
        return self.start <= self._to_int(ip) <= self.end

    def __repr__(self):
        return f"IPRange(...)"

lan = IPRange("192.168.1.0", "192.168.1.255")
print("192.168.1.5"   in lan)   # True
print("192.168.1.100" in lan)   # True
print("10.0.0.1"      in lan)   # False
print("192.168.2.1"   in lan)   # False
```

**Why:** `__contains__` powers the `in` operator. Without it, Python falls back to iterating the object (calls `__iter__`), which is O(n). A custom `__contains__` can be O(1).
</details>

---

<a id="q9"></a>

### Q9 🟡 · context manager — `__enter__` and `__exit__`

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:** Build a `ManagedFile` context manager class from scratch (without `contextlib`). It should open a file in `__enter__`, return the file object, and close it in `__exit__`. It should also suppress `FileNotFoundError` and print a warning instead.

<details>
<summary>💡 Hint</summary>
`__exit__` receives `(exc_type, exc_val, exc_tb)`. Return `True` to suppress the exception, `False` or `None` to propagate it.
</details>

<details>
<summary>✅ Answer</summary>

```python
class ManagedFile:
    def __init__(self, path, mode="r"):
        self.path = path
        self.mode = mode
        self._file = None

    def __enter__(self):
        self._file = open(self.path, self.mode)
        return self._file   # bound to 'as' variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            self._file.close()
        if exc_type is FileNotFoundError:
            print(f"Warning: {self.path} not found — suppressed")
            return True    # suppress FileNotFoundError
        return False       # propagate all other exceptions

with ManagedFile("/tmp/test.txt", "w") as f:
    f.write("hello")

with ManagedFile("/nonexistent.txt") as f:   # FileNotFoundError suppressed
    pass

print("Still running")
```

**Why:** `__enter__` sets up the resource, `__exit__` always runs (even if an exception occurs) — guaranteed cleanup. Return `True` to suppress the exception, `False` to re-raise it.
</details>

---

<a id="q10"></a>

### Q10 🟠 · scalar multiplication — `__mul__` and `__rmul__`

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:** Extend `Vector2D` with `__mul__` (scalar multiplication: `v * 3`) and `__rmul__` (so `3 * v` also works), plus `__abs__` for magnitude. Verify `3 * v == v * 3`.

<details>
<summary>💡 Hint</summary>
`__rmul__` is called when the scalar is on the left and doesn't know how to multiply with a Vector. For commutative scalar multiplication, `__rmul__` can just delegate to `__mul__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import math

class Vector2D:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector2D(self.x * scalar, self.y * scalar)
        return NotImplemented

    def __rmul__(self, scalar):
        return self.__mul__(scalar)   # commutative

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __eq__(self, other):
        if isinstance(other, Vector2D):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __repr__(self):
        return f"Vector2D({self.x}, {self.y})"

v = Vector2D(3, 4)
print(v * 2)    # Vector2D(6, 8)
print(2 * v)    # Vector2D(6, 8)  — uses __rmul__
print(v * 2 == 2 * v)  # True
print(abs(v))   # 5.0
```

**Why:** `__rmul__` gives the right-hand operand a chance when the left operand's `__mul__` returns `NotImplemented`. Without it, `2 * v` would raise TypeError.
</details>

---

<a id="q11"></a>

### Q11 🟠 · callable — make a class callable (callable counter)

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



**Problem:** Create a `CallCounter` class that wraps any function. When called, it increments an internal counter and delegates to the wrapped function. It should have a `.count` attribute and a `.reset()` method.

<details>
<summary>💡 Hint</summary>
Callable objects preserve state between calls — this is their main advantage over plain functions. `callable(obj)` returns `True` if `type(obj)` has `__call__`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class CallCounter:
    def __init__(self, func):
        self.func = func
        self.count = 0
        self.__name__ = getattr(func, '__name__', str(func))

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)

    def reset(self):
        self.count = 0

    def __repr__(self):
        return f"CallCounter({self.__name__!r}, calls={self.count})"

@CallCounter
def add(a, b):
    return a + b

add(1, 2)
add(3, 4)
add(5, 6)
print(add.count)   # 3
print(add(10, 20)) # 30
print(add.count)   # 4
add.reset()
print(add.count)   # 0

print(callable(add))   # True — __call__ is defined on type(add)
```

**Why:** Callable objects maintain state between calls — impossible with a plain function or lambda. The `@CallCounter` syntax applies it as a decorator.
</details>

---

<a id="q12"></a>

### Q12 🟠 · capstone — Matrix class with `+`, `*`, `==`

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



**Problem:** Build a `Matrix` class supporting element-wise `+`, scalar `*` (from both sides), element-wise `==`, and `__repr__`. Raise `ValueError` for shape mismatches in `+`.

<details>
<summary>💡 Hint</summary>
Store data as a list of lists. For `__eq__`, compare data field by field. For `__repr__`, use `f"Matrix({self.data!r})"`. For `__rmul__`, delegate to `__mul__` since scalar multiplication is commutative.
</details>

<details>
<summary>✅ Answer</summary>

```python
class Matrix:
    def __init__(self, data):
        self.data = [list(row) for row in data]
        self.rows = len(data)
        self.cols = len(data[0])

    def __add__(self, other):
        if isinstance(other, Matrix):
            if (self.rows, self.cols) != (other.rows, other.cols):
                raise ValueError(f"Shape mismatch: {self.rows}x{self.cols} vs {other.rows}x{other.cols}")
            return Matrix([
                [self.data[i][j] + other.data[i][j] for j in range(self.cols)]
                for i in range(self.rows)
            ])
        return NotImplemented

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Matrix([[x * scalar for x in row] for row in self.data])
        return NotImplemented

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __eq__(self, other):
        if isinstance(other, Matrix):
            return self.data == other.data
        return NotImplemented

    def __repr__(self):
        return f"Matrix({self.data!r})"

A = Matrix([[1, 2], [3, 4]])
B = Matrix([[5, 6], [7, 8]])
print(A + B)        # Matrix([[6, 8], [10, 12]])
print(A * 2)        # Matrix([[2, 4], [6, 8]])
print(2 * A)        # Matrix([[2, 4], [6, 8]])  — uses __rmul__
print(A == A)       # True
print(A == B)       # False
```

**Why:** This capstone combines the reflected operator pattern, shape-checking, element-wise operations, and equality — a complete operator-overloaded class.
</details>

---

## Navigation

| | |
|---|---|
| Root theory | [../theory.md](../theory.md) |
| Subfolder theory | [theory.md](./theory.md) |
| Next subfolder | [../02_descriptors/practice.md](../02_descriptors/practice.md) |
| Root practice | [../practice.md](../practice.md) |
