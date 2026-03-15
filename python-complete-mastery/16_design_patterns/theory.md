# 🏗 Design Patterns in Python  
From Clean Code to Scalable Architecture

---

# 🎯 Why Design Patterns Exist

Imagine building a large system.

Over time:

- Code becomes messy
- Classes depend on each other tightly
- Adding new features becomes risky
- Testing becomes hard
- Changing one thing breaks many things

Design patterns are:

Proven solutions to common design problems.

They are not rules.
They are guidelines.

They help you:

✔ Reduce duplication  
✔ Improve flexibility  
✔ Improve maintainability  
✔ Improve readability  
✔ Scale systems cleanly  

Design patterns are architecture tools.

---

# 🧠 1️⃣ What Is a Design Pattern?

A design pattern is:

A reusable solution to a recurring design problem.

It is NOT:

- A library
- A framework
- A ready-made code

It is a structured idea.

---

# 🧩 2️⃣ Singleton Pattern

---

## 🔹 Problem

You need:

Only ONE instance of a class.

Examples:

- Database connection
- Logger
- Configuration manager

You don’t want:

Multiple conflicting instances.

---

## 🔹 Basic Implementation

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

Now:

```python
a = Singleton()
b = Singleton()
```

a and b are same object.

---

## 🔹 When to Use

- Shared configuration
- Shared resources
- Global services

---

## 🔹 When NOT to Use

- When global state causes hidden dependencies
- When it harms testability

Singleton often overused.

---

# 🏭 3️⃣ Factory Pattern

---

## 🔹 Problem

You need to create objects,
but don’t want to tightly couple object creation logic.

Example:

Payment system:

- CreditCardPayment
- PayPalPayment
- CryptoPayment

Instead of:

```python
if payment_type == "card":
    return CreditCardPayment()
```

Use factory.

---

## 🔹 Example

```python
class PaymentFactory:
    @staticmethod
    def create(payment_type):
        if payment_type == "card":
            return CreditCardPayment()
        elif payment_type == "paypal":
            return PayPalPayment()
```

---

## 🔹 Benefits

- Centralized creation logic
- Easy to extend
- Cleaner code

---

# 🧠 4️⃣ Strategy Pattern

---

## 🔹 Problem

You have multiple algorithms,
and want to switch them dynamically.

Example:

Sorting strategies:

- QuickSort
- MergeSort
- BubbleSort

Instead of huge if-else blocks,
use strategy.

---

## 🔹 Structure

```python
class Strategy:
    def execute(self):
        pass

class ConcreteStrategyA(Strategy):
    def execute(self):
        print("Strategy A")

class ConcreteStrategyB(Strategy):
    def execute(self):
        print("Strategy B")

class Context:
    def __init__(self, strategy):
        self.strategy = strategy

    def run(self):
        self.strategy.execute()
```

---

## 🔹 Why Useful?

- Easily change behavior at runtime
- Open for extension, closed for modification

Used heavily in:

- Pricing engines
- Payment processing
- Validation systems

---

# 👀 5️⃣ Observer Pattern

---

## 🔹 Problem

You want objects to be notified when something changes.

Example:

Stock price update → notify subscribers.

---

## 🔹 Basic Structure

```python
class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self):
        for observer in self._observers:
            observer.update()
```

Observers implement update().

---

## 🔹 Used In

- Event systems
- Notification systems
- UI frameworks
- Message queues

---

# 🔄 6️⃣ Dependency Injection (DI)

---

## 🔹 Problem

Class directly creates dependencies.

Example:

```python
class Service:
    def __init__(self):
        self.db = Database()
```

Hard to test.

---

## 🔹 Better Approach

Inject dependency:

```python
class Service:
    def __init__(self, db):
        self.db = db
```

Now:

```python
service = Service(MockDatabase())
```

Improves:

- Testability
- Flexibility
- Decoupling

DI is very important in large systems.

---

# 🧠 7️⃣ Why Patterns Improve Architecture

Design patterns:

- Reduce tight coupling
- Improve testability
- Improve extensibility
- Encourage clean abstractions
- Promote separation of concerns

They support:

SOLID principles.

---

# ⚠️ 8️⃣ Common Mistakes

❌ Overusing patterns  
❌ Forcing patterns unnecessarily  
❌ Making code overly complex  
❌ Copying patterns without understanding  
❌ Not adapting to Python’s dynamic nature  

Patterns must simplify code,
not complicate it.

---

# 🏗 9️⃣ Real Production Examples

---

## 🔹 Django ORM

Uses:

- Metaclasses
- Factory-like behavior

---

## 🔹 Logging Systems

Often Singleton or shared service.

---

## 🔹 Payment Gateways

Use Strategy pattern.

---

## 🔹 Event Systems

Use Observer pattern.

---

## 🔹 Web Frameworks

Use Dependency Injection heavily.

---

# 🏆 1️⃣0️⃣ Engineering Maturity Levels

Beginner:
Writes working code.

Intermediate:
Understands basic patterns.

Advanced:
Applies patterns appropriately.

Senior:
Designs scalable architecture using patterns wisely.

Architect:
Knows when NOT to use patterns.

---

# 🧠 Final Mental Model

Design patterns are:

Architecture tools.

Not rules.
Not magic.
Not required everywhere.

They help when:

- System grows
- Complexity increases
- Multiple developers collaborate
- Testing becomes important
- Flexibility required

Good engineers know patterns.
Great engineers know when to use them.

---

# 🔁 Navigation

Previous:  
[15_advanced_python/interview.md](../15_advanced_python/interview.md)

Next:  
[16_design_patterns/interview.md](./interview.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Advanced Python — Interview Q&A](../15_advanced_python/interview.md) &nbsp;|&nbsp; **Next:** [Dependency Injection →](./dependency_injection.md)

**Related Topics:** [Dependency Injection](./dependency_injection.md) · [Interview Q&A](./interview.md)
