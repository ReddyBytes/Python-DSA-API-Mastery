# 🔬 17 — Descriptors: The Protocol Behind `@property`

> *"Descriptors are the machinery underneath @property, @classmethod, @staticmethod,*
> *and even how attribute access works in Python.*
> *Understanding them means understanding Python's object model deeply."*

---

## 🎬 The Story

You want a `validated_int` attribute that:
- Always stays between a min and max value
- Works across ANY class without repeating validation code
- Works exactly like a normal attribute from the outside

You could write a `@property` in each class.
But if 10 classes need the same validation, you'd duplicate the logic 10 times.

**Descriptors solve this** — write the validation once, reuse it in any class as an attribute.

---

## 🔑 What Is a Descriptor?

A descriptor is any object that implements one or more of:

```python
__get__(self, obj, objtype=None)   → called when attribute is READ
__set__(self, obj, value)          → called when attribute is WRITTEN
__delete__(self, obj)              → called when attribute is DELETED
```

When you access `instance.attr`, Python checks if `attr` in the class has a `__get__` method.
If so, it calls that method instead of returning the attribute directly.

---

## 🔧 Your First Descriptor

```python
class Positive:
    """A descriptor that only allows positive numbers."""

    def __set_name__(self, owner, name):
        # Called when descriptor is assigned in a class body
        # owner = the class it's assigned to
        # name  = the attribute name it's assigned to
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self     # accessed on CLASS, not instance → return descriptor itself
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be numeric, got {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"{self.name} must be positive, got {value}")
        setattr(obj, self.private_name, value)

    def __delete__(self, obj):
        delattr(obj, self.private_name)


# Now use it in ANY class:
class Product:
    price    = Positive()   # ← descriptor instance as class attribute
    quantity = Positive()   # ← another one

    def __init__(self, name, price, quantity):
        self.name     = name
        self.price    = price        # calls Positive.__set__()
        self.quantity = quantity     # calls Positive.__set__()

class Circle:
    radius = Positive()   # same descriptor, different class!

    def __init__(self, radius):
        self.radius = radius


p = Product("Laptop", 80000, 5)
print(p.price)        # 80000    ← calls Positive.__get__()
p.price = 75000       # updates via __set__()

# p.price = -100      # ← ValueError: price must be positive
# p.price = "free"    # ← TypeError: price must be numeric

c = Circle(10)
print(c.radius)    # 10
# c.radius = 0     # ← ValueError: radius must be positive
```

---

## 🗂️ Data vs Non-Data Descriptors

```
DATA DESCRIPTOR:       implements __set__ (or __delete__) AND __get__
                       Takes priority over instance __dict__

NON-DATA DESCRIPTOR:   implements only __get__
                       Instance __dict__ takes priority
```

```python
class DataDesc:
    def __get__(self, obj, objtype):
        return "data descriptor"
    def __set__(self, obj, val):
        pass    # has __set__ → DATA descriptor

class NonDataDesc:
    def __get__(self, obj, objtype):
        return "non-data descriptor"
    # no __set__ → NON-DATA descriptor

class MyClass:
    data    = DataDesc()
    nondata = NonDataDesc()

obj = MyClass()
obj.__dict__['data']    = "instance"   # set in instance dict
obj.__dict__['nondata'] = "instance"   # set in instance dict

print(obj.data)       # "data descriptor"  ← DATA descriptor wins over instance dict!
print(obj.nondata)    # "instance"          ← instance dict wins over non-data descriptor!
```

```
ATTRIBUTE LOOKUP PRIORITY:
  1. Data descriptors in class (highest priority)
  2. Instance __dict__
  3. Non-data descriptors in class + class attributes
```

---

## 🏗️ How `@property` Is a Descriptor

`@property` is a built-in descriptor class:

```python
# This:
class Circle:
    @property
    def area(self):
        return 3.14 * self.radius ** 2

# Is exactly:
class Circle:
    def _area_getter(self):
        return 3.14 * self.radius ** 2

    area = property(fget=_area_getter)   # property is a descriptor!
```

When Python sees `circle.area`:
1. Finds `area` in `Circle.__dict__`
2. Sees it has `__get__` → it's a descriptor
3. Calls `area.__get__(circle, Circle)`
4. Returns the computed value

---

## 🔧 Reusable Type-Checking Descriptor

```python
class TypedField:
    def __set_name__(self, owner, name):
        self.name         = name
        self.private_name = f"_{name}"

    def __init__(self, expected_type):
        self.expected_type = expected_type

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"'{self.name}' expects {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        setattr(obj, self.private_name, value)


class Person:
    name  = TypedField(str)
    age   = TypedField(int)
    score = TypedField(float)

    def __init__(self, name, age, score):
        self.name  = name
        self.age   = age
        self.score = score

p = Person("Alice", 25, 9.5)
print(p.name)    # Alice

# p.age = "twenty"   # TypeError: 'age' expects int, got str
# p.score = 9        # TypeError: 'score' expects float, got int  (use 9.0)
```

---

## 🔍 Caching Descriptor (Lazy Computation)

```python
class CachedProperty:
    """Compute value on first access, cache it forever."""

    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # Compute and store in instance __dict__ directly:
        value = self.func(obj)
        obj.__dict__[self.name] = value    # cached! Next access hits __dict__ first
        return value
        # This works because CachedProperty is a NON-DATA descriptor
        # (no __set__) so instance __dict__ takes priority after first call


class DataSet:
    def __init__(self, data):
        self._data = data

    @CachedProperty
    def mean(self):
        print("Computing mean...")
        return sum(self._data) / len(self._data)

    @CachedProperty
    def std_dev(self):
        print("Computing std dev...")
        avg = self.mean
        variance = sum((x - avg)**2 for x in self._data) / len(self._data)
        return variance ** 0.5

ds = DataSet([1, 2, 3, 4, 5])
print(ds.mean)    # Computing mean...  ← computed
print(ds.mean)    # 3.0                ← cached, no recompute!
print(ds.std_dev) # Computing std dev... ← computed
print(ds.std_dev) # 1.41...             ← cached!
```

> Python 3.8+ ships `functools.cached_property` which does this same pattern.

---

## 🎯 Key Takeaways

```
• Descriptor = object with __get__, __set__, or __delete__
• Placed as a CLASS attribute, not instance attribute
• __get__(self, obj, objtype): obj=None means accessed on class
• Data descriptor (has __set__): beats instance __dict__
• Non-data descriptor (only __get__): instance __dict__ wins
• @property, @classmethod, @staticmethod are all built-in descriptors
• __set_name__ is called at class creation — use to grab attribute name
• Descriptors enable reusable validation across any number of classes
• functools.cached_property is a production-ready cached non-data descriptor
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [16 — Metaclasses](./16_metaclasses.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [18 — Mixins](./18_mixins.md) |
