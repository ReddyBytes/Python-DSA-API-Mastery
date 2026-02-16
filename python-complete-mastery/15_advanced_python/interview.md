# 🎯 Advanced Python — Interview Preparation Guide  
From Dunder Methods to Metaclasses

---

# 🧠 What Interviewers Actually Test

Advanced Python questions test:

- Do you understand how Python objects work internally?
- Can you explain magic methods clearly?
- Do you understand descriptors?
- Do you know when to use dataclasses?
- Can you explain metaclasses without confusion?
- Can you design clean abstractions?

This is senior-level evaluation.

---

# 🔹 Level 1: 0–2 Years Experience

Basic awareness expected.

---

## 1️⃣ What are dunder methods?

Strong answer:

> Dunder methods (double underscore methods) are special methods in Python that define object behavior. For example, `__init__`, `__str__`, `__len__`, and `__add__`.

Mention:
They are invoked implicitly by built-in operations.

---

## 2️⃣ What is the difference between __str__ and __repr__?

Strong answer:

- `__str__` → human-readable representation.
- `__repr__` → unambiguous developer representation.

Best practice:
`__repr__` should ideally recreate the object.

Example:

```python
User(name="Alice", age=30)
```

---

## 3️⃣ What is operator overloading?

Redefining operators for custom objects.

Example:
Using `__add__` to define `+`.

Mention:
Used in mathematical or domain-specific libraries.

---

# 🔹 Level 2: 2–5 Years Experience

Now interviewer expects:

- Dataclass knowledge
- __slots__ understanding
- Descriptor basics
- Callable object explanation
- Introspection clarity

---

## 4️⃣ What are dataclasses and why use them?

Strong answer:

> Dataclasses automatically generate methods like `__init__`, `__repr__`, and `__eq__` for classes primarily used to store data.

Advantages:

- Less boilerplate
- Cleaner syntax
- Easier maintenance

---

## 5️⃣ What is __slots__ and why use it?

Strong answer:

> `__slots__` restricts attribute creation and removes per-object `__dict__`, reducing memory usage.

Used when:

- Creating millions of objects
- Optimizing memory

Important limitation:
Cannot dynamically add new attributes.

---

## 6️⃣ What is a descriptor?

Strong answer:

> A descriptor is an object that defines `__get__`, `__set__`, or `__delete__` methods to control attribute access in another class.

Used in:

- Properties
- ORMs
- Framework internals

---

## 7️⃣ What is introspection?

Ability to inspect objects at runtime.

Functions:

- type()
- dir()
- isinstance()
- getattr()
- hasattr()

Used in frameworks and debugging.

---

## 8️⃣ What is a callable object?

An object with `__call__()` method.

Example:

```python
obj()
```

Internally calls:

```python
obj.__call__()
```

Used in:

- Decorators
- Strategy patterns

---

# 🔹 Level 3: 5–10 Years Experience

Now interview moves into internals and design.

---

## 9️⃣ How does Python create a class internally?

Strong answer:

> Python uses a metaclass to create classes. By default, the metaclass is `type`. When a class is defined, Python calls `type()` to construct the class object.

Example:

```python
MyClass = type("MyClass", (), {})
```

This shows deep understanding.

---

## 🔟 What is a metaclass?

Strong answer:

> A metaclass defines how classes themselves are created. It is essentially a class of a class.

Used in:

- ORMs
- Enum implementations
- Advanced frameworks

Important:
Use rarely and only when necessary.

---

## 1️⃣1️⃣ When would you use metaclasses?

Use cases:

- Enforcing class-level validation
- Registering subclasses automatically
- Creating custom class behaviors
- Building DSL frameworks

Mention:
Most applications do not require metaclasses.

---

## 1️⃣2️⃣ What are common mistakes when using magic methods?

- Breaking operator consistency
- Returning wrong types
- Forgetting immutability
- Overloading unnecessarily

Design matters.

---

## 1️⃣3️⃣ How do descriptors differ from properties?

property:
Simplified descriptor.

Descriptors:
More powerful and reusable.

Property is built using descriptor protocol.

---

## 1️⃣4️⃣ What are performance implications of advanced features?

- __slots__ improves memory
- Excessive metaclass logic increases complexity
- Operator overloading can reduce readability
- Dynamic attribute handling may slow performance

Balance power and clarity.

---

# 🔥 Scenario-Based Questions

---

## Scenario 1:
You need to create many lightweight objects efficiently.

Solution:
Use __slots__.

Explain memory benefit.

---

## Scenario 2:
You need automatic validation when setting attribute.

Solution:
Use descriptor or property.

Example:
Validate age >= 0.

---

## Scenario 3:
Framework automatically registers subclasses.

How?

Use metaclass or class decorator.

Strong candidate explains difference.

---

## Scenario 4:
Need object to behave like function.

Solution:
Implement __call__.

Used in strategy or configuration objects.

---

## Scenario 5:
Need custom equality comparison.

Implement:

```python
__eq__
__hash__
```

Important for dictionary keys.

---

# 🧠 How to Answer Like a Strong Candidate

Weak:

“Metaclass is advanced feature.”

Strong:

> “Metaclasses define how classes are constructed. Since classes in Python are objects, they are created using a metaclass—by default, `type`. Metaclasses allow customization of class creation, but they should be used sparingly to avoid complexity.”

Clear.
Precise.
Mature.

---

# ⚠️ Common Weak Candidate Mistakes

- Overusing metaclasses
- Confusing descriptors with decorators
- Not understanding __slots__ limitations
- Ignoring immutability in operator overloading
- Not knowing that classes are objects

---

# 🎯 Rapid-Fire Revision

- Dunder methods define object behavior
- __str__ vs __repr__
- Dataclasses reduce boilerplate
- __slots__ reduces memory
- Descriptors control attribute access
- Metaclasses control class creation
- Introspection inspects objects
- __call__ makes object callable
- Advanced features require careful design

---

# 🏆 Final Interview Mindset

Advanced Python questions test:

- Internal language understanding
- Clean abstraction ability
- Framework-level thinking
- Design maturity

If you demonstrate:

- Clear explanation of object model
- Proper use-case reasoning
- Memory optimization awareness
- Descriptor clarity
- Metaclass understanding (without confusion)

You appear as strong senior Python engineer.

Advanced Python is not about showing off knowledge.

It is about understanding how the language truly works.

---

# 🔁 Navigation

Previous:  
[15_advanced_python/theory.md](./theory.md)

Next:  
[16_design_patterns/theory.md](../16_design_patterns/theory.md)

