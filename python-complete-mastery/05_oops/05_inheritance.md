# 🧬 05 — Inheritance: Code Reuse & Hierarchy

> *"Inheritance says: 'I am a more specific version of you.*
> *I have everything you have, and then some more.'"*

---

## 🎬 The Story

You're building a school management system.
You need: `Teacher`, `Student`, `Admin` — all are people.
All have: name, email, age, phone.
All can: login, logout, update_profile.

Without inheritance, you write these 4 attributes and 3 methods in 3 classes = 21 lines of duplication.
Then the email format rule changes. You update 3 files. Miss one. Bug in production.

With inheritance: write shared code ONCE in `Person`. All three inherit it.
Change the rule in ONE place. All three automatically get the fix.

---

## 🔧 Basic Inheritance — Single Parent

```python
class Person:
    def __init__(self, name, email, age):
        self.name  = name
        self.email = email
        self.age   = age

    def login(self):
        print(f"{self.name} logged in")

    def update_profile(self, name=None, email=None):
        if name:  self.name  = name
        if email: self.email = email
        print(f"Profile updated for {self.name}")

    def __str__(self):
        return f"{self.name} ({self.email})"


class Teacher(Person):             # ← inherits from Person
    def __init__(self, name, email, age, subject):
        super().__init__(name, email, age)    # ← call parent __init__ first!
        self.subject = subject                 # ← teacher-specific attribute

    def grade_assignment(self, student, score):
        print(f"{self.name} gave {student.name} a score of {score}")


class Student(Person):
    def __init__(self, name, email, age, student_id):
        super().__init__(name, email, age)
        self.student_id  = student_id
        self.grades      = {}

    def submit_assignment(self, subject, work):
        print(f"{self.name} submitted {subject} assignment")


# Using them:
teacher = Teacher("Ms. Priya", "priya@school.com", 35, "Mathematics")
student = Student("Arjun",     "arjun@school.com", 18, "S2024001")

# Inherited methods work:
teacher.login()          # Ms. Priya logged in
student.login()          # Arjun logged in
teacher.update_profile(email="newemail@school.com")

# Class-specific methods:
teacher.grade_assignment(student, 95)
student.submit_assignment("Math", "Homework 3")
```

---

## 🔑 `super()` — The Right Way to Call the Parent

`super()` means: "go to the next class in the [MRO](./13_mro_and_super.md) chain and call the method there."
(See [13_mro_and_super.md](./13_mro_and_super.md) for MRO deep dive.)

```python
class Animal:
    def __init__(self, name, species):
        self.name    = name
        self.species = species
        print(f"Animal.__init__ called for {name}")

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name, "Canis lupus")  # call parent init
        self.breed = breed
        print(f"Dog.__init__ called for {name}")

d = Dog("Rex", "Labrador")
# Animal.__init__ called for Rex
# Dog.__init__ called for Rex

print(d.name)     # Rex      ← from Animal
print(d.species)  # Canis lupus ← from Animal
print(d.breed)    # Labrador ← from Dog
```

**What happens if you forget `super().__init__()`:**
```python
class Dog(Animal):
    def __init__(self, name, breed):
        # FORGOT super().__init__()!
        self.breed = breed

d = Dog("Rex", "Labrador")
print(d.breed)    # Labrador ← works
print(d.name)     # AttributeError! name was never set by Animal.__init__
```

---

## 🔄 Method Overriding

Child class can replace (override) a parent method with its own version.

```python
class Shape:
    def area(self):
        return 0

    def describe(self):
        print(f"I am a shape with area {self.area()}")

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):              # overrides Shape.area()
        return 3.14159 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width  = width
        self.height = height

    def area(self):              # overrides Shape.area()
        return self.width * self.height

c = Circle(5)
r = Rectangle(4, 6)

print(c.area())      # 78.539...
print(r.area())      # 24

c.describe()         # "I am a shape with area 78.539..."  ← calls Circle.area()!
r.describe()         # "I am a shape with area 24"         ← calls Rectangle.area()!
```

**Calling the parent's version alongside your own:**
```python
class Employee(Person):
    def __init__(self, name, email, age, department):
        super().__init__(name, email, age)
        self.department = department

    def __str__(self):
        parent_str = super().__str__()    # get parent's string
        return f"{parent_str} | Dept: {self.department}"

emp = Employee("Alice", "alice@co.com", 30, "Engineering")
print(emp)    # Alice (alice@co.com) | Dept: Engineering
```

---

## 🏗️ Multi-Level Inheritance

A chain: A → B → C

```python
class Vehicle:
    def __init__(self, brand, speed):
        self.brand = brand
        self.speed = speed

    def move(self):
        print(f"{self.brand} moving at {self.speed} km/h")

class Car(Vehicle):
    def __init__(self, brand, speed, doors):
        super().__init__(brand, speed)
        self.doors = doors

    def honk(self):
        print(f"{self.brand}: Beep beep!")

class ElectricCar(Car):
    def __init__(self, brand, speed, doors, battery_kwh):
        super().__init__(brand, speed, doors)
        self.battery_kwh = battery_kwh

    def charge(self):
        print(f"Charging {self.brand}... {self.battery_kwh} kWh battery")

tesla = ElectricCar("Tesla", 250, 4, 100)
tesla.move()    # Vehicle.move() — inherited through chain
tesla.honk()    # Car.honk()     — inherited from Car
tesla.charge()  # ElectricCar.charge() — own method

print(tesla.brand)       # Tesla   ← from Vehicle
print(tesla.doors)       # 4       ← from Car
print(tesla.battery_kwh) # 100     ← from ElectricCar
```

```
Inheritance chain (MRO):
ElectricCar → Car → Vehicle → object
```

---

## 🌐 Multiple Inheritance

A class inherits from MORE THAN ONE parent.

```python
class Flyable:
    def fly(self):
        print(f"{self.name} is flying!")

class Swimmable:
    def swim(self):
        print(f"{self.name} is swimming!")

class Duck(Flyable, Swimmable):
    def __init__(self, name):
        self.name = name

    def quack(self):
        print(f"{self.name}: Quack!")

d = Duck("Donald")
d.fly()     # Donald is flying!
d.swim()    # Donald is swimming!
d.quack()   # Donald: Quack!
```

### ⚠️ The Diamond Problem

```
        Animal
       /      \
    Dog        Cat
       \      /
        DogCat  ← inherits from both Dog and Cat
                   both override Animal.speak()
                   which speak() does DogCat use?
```

```python
class Animal:
    def speak(self):
        print("Animal speaks")

class Dog(Animal):
    def speak(self):
        print("Woof")

class Cat(Animal):
    def speak(self):
        print("Meow")

class DogCat(Dog, Cat):    # inherits from both!
    pass

dc = DogCat()
dc.speak()    # "Woof"  ← uses Dog.speak() — MRO decides!

print(DogCat.__mro__)
# (<class 'DogCat'>, <class 'Dog'>, <class 'Cat'>, <class 'Animal'>, <class 'object'>)
```

Python resolves diamond problems using **C3 Linearization** (the MRO algorithm).
Rule: left parent wins. `DogCat(Dog, Cat)` → Dog's methods take priority over Cat's.

**Using `super()` cooperatively in multiple inheritance:**
```python
class A:
    def method(self):
        print("A")
        super().method()    # passes to next in MRO!

class B(A):
    def method(self):
        print("B")
        super().method()

class C(A):
    def method(self):
        print("C")
        super().method()

class D(B, C):
    def method(self):
        print("D")
        super().method()

D().method()
# D
# B
# C
# A
# (MRO: D → B → C → A → object)
```

---

## 🛡️ `isinstance()` and `issubclass()`

```python
class Animal: pass
class Dog(Animal): pass
class GoldenRetriever(Dog): pass

d = GoldenRetriever()

isinstance(d, GoldenRetriever)   # True  — exact class
isinstance(d, Dog)               # True  — parent class!
isinstance(d, Animal)            # True  — grandparent!
isinstance(d, str)               # False — unrelated

issubclass(GoldenRetriever, Dog)     # True
issubclass(GoldenRetriever, Animal)  # True
issubclass(Dog, GoldenRetriever)     # False — wrong direction!
issubclass(Dog, Dog)                 # True  — a class is a subclass of itself
```

---

## ⚠️ When NOT to Use Inheritance

```
USE INHERITANCE for genuine IS-A relationships:
  Dog IS-A Animal ✓
  SavingsAccount IS-A BankAccount ✓
  AdminUser IS-A User ✓

DO NOT USE inheritance for HAS-A relationships:
  Car HAS-A Engine ✗  (use Composition instead)
  User HAS-A Address ✗ (use Composition instead)

DO NOT USE inheritance to reuse code if there's no IS-A relationship:
  StringUtils inherits from list  ← wrong! Use composition or functions
```

---

## 🎯 Key Takeaways

```
• Inheritance = child class gets everything from parent + adds its own
• Always call super().__init__() at the start of child __init__
• Method overriding = child replaces parent's method
• super() calls next in MRO — not just "parent"
• Multiple inheritance: Python uses C3 Linearization to resolve order
• MRO: check ClassName.__mro__ to see the order
• isinstance() checks up the full inheritance chain
• Use inheritance for IS-A, not HAS-A
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [04 — Encapsulation](./04_encapsulation.md) |
| 📖 Index | [README.md](./README.md) |
| ➡️ Next | [06 — Polymorphism](./06_polymorphism.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Encapsulation](./04_encapsulation.md) &nbsp;|&nbsp; **Next:** [Polymorphism →](./06_polymorphism.md)

**Related Topics:** [Why Oop](./01_why_oop.md) · [Classes And Objects](./02_classes_and_objects.md) · [Init And Self](./03_init_and_self.md) · [Encapsulation](./04_encapsulation.md) · [Polymorphism](./06_polymorphism.md) · [Abstraction](./07_abstraction.md) · [Dunder Methods](./08_dunder_methods.md) · [Class Instance Static Methods](./09_class_instance_static_methods.md) · [Class Vs Instance Variables](./10_class_vs_instance_variables.md) · [Properties](./11_properties.md) · [Theory Part 1](./theory_part1.md) · [Composition Vs Inheritance](./12_composition_vs_inheritance.md) · [Theory Part 2](./theory_part2.md) · [Mro And Super](./13_mro_and_super.md) · [Theory Part 3](./theory_part3.md) · [Dataclasses](./14_dataclasses.md) · [Slots](./15_slots.md) · [Metaclasses](./16_metaclasses.md) · [Descriptors](./17_descriptors.md) · [Mixins](./18_mixins.md) · [Solid Principles](./19_solid_principles.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
