"""
05_oops/practice.py
=====================
CONCEPT: Object-Oriented Programming — modeling real-world entities as objects
with state (attributes) and behavior (methods).
WHY THIS MATTERS: OOP is the dominant paradigm in Python backend code, APIs,
data pipelines, and ML frameworks. Every Django model, SQLAlchemy table, Pydantic
schema, and dataclass you write is OOP. Understanding classes deeply means
understanding every major Python framework.

Prerequisite: Modules 01-04 (fundamentals, control flow, data types, functions)
"""

# =============================================================================
# SECTION 1: Class basics — __init__, self, instance vs class attributes
# =============================================================================

# CONCEPT: A class is a blueprint. An instance is a concrete object from that
# blueprint. `self` refers to the specific instance being acted on.
# __init__ runs automatically when an instance is created — it's the constructor.

print("=== Section 1: Class Basics ===")

class BankAccount:
    """A simple bank account demonstrating class fundamentals."""

    # CLASS attribute: shared by ALL instances of BankAccount
    # WHY: bank-wide settings that apply to every account
    interest_rate = 0.05   # 5% annual interest
    total_accounts = 0     # track how many accounts exist

    def __init__(self, owner: str, initial_balance: float = 0.0):
        """
        Instance attributes: unique to EACH instance.
        WHY self.owner vs just owner: self.owner is stored ON the object
        and persists across method calls. `owner` is just a local parameter.
        """
        self.owner = owner
        self.balance = initial_balance
        self._transactions = []   # _prefix = internal, not for outside use
        BankAccount.total_accounts += 1   # increment class-level counter

    def deposit(self, amount: float) -> None:
        """Mutates self.balance — this is why we need self."""
        if amount <= 0:
            raise ValueError(f"Deposit amount must be positive, got {amount}")
        self.balance += amount
        self._transactions.append(("deposit", amount))

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal must be positive")
        if amount > self.balance:
            raise ValueError(f"Insufficient funds: {self.balance:.2f} available")
        self.balance -= amount
        self._transactions.append(("withdraw", amount))

    def get_statement(self) -> str:
        """Returns a formatted summary of all transactions."""
        lines = [f"Account: {self.owner}"]
        for tx_type, amount in self._transactions:
            sign = "+" if tx_type == "deposit" else "-"
            lines.append(f"  {tx_type:10} {sign}${amount:.2f}")
        lines.append(f"  Balance: ${self.balance:.2f}")
        return "\n".join(lines)

    def apply_interest(self) -> float:
        """Uses the class attribute interest_rate — shared across all accounts."""
        interest = self.balance * BankAccount.interest_rate
        self.deposit(interest)
        return interest

    # __repr__: shown in REPL/debugger — should be unambiguous, ideally eval-able
    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self.balance:.2f})"

    # __str__: human-readable version shown by print()
    def __str__(self) -> str:
        return f"{self.owner}'s account: ${self.balance:.2f}"


alice_account = BankAccount("Alice", 1000.0)
bob_account   = BankAccount("Bob")   # initial_balance defaults to 0.0

alice_account.deposit(500)
alice_account.withdraw(200)
interest = alice_account.apply_interest()

print(alice_account)   # calls __str__
print(repr(alice_account))   # calls __repr__
print(f"\n{alice_account.get_statement()}")
print(f"\nInterest earned: ${interest:.2f}")
print(f"Total accounts created: {BankAccount.total_accounts}")

# Class attribute is shared — changing it affects ALL instances
print(f"\nCurrent interest rate: {alice_account.interest_rate}")
BankAccount.interest_rate = 0.06   # change on class, not instance
print(f"After rate change — Alice: {alice_account.interest_rate}, Bob: {bob_account.interest_rate}")


# =============================================================================
# SECTION 2: Class methods and static methods
# =============================================================================

# CONCEPT:
# Instance method: takes `self`, operates on/with instance data
# Class method:    takes `cls`, operates on class-level data, can create instances
# Static method:   no self or cls, just a function organized inside the class

print("\n=== Section 2: Class and Static Methods ===")

class Temperature:
    """Demonstrates all three method types."""

    def __init__(self, celsius: float):
        self._celsius = celsius

    # --- Instance method: needs specific Temperature instance ---
    def to_fahrenheit(self) -> float:
        return self._celsius * 9/5 + 32

    def to_kelvin(self) -> float:
        return self._celsius + 273.15

    # --- Class methods: alternative constructors (the main use case) ---
    # WHY: sometimes data arrives in a different format — the class method
    # converts it before calling __init__
    @classmethod
    def from_fahrenheit(cls, f: float) -> "Temperature":
        """Factory: create Temperature from Fahrenheit degrees."""
        celsius = (f - 32) * 5/9
        return cls(celsius)   # cls() is same as Temperature() — works in subclasses too

    @classmethod
    def from_kelvin(cls, k: float) -> "Temperature":
        """Factory: create Temperature from Kelvin."""
        return cls(k - 273.15)

    # --- Static method: utility that belongs here but doesn't need instance/class ---
    @staticmethod
    def is_valid_celsius(value: float) -> bool:
        """Pure utility — checks if a temperature value is physically possible."""
        return value >= -273.15   # absolute zero

    def __repr__(self):
        return f"Temperature({self._celsius:.2f}°C)"


# Different ways to create a Temperature
t1 = Temperature(100)                    # from Celsius
t2 = Temperature.from_fahrenheit(212)    # factory method
t3 = Temperature.from_kelvin(373.15)    # factory method

print(f"t1 (100°C): {t1}")
print(f"t2 (212°F): {t2}")
print(f"t3 (373K):  {t3}")
print(f"t1 to F: {t1.to_fahrenheit()}°F")
print(f"Valid celsius -300: {Temperature.is_valid_celsius(-300)}")
print(f"Valid celsius -270: {Temperature.is_valid_celsius(-270)}")


# =============================================================================
# SECTION 3: Inheritance — building hierarchies
# =============================================================================

# CONCEPT: Inheritance lets a child class reuse and extend parent class behavior.
# `super()` calls the parent class method — always call super().__init__()
# in a subclass to ensure proper initialization chain.
# WHY use inheritance: when objects share IS-A relationship (SavingsAccount IS-A BankAccount)

print("\n=== Section 3: Inheritance ===")

class Account:
    """Base account class."""
    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount: float):
        self.balance += amount
        return self

    def withdraw(self, amount: float):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self

    def __str__(self):
        return f"{type(self).__name__}({self.owner}: ${self.balance:.2f})"


class SavingsAccount(Account):
    """Savings account — extends Account with interest and withdrawal limit."""

    WITHDRAWAL_LIMIT = 3   # can only withdraw 3 times per period

    def __init__(self, owner: str, balance: float = 0.0, rate: float = 0.05):
        super().__init__(owner, balance)   # call parent's __init__ first!
        self.rate = rate
        self._withdrawals_this_period = 0  # track for limit enforcement

    def withdraw(self, amount: float):
        """OVERRIDES parent's withdraw to add limit checking."""
        if self._withdrawals_this_period >= self.WITHDRAWAL_LIMIT:
            raise ValueError(f"Withdrawal limit ({self.WITHDRAWAL_LIMIT}) reached for this period")
        super().withdraw(amount)   # call parent's withdraw for the actual deduction
        self._withdrawals_this_period += 1
        return self

    def add_interest(self):
        interest = self.balance * self.rate
        self.deposit(interest)
        return interest


class CheckingAccount(Account):
    """Checking account — extends Account with overdraft protection."""

    def __init__(self, owner: str, balance: float = 0.0, overdraft_limit: float = 100.0):
        super().__init__(owner, balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount: float):
        """OVERRIDES parent's withdraw to allow overdraft up to limit."""
        if amount > self.balance + self.overdraft_limit:
            raise ValueError(f"Exceeds overdraft limit of ${self.overdraft_limit}")
        self.balance -= amount   # can go negative up to overdraft_limit
        return self


savings  = SavingsAccount("Alice", 1000, rate=0.04)
checking = CheckingAccount("Bob", 500, overdraft_limit=200)

savings.deposit(500).deposit(100)   # method chaining! each returns self
print(savings)

checking.withdraw(650)   # below zero but within overdraft
print(checking)

interest = savings.add_interest()
print(f"Interest added: ${interest:.2f}")
print(savings)

# isinstance — checks the inheritance chain
print(f"\nisinstance(savings, SavingsAccount): {isinstance(savings, SavingsAccount)}")
print(f"isinstance(savings, Account):        {isinstance(savings, Account)}")   # True — it IS-A Account
print(f"isinstance(checking, SavingsAccount): {isinstance(checking, SavingsAccount)}")  # False


# =============================================================================
# SECTION 4: Polymorphism — same interface, different behavior
# =============================================================================

# CONCEPT: Polymorphism means "many forms." A function that works with Account
# objects doesn't need to know IF it's a savings or checking account — it just
# calls the same method and each type does the right thing.
# WHY: code that works with a base class interface works with ALL subclasses.

print("\n=== Section 4: Polymorphism ===")

class Shape:
    def area(self) -> float:
        raise NotImplementedError("Each shape must implement area()")

    def perimeter(self) -> float:
        raise NotImplementedError("Each shape must implement perimeter()")

    def describe(self) -> str:
        return f"{type(self).__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"

import math

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def perimeter(self):
        return 2 * math.pi * self.radius

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c

    def area(self):
        # Heron's formula
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s * (s-self.a) * (s-self.b) * (s-self.c))

    def perimeter(self):
        return self.a + self.b + self.c


# Polymorphic function: works with ANY Shape subclass
def print_shape_info(shape: Shape):
    """This function doesn't care whether it gets a Circle, Rectangle, or Triangle."""
    print(f"  {shape.describe()}")

shapes = [Circle(5), Rectangle(4, 6), Triangle(3, 4, 5)]

print("All shapes:")
for shape in shapes:
    print_shape_info(shape)   # each calls its own area() and perimeter()

# Sorting by area — works because all shapes have .area()
shapes.sort(key=lambda s: s.area())
print("\nSorted by area:")
for shape in shapes:
    print(f"  {type(shape).__name__}: {shape.area():.2f}")


# =============================================================================
# SECTION 5: Properties — controlled attribute access
# =============================================================================

# CONCEPT: @property turns a method into an attribute access syntax.
# Use it to: validate values on set, compute derived values on get,
# make attributes read-only. This is Python's way of doing "getters/setters"
# but without the ugly Java-style `getX()`/`setX()` methods.

print("\n=== Section 5: Properties ===")

class Product:
    def __init__(self, name: str, price: float, quantity: int):
        self.name = name
        self.price = price       # calls the setter defined below
        self.quantity = quantity

    @property
    def price(self) -> float:
        """Getter: called when you READ product.price"""
        return self._price

    @price.setter
    def price(self, value: float):
        """Setter: called when you WRITE product.price = x"""
        if value < 0:
            raise ValueError(f"Price cannot be negative: {value}")
        self._price = value   # store in _price to avoid infinite recursion

    @property
    def total_value(self) -> float:
        """Read-only computed property — no setter needed."""
        return self._price * self.quantity

    @property
    def is_available(self) -> bool:
        return self.quantity > 0

    def __repr__(self):
        return f"Product({self.name!r}, ${self.price:.2f} x {self.quantity})"

widget = Product("Widget", 9.99, 50)
print(f"{widget}")
print(f"Total value: ${widget.total_value:.2f}")
print(f"Available: {widget.is_available}")

widget.price = 12.99   # calls the setter — validated!
print(f"After price update: {widget}")

try:
    widget.price = -5   # setter raises ValueError
except ValueError as e:
    print(f"Caught: {e}")

try:
    widget.total_value = 100   # read-only — no setter
except AttributeError as e:
    print(f"Read-only: {e}")


print("\n=== OOP practice complete ===")
print("Core OOP concepts demonstrated:")
print("  1. __init__: constructor; self: the instance")
print("  2. Class attrs (shared) vs instance attrs (per-object)")
print("  3. @classmethod: factory constructors; @staticmethod: utilities")
print("  4. Inheritance + super(): extend parent without duplicating code")
print("  5. Polymorphism: write code against an interface, works for all subclasses")
print("  6. @property: controlled attribute access with validation")
