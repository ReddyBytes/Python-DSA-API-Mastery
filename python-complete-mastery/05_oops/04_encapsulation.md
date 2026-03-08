# 🔐 04 — Encapsulation: Protecting & Controlling State

> *"Encapsulation is not about hiding things.*
> *It's about protecting invariants — the rules that must always be true.*
> *A bank balance should never go below -overdraft_limit. Encapsulation enforces that."*

---

## 🎬 The Story

Imagine a hospital system.
A patient's medical records contain: blood type, allergies, medications, test results.

If anyone — a receptionist, a cleaning staff member, an intern — can directly edit these records,
the system is dangerous. A wrong blood type entry could kill a patient.

The records should be:
- Readable by authorized people
- Modifiable only through controlled procedures
- Never directly writable by random code

This is encapsulation.

---

## 🔑 The 3 Levels of Access in Python

Python uses naming conventions (not strict language enforcement like Java's `private`):

```
┌──────────────────────────────────────────────────────────────────────┐
│  CONVENTION    EXAMPLE          MEANING                              │
├──────────────────────────────────────────────────────────────────────┤
│  name          self.balance     Public — anyone can access           │
│  _name         self._balance    Protected — convention: internal use │
│  __name        self.__balance   Private — name mangled by Python     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ Public Attributes (no underscore)

Anyone can read or write — no restriction.

```python
class Car:
    def __init__(self, brand, speed):
        self.brand = brand    # public
        self.speed = speed    # public

car = Car("Toyota", 120)
car.speed = 999    # ← no restriction, direct access
print(car.speed)   # 999
```

Use public when there is genuinely no constraint on the data.

---

## 2️⃣ Protected Attributes (single underscore `_`)

Single underscore is a **convention** — Python doesn't technically enforce it.
It signals: "This is internal. Don't use it from outside unless you know what you're doing."

```python
class BankAccount:
    def __init__(self, balance):
        self._balance = balance    # convention: treat as internal

    def _validate_amount(self, amount):    # protected method
        return amount > 0

account = BankAccount(5000)
print(account._balance)      # works — Python allows it, but you shouldn't!
account._balance = -1000     # works, but breaks the design contract
```

> **When to use `_`:** Methods or attributes meant for subclasses or internal use.
> Not for random external code.

---

## 3️⃣ Private Attributes (double underscore `__`)

Double underscore triggers **name mangling**.
Python renames `__balance` to `_BankAccount__balance` internally.
This makes accidental access from outside much harder.

```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner    = owner
        self.__balance = balance    # private — name-mangled!

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.__balance += amount

    def get_balance(self):
        return self.__balance

account = BankAccount("Alice", 5000)

# These FAIL:
# print(account.__balance)         # AttributeError!
# account.__balance = -999999      # Creates a NEW attribute — doesn't change the real one!

# This is the correct way:
print(account.get_balance())       # 5000  ✓
account.deposit(1000)
print(account.get_balance())       # 6000  ✓
```

### Name Mangling — The Actual Mechanism

```python
print(dir(account))
# You'll see: '_BankAccount__balance'  ← the real name!

# You CAN access it this way (but absolutely should not in production):
print(account._BankAccount__balance)    # 6000

# This is why __ is "harder" but not "impossible" to access.
# Python doesn't have truly private attributes — it only has conventions.
```

```
NAME MANGLING RULE:
__attr  inside class  BankAccount
  ↓ becomes
_BankAccount__attr
```

---

## 🏠 The `@property` Decorator — The Professional Way

Using getter/setter methods directly is verbose.
Python's `@property` gives you attribute-style access with method-level control.

```python
class Temperature:
    def __init__(self, celsius):
        self.__celsius = celsius

    @property
    def celsius(self):             # getter — accessed like attribute
        return self.__celsius

    @celsius.setter
    def celsius(self, value):      # setter — called on assignment
        if value < -273.15:
            raise ValueError(f"Temperature {value}°C is below absolute zero")
        self.__celsius = value

    @celsius.deleter
    def celsius(self):             # deleter — called on del
        print("Deleting temperature")
        del self.__celsius

    @property
    def fahrenheit(self):          # computed property — no setter needed
        return (self.__celsius * 9/5) + 32

# Usage looks like attribute access — but runs method logic:
t = Temperature(25)

print(t.celsius)        # 25       ← calls getter
t.celsius = 100         # ← calls setter (validates!)
print(t.fahrenheit)     # 212.0    ← computed property

# t.celsius = -300      # ← ValueError: below absolute zero
del t.celsius           # ← calls deleter
```

### Why `@property` is Better Than Raw Getters/Setters

```python
# Java-style (not Pythonic):
class Circle:
    def get_radius(self): return self.__radius
    def set_radius(self, r): self.__radius = r

c = Circle()
c.set_radius(5)
print(c.get_radius())

# Pythonic way with @property:
class Circle:
    def __init__(self, radius):
        self.radius = radius     # calls the setter!

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self.__radius = value

    @property
    def area(self):              # computed, read-only
        return 3.14159 * self.__radius ** 2

c = Circle(5)
print(c.radius)    # 5       ← attribute style!
print(c.area)      # 78.53   ← computed on the fly
c.radius = 10      # ← validates!
# c.area = 100     # AttributeError — no setter defined
```

---

## 🏦 Real Production Example — BankAccount With Full Encapsulation

```python
class BankAccount:
    OVERDRAFT_LIMIT = -500      # class attribute — same for all accounts

    def __init__(self, owner, initial_balance=0):
        self.__owner   = owner
        self.__balance = 0       # always start at 0
        self.__history = []      # transaction history

        if initial_balance > 0:
            self.deposit(initial_balance)    # use the controlled method!

    @property
    def owner(self):
        return self.__owner       # read-only — owner can't be changed

    @property
    def balance(self):
        return self.__balance     # read-only — can't set directly

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError(f"Deposit must be positive, got {amount}")
        self.__balance += amount
        self.__history.append(f"+ {amount} → balance: {self.__balance}")

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError(f"Withdrawal must be positive, got {amount}")
        if self.__balance - amount < self.OVERDRAFT_LIMIT:
            raise ValueError(f"Insufficient funds. Balance: {self.__balance}")
        self.__balance -= amount
        self.__history.append(f"- {amount} → balance: {self.__balance}")

    def get_history(self):
        return list(self.__history)    # return a COPY, not the real list!

    def __str__(self):
        return f"Account({self.__owner}, balance={self.__balance})"

# Usage:
acc = BankAccount("Alice", 5000)
acc.deposit(1000)
acc.withdraw(200)

print(acc.balance)       # 5800   ← property access
print(acc.owner)         # Alice  ← read-only property

# These are blocked:
# acc.balance = 99999    # AttributeError — no setter
# acc.owner = "Hacker"   # AttributeError — no setter
# acc.__balance = 99999  # Creates new attr, doesn't change real balance!

print(acc.get_history())
# ['+ 5000 → balance: 5000', '+ 1000 → balance: 6000', '- 200 → balance: 5800']
```

---

## 🆚 Public vs Protected vs Private — When to Use What

```
┌──────────────────────────────────────────────────────────────────────────┐
│  USE PUBLIC (name)     → Data with no constraints, no logic needed      │
│                          Example: self.name, self.color                 │
│                                                                          │
│  USE PROTECTED (_name) → Internal implementation details that           │
│                          subclasses might need to use                   │
│                          Example: self._cache, self._connection         │
│                                                                          │
│  USE PRIVATE (__name)  → Data with strict invariants that MUST be       │
│                          protected from direct modification             │
│                          Example: self.__balance, self.__password_hash  │
│                                                                          │
│  USE @property         → When you want attribute-style access but       │
│                          need validation, computation, or read-only     │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Common Mistakes

```python
# ❌ Mistake 1: Using __ for everything unnecessarily
class Overkill:
    def __init__(self, name):
        self.__name = name     # unnecessary if there's no invariant to protect!

# ✅ Use public unless there's a reason to protect it

# ❌ Mistake 2: Confusing __ with truly private
acc = BankAccount("Alice", 5000)
acc.__balance = 99999   # this doesn't change the real __balance!
                        # it creates a NEW public attribute named __balance!
print(acc.__balance)       # 99999  ← your new attribute
print(acc.balance)         # 5000   ← the real one (unchanged!)

# ❌ Mistake 3: Not returning a copy from getters of mutable data
class Bad:
    def get_history(self):
        return self.__history   # caller can mutate your private list!

class Good:
    def get_history(self):
        return list(self.__history)  # returns a copy — safe!
```

---

## 🎯 Key Takeaways

```
• Encapsulation = bundle data + behavior + protect invariants
• _ prefix = convention "internal use only" — NOT enforced
• __ prefix = name mangling: __attr becomes _ClassName__attr
• @property = attribute syntax + method logic (the Pythonic way)
• Getter/setter/deleter all use the same property name
• Return COPIES of mutable private data from getters
• Encapsulation prevents invalid state — not just hiding data
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [03 — `__init__` & `self`](./03_init_and_self.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [05 — Inheritance](./05_inheritance.md) |
