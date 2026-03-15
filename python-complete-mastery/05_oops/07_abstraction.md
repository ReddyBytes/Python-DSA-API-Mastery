# 🔭 07 — Abstraction: Abstract Classes & Interfaces

> *"Abstraction is the art of hiding the 'how'*
> *and exposing only the 'what'.*
> *You press a button. You don't rewire the circuit."*

---

## 🎬 The Story

You're building a plugin system for a video editor.
Third-party developers will write plugins: noise reduction, color correction, blur.
Your editor will load and run them.

The problem: how do you ensure every plugin implements the right methods?
You can't test each plugin manually.
You need a **contract** — a guaranteed interface every plugin must follow.

In Python, that contract is an **Abstract Base Class (ABC)**.

---

## 🧠 What Is Abstraction?

```
ABSTRACTION means:
  • Hide internal implementation details
  • Show only what the user of the class needs
  • Define a contract: "every subclass MUST implement these methods"

EXAMPLES FROM REAL LIFE:
  • ATM: You see Withdraw/Deposit. Not the bank's internal systems.
  • TV Remote: You press Power. Not configure voltage and circuits.
  • Car: You press Accelerate. Not inject fuel and fire pistons.
```

---

## 🏗️ Abstract Base Classes — The Mechanism

Python's `abc` module provides:
- `ABC` — base class for abstract classes
- `@abstractmethod` — decorator to mark methods as abstract (must be implemented)

```python
from abc import ABC, abstractmethod

class Plugin(ABC):             # ← inherits from ABC = this is abstract

    @abstractmethod
    def process(self, frame):
        """Apply effect to a video frame. Must be implemented by subclass."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name. Must be implemented by subclass."""
        pass

    def validate(self, frame):           # ← NOT abstract: common shared logic
        if frame is None:
            raise ValueError("Frame cannot be None")
        return True

# Cannot instantiate an abstract class:
# p = Plugin()    # TypeError: Can't instantiate abstract class Plugin
#                 # with abstract methods: get_name, process
```

```python
# Subclass MUST implement all abstract methods:
class BlurPlugin(Plugin):
    def process(self, frame):
        return f"[blurred] {frame}"    # actual blur logic here

    def get_name(self):
        return "Gaussian Blur"

class NoiseReductionPlugin(Plugin):
    def process(self, frame):
        return f"[denoised] {frame}"

    def get_name(self):
        return "Noise Reduction v2"

# Now you can instantiate:
blur = BlurPlugin()
denoise = NoiseReductionPlugin()

print(blur.get_name())             # Gaussian Blur
print(blur.process("frame_001"))   # [blurred] frame_001
blur.validate("frame_001")         # uses shared method from Plugin
```

---

## ⚠️ What Happens If a Subclass Doesn't Implement All Abstract Methods?

```python
class IncompletePlugin(Plugin):
    def process(self, frame):
        return frame
    # FORGOT get_name()!

p = IncompletePlugin()
# TypeError: Can't instantiate abstract class IncompletePlugin
# with abstract method: get_name
```

> This is the power of ABC — it enforces the contract at **instantiation time**, not at runtime when the method is called. You catch the error early.

---

## 🏦 Real Production Example — Payment Gateway Interface

```python
from abc import ABC, abstractmethod
from typing import Optional

class PaymentGateway(ABC):
    """Abstract interface for all payment gateways."""

    @abstractmethod
    def charge(self, amount: float, currency: str, card_token: str) -> dict:
        """
        Charge a card.
        Returns: {"success": bool, "transaction_id": str, "message": str}
        """
        pass

    @abstractmethod
    def refund(self, transaction_id: str, amount: Optional[float] = None) -> bool:
        """Refund a transaction. amount=None means full refund."""
        pass

    @abstractmethod
    def get_balance(self) -> float:
        """Return current available balance in the merchant account."""
        pass

    # Shared (concrete) method — all gateways use this:
    def charge_with_retry(self, amount, currency, card_token, max_retries=3):
        for attempt in range(max_retries):
            result = self.charge(amount, currency, card_token)
            if result["success"]:
                return result
            print(f"Attempt {attempt+1} failed: {result['message']}")
        raise RuntimeError(f"Payment failed after {max_retries} attempts")


class StripeGateway(PaymentGateway):
    def charge(self, amount, currency, card_token):
        print(f"Stripe charging {currency} {amount}")
        return {"success": True, "transaction_id": "stripe_txn_123", "message": "OK"}

    def refund(self, transaction_id, amount=None):
        print(f"Stripe refunding {transaction_id}")
        return True

    def get_balance(self):
        return 50000.00


class RazorpayGateway(PaymentGateway):
    def charge(self, amount, currency, card_token):
        print(f"Razorpay charging {currency} {amount}")
        return {"success": True, "transaction_id": "rzp_123", "message": "OK"}

    def refund(self, transaction_id, amount=None):
        print(f"Razorpay refunding {transaction_id}")
        return True

    def get_balance(self):
        return 25000.00


# Any code that uses PaymentGateway works with both:
def process_order(gateway: PaymentGateway, amount: float):
    result = gateway.charge(amount, "USD", "card_tok_xyz")
    if result["success"]:
        print(f"Order processed: {result['transaction_id']}")
    return result

process_order(StripeGateway(), 999)
process_order(RazorpayGateway(), 499)
```

---

## 🔑 Abstract Properties

You can also make properties abstract:

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @property
    @abstractmethod
    def area(self) -> float:
        """Every shape must have an area."""
        pass

    @property
    @abstractmethod
    def perimeter(self) -> float:
        pass

    def describe(self):          # concrete method using abstract properties
        print(f"Area: {self.area:.2f}, Perimeter: {self.perimeter:.2f}")


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return 3.14159 * self.radius ** 2

    @property
    def perimeter(self):
        return 2 * 3.14159 * self.radius


class Rectangle(Shape):
    def __init__(self, w, h):
        self.w, self.h = w, h

    @property
    def area(self):
        return self.w * self.h

    @property
    def perimeter(self):
        return 2 * (self.w + self.h)


shapes = [Circle(5), Rectangle(4, 6)]
for s in shapes:
    s.describe()    # works for both!
# Area: 78.54, Perimeter: 31.42
# Area: 24.00, Perimeter: 20.00
```

---

## 🆚 Abstract Class vs Regular Class vs Interface

```
┌────────────────────────────────────────────────────────────────────────┐
│                    COMPARISON                                           │
├──────────────────┬─────────────────────────────────────────────────────┤
│  REGULAR CLASS   │  Can be instantiated directly                       │
│                  │  All methods can have implementations               │
│                  │  No enforcement of subclass methods                 │
├──────────────────┼─────────────────────────────────────────────────────┤
│  ABSTRACT CLASS  │  CANNOT be instantiated                             │
│                  │  Mix of abstract (no impl) and concrete (has impl)  │
│                  │  Subclass MUST implement all abstract methods       │
│                  │  CAN have __init__, class variables, etc.           │
├──────────────────┼─────────────────────────────────────────────────────┤
│  INTERFACE       │  Python has no `interface` keyword                  │
│ (Python style)   │  Simulate with ABC where ALL methods are abstract  │
│                  │  No shared state, just pure method contracts        │
└──────────────────┴─────────────────────────────────────────────────────┘
```

---

## 🔍 `ABCMeta` — Behind the Scenes

`ABC` is just a shortcut. Under the hood, it uses `ABCMeta` as the metaclass.

```python
from abc import ABCMeta, abstractmethod

class MyAbstract(metaclass=ABCMeta):    # same as inheriting ABC
    @abstractmethod
    def do_something(self): pass

# This is identical:
class MyAbstract(ABC):
    @abstractmethod
    def do_something(self): pass
```

You can also register "virtual subclasses" — classes that ABC treats as implementations
even though they don't inherit from it:

```python
from abc import ABC

class Drawable(ABC):
    @abstractmethod
    def draw(self): pass

class ExternalShape:          # doesn't inherit Drawable
    def draw(self):
        print("Drawing external shape")

Drawable.register(ExternalShape)   # register as virtual subclass

print(isinstance(ExternalShape(), Drawable))    # True!
print(issubclass(ExternalShape, Drawable))      # True!
```

---

## ⚠️ Common Mistakes

```python
# ❌ Mistake 1: Trying to instantiate abstract class
class Animal(ABC):
    @abstractmethod
    def speak(self): pass

a = Animal()    # TypeError! Must implement speak() first.

# ❌ Mistake 2: Forgetting @abstractmethod makes it NOT abstract
class Animal(ABC):
    def speak(self): pass    # no @abstractmethod → concrete method!
    # Subclasses don't HAVE to override this!

# ❌ Mistake 3: Implementing wrong method name
class Dog(Animal):
    def speaks(self): return "Woof"   # typo! 'speaks' ≠ 'speak'
    # Dog still has abstract 'speak' → TypeError on instantiation!

# ❌ Mistake 4: Not ordering @property + @abstractmethod correctly
class Shape(ABC):
    @abstractmethod          # wrong order!
    @property
    def area(self): pass

# ✅ Correct: @property FIRST, then @abstractmethod:
class Shape(ABC):
    @property
    @abstractmethod
    def area(self): pass
```

---

## 🎯 Key Takeaways

```
• Abstraction = hide implementation, expose interface
• ABC = class that cannot be instantiated directly
• @abstractmethod = method that MUST be implemented by subclass
• Catches missing implementations at instantiation, not at call time
• Can mix abstract and concrete methods in same ABC
• @property @abstractmethod: property order matters — @property first
• Useful for: plugin systems, payment gateways, storage backends,
              notification channels — any "switchable component"
• ABCMeta.register() for virtual subclasses (duck typing + contracts)
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [06 — Polymorphism](./06_polymorphism.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [08 — Dunder Methods](./08_dunder_methods.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Polymorphism](./06_polymorphism.md) &nbsp;|&nbsp; **Next:** [Dunder Methods →](./08_dunder_methods.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Polymorphism](./06_polymorphism.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Slots](./15_slots.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
