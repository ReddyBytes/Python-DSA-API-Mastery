# ⚙️ 09 — Class, Instance & Static Methods: Three Types Explained

> *"Choosing the wrong method type isn't just stylistic.*
> *It signals whether you understand what the method actually belongs to."*

---

## 🎬 The Story

You're modeling a `User` class for a web app.

Some methods work on **one specific user** (check this user's password, update this user's profile).
Some methods work on the **class as a whole** (count all users, create user from Google login).
Some methods are **utility logic** that belong in this class conceptually but don't touch any user data (validate an email format).

Python has a specific method type for each of these situations.

---

## 🗺️ The Three Types at a Glance

```
┌───────────────────────────────────────────────────────────────────────┐
│  TYPE              FIRST PARAM  DECORATOR     WHAT IT ACCESSES       │
├───────────────────────────────────────────────────────────────────────┤
│  Instance method   self         (none)        instance + class state  │
│  Class method      cls          @classmethod  class state only        │
│  Static method     (none)       @staticmethod neither instance nor    │
│                                               class state             │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ Instance Methods — The Default (self)

Most methods are instance methods.
They receive `self` — the specific object they were called on.
They can access and modify **both** instance attributes and class attributes.

```python
class BankAccount:
    bank_name = "PyBank"     # class attribute

    def __init__(self, owner, balance):
        self.owner   = owner      # instance attribute
        self.balance = balance    # instance attribute

    # Instance method — operates on THIS specific account:
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self.balance

    def get_summary(self):
        return f"{self.bank_name} | {self.owner}: ₹{self.balance}"
        #              ↑ class attr          ↑ instance attrs

account = BankAccount("Alice", 5000)
account.deposit(1000)
print(account.get_summary())    # PyBank | Alice: ₹6000
```

---

## 2️⃣ Class Methods — `@classmethod` and `cls`

Class methods receive `cls` — the **class itself**, not an instance.
They can access and modify class attributes, but NOT instance attributes.

### Primary Use Case 1: Alternative Constructors (Factory Methods)

```python
import json
from datetime import date

class User:
    user_count = 0     # class attribute: tracks all users

    def __init__(self, name, email, birth_year):
        self.name       = name
        self.email      = email
        self.birth_year = birth_year
        User.user_count += 1

    # Regular constructor: User("Alice", "alice@mail.com", 1998)

    # Alternative constructor: create from a dict
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name       = data["name"],
            email      = data["email"],
            birth_year = data["birth_year"]
        )

    # Alternative constructor: create from JSON string
    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls.from_dict(data)

    # Alternative constructor: create a guest user (no email needed)
    @classmethod
    def create_guest(cls):
        return cls("Guest", "guest@temp.com", 2000)

    @classmethod
    def get_user_count(cls):
        return cls.user_count

    def age(self):
        return date.today().year - self.birth_year

    def __repr__(self):
        return f"User({self.name}, {self.email})"

# Three ways to create a User:
u1 = User("Alice", "alice@mail.com", 1998)
u2 = User.from_dict({"name": "Bob", "email": "bob@mail.com", "birth_year": 1995})
u3 = User.from_json('{"name":"Charlie","email":"c@mail.com","birth_year":2000}')
u4 = User.create_guest()

print(User.get_user_count())    # 4
print(u1.age())                  # 27 (or similar)
```

### Primary Use Case 2: Modifying Class-Level State

```python
class Config:
    _debug   = False
    _log_level = "INFO"

    @classmethod
    def enable_debug(cls):
        cls._debug     = True
        cls._log_level = "DEBUG"
        print("Debug mode enabled")

    @classmethod
    def set_log_level(cls, level):
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if level not in allowed:
            raise ValueError(f"Level must be one of {allowed}")
        cls._log_level = level

    @classmethod
    def get_settings(cls):
        return {"debug": cls._debug, "log_level": cls._log_level}

Config.enable_debug()
print(Config.get_settings())    # {'debug': True, 'log_level': 'DEBUG'}
```

---

## 3️⃣ Static Methods — `@staticmethod`

Static methods receive NO implicit first argument — neither `self` nor `cls`.
They are essentially regular functions that live inside a class for **organizational** reasons.
They belong to the class logically but don't need access to any instance or class data.

```python
class EmailService:
    DEFAULT_DOMAIN = "company.com"

    def __init__(self, sender_email):
        self.sender = sender_email

    def send(self, to, subject, body):
        if not self.is_valid_email(to):     # can call static from instance
            raise ValueError(f"Invalid email: {to}")
        print(f"Sending from {self.sender} to {to}: {subject}")

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format. Doesn't need self or cls."""
        return "@" in email and "." in email.split("@")[-1]

    @staticmethod
    def format_subject(subject: str) -> str:
        return subject.strip().title()

    @staticmethod
    def create_signature(name: str, title: str) -> str:
        return f"\n\nBest regards,\n{name}\n{title}"

# Can call static methods on the class OR on an instance:
print(EmailService.is_valid_email("alice@mail.com"))   # True
print(EmailService.is_valid_email("not-an-email"))      # False

svc = EmailService("noreply@company.com")
print(svc.is_valid_email("test@test.com"))   # True — also works on instance
```

---

## 🆚 Comparison — When to Choose Which

```
┌──────────────────────────────────────────────────────────────────────┐
│  QUESTION                                 USE THIS                   │
├──────────────────────────────────────────────────────────────────────┤
│  Does it need to read/write THIS          Instance method (self)     │
│  specific object's data?                                             │
│                                                                      │
│  Does it create a new instance           Class method (@classmethod) │
│  in a special way?  (factory method)                                 │
│                                                                      │
│  Does it need to read/write              Class method (@classmethod) │
│  class-level state?                                                  │
│                                                                      │
│  Is it utility logic that belongs        Static method               │
│  in this class but doesn't touch         (@staticmethod)            │
│  any instance or class state?                                        │
└──────────────────────────────────────────────────────────────────────┘
```

```python
class TemperatureConverter:
    scale = "Celsius"     # class attribute

    def __init__(self, value):
        self.value = value

    # Instance method — operates on this specific value:
    def to_fahrenheit(self):
        return (self.value * 9/5) + 32

    # Class method — changes class-level scale setting:
    @classmethod
    def set_default_scale(cls, scale):
        cls.scale = scale

    # Static method — pure utility, no state needed:
    @staticmethod
    def celsius_to_fahrenheit(c):
        return (c * 9/5) + 32

    @staticmethod
    def fahrenheit_to_celsius(f):
        return (f - 32) * 5/9

t = TemperatureConverter(100)
print(t.to_fahrenheit())                           # 212.0  — instance method
print(TemperatureConverter.celsius_to_fahrenheit(0))  # 32.0 — static method, no object needed
TemperatureConverter.set_default_scale("Fahrenheit")  # class method
print(TemperatureConverter.scale)                  # Fahrenheit
```

---

## 🔬 Calling Behaviour — Instance vs Class vs Static

```python
class Demo:
    class_var = "I am class"

    def __init__(self):
        self.inst_var = "I am instance"

    def instance_method(self):
        return f"instance_method: self.inst_var={self.inst_var}, class_var={self.class_var}"

    @classmethod
    def class_method(cls):
        return f"class_method: cls.class_var={cls.class_var}"
        # cls.inst_var ← AttributeError! class doesn't have inst_var

    @staticmethod
    def static_method():
        return "static_method: no self or cls"
        # self.inst_var ← NameError! no self
        # cls.class_var ← NameError! no cls

obj = Demo()

# All three can be called on instance:
print(obj.instance_method())
print(obj.class_method())     # cls = Demo
print(obj.static_method())

# Only class and static can be called on the class:
print(Demo.class_method())
print(Demo.static_method())
# Demo.instance_method()  ← TypeError: missing 'self' argument
```

---

## 🏗️ Inheritance + Class Methods = Very Powerful

Class methods work correctly with inheritance — `cls` refers to the actual called class:

```python
class Animal:
    sound = "..."

    @classmethod
    def describe(cls):
        return f"I am a {cls.__name__} and I say {cls.sound}"

class Dog(Animal):
    sound = "Woof"

class Cat(Animal):
    sound = "Meow"

print(Animal.describe())  # I am a Animal and I say ...
print(Dog.describe())     # I am a Dog and I say Woof
print(Cat.describe())     # I am a Cat and I say Meow
```

This is also why factory class methods work correctly in subclasses:

```python
class Vehicle:
    def __init__(self, brand):
        self.brand = brand

    @classmethod
    def create(cls, brand):
        return cls(brand)    # cls = whatever class called this!

class Car(Vehicle):
    def __repr__(self): return f"Car({self.brand})"

class Truck(Vehicle):
    def __repr__(self): return f"Truck({self.brand})"

car   = Car.create("Toyota")    # cls = Car  → creates Car
truck = Truck.create("Tata")    # cls = Truck → creates Truck
print(car)    # Car(Toyota)
print(truck)  # Truck(Tata)
```

---

## ⚠️ Common Mistakes

```python
# ❌ Using instance method when you should use staticmethod:
class MathUtils:
    def add(self, a, b):    # ← self is never used!
        return a + b

# ✅ Use @staticmethod:
class MathUtils:
    @staticmethod
    def add(a, b):
        return a + b

# ❌ Using classmethod for factory but forgetting to use cls:
class User:
    @classmethod
    def from_email(cls, email):
        return User(email)    # ← hardcoded class! Won't work right in subclasses

# ✅ Always use cls in classmethod:
class User:
    @classmethod
    def from_email(cls, email):
        return cls(email)     # ← uses the actual class (works with subclasses!)

# ❌ Trying to access self inside classmethod:
class Counter:
    count = 0

    @classmethod
    def increment(cls):
        self.count += 1    # ← NameError! No 'self' in classmethod

# ✅ Use cls:
    @classmethod
    def increment(cls):
        cls.count += 1
```

---

## 🎯 Key Takeaways

```
• Instance method (self) → needs access to instance data (most methods)
• Class method (@classmethod, cls) → factory methods, class-level state
• Static method (@staticmethod) → utility functions organized in a class
• All three can be called on an instance
• Only class and static can be called on the class directly
• In class methods, cls refers to the ACTUAL called class (not always the parent)
• This makes class methods work correctly with inheritance
• If a method doesn't use self or cls — make it a @staticmethod
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [08 — Dunder Methods](./08_dunder_methods.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [10 — Class vs Instance Variables](./10_class_vs_instance_variables.md) |
