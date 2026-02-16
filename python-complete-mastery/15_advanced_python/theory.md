# 🧙 Advanced Python  
Deep Internals & Powerful Language Features

---

# 🎯 Why Advanced Python Matters

Most developers use Python.
Few understand how it works internally.

Advanced Python concepts help you:

- Write clean APIs
- Build frameworks
- Optimize memory
- Design reusable libraries
- Understand Python internals
- Debug complex issues
- Pass senior-level interviews

This is where you move from:

User of Python  
to  
Engineer of Python.

---

# 🧩 1️⃣ Dunder (Magic) Methods

Dunder means:

Double underscore methods.

Example:

```python
__init__
__str__
__repr__
__len__
__add__
__call__
```

These methods define how objects behave.

---

## 🔹 Why They Exist

When you write:

```python
a + b
```

Internally Python calls:

```python
a.__add__(b)
```

When you write:

```python
len(obj)
```

Python calls:

```python
obj.__len__()
```

Magic methods define object behavior.

---

# 🧠 Important Dunder Methods

---

## __init__

Constructor.

Called when object created.

---

## __str__

Human-readable string.

Used by print().

---

## __repr__

Developer representation.

Used in debugging.

Best practice:
Make __repr__ unambiguous.

---

## __len__

Defines length.

---

## __add__

Defines addition behavior.

Used for operator overloading.

---

## __eq__

Defines equality behavior.

---

## __call__

Makes object callable like function.

Example:

```python
class A:
    def __call__(self):
        print("Called")

a = A()
a()  # works
```

---

# ⚙️ 2️⃣ Operator Overloading

You can redefine operators.

Example:

```python
class Vector:
    def __init__(self, x):
        self.x = x

    def __add__(self, other):
        return Vector(self.x + other.x)
```

Now:

```python
v1 + v2
```

Works.

Used in:

- Mathematical libraries
- Custom data structures
- Domain-specific APIs

---

# 🧠 3️⃣ Dataclasses

Before dataclasses:

You had to manually write:

- __init__
- __repr__
- __eq__

Dataclasses simplify this.

Example:

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
```

Automatically generates:

- __init__
- __repr__
- __eq__

Cleaner and shorter.

---

## Advanced Dataclass Features

---

### Default values

```python
age: int = 18
```

---

### Frozen dataclasses (immutable)

```python
@dataclass(frozen=True)
```

Prevents modification.

---

### Order support

```python
@dataclass(order=True)
```

Enables comparison operators.

---

# 🧠 4️⃣ __slots__

By default:

Each object has __dict__.

Consumes memory.

Using:

```python
class User:
    __slots__ = ['name', 'age']
```

Prevents dynamic attribute creation.
Reduces memory footprint.

Used in:

High-scale systems with many objects.

---

# 🧠 5️⃣ Descriptors

One of the most advanced topics.

Descriptor is an object that:

Implements:

- __get__
- __set__
- __delete__

Used to control attribute access.

---

## Example

```python
class Descriptor:
    def __get__(self, obj, objtype):
        return "Value"

class MyClass:
    attr = Descriptor()
```

Accessing:

```python
obj.attr
```

Calls __get__.

Descriptors power:

- Properties
- Methods
- Class methods
- Static methods
- Dataclasses internals
- ORM frameworks

Very powerful.

---

# 🧠 6️⃣ Property Decorator (Descriptor Example)

Example:

```python
class User:
    def __init__(self, age):
        self._age = age

    @property
    def age(self):
        return self._age
```

Now:

```python
user.age
```

Calls getter method.

property is built using descriptor protocol.

---

# 🧠 7️⃣ Metaclasses

Most advanced concept.

Class itself is object.

Created by metaclass.

Default metaclass:

type

Example:

```python
class MyClass:
    pass
```

Internally:

```python
MyClass = type("MyClass", (), {})
```

Metaclass defines:

How class is created.

Used in:

- Django ORM
- Enum
- Advanced frameworks

Rarely needed in normal apps.

---

# 🧠 8️⃣ Introspection

Introspection means:

Inspecting objects at runtime.

Useful functions:

```python
type(obj)
dir(obj)
isinstance(obj, Class)
hasattr(obj, 'name')
getattr(obj, 'name')
```

Used in:

- Debugging
- Frameworks
- Serialization
- Reflection systems

---

# 🧠 9️⃣ Callable Objects

If class defines __call__:

Object behaves like function.

Example:

```python
class Multiply:
    def __init__(self, n):
        self.n = n

    def __call__(self, x):
        return x * self.n
```

Used in:

- Decorators
- Strategy pattern
- Custom callable logic

---

# 🧠 🔟 Dynamic Attribute Handling

Using:

```python
__getattr__
__setattr__
```

Allows:

Custom attribute access behavior.

Used in:

- ORMs
- Proxies
- Lazy-loading objects

---

# 🏗 1️⃣1️⃣ Real Production Use Cases

---

## 🔹 ORMs (Django)

Use metaclasses and descriptors.

---

## 🔹 Data Validation Libraries

Use descriptors and properties.

---

## 🔹 Frameworks

Use introspection heavily.

---

## 🔹 Scientific Libraries

Use operator overloading.

---

# ⚠️ 1️⃣2️⃣ Common Mistakes

❌ Overusing magic methods  
❌ Misusing metaclasses unnecessarily  
❌ Breaking readability  
❌ Ignoring __repr__  
❌ Overengineering simple classes  

Advanced features must be used carefully.

---

# 🏆 1️⃣3️⃣ Engineering Maturity Levels

Beginner:
Uses classes normally.

Intermediate:
Uses dataclasses and properties.

Advanced:
Understands dunder methods.

Senior:
Understands descriptors and metaclasses.

Architect:
Uses advanced internals wisely.

---

# 🧠 Final Mental Model

Advanced Python gives you:

Control over object behavior.

Key concepts:

- Dunder methods define behavior
- Operator overloading customizes operators
- Dataclasses simplify data containers
- __slots__ optimizes memory
- Descriptors control attribute access
- Metaclasses control class creation
- Introspection inspects objects
- __call__ makes objects callable

These tools make Python powerful.

But power requires responsibility.

Use them when needed.

---

# 🔁 Navigation

Previous:  
[14_memory_management/interview.md](../14_memory_management/interview.md)

Next:  
[15_advanced_python/interview.md](./interview.md)

