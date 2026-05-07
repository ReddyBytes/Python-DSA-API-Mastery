# Dunder Methods — Deep Dive

Think of Python's syntax as a switchboard. When you write `len(x)`, the switch connects to `x.__len__()`. When you write `a + b`, it connects to `a.__add__(b)`. **Dunder methods are the wires behind the switchboard** — and once you can see them, you can make any object behave like a built-in type.

> Key fact: Python calls dunders on the **class**, not the instance. `len(obj)` is really `type(obj).__len__(obj)` — this is deliberate and prevents monkey-patching the protocol.

---

## Learning Priority

**Must Learn:** `__str__` · `__repr__` · `__len__` · `__eq__` · `__lt__` · `__enter__` / `__exit__`

**Should Learn:** `__add__` · `__mul__` · `__contains__` · `__iter__` · `__next__` · `__getitem__`

**Good to Know:** `__new__` · `__del__` · `__hash__` · `__format__`

**Reference:** `__init_subclass__` · `__class_getitem__`

---

## Chapter 1: The Protocol System

Every Python operator and built-in maps to a dunder. The table below IS Python's object model:

```
SYNTAX              DUNDER CALL
------------------------------------------------------
len(obj)         →  obj.__len__()
obj[key]         →  obj.__getitem__(key)
obj[key] = val   →  obj.__setitem__(key, val)
del obj[key]     →  obj.__delitem__(key)
x in obj         →  obj.__contains__(x)
for x in obj     →  obj.__iter__() + obj.__next__()
obj + other      →  obj.__add__(other)
obj == other     →  obj.__eq__(other)
str(obj)         →  obj.__str__()
repr(obj)        →  obj.__repr__()
bool(obj)        →  obj.__bool__()
obj()            →  obj.__call__()
with obj:        →  obj.__enter__() / obj.__exit__()
abs(obj)         →  obj.__abs__()
hash(obj)        →  obj.__hash__()
```

**Protocol table** — implement these to satisfy each protocol:

```
Protocol         Required Methods
-------------------------------------------------
Sized            __len__
Iterable         __iter__
Iterator         __iter__, __next__
Sequence         __len__, __getitem__
Mapping          __len__, __getitem__, __iter__
Callable         __call__
Context Manager  __enter__, __exit__
Comparable       __eq__, __lt__ (+ total_ordering)
```

**Why dunders are called on the class, not the instance:**

```python
class Sneaky:
    def __len__(self):
        return 5

s = Sneaky()
s.__len__ = lambda: 999   # monkey-patch instance attribute

len(s)      # → 5   (calls type(s).__len__(s), ignores instance)  # ←
s.__len__() # → 999 (direct call bypasses protocol)
```

This is a deliberate CPython security/performance decision.

---

## Chapter 2: Object Lifecycle — `__new__`, `__init__`, `__del__`

`__new__` creates the instance. `__init__` initializes it. They are separate because **creation and initialization are conceptually different** — relevant for immutable types and singletons.

```python
# Singleton using __new__:
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)   # ← create only once
        return cls._instance

    def __init__(self, value):
        if not hasattr(self, '_initialized'):      # ← guard: __init__ runs EVERY call
            self.value = value
            self._initialized = True

a = Singleton(1)
b = Singleton(2)
print(a is b)      # True — same object
print(a.value)     # 1 — not overwritten because of guard
```

**Subclassing immutable types** — must use `__new__` because you can't modify after creation:

```python
class AlwaysPositive(int):
    def __new__(cls, value):
        return super().__new__(cls, abs(value))  # ← value set in __new__, not __init__

n = AlwaysPositive(-42)
print(n)   # 42
```

**`__del__`** — called when object is garbage collected. Avoid relying on it (non-deterministic, may never run in PyPy, silently ignores exceptions). Use context managers instead.

---

## Chapter 3: String Representations — `__str__`, `__repr__`, `__format__`

```
Method       Called by           Purpose
-----------------------------------------------------------
__repr__     repr(obj)           Unambiguous, for developers
             str() fallback      Ideal: eval(repr(obj)) == obj
             f"{obj!r}"
__str__      str(obj)            Human-readable, for users
             print(obj)          Falls back to __repr__ if missing
             f"{obj}"
__format__   format(obj, spec)   Custom format spec
             f"{obj:spec}"
```

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        # Ideal: eval(repr(v)) == v
        return f"Vector({self.x!r}, {self.y!r})"   # ← !r applies repr() to each value

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __format__(self, spec):
        if spec == "polar":
            import math
            r = math.sqrt(self.x**2 + self.y**2)
            theta = math.atan2(self.y, self.x)
            return f"({r:.2f}, {theta:.2f}rad)"
        elif spec == "":
            return str(self)
        return format(str(self), spec)   # ← delegate to str's format for width specs

v = Vector(1, 2)
repr(v)        # "Vector(1, 2)"
str(v)         # "(1, 2)"
print(v)       # "(1, 2)"
f"{v!r}"       # "Vector(1, 2)"
f"{v:polar}"   # "(2.24, 1.11rad)"
```

---

## Chapter 4: Comparison and Ordering — `__eq__`, `__lt__`, `__hash__`

**Why return `NotImplemented` and not `False`?**

When Python evaluates `a == b`:
1. Call `a.__eq__(b)` — if `NotImplemented`, continue
2. Call `b.__eq__(a)` (reflected) — if `NotImplemented`, fall back to identity
3. Fall back: `a is b`

If you return `False` instead of `NotImplemented`, Python never asks the right-hand object.

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __eq__(self, other):
        if isinstance(other, Temperature):
            return self.celsius == other.celsius
        return NotImplemented   # ← NOT False — allows reflected check

    def __lt__(self, other):
        if isinstance(other, Temperature):
            return self.celsius < other.celsius
        return NotImplemented
```

**`__hash__` contract:** if `a == b`, then `hash(a) == hash(b)`. If you define `__eq__`, Python sets `__hash__ = None` unless you also define it.

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __hash__(self):
        return hash((self.x, self.y))   # ← tuple hash — safe and consistent with __eq__
```

**`@total_ordering`** — define `__eq__` + one of `__lt__/__le__/__gt__/__ge__`, get all six:

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

v1, v2 = Version(1, 2, 0), Version(2, 0, 0)
print(v1 < v2)   # True
print(v1 > v2)   # False  (derived by @total_ordering)
print(v1 <= v2)  # True   (derived)
print(sorted([Version(1,0,0), Version(0,9,0), Version(1,1,0)]))
```

---

## Chapter 5: Arithmetic Operators — `__add__`, `__radd__`, `__iadd__`

**Full operator table:**

```
Method        Operator    Reflected    In-Place
---------------------------------------------------
__add__       a + b       __radd__     __iadd__ (+=)
__sub__       a - b       __rsub__     __isub__ (-=)
__mul__       a * b       __rmul__     __imul__ (*=)
__truediv__   a / b       __rtruediv__ __itruediv__ (/=)
__floordiv__  a // b      __rfloordiv__ __ifloordiv__ (//=)
__mod__       a % b       __rmod__     __imod__ (%=)
__pow__       a ** b      __rpow__     __ipow__ (**=)
__matmul__    a @ b       __rmatmul__  __imatmul__ (@=)
```

**Why `__radd__` exists** — when Python evaluates `a + b`:
1. Call `a.__add__(b)` — if `NotImplemented`, continue
2. Call `b.__radd__(a)` — if `NotImplemented`, raise TypeError

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        if isinstance(other, (int, float)):    # scalar add
            return Vector(self.x + other, self.y + other)
        return NotImplemented

    def __radd__(self, other):
        # Called when: other + self (and other.__add__(self) returned NotImplemented)
        return self.__add__(other)   # ← commutative — just delegate

    def __iadd__(self, other):
        # Called for += — modifies self in place, returns self (efficient!)
        if isinstance(other, Vector):
            self.x += other.x
            self.y += other.y
            return self
        return NotImplemented

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        return NotImplemented

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __neg__(self):    return Vector(-self.x, -self.y)  # unary -
    def __pos__(self):    return Vector(self.x, self.y)    # unary +, returns copy
    def __abs__(self):    return (self.x**2 + self.y**2) ** 0.5  # abs() = magnitude

    def __repr__(self): return f"Vector({self.x}, {self.y})"

v = Vector(1, 2)
print(v + Vector(10, 20))  # Vector(11, 22)
print(v + 5)               # Vector(6, 7)
print(5 + v)               # Vector(6, 7)  — uses __radd__
print(3 * v)               # Vector(3, 6)  — uses __rmul__
print(-v)                  # Vector(-1, -2)
print(abs(v))              # 2.23...
```

---

## Chapter 6: Container Protocol — `__len__`, `__getitem__`, `__contains__`

The container protocol makes your class behave like a list, dict, or sequence.

```python
class Matrix:
    def __init__(self, rows, cols, default=0):
        self.rows, self.cols = rows, cols
        self._data = [[default] * cols for _ in range(rows)]

    def __len__(self):
        return self.rows   # ← convention: len of 2D = number of rows

    def __getitem__(self, key):
        row, col = key     # ← allows m[0, 1] syntax (passes as a tuple)
        return self._data[row][col]

    def __setitem__(self, key, value):
        row, col = key
        self._data[row][col] = value

    def __contains__(self, value):
        return any(value in row for row in self._data)

    def __iter__(self):
        return iter(self._data)   # ← iterate rows

    def __bool__(self):
        return any(any(row) for row in self._data)  # ← False if all zeros

m = Matrix(3, 3)
m[0, 0] = 1
m[1, 1] = 5
print(m[1, 1])   # 5
print(5 in m)    # True
```

**Slice support** in `__getitem__`:

```python
def __getitem__(self, index):
    if isinstance(index, slice):
        indices = range(*index.indices(len(self)))  # ← .indices() handles step/negative
        return [self._get_item(i) for i in indices]
    if index < 0:
        index += len(self)
    ...
```

---

## Chapter 7: Iteration Protocol — `__iter__`, `__next__`

Two types of objects work in `for` loops:

```
Iterable  — has __iter__, returns an iterator (can be looped multiple times)
Iterator  — has __iter__ + __next__, is consumed in one pass
```

```python
# Iterable + Iterator combined (single-pass):
class CountDown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self   # ← returning self means single-use iterator

    def __next__(self):
        if self.current <= 0:
            raise StopIteration   # ← MUST raise StopIteration to signal end
        value = self.current
        self.current -= 1
        return value

# Separate iterable and iterator (re-usable):
class Range:
    def __init__(self, stop):
        self.stop = stop

    def __iter__(self):
        return RangeIterator(self.stop)   # ← new iterator each time, so re-usable

class RangeIterator:
    def __init__(self, stop):
        self.stop, self.current = stop, 0

    def __iter__(self): return self   # ← iterators must return self
    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        val = self.current
        self.current += 1
        return val

r = Range(3)
list(r)   # [0, 1, 2]
list(r)   # [0, 1, 2]  — works again! Because Range creates a new iterator each time
```

---

## Chapter 8: Callable Protocol — `__call__`

Any object with `__call__` can be called like a function. **Callable objects preserve state between calls** — something plain functions and lambdas cannot do.

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, x):
        return x * self.factor

double = Multiplier(2)
triple = Multiplier(3)
print(double(5))   # 10
print(triple(5))   # 15

# Callable objects are great for configurable predicates:
class InRange:
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
    def __call__(self, x):
        return self.lo <= x <= self.hi

is_valid_port = InRange(1, 65535)
print(is_valid_port(80))     # True
print(is_valid_port(99999))  # False
print(list(filter(is_valid_port, [0, 80, 443, 65536])))  # [80, 443]

callable(double)  # True  — checks for __call__ on the TYPE
callable(42)      # False
```

---

## Chapter 9: Context Manager Protocol — `__enter__`, `__exit__`

```python
import time

class Timer:
    def __enter__(self):
        self._start = time.time()
        return self   # ← bound to the 'as' variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self._start
        return False  # ← False = propagate exceptions; True = suppress them

with Timer() as t:
    result = sum(range(1_000_000))
print(f"Elapsed: {t.elapsed:.3f}s")
```

**`__exit__` signature:** receives exception info if an exception was raised inside the `with` block. Return `True` to suppress it, `False` (or `None`) to re-raise.

```python
class SuppressOSError:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is OSError:
            return True    # ← suppress this exception type
        return False       # ← propagate everything else

with SuppressOSError():
    open("/nonexistent/path")   # silently ignored
print("Still running")
```

---

## Chapter 10: Operator Overloading — Matrix Example

Full operator overloading combining `__matmul__`, `__add__`, `__mul__`, `__eq__`:

```python
class Matrix:
    def __init__(self, data):
        self.data = [list(row) for row in data]
        self.rows, self.cols = len(data), len(data[0])

    def __matmul__(self, other):
        """Matrix multiplication: A @ B"""
        if isinstance(other, Matrix):
            if self.cols != other.rows:
                raise ValueError(f"Shape mismatch: {self.rows}x{self.cols} @ {other.rows}x{other.cols}")
            result = [[sum(self.data[i][k] * other.data[k][j]
                          for k in range(self.cols))
                       for j in range(other.cols)]
                      for i in range(self.rows)]
            return Matrix(result)
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, Matrix):
            if (self.rows, self.cols) != (other.rows, other.cols):
                raise ValueError("Shape mismatch")
            return Matrix([[self.data[i][j] + other.data[i][j]
                            for j in range(self.cols)]
                           for i in range(self.rows)])
        return NotImplemented

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Matrix([[x * scalar for x in row] for row in self.data])
        return NotImplemented

    def __rmul__(self, scalar): return self.__mul__(scalar)

    def __eq__(self, other):
        if isinstance(other, Matrix):
            return self.data == other.data
        return NotImplemented

    def __repr__(self):
        return f"Matrix({self.data})"

A = Matrix([[1, 2], [3, 4]])
B = Matrix([[5, 6], [7, 8]])
print(A @ B)    # Matrix([[19, 22], [43, 50]])
print(A + B)    # element-wise
print(3 * A)    # scalar from left — uses __rmul__
```

---

## Chapter 11: Attribute Access — `__getattr__`, `__getattribute__`

```
obj.name access order:
1. type(obj).__mro__ → data descriptor (has __get__ AND __set__)
2. obj.__dict__
3. type(obj).__mro__ → non-data descriptor (has __get__ only) or class var
4. type(obj).__getattr__(name)  — if defined, last resort
```

**`__getattr__`** — called only when normal lookup fails:

```python
class Proxy:
    def __init__(self, target):
        object.__setattr__(self, '_target', target)   # ← bypass our __setattr__

    def __getattr__(self, name):
        # Only reached when attribute NOT found normally
        return getattr(self._target, name)
```

**`__getattribute__`** — called for EVERY attribute access (use with extreme care):

```python
class TracingProxy:
    def __init__(self, target):
        object.__setattr__(self, '_target', target)

    def __getattribute__(self, name):
        # Intercepts EVERYTHING — including '_target'!
        target = object.__getattribute__(self, '_target')  # ← must use object's version
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        print(f"Accessing: {name}")
        return getattr(target, name)
```

---

## Chapter 12: Pickling and Copy

```python
# __getstate__ / __setstate__ — exclude unpicklable attributes:
class Connection:
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_socket']   # ← exclude socket from pickle
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._socket = self._connect()  # ← reconnect on restore

# __copy__ / __deepcopy__:
import copy

class Graph:
    def __copy__(self):
        return Graph(self.nodes)   # shares nodes list (shallow)

    def __deepcopy__(self, memo):
        return Graph(copy.deepcopy(self.nodes, memo))  # ← memo prevents infinite recursion
```

---

## Common Mistakes

**Returning `False` instead of `NotImplemented`:**
```python
# WRONG:
def __eq__(self, other):
    if isinstance(other, MyClass):
        return self.x == other.x
    return False   # ← blocks reflected check; subclasses can never compare equal

# CORRECT:
    return NotImplemented
```

**Defining `__eq__` without `__hash__`:**
```python
class Broken:
    def __eq__(self, other): ...
    # Python silently sets __hash__ = None — instances can't be in sets or dict keys!
```

**`__iadd__` forgetting to return `self`:**
```python
def __iadd__(self, other):
    self.x += other.x
    # forgetting: return self
    # Python then sets the variable to None!
```

**Single-use iterators from `__iter__` returning `self`:**
```python
class Data:
    def __iter__(self): return self  # ← exhausted after one loop, never resets
```

---

## Navigation

| | |
|---|---|
| Root theory | [../theory.md](../theory.md) |
| Root practice | [../practice.md](../practice.md) |
| Practice | [practice.md](./practice.md) |
| Next: Descriptors | [../02_descriptors/theory.md](../02_descriptors/theory.md) |

**[Back to 15_advanced_python](../theory.md)**
