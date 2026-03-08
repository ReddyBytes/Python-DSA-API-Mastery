# 🏗️ 12 — Composition vs Inheritance: IS-A vs HAS-A

> *"Favor composition over inheritance.*
> *Inheritance is a strong relationship. Composition is flexible.*
> *Most experienced engineers reach for composition first."*
> — Gang of Four (Design Patterns)

---

## 🎬 The Story

You're building a character system for a game.
A `Warrior` can fight and walk.
A `Mage` can cast spells and walk.
A `FlyingMage` can cast spells, walk, AND fly.

**The Inheritance approach:**
```
Character
├── Warrior  (fight + walk)
├── Mage     (spell + walk)
└── FlyingMage  ← inherits from Mage? from Character? From a FlyingMixin?
```

The moment you need mixed combinations of abilities,
inheritance hierarchies become messy — deeply nested, brittle, hard to change.

**The Composition approach:**
```
Fighter behavior  = an object
Walker behavior   = an object
SpellCaster behavior = an object
Flyer behavior    = an object

FlyingMage HAS-A SpellCaster
           HAS-A Walker
           HAS-A Flyer
```

Plug in any combination. Change one without breaking others.

---

## 🔑 The Fundamental Test

```
IS-A test (Inheritance):
  "Is a SavingsAccount a BankAccount?"        → YES → use inheritance
  "Is a Dog an Animal?"                        → YES → use inheritance
  "Is a Car an Engine?"                        → NO  → don't use inheritance!

HAS-A test (Composition):
  "Does a Car HAVE an Engine?"                 → YES → use composition
  "Does a User HAVE an Address?"              → YES → use composition
  "Does an Order HAVE a list of Products?"   → YES → use composition
```

---

## 🔧 Inheritance in Action (When It's Right)

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def breathe(self):
        print(f"{self.name} breathes")

class Dog(Animal):      # Dog IS-A Animal ✓
    def bark(self):
        print(f"{self.name}: Woof!")

class Cat(Animal):      # Cat IS-A Animal ✓
    def meow(self):
        print(f"{self.name}: Meow!")

# This is correct. Dog and Cat share real "is-a" relationship.
```

---

## 🔧 Composition in Action

```python
# Behaviours as separate objects:
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower

    def start(self):
        print(f"Engine ({self.horsepower}hp) started")

    def stop(self):
        print("Engine stopped")

class GPS:
    def navigate(self, destination):
        print(f"Navigating to {destination}")

class AudioSystem:
    def play(self, song):
        print(f"Playing: {song}")

# Car COMPOSES these:
class Car:
    def __init__(self, brand, horsepower):
        self.brand  = brand
        self.engine = Engine(horsepower)   # HAS-A Engine
        self.gps    = GPS()                # HAS-A GPS
        self.audio  = AudioSystem()        # HAS-A AudioSystem

    def start(self):
        print(f"{self.brand} starting...")
        self.engine.start()

    def go_to(self, destination):
        self.gps.navigate(destination)

car = Car("Toyota", 150)
car.start()                        # Toyota starting... Engine (150hp) started
car.go_to("Mumbai Airport")        # Navigating to Mumbai Airport
car.audio.play("Imagine Dragons")  # Playing: Imagine Dragons
```

---

## ⚠️ The Fragile Base Class Problem

Deep inheritance chains are fragile. Changing the parent breaks all children.

```python
# A seemingly innocent change breaks things:
class Logger:
    def log(self, msg):
        print(f"[LOG] {msg}")

class Service(Logger):
    def process(self, data):
        self.log(f"Processing {data}")    # uses inherited log()
        return data.upper()

class AuditedService(Service):
    def process(self, data):
        self.log(f"AUDIT: {data}")        # also uses log()
        return super().process(data)

# Now the team decides Logger should write to a file.
# They add a required 'filepath' parameter to Logger.__init__.
# EVERY class that inherits Logger is now broken.
# AuditedService → Service → Logger: all need __init__ updates.

# With composition, you'd just swap the logger object. Nothing else breaks.
```

---

## 🔄 Same Problem, Both Solutions Side-by-Side

### Problem: A `Report` that can be saved to different formats.

```python
# ── INHERITANCE APPROACH (gets messy fast) ──────────────────────────
class Report:
    def generate(self): return "Report data"

class PDFReport(Report):
    def save(self): print("Saving as PDF")

class CSVReport(Report):
    def save(self): print("Saving as CSV")

class EmailablePDFReport(PDFReport):    # what if we need both?
    def email(self): print("Emailing PDF")

# With 5 formats and 3 delivery methods = 15 subclasses!
```

```python
# ── COMPOSITION APPROACH (clean and flexible) ──────────────────────
class PDFFormatter:
    def format(self, data): return f"PDF: {data}"

class CSVFormatter:
    def format(self, data): return f"CSV: {data}"

class JSONFormatter:
    def format(self, data): return f"JSON: {data}"

class EmailDelivery:
    def deliver(self, content): print(f"Emailing: {content}")

class FileDelivery:
    def deliver(self, content, path="output"):
        print(f"Saving to {path}: {content}")

class Report:
    def __init__(self, formatter, delivery):
        self.formatter = formatter    # HAS-A formatter
        self.delivery  = delivery     # HAS-A delivery method

    def generate_and_send(self, data):
        formatted = self.formatter.format(data)
        self.delivery.deliver(formatted)

# Mix any formatter with any delivery — 3×3 = 9 combinations, 0 new classes!
r1 = Report(PDFFormatter(), EmailDelivery())
r2 = Report(CSVFormatter(), FileDelivery())
r3 = Report(JSONFormatter(), EmailDelivery())

r1.generate_and_send("Q4 Sales")   # Emailing: PDF: Q4 Sales
r2.generate_and_send("Q4 Sales")   # Saving to output: CSV: Q4 Sales
```

---

## 🏆 Combining Both — The Real World

In practice, good design uses **both**:
- Inheritance for genuine "is-a" type hierarchies
- Composition for capabilities/behaviors

```python
from abc import ABC, abstractmethod

class Shape(ABC):              # inheritance: Circle IS-A Shape ✓
    @abstractmethod
    def area(self) -> float: pass

    @abstractmethod
    def perimeter(self) -> float: pass

class Color:                   # behaviour object for composition
    def __init__(self, r, g, b):
        self.r, self.g, self.b = r, g, b

    def as_hex(self):
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

class Border:
    def __init__(self, width, style="solid"):
        self.width = width
        self.style = style

class Circle(Shape):           # IS-A Shape (inheritance)
    def __init__(self, radius, fill_color=None, border=None):
        self.radius = radius
        self.fill   = fill_color    # HAS-A Color (composition)
        self.border = border        # HAS-A Border (composition)

    def area(self):
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159 * self.radius

    def describe(self):
        color  = self.fill.as_hex() if self.fill else "none"
        border = f"{self.border.width}px {self.border.style}" if self.border else "none"
        print(f"Circle r={self.radius}, fill={color}, border={border}")

c = Circle(5, Color(255, 0, 0), Border(2))
c.describe()    # Circle r=5, fill=#ff0000, border=2px solid
```

---

## 📊 Decision Guide

```
┌────────────────────────────────────────────────────────────────────┐
│  USE INHERITANCE WHEN:                                             │
│    ✓ Genuine IS-A relationship exists                              │
│    ✓ Child is a specialised version of parent                      │
│    ✓ You want to share interface (polymorphism)                    │
│    ✓ Hierarchy is shallow (1-2 levels deep)                        │
│                                                                    │
│  USE COMPOSITION WHEN:                                             │
│    ✓ HAS-A relationship (object uses another object)               │
│    ✓ You need to mix capabilities in various combinations          │
│    ✓ You want to swap implementations at runtime                   │
│    ✓ You want to avoid the fragile base class problem              │
│    ✓ The hierarchy would go 3+ levels deep                         │
│    ✓ In doubt — prefer composition                                 │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

```
• IS-A → Inheritance  |  HAS-A → Composition
• Inheritance creates tight coupling — changes in parent break children
• Composition is more flexible — swap components without breaking users
• "Favor composition over inheritance" — Gang of Four (1994)
• Deep inheritance (3+ levels) is almost always the wrong design
• Composition: inject dependencies → enables testing with mocks
• In real systems: use inheritance for type hierarchy + composition for behaviour
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [11 — Properties](./11_properties.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [13 — MRO & super()](./13_mro_and_super.md) |
