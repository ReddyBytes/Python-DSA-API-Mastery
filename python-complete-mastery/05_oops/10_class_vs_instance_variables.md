# ⚡ 10 — Class Variables vs Instance Variables: The Shared State Trap

> *"This is one of the most common Python OOP bugs in production.*
> *It's subtle, sneaky, and will confuse you — until you understand it completely."*

---

## 🎬 The Story

You're building a game. Every player tracks their own score.
You also want to know the total number of players ever created.

```python
class Player:
    total_players = 0    # class variable — shared
    high_score    = 0    # class variable — shared

    def __init__(self, name):
        self.name  = name    # instance variable — unique
        self.score = 0       # instance variable — unique
        Player.total_players += 1
```

This works perfectly.
But if you're not careful, shared state becomes shared chaos.

---

## 🔑 The Fundamental Difference

```
┌──────────────────────────────────────────────────────────────────────┐
│  INSTANCE VARIABLE          │  CLASS VARIABLE                        │
├──────────────────────────────────────────────────────────────────────┤
│  Defined in __init__        │  Defined directly in class body        │
│  using self.name = value    │  as name = value                       │
│                              │                                        │
│  Unique per object           │  Shared across ALL instances          │
│  Lives in object.__dict__    │  Lives in Class.__dict__              │
│  Each object has its own     │  ONE copy, everyone reads it          │
│  copy in memory              │                                        │
└──────────────────────────────────────────────────────────────────────┘
```

```python
class Dog:
    species = "Canis lupus familiaris"   # class variable — ALL dogs share this

    def __init__(self, name, breed):
        self.name  = name    # instance variable — unique to THIS dog
        self.breed = breed   # instance variable — unique to THIS dog

d1 = Dog("Rex",    "Labrador")
d2 = Dog("Buddy",  "Poodle")
d3 = Dog("Shadow", "German Shepherd")

# Instance variables — each dog has their own:
print(d1.name)    # Rex
print(d2.name)    # Buddy

# Class variable — everyone shares:
print(d1.species)    # Canis lupus familiaris
print(d2.species)    # Canis lupus familiaris
print(Dog.species)   # Canis lupus familiaris  ← same object
```

---

## 🧠 Memory Model

```
CLASS DICT (Dog.__dict__):
┌────────────────────────────────────────┐
│  species = "Canis lupus familiaris"    │  ← ONE copy, shared
└────────────────────────────────────────┘

INSTANCE DICTS:
┌───────────────────────┐  ┌───────────────────────┐
│  d1.__dict__          │  │  d2.__dict__          │
│  name  = "Rex"        │  │  name  = "Buddy"      │
│  breed = "Labrador"   │  │  breed = "Poodle"     │
└───────────────────────┘  └───────────────────────┘

When Python reads d1.species:
  1. Look in d1.__dict__     → not found
  2. Look in Dog.__dict__    → found! "Canis lupus familiaris"
  3. Return it
```

---

## ✅ Good Uses of Class Variables

```python
class BankAccount:
    INTEREST_RATE    = 0.05     # constant — same for all accounts
    OVERDRAFT_LIMIT  = -500     # constant — same for all accounts
    _total_accounts  = 0        # counter — tracks across all instances

    def __init__(self, owner, balance=0):
        self.owner   = owner
        self.balance = balance
        BankAccount._total_accounts += 1

    @classmethod
    def get_account_count(cls):
        return cls._total_accounts

    @classmethod
    def update_interest_rate(cls, new_rate):
        cls.INTEREST_RATE = new_rate   # changes for ALL accounts!

a1 = BankAccount("Alice", 5000)
a2 = BankAccount("Bob",   8000)

print(BankAccount.get_account_count())    # 2

BankAccount.update_interest_rate(0.07)
print(a1.INTEREST_RATE)    # 0.07  ← a1 sees the update
print(a2.INTEREST_RATE)    # 0.07  ← a2 sees it too
```

---

## ⚠️ THE MUTABLE CLASS VARIABLE TRAP — The Most Dangerous Bug

This is where developers get burned.

```python
class Student:
    grades = []    # ← DANGER: mutable class variable!

    def __init__(self, name):
        self.name = name

    def add_grade(self, grade):
        self.grades.append(grade)   # modifying the SHARED list!

s1 = Student("Alice")
s2 = Student("Bob")

s1.add_grade(90)
s1.add_grade(85)

print(s1.grades)   # [90, 85]  ← looks correct
print(s2.grades)   # [90, 85]  ← WAIT WHAT?! Bob has Alice's grades?!
print(Student.grades)  # [90, 85]  ← it's the SAME list!
```

```
WHY IT HAPPENS:
  s1.grades.append(90)
      ↓
  Python looks up s1.grades:
    → Not in s1.__dict__
    → Found in Student.__dict__  ← the shared list!
  Python calls .append() on THAT shared list.
  Both s1 and s2 see the SAME list.
```

**The Fix — always use instance variables for mutable per-object data:**

```python
class Student:
    def __init__(self, name):
        self.name   = name
        self.grades = []    # ← instance variable — each student gets their OWN list!

    def add_grade(self, grade):
        self.grades.append(grade)

s1 = Student("Alice")
s2 = Student("Bob")

s1.add_grade(90)
s1.add_grade(85)

print(s1.grades)   # [90, 85]  ✓
print(s2.grades)   # []        ✓  Bob has his own empty list
```

---

## 🔁 Immutable Class Variable — Surprisingly Safe (But Confusing)

When you ASSIGN to an instance attribute with the same name as a class attribute,
Python creates a NEW instance attribute that **shadows** the class attribute — it doesn't modify it.

```python
class Config:
    debug = False     # class variable

c1 = Config()
c2 = Config()

c1.debug = True    # ← creates a NEW instance attr on c1!
                   # Does NOT change Config.debug or c2.debug

print(c1.debug)        # True   ← c1's own instance attribute
print(c2.debug)        # False  ← still sees the class attribute
print(Config.debug)    # False  ← class attribute unchanged!
```

```
BEFORE c1.debug = True:
  c1.__dict__ = {}          (no 'debug' here)
  Config.__dict__ = {debug: False}

AFTER c1.debug = True:
  c1.__dict__ = {debug: True}   ← new instance attr created!
  c2.__dict__ = {}              (no 'debug' here — still uses class attr)
  Config.__dict__ = {debug: False}  ← unchanged!

c1.debug  → found in c1.__dict__ first → True
c2.debug  → not in c2.__dict__ → found in Config.__dict__ → False
```

This is WHY immutable class vars are "safer" — assignment creates a local shadow rather than mutating the shared value.
But with MUTABLE objects like lists, `.append()` doesn't assign — it mutates in place. So the shadow trick doesn't happen!

---

## 📊 Decision Guide

```
┌──────────────────────────────────────────────────────────────────────┐
│  Use CLASS VARIABLE when:                                            │
│    • Value is same for every instance (constants, rates, limits)    │
│    • Tracking something across all instances (counter, registry)    │
│    • Configuration that applies to the whole class                  │
│    • Immutable value (int, float, str, tuple)                       │
├──────────────────────────────────────────────────────────────────────┤
│  Use INSTANCE VARIABLE when:                                         │
│    • Every object needs its own copy of the data                    │
│    • The value is unique per object                                  │
│    • The value is mutable (list, dict, set)                         │
│    • You're not sure — default to instance variable                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

## ⚠️ The `del` Behaviour

```python
class Animal:
    sound = "..."

a = Animal()
a.sound = "Woof"       # creates instance attribute shadowing class attr

print(a.sound)         # "Woof"  ← instance attr
del a.sound            # delete the instance attr
print(a.sound)         # "..."   ← now falls back to class attr!
```

---

## 🎯 Key Takeaways

```
• Class variables live in Class.__dict__ — shared by all instances
• Instance variables live in instance.__dict__ — unique per object
• Attribute lookup: instance.__dict__ first → then Class.__dict__
• ASSIGNING to instance creates a shadow (safe for immutables)
• MUTATING a mutable class variable (list.append) affects ALL instances
• Rule: mutable data → always use instance variables in __init__
• Class variables good for: constants, counters, shared config
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [09 — Class/Instance/Static Methods](./09_class_instance_static_methods.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [11 — Properties](./11_properties.md) |
