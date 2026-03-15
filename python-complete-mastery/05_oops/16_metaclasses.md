# 🧬 16 — Metaclasses: Classes That Create Classes

> *"Classes are factories for objects.*
> *Metaclasses are factories for classes.*
> *Understanding metaclasses means understanding how Python itself works."*

---

## 🎬 The Story

You're building an ORM (like Django's models).
You want users to write:

```python
class User(Model):
    name  = CharField(max_length=100)
    email = EmailField(unique=True)
    age   = IntegerField()
```

And somehow Python automatically creates:
- A database table named `user`
- Validation on each field
- A `save()`, `find()`, `delete()` method
- All without the user calling any setup function

How does `class User(Model)` trigger all this magic?

The answer: **Metaclasses**.

---

## 🔑 The `type` Function — Python's Root Metaclass

Everything in Python is created by `type`.

```python
# type() with ONE argument → shows the class of an object:
print(type(42))         # <class 'int'>
print(type("hello"))    # <class 'str'>
print(type([]))         # <class 'list'>

# But what is the class of a CLASS?
print(type(int))        # <class 'type'>
print(type(str))        # <class 'type'>
print(type(list))       # <class 'type'>

# Even user-defined classes:
class Dog: pass
print(type(Dog))        # <class 'type'>
```

> Every class is an instance of `type`. `type` is the metaclass of all classes.

---

## 🔧 Creating a Class Dynamically With `type()`

`type()` with THREE arguments creates a new class:

```python
# type(name, bases, attributes)

# This:
class Dog:
    sound = "Woof"
    def bark(self): print(self.sound)

# Is EXACTLY equivalent to this:
Dog = type("Dog", (object,), {
    "sound": "Woof",
    "bark": lambda self: print(self.sound)
})

d = Dog()
d.bark()    # Woof
print(type(Dog))    # <class 'type'>
```

---

## 🏗️ Creating a Custom Metaclass

A metaclass is a class that inherits from `type` and overrides its methods.

```python
class MyMeta(type):
    def __new__(mcs, name, bases, namespace):
        # mcs   = the metaclass itself (MyMeta)
        # name  = name of the class being created ("Dog")
        # bases = tuple of parent classes ((Animal,))
        # namespace = dict of class body (methods, attributes)

        print(f"Creating class: {name}")
        print(f"  bases: {bases}")
        print(f"  attrs: {list(namespace.keys())}")

        # Create the actual class using type.__new__:
        cls = super().__new__(mcs, name, bases, namespace)
        return cls

class Animal(metaclass=MyMeta):
    sound = "..."

class Dog(Animal):         # ← Creating class: Dog
    def bark(self): pass   # ←   bases: (<class 'Animal'>,)
                           # ←   attrs: ['bark', ...]
```

---

## 🏭 Real Use Case — Auto-Register Subclasses

```python
class PluginMeta(type):
    registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:    # don't register the base class itself
            mcs.registry[name] = cls
            print(f"Registered plugin: {name}")
        return cls

class Plugin(metaclass=PluginMeta):
    def run(self): raise NotImplementedError

class AudioPlugin(Plugin):     # auto-registered!
    def run(self): print("Processing audio")

class VideoPlugin(Plugin):     # auto-registered!
    def run(self): print("Processing video")

# Now you can look up any plugin by name:
print(PluginMeta.registry)
# {'AudioPlugin': <class 'AudioPlugin'>, 'VideoPlugin': <class 'VideoPlugin'>}

# Run any plugin by name:
plugin_name = "AudioPlugin"
PluginMeta.registry[plugin_name]().run()    # Processing audio
```

---

## 🔒 Use Case — Enforce Interface At Class Creation Time

```python
class InterfaceMeta(type):
    REQUIRED_METHODS = set()

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        # Skip the base class itself:
        if not any(isinstance(b, InterfaceMeta) for b in bases):
            return cls

        # Check all required methods are implemented:
        missing = mcs.REQUIRED_METHODS - set(namespace)
        if missing:
            raise TypeError(
                f"Class '{name}' must implement: {missing}"
            )
        return cls

class StorageBackend(metaclass=InterfaceMeta):
    class InterfaceMeta(type):
        REQUIRED_METHODS = {'read', 'write', 'delete'}

# Actually, a cleaner real-world pattern uses ABC for this.
# Metaclasses shine in more automated/framework-level scenarios.
```

---

## 🗂️ Use Case — Add Methods Automatically (ORM-Style)

```python
class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        # Add a table name attribute automatically:
        cls._table = name.lower() + "s"

        # Add CRUD methods to every Model subclass:
        def save(self):
            print(f"INSERT INTO {self._table} VALUES {vars(self)}")

        def delete(self):
            print(f"DELETE FROM {self._table} WHERE id={self.id}")

        @classmethod
        def find(klass, **kwargs):
            print(f"SELECT * FROM {klass._table} WHERE {kwargs}")

        cls.save   = save
        cls.delete = delete
        cls.find   = find

        return cls

class Model(metaclass=ModelMeta): pass

class User(Model):
    def __init__(self, id, name, email):
        self.id, self.name, self.email = id, name, email

class Product(Model):
    def __init__(self, id, name, price):
        self.id, self.name, self.price = id, name, price

# Every Model subclass automatically gets these:
u = User(1, "Alice", "alice@mail.com")
u.save()         # INSERT INTO users VALUES {'id': 1, 'name': 'Alice', ...}
u.delete()       # DELETE FROM users WHERE id=1

User.find(name="Alice")     # SELECT * FROM users WHERE {'name': 'Alice'}
Product.find(price=999)     # SELECT * FROM products WHERE {'price': 999}
```

---

## 🔍 `__init_subclass__` — Simpler Alternative to Metaclasses

For many metaclass use cases, Python 3.6+ introduced `__init_subclass__` — much simpler:

```python
class Plugin:
    _registry = {}

    def __init_subclass__(cls, plugin_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if plugin_type:
            Plugin._registry[plugin_type] = cls
            print(f"Registered: {plugin_type} → {cls.__name__}")

class AudioProcessor(Plugin, plugin_type="audio"):
    def run(self): print("Processing audio")

class VideoProcessor(Plugin, plugin_type="video"):
    def run(self): print("Processing video")

# Registered: audio → AudioProcessor
# Registered: video → VideoProcessor

print(Plugin._registry)
# {'audio': <class 'AudioProcessor'>, 'video': <class 'VideoProcessor'>}
```

> **Rule of thumb:**
> - Try `__init_subclass__` first — simpler, more readable
> - Use metaclass only when you need to modify the class creation process itself

---

## 📊 When to Use Metaclasses

```
┌──────────────────────────────────────────────────────────────────────┐
│  USE METACLASS WHEN:                                                 │
│    • Building a framework (ORM, API framework, plugin system)       │
│    • Need to modify class structure at creation time                 │
│    • Auto-registration of subclasses                                 │
│    • Enforcing class-level constraints                               │
│    • Adding methods/attributes to all subclasses automatically       │
│                                                                      │
│  AVOID METACLASS WHEN:                                               │
│    • __init_subclass__ or ABC can do the same thing                 │
│    • You're not building a framework                                 │
│    • It adds complexity without clear benefit                        │
│                                                                      │
│  "If you're not sure whether you need metaclasses, you don't."      │
│  — Tim Peters                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

```
• type() is Python's root metaclass — all classes are instances of type
• type(name, bases, attrs) creates a class dynamically
• A metaclass is a class that inherits from type
• Metaclass __new__(mcs, name, bases, namespace) intercepts class creation
• Use cases: ORM, plugin registry, auto-add methods, enforce interface
• __init_subclass__ is simpler for most subclass customisation needs
• Don't use metaclasses unless you're building a framework
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [15 — `__slots__`](./15_slots.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [17 — Descriptors](./17_descriptors.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Slots](./15_slots.md) &nbsp;|&nbsp; **Next:** [Descriptors →](./17_descriptors.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Inheritance](./05_inheritance.md) · [Polymorphism](./06_polymorphism.md) · [Abstraction](./07_abstraction.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Slots](./15_slots.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
