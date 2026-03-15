# 🎭 06 — Polymorphism: One Interface, Many Behaviors

> *"Polymorphism means you can write one piece of code*
> *that works correctly with dozens of different types —*
> *without needing to know which specific type you're dealing with."*

---

## 🎬 The Story

You're building a notification system.
The system must send notifications via: Email, SMS, Push Notification, WhatsApp.

Without polymorphism:
```python
def send_notification(method, message):
    if method == "email":
        send_email(message)
    elif method == "sms":
        send_sms(message)
    elif method == "push":
        send_push(message)
    elif method == "whatsapp":
        send_whatsapp(message)
    # Add new method? Edit this function. Always.
```

With polymorphism:
```python
def send_notification(notifier, message):
    notifier.send(message)    # works for ANY notifier — current or future

# EmailNotifier, SMSNotifier, PushNotifier all have .send()
# Add WhatsApp? Create WhatsAppNotifier with .send() — done. No existing code changes.
```

---

## 🔑 What Polymorphism Means

> `poly` = many, `morph` = form
> Same method name, different implementations per class.

```
Animal → speak()
  Dog  → speak() → "Woof"
  Cat  → speak() → "Meow"
  Cow  → speak() → "Moo"

The caller doesn't care which animal it has.
It just calls .speak() and gets the right behavior.
```

---

## 1️⃣ Polymorphism Through Inheritance (Method Overriding)

```python
class Notification:
    def send(self, message):
        raise NotImplementedError("Subclass must implement send()")

class EmailNotification(Notification):
    def __init__(self, recipient):
        self.recipient = recipient

    def send(self, message):
        print(f"Email to {self.recipient}: {message}")

class SMSNotification(Notification):
    def __init__(self, phone):
        self.phone = phone

    def send(self, message):
        print(f"SMS to {self.phone}: {message}")

class PushNotification(Notification):
    def __init__(self, device_token):
        self.device_token = device_token

    def send(self, message):
        print(f"Push to {self.device_token}: {message}")

# The power: one function works for ALL types
def broadcast(notifiers, message):
    for notifier in notifiers:
        notifier.send(message)    # same call, different behavior

notifiers = [
    EmailNotification("alice@mail.com"),
    SMSNotification("+91-9999999999"),
    PushNotification("token-abc123"),
]

broadcast(notifiers, "Your order has shipped!")
# Email to alice@mail.com: Your order has shipped!
# SMS to +91-9999999999: Your order has shipped!
# Push to token-abc123: Your order has shipped!
```

---

## 2️⃣ Duck Typing — Python's Most Powerful Polymorphism

> "If it walks like a duck and quacks like a duck, it IS a duck."
> Python doesn't check what TYPE an object is — it checks what it can DO.

```python
# These classes have NO common parent:
class Dog:
    def speak(self):
        return "Woof!"

class Cat:
    def speak(self):
        return "Meow!"

class Robot:
    def speak(self):
        return "BEEP BOOP"

class Baby:
    def speak(self):
        return "Waaah!"

# Python doesn't care about the type — only the capability:
def make_noise(speaker):
    print(speaker.speak())    # just needs a .speak() method

# Works for ALL of them — no inheritance needed!
make_noise(Dog())     # Woof!
make_noise(Cat())     # Meow!
make_noise(Robot())   # BEEP BOOP
make_noise(Baby())    # Waaah!
```

**Duck typing in real Python code:**
```python
# len() works on ANY object that has __len__:
print(len("hello"))       # 5  — str has __len__
print(len([1, 2, 3]))     # 3  — list has __len__
print(len({"a": 1}))      # 1  — dict has __len__

# for loops work on ANY object that is iterable:
for x in "abc":     print(x)     # str is iterable
for x in [1,2,3]:  print(x)     # list is iterable
for x in (1,2,3):  print(x)     # tuple is iterable
for x in {1,2,3}:  print(x)     # set is iterable

# The loop doesn't check type — it checks if __iter__ exists
```

---

## 3️⃣ Operator Overloading (Polymorphism for Operators)

Python operators are polymorphic via dunder methods.
`+` means different things for different types:

```python
print(5 + 3)              # 8   — int addition
print("hello" + " world") # "hello world" — string concatenation
print([1,2] + [3,4])      # [1,2,3,4] — list concatenation
```

You can define what operators mean for your own classes:

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):          # v1 + v2
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):          # v1 - v2
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):         # v * 3
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):        # 3 * v  (scalar on left)
        return self.__mul__(scalar)

    def __eq__(self, other):           # v1 == v2
        return self.x == other.x and self.y == other.y

    def __abs__(self):                 # abs(v) → magnitude
        return (self.x**2 + self.y**2) ** 0.5

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(1, 2)
v2 = Vector(3, 4)

print(v1 + v2)      # Vector(4, 6)
print(v1 - v2)      # Vector(-2, -2)
print(v1 * 3)       # Vector(3, 6)
print(3 * v1)       # Vector(3, 6)
print(abs(v2))      # 5.0  (3²+4²=25, √25=5)
print(v1 == Vector(1, 2))  # True
```

---

## 4️⃣ Built-in Polymorphic Functions

Python's built-in functions rely on polymorphism:

```python
# sorted() works on any iterable:
sorted([3, 1, 2])               # [1, 2, 3]
sorted("hello")                  # ['e', 'h', 'l', 'l', 'o']
sorted({"b": 2, "a": 1})        # ['a', 'b']

# str() calls __str__ on any object:
str(42)           # "42"
str([1,2,3])      # "[1, 2, 3]"
str(your_object)  # calls your_object.__str__()

# len() calls __len__ on any sized object:
len("hello")      # 5
len([1,2,3])      # 3
len(your_object)  # calls your_object.__len__()
```

---

## 🏦 Real-World Production Pattern

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount: float) -> bool:
        """Process a payment. Return True if successful."""
        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> bool:
        pass

class StripeProcessor(PaymentProcessor):
    def process(self, amount):
        print(f"Stripe: charging ${amount}")
        return True    # simulate success

    def refund(self, transaction_id):
        print(f"Stripe: refunding {transaction_id}")
        return True

class RazorpayProcessor(PaymentProcessor):
    def process(self, amount):
        print(f"Razorpay: charging ₹{amount}")
        return True

    def refund(self, transaction_id):
        print(f"Razorpay: refunding {transaction_id}")
        return True

class PayPalProcessor(PaymentProcessor):
    def process(self, amount):
        print(f"PayPal: charging ${amount}")
        return True

    def refund(self, transaction_id):
        print(f"PayPal: refunding {transaction_id}")
        return True

# The Order class doesn't care WHICH processor — it uses the interface:
class Order:
    def __init__(self, amount, processor: PaymentProcessor):
        self.amount    = amount
        self.processor = processor    # any PaymentProcessor works!

    def checkout(self):
        success = self.processor.process(self.amount)
        if success:
            print("Order confirmed!")
        return success

# Works with any processor — switch without changing Order:
order1 = Order(999, StripeProcessor())
order2 = Order(499, RazorpayProcessor())
order1.checkout()    # Stripe: charging $999
order2.checkout()    # Razorpay: charging ₹499
```

---

## 🆚 Polymorphism Approaches Comparison

```
┌──────────────────────────────────────────────────────────────────────────┐
│  APPROACH              REQUIRES         BEST FOR                        │
├──────────────────────────────────────────────────────────────────────────┤
│  Method Overriding     Common parent    Related types in hierarchy      │
│  Duck Typing           Just the method  Flexible, mixed types           │
│  Operator Overloading  Dunder methods   Custom numeric/comparable types │
│  ABC + abstractmethod  Abstract base    Enforced interface contracts    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

```
• Polymorphism = same interface, different behavior per class
• Method overriding: child replaces parent method
• Duck typing: Python checks capability, not type — very Pythonic
• Operator overloading: define dunder methods to support +, -, ==, etc.
• Polymorphism removes if/elif chains that grow with every new type
• The "Open/Closed Principle": open for extension, closed for modification
• Built-in functions (len, str, sorted) use polymorphism via dunder methods
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [05 — Inheritance](./05_inheritance.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [07 — Abstraction](./07_abstraction.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Inheritance](./05_inheritance.md) &nbsp;|&nbsp; **Next:** [Abstraction →](./07_abstraction.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Abstraction](./07_abstraction.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Slots](./15_slots.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
