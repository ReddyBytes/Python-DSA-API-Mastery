# 🏛️ 02 — Classes & Objects: Blueprint vs Instance

> *"A class is the idea. An object is the reality.*
> *The blueprint is not the house. The house is the house."*

---

## 🎬 The Story

An architect designs a blueprint for a house.
The blueprint specifies: 3 rooms, 2 bathrooms, a kitchen.
The blueprint itself is NOT a house. You can't live in a blueprint.

But from ONE blueprint, you can build MANY houses.
Each house is independent — you can paint house #1 red without affecting house #2.

This is exactly how classes and objects work.

```
CLASS  = the blueprint (design, no memory allocated)
OBJECT = the actual house built from that blueprint (memory allocated)
```

---

## 🏗️ Creating Your First Class

```python
class BankAccount:
    pass
```

This is a class. Right now:
- No memory is used for any account
- No balance exists anywhere
- Nothing happens — it's just a blueprint registered in memory

```python
# Creating objects (instances) FROM the class:
account1 = BankAccount()
account2 = BankAccount()
account3 = BankAccount()

# Three completely independent objects in memory
# From ONE blueprint
```

---

## 🧠 What Happens in Memory When You Create an Object

```python
account1 = BankAccount()
```

```
STEP BY STEP:

1. Python calls BankAccount.__new__(BankAccount)
   → allocates a blank object in HEAP memory

2. Python calls BankAccount.__init__(the_new_object)
   → fills in initial data

3. A reference to the heap object is returned
   → stored in the variable 'account1'

MEMORY MODEL:
┌──────────────────────────────────────────────────────────────┐
│  STACK (names/references)                                    │
│  account1 → ──────────────┐                                  │
│  account2 → ──────────┐   │                                  │
│                        │   │                                  │
│  HEAP (actual objects) │   │                                  │
│  ┌─────────────────┐   │   │                                  │
│  │ BankAccount     │ ←─┘   │                                  │
│  │ id: 0xB456      │       │                                  │
│  └─────────────────┘       │                                  │
│  ┌─────────────────┐       │                                  │
│  │ BankAccount     │ ←─────┘                                  │
│  │ id: 0xA123      │                                          │
│  └─────────────────┘                                          │
└──────────────────────────────────────────────────────────────┘

account1 and account2 are different objects at different memory addresses.
```

---

## 🔍 Proving Objects Are Independent

```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner   = owner
        self.balance = balance

account1 = BankAccount("Alice", 5000)
account2 = BankAccount("Bob",   12000)

# Modifying one does NOT affect the other:
account1.balance += 1000

print(account1.balance)    # 6000  ← changed
print(account2.balance)    # 12000 ← untouched

# They are completely separate objects:
print(account1 is account2)    # False
print(id(account1))            # different memory address
print(id(account2))            # different memory address
```

---

## 📦 Class Attributes vs Instance Attributes

This is one of the most confusing distinctions. Understand it deeply.

```
INSTANCE ATTRIBUTE  → unique per object, defined in __init__ using self
CLASS ATTRIBUTE     → shared across ALL instances, defined directly in class body
```

```python
class BankAccount:
    bank_name = "PyBank"      # ← CLASS attribute: shared by all accounts
    interest_rate = 0.05      # ← CLASS attribute: same for all

    def __init__(self, owner, balance):
        self.owner   = owner       # ← INSTANCE attribute: unique per object
        self.balance = balance     # ← INSTANCE attribute: unique per object

a1 = BankAccount("Alice", 5000)
a2 = BankAccount("Bob",   8000)

# Instance attributes — each has their own:
print(a1.owner)    # "Alice"
print(a2.owner)    # "Bob"

# Class attributes — shared:
print(a1.bank_name)    # "PyBank"
print(a2.bank_name)    # "PyBank"
print(BankAccount.bank_name)    # "PyBank" ← access via class directly
```

### ⚠️ The Class Attribute Trap

```python
class Counter:
    count = 0    # class attribute — shared!

c1 = Counter()
c2 = Counter()

Counter.count += 1    # changes the class attribute

print(c1.count)    # 1  ← sees the change!
print(c2.count)    # 1  ← sees the change too!
```

```python
# But assign to instance → creates an instance attribute (shadows class attr):
c1.count = 99       # creates a NEW instance attribute on c1 only!

print(c1.count)           # 99  ← c1's own instance attribute
print(c2.count)           # 1   ← still sees the class attribute
print(Counter.count)      # 1   ← class attribute unchanged
```

```
ATTRIBUTE LOOKUP ORDER:
1. Instance's own __dict__   ← found? use it. stop.
2. Class's __dict__          ← found? use it. stop.
3. Parent classes (MRO)      ← found? use it. stop.
4. AttributeError            ← not found anywhere
```

---

## 🔑 `self` — What It Actually Is

`self` is the biggest confusion for beginners.

> `self` is NOT a keyword in Python.
> It is just a conventional name for the first parameter.
> Python passes the object itself as the first argument automatically.

```python
class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        print(f"{self.name} says: Woof!")

d = Dog("Rex")
d.bark()    # Python translates this to:
            # Dog.bark(d)   ← d is passed as 'self'
```

```
d.bark()
  ↓ Python automatically does:
Dog.bark(d)
         ↑
         self inside the method = d = the object
```

---

## 🧪 Useful Built-in Tools for Objects

```python
class Car:
    wheels = 4
    def __init__(self, brand, speed):
        self.brand = brand
        self.speed = speed

car = Car("Toyota", 120)

# type() — what class is this?
print(type(car))              # <class '__main__.Car'>

# isinstance() — is this an instance of a class?
print(isinstance(car, Car))   # True
print(isinstance(car, str))   # False

# id() — memory address of the object
print(id(car))                # some memory address like 140234567

# __dict__ — see all instance attributes as a dictionary
print(car.__dict__)           # {'brand': 'Toyota', 'speed': 120}

# vars() — same as __dict__ but cleaner:
print(vars(car))              # {'brand': 'Toyota', 'speed': 120}

# hasattr() — does this attribute exist?
print(hasattr(car, 'brand'))   # True
print(hasattr(car, 'color'))   # False

# getattr() — safely get an attribute with default:
print(getattr(car, 'color', 'unknown'))   # 'unknown'  (no crash!)

# setattr() — set an attribute dynamically:
setattr(car, 'color', 'red')
print(car.color)              # 'red'

# delattr() — delete an attribute:
delattr(car, 'color')
```

---

## 🧬 Everything in Python Is an Object

This is the profound truth about Python.

```python
# int is an object:
x = 42
print(type(x))      # <class 'int'>
print(x.__class__)  # <class 'int'>

# Functions are objects:
def greet(): pass
print(type(greet))  # <class 'function'>
print(id(greet))    # memory address!

# Even the class itself is an object:
print(type(Car))    # <class 'type'>   ← Car is an instance of 'type'!
```

```
THE OBJECT HIERARCHY:
         type            ← the metaclass that creates all classes
          │
    ┌─────┴─────┐
    │           │
   int         Car       ← classes are instances of 'type'
    │           │
   42         car        ← objects are instances of their class
```

---

## 🎯 Key Takeaways

```
• Class = blueprint, no memory used, just a design
• Object = instance of class, real memory in heap
• self = the object passed automatically as first argument
• Class attributes are SHARED — instance attributes are UNIQUE
• Assigning to instance creates instance attr (shadows class attr)
• type(), isinstance(), id(), __dict__ are your debugging tools
• In Python, EVERYTHING is an object — functions, classes, integers
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [01 — Why OOP](./01_why_oop.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [03 — `__init__` & `self`](./03_init_and_self.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Why Oop](./01_why_oop.md) &nbsp;|&nbsp; **Next:** [Init And Self →](./03_init_and_self.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Polymorphism](./06_polymorphism.md) · [Abstraction](./07_abstraction.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Slots](./15_slots.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
