# 🏗️ Object-Oriented Programming — Master Index

> *"OOP is not about classes and syntax.*
> *It is about modeling reality, controlling complexity, and building systems that scale."*

---

## 🗺️ How This Module Is Organized

Unlike other modules, OOP has too many concepts to fit in one file without losing clarity.
Each concept has its own dedicated file — deep, complete, and self-contained.
Read them in order for the full journey, or jump directly to what you need.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    OOP LEARNING ARCHITECTURE                             │
│                                                                          │
│   PILLAR 1         PILLAR 2          PILLAR 3         PILLAR 4          │
│   Foundations      4 OOP Pillars     Python-Specific  Advanced          │
│   ──────────       ────────────      ───────────────  ────────          │
│   Why OOP          Inheritance       Dunder Methods   Dataclasses       │
│   Classes          Polymorphism      3 Method Types   __slots__         │
│   Objects          Abstraction       Properties       Metaclasses       │
│   __init__                           Class vs Inst.   Descriptors       │
│   Encapsulation                      Composition      Mixins            │
│                                                       SOLID             │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 📚 All Concepts — Complete Navigation

### 🟢 Pillar 1 — Core Foundations

| # | Concept | File | Status |
|---|---------|------|--------|
| 01 | Why OOP Exists — The Problem It Solves | [01_why_oop.md](./01_why_oop.md) | ✅ |
| 02 | Classes & Objects — Blueprint vs Instance | [02_classes_and_objects.md](./02_classes_and_objects.md) | ✅ |
| 03 | `__init__` & `self` — Initialization Deep Dive | [03_init_and_self.md](./03_init_and_self.md) | ✅ |
| 04 | Encapsulation — Protecting & Controlling State | [04_encapsulation.md](./04_encapsulation.md) | ✅ |

### 🔵 Pillar 2 — The 4 OOP Pillars

| # | Concept | File | Status |
|---|---------|------|--------|
| 05 | Inheritance — Code Reuse & Hierarchy | [05_inheritance.md](./05_inheritance.md) | ✅ |
| 06 | Polymorphism — One Interface, Many Behaviors | [06_polymorphism.md](./06_polymorphism.md) | ✅ |
| 07 | Abstraction — Abstract Classes & Interfaces | [07_abstraction.md](./07_abstraction.md) | ✅ |

### 🟣 Pillar 3 — Python-Specific OOP

| # | Concept | File | Status |
|---|---------|------|--------|
| 08 | Dunder / Magic Methods — Objects That Behave Like Built-ins | [08_dunder_methods.md](./08_dunder_methods.md) | ✅ |
| 09 | Class, Instance & Static Methods — Three Types Explained | [09_class_instance_static_methods.md](./09_class_instance_static_methods.md) | ✅ |
| 10 | Class Variables vs Instance Variables — The Trap | [10_class_vs_instance_variables.md](./10_class_vs_instance_variables.md) | ✅ |
| 11 | Properties — `@property`, getter, setter, deleter | [11_properties.md](./11_properties.md) | ✅ |
| 12 | Composition vs Inheritance — IS-A vs HAS-A | [12_composition_vs_inheritance.md](./12_composition_vs_inheritance.md) | ✅ |
| 13 | MRO & `super()` — Method Resolution Order Deep Dive | [13_mro_and_super.md](./13_mro_and_super.md) | ✅ |

### 🔴 Pillar 4 — Advanced & Production

| # | Concept | File | Status |
|---|---------|------|--------|
| 14 | Dataclasses — Modern Python OOP | [14_dataclasses.md](./14_dataclasses.md) | ✅ |
| 15 | `__slots__` — Memory Optimization | [15_slots.md](./15_slots.md) | ✅ |
| 16 | Metaclasses — Classes That Create Classes | [16_metaclasses.md](./16_metaclasses.md) | ✅ |
| 17 | Descriptors — The Protocol Behind `@property` | [17_descriptors.md](./17_descriptors.md) | ✅ |
| 18 | Mixins — Reusable Behavior Without Full Inheritance | [18_mixins.md](./18_mixins.md) | ✅ |
| 19 | SOLID Principles — Architecture Rules with Python | [19_solid_principles.md](./19_solid_principles.md) | ✅ |

### 🎯 Interview & Quick Reference

| File | Purpose |
|------|---------|
| [interview.md](./interview.md) | Interview questions by experience level | ✅ |
| [cheatsheet.md](./cheatsheet.md) | Quick reference for syntax & patterns | ✅ |
| [practice.py](./practice.py) | Practice exercises |

---

## 🧭 Recommended Learning Path

```
If you're a BEGINNER:
  01 → 02 → 03 → 04 → 05 → 06 → 07

If you're INTERMEDIATE (know the 4 pillars):
  08 → 09 → 10 → 11 → 12 → 13

If you're preparing for INTERVIEWS:
  All pillars 1-2 → interview.md → cheatsheet.md

If you're going SENIOR / PRODUCTION level:
  Pillar 3 complete → 14 → 15 → 19 (SOLID) → 16 → 17 → 18
```

---

## 🌍 The Big Picture — What OOP Actually Is

```
WITHOUT OOP                          WITH OOP
────────────────────                 ────────────────────────────
user1_name = "Alice"                 class User:
user1_email = "a@mail.com"               def __init__(self, name, email):
user1_age = 25                               self.name = name
                                             self.email = email
user2_name = "Bob"                           self.age = age
user2_email = "b@mail.com"
user2_age = 30                       u1 = User("Alice", "a@mail.com", 25)
                                     u2 = User("Bob",   "b@mail.com", 30)
→ 1 million users = chaos
→ No structure, no safety            → 1 million users = User objects
→ Hard to maintain                   → Structured, validated, maintainable
```

---

## 🔑 The 4 OOP Pillars — One-Line Summary Each

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  ENCAPSULATION   Bundle data + behavior, hide internal details         │
│                  "A BankAccount controls who can change its balance"   │
│                                                                         │
│  INHERITANCE     Child class reuses and extends parent class           │
│                  "SavingsAccount IS-A BankAccount"                     │
│                                                                         │
│  POLYMORPHISM    Same method name, different behavior per class        │
│                  "Every Animal can speak(), but each speaks different" │
│                                                                         │
│  ABSTRACTION     Hide complexity, show only what's needed              │
│                  "You press Accelerate — don't know about fuel inject" │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ⚠️ The 5 Most Common OOP Mistakes (Preview)

```
1. Using inheritance when composition is better
2. Making everything a class (sometimes functions are enough)
3. Confusing class variables and instance variables (causes shared state bugs)
4. Not using @property and directly exposing attributes
5. Overriding methods without calling super() — breaks parent initialization
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous Module | [04 — Functions](../04_functions/theory.md) |
| ➡️ Next Module | [06 — Exceptions](../06_exceptions_error_handling/theory.md) |
| 🏠 Home | [python-complete-mastery](../README.md) |
