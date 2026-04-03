# 🔑 03 — `__init__` & `self`: Initialization Deep Dive

> *"`__init__` is not the constructor. It's the initializer.*
> *`__new__` is the constructor. Knowing the difference is a senior-level signal."*

---

## 🎬 The Story

When you hire a new employee, two things happen:
1. HR creates an employee ID and a file (allocates space)
2. HR fills in the file: name, department, salary (initializes data)

Step 1 = `__new__` (Python handles this)
Step 2 = `__init__` (you write this)

Most developers only know step 2. That's fine for most code.
But knowing step 1 separates intermediate from senior engineers.

---

## 🔧 `__init__` — What It Actually Does

`__init__` is called after the object is created.
Its job: initialize the object's instance attributes.

```python
class Employee:
    def __init__(self, name, department, salary):
        self.name       = name          # instance attribute
        self.department = department    # instance attribute
        self.salary     = salary        # instance attribute
        self.is_active  = True          # default attribute — same for everyone
        self._id        = None          # will be set later

emp1 = Employee("Alice", "Engineering", 80000)
emp2 = Employee("Bob",   "Marketing",   65000)

print(emp1.name)        # Alice
print(emp2.department)  # Marketing
print(emp1.is_active)   # True
```

**What Python does when you call `Employee("Alice", ...)`:**
```
1. Python calls Employee.__new__(Employee)
   → creates blank object in heap memory

2. Python calls Employee.__init__(new_object, "Alice", "Engineering", 80000)
   → new_object is 'self'
   → sets self.name = "Alice", etc.

3. Returns the initialized object
   → stored in emp1
```

---

## 🧠 `self` — The Full Picture

`self` is the most misunderstood concept in Python OOP.

### What self IS:
- The first parameter of any instance method
- A reference to the specific object the method was called on
- Automatically passed by Python — you don't pass it manually

### What self IS NOT:
- A keyword (you can name it anything — but NEVER do that in real code)
- Magic — it's just the first argument

```python
class Dog:
    def __init__(this, name):      # 'this' works — but don't do this in real code!
        this.name = name

    def bark(this):
        print(f"{this.name}: Woof!")

d = Dog("Rex")
d.bark()    # Rex: Woof!
```

### How Python passes self:

```python
class Cat:
    def __init__(self, name):
        self.name = name

    def meow(self):
        print(f"{self.name}: Meow!")

c = Cat("Whiskers")

# These two lines are IDENTICAL:
c.meow()               # regular call — Python auto-passes c as self
Cat.meow(c)            # explicit call — manually passing the object
```

```
c.meow()
   ↓ Python translates to:
Cat.meow(c)
         ↑
   This is 'self' inside meow()
```

---

## 🔬 `__new__` — The Real Constructor

`__new__` is called BEFORE `__init__`.
It's responsible for actually creating and returning the object.

```python
class MyClass:
    def __new__(cls, *args, **kwargs):
        print(f"__new__ called — creating object for {cls}")
        instance = super().__new__(cls)   # actually allocates memory
        return instance                    # MUST return the object!

    def __init__(self, value):
        print(f"__init__ called — initializing with {value}")
        self.value = value

obj = MyClass(42)
# Output:
# __new__ called — creating object for <class '__main__.MyClass'>
# __init__ called — initializing with 42
```

**If `__new__` doesn't return an instance of the class, `__init__` is never called:**

```python
class Weird:
    def __new__(cls):
        print("__new__ called")
        return 42          # returns an int, not an instance!

    def __init__(self):
        print("__init__ called")   # ← NEVER runs!

w = Weird()
print(w)      # 42   ← w is just the integer 42!
```

### Real use case for `__new__` — Singleton pattern:

```python
class Singleton:
    _instance = None    # class attribute to hold the single instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance    # always returns the SAME object

s1 = Singleton()
s2 = Singleton()

print(s1 is s2)    # True — same object!
print(id(s1) == id(s2))    # True
```

---

## 🏗️ When and How to Override `__new__`

Most developers never override `__new__`. But three real-world patterns require it.

---

### Pattern 1: Singleton — Only One Instance Ever

The simple Singleton above works, but in practice `__init__` is called every time you "create" an instance — which re-initializes the already-existing object. Guard against that:

```python
class DatabaseConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)  # create the ONE instance
        return cls._instance                       # always return the same one

    def __init__(self, host, port):
        # __init__ is called every time — guard against re-initialization
        if not hasattr(self, '_initialized'):
            self.host = host
            self.port = port
            self._initialized = True

db1 = DatabaseConnection("localhost", 5432)
db2 = DatabaseConnection("otherhost", 5433)

print(db1 is db2)       # True — same object!
print(db1.host)         # "localhost"  (first init won)
```

---

### Pattern 2: Immutable Type Subclass

You **cannot** set attributes in `__init__` on immutable types like `int` and `tuple` — the object is already sealed by the time `__init__` runs. Use `__new__` instead.

```python
class PositiveInt(int):
    def __new__(cls, value):
        if value <= 0:
            raise ValueError(f"PositiveInt requires value > 0, got {value}")
        return super().__new__(cls, value)  # create the int with the validated value

x = PositiveInt(5)
print(x + 3)        # 8 — behaves exactly like int
print(type(x))      # <class 'PositiveInt'>

y = PositiveInt(-1) # ValueError: PositiveInt requires value > 0
```

The key: `super().__new__(cls, value)` passes `value` to `int.__new__`, which sets the immutable value. You cannot do this in `__init__` — by then `int` is already sealed.

---

### The `__new__` → `__init__` Sequence

```
MyClass(arg1, arg2)
    │
    ├─ Step 1: MyClass.__new__(MyClass, arg1, arg2)
    │          → allocates memory
    │          → returns a new object (usually instance of MyClass)
    │
    └─ Step 2: if returned object is instance of MyClass:
               MyClass.__init__(new_object, arg1, arg2)
               → initializes attributes on the object
```

```python
class TrackedCreation:
    def __new__(cls, *args, **kwargs):
        print(f"__new__ called — allocating {cls.__name__}")
        instance = super().__new__(cls)
        return instance

    def __init__(self, name):
        print(f"__init__ called — initializing with name={name}")
        self.name = name

t = TrackedCreation("test")
# __new__ called — allocating TrackedCreation
# __init__ called — initializing with name=test
```

---

### When to Use Each

```
__init__:  Almost always. Sets instance attributes. Called after object exists.
__new__:   Rarely. When you need to control object creation itself:
           • Singleton pattern
           • Subclassing immutable types (int, str, float, tuple, frozenset)
           • Custom memory allocation or object pooling
           • Factory patterns that return different types
```

---

## ✅ Validation Inside `__init__`

`__init__` is the right place to validate input.

```python
class Temperature:
    def __init__(self, celsius):
        if not isinstance(celsius, (int, float)):
            raise TypeError(f"Temperature must be a number, got {type(celsius)}")
        if celsius < -273.15:
            raise ValueError(f"Temperature below absolute zero: {celsius}°C")
        self.celsius = celsius

    @property
    def fahrenheit(self):
        return (self.celsius * 9/5) + 32

t = Temperature(100)
print(t.fahrenheit)    # 212.0

# Temperature(-300)    # ← ValueError: below absolute zero
# Temperature("hot")   # ← TypeError: not a number
```

---

## 🔁 `__init__` With Default Values

```python
class Product:
    def __init__(self, name, price, category="General", in_stock=True):
        self.name     = name
        self.price    = price
        self.category = category
        self.in_stock = in_stock

p1 = Product("Laptop", 80000)                  # uses defaults
p2 = Product("Pen", 20, "Stationery", True)    # all specified
p3 = Product("Course", 999, category="Education")  # mixed

print(p1.category)    # "General"
print(p2.category)    # "Stationery"
print(p3.in_stock)    # True
```

---

## 🧩 Calling Parent `__init__` with `super()`

When a child class has its own `__init__`, it must explicitly call the parent's `__init__` using `super()`. If you don't, the parent's attributes are never set up.

```python
class Animal:
    def __init__(self, name, sound):
        self.name  = name
        self.sound = sound

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name, "Woof")    # ← call parent's __init__
        self.breed = breed                 # ← then add own attributes

d = Dog("Rex", "Labrador")
print(d.name)    # "Rex"   ← set by Animal.__init__
print(d.sound)   # "Woof"  ← set by Animal.__init__
print(d.breed)   # "Labrador" ← set by Dog.__init__
```

**What happens if you forget `super().__init__()`:**
```python
class Dog(Animal):
    def __init__(self, name, breed):
        # FORGOT: super().__init__(name, "Woof")
        self.breed = breed

d = Dog("Rex", "Labrador")
print(d.breed)    # "Labrador"  ← works
print(d.name)     # AttributeError! name was never set!
```

---

## 🗃️ `__init__` vs `__post_init__` (Dataclasses)

With regular classes, you write `__init__` manually.
With `dataclasses`, it's auto-generated — but you can hook into post-initialization with `__post_init__`:

```python
from dataclasses import dataclass

@dataclass
class Circle:
    radius: float

    def __post_init__(self):
        if self.radius < 0:
            raise ValueError("Radius cannot be negative")
        self.area = 3.14159 * self.radius ** 2   # computed attribute

c = Circle(5)
print(c.area)    # 78.53975
```

---

## 🗺️ Full Object Creation Flow

```
User code:  account = BankAccount("Alice", 5000)
                              ↓
             Python calls:  BankAccount.__new__(BankAccount, "Alice", 5000)
                              ↓
             __new__ calls: object.__new__(BankAccount)
                              ↓
             Blank BankAccount object created in heap memory
                              ↓
             __new__ returns the blank object
                              ↓
             Python calls:  BankAccount.__init__(blank_object, "Alice", 5000)
                              ↓
             __init__ sets: self.owner = "Alice", self.balance = 5000
                              ↓
             Initialized object returned → stored in 'account'
```

---

## ⚠️ Common Mistakes

```python
# ❌ Mistake 1: Forgetting self on instance attributes
class Broken:
    def __init__(self, name):
        name = name       # local variable! NOT an instance attribute!

b = Broken("Alice")
print(b.name)    # AttributeError: 'Broken' object has no attribute 'name'

# ✅ Fix:
class Fixed:
    def __init__(self, name):
        self.name = name   # instance attribute ✓

# ❌ Mistake 2: Calling __init__ directly (almost never needed)
obj = BankAccount.__init__("Alice", 5000)   # wrong — no object created!

# ✅ Correct:
obj = BankAccount("Alice", 5000)

# ❌ Mistake 3: Not calling super().__init__() in child class
# ✅ Always call super().__init__() at the START of child __init__

# ❌ Mistake 4: Returning a value from __init__
class Bad:
    def __init__(self, x):
        self.x = x
        return self.x    # ← TypeError! __init__ must return None
```

---

## 🎯 Key Takeaways

```
• __init__ initializes the object — does NOT create it
• __new__ creates the object — rarely overridden
• self = the current object, automatically passed by Python
• self is NOT a keyword — just a very strong convention
• Validate inputs inside __init__ — fail early, fail loudly
• Always call super().__init__() in child classes
• __new__ is needed for: singletons, immutable types, metaclasses
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [02 — Classes & Objects](./02_classes_and_objects.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [04 — Encapsulation](./04_encapsulation.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Classes And Objects](./02_classes_and_objects.md) &nbsp;|&nbsp; **Next:** [Encapsulation →](./04_encapsulation.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Polymorphism](./06_polymorphism.md) · [Abstraction](./07_abstraction.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Slots](./15_slots.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
