# Operator Overloading — Theory + Practice

# =============================================================================
# THEORY: Operator overloading in Python
# =============================================================================
#
# Python maps every operator to a dunder method. When you write a + b, Python:
#   1. Calls type(a).__add__(a, b)
#   2. If that returns NotImplemented → calls type(b).__radd__(b, a)
#   3. If that also returns NotImplemented → raises TypeError
#
# The reflected (r-prefixed) methods exist so the right-hand operand
# gets a chance. This is critical for mixed-type arithmetic.
#
# OPERATOR → METHOD MAPPING:
#   a + b       __add__      /  __radd__     (+=  __iadd__)
#   a - b       __sub__      /  __rsub__     (-=  __isub__)
#   a * b       __mul__      /  __rmul__     (*=  __imul__)
#   a / b       __truediv__  /  __rtruediv__ (/=  __itruediv__)
#   a // b      __floordiv__ /  __rfloordiv__
#   a % b       __mod__      /  __rmod__
#   a ** b      __pow__      /  __rpow__
#   a @ b       __matmul__   /  __rmatmul__  (Matrix multiply, Python 3.5+)
#   a & b       __and__      /  __rand__
#   a | b       __or__       /  __ror__
#   a ^ b       __xor__      /  __rxor__
#   a << b      __lshift__   /  __rlshift__
#   a >> b      __rshift__   /  __rrshift__
#   -a          __neg__
#   +a          __pos__
#   abs(a)      __abs__
#   ~a          __invert__
#
# CRITICAL RULE: Return NotImplemented (not raise, not return False)
# when your type doesn't know how to handle the other operand.
# =============================================================================

from __future__ import annotations
from functools import total_ordering
import math


# =============================================================================
# EXAMPLE 1: Matrix — @matmul and full arithmetic
# =============================================================================

class Matrix:
    """
    Simple matrix class demonstrating @, *, +, - and scalar operations.
    Shows how __matmul__ (@) is the right operator for matrix multiplication.
    """

    def __init__(self, data: list[list[float]]):
        if not data or not data[0]:
            raise ValueError("Matrix cannot be empty")
        cols = len(data[0])
        if any(len(row) != cols for row in data):
            raise ValueError("All rows must have equal length")
        self.data = [list(row) for row in data]  # defensive copy
        self.rows = len(data)
        self.cols = cols

    @classmethod
    def zeros(cls, rows: int, cols: int) -> Matrix:
        return cls([[0.0] * cols for _ in range(rows)])

    @classmethod
    def identity(cls, n: int) -> Matrix:
        m = cls.zeros(n, n)
        for i in range(n):
            m.data[i][i] = 1.0
        return m

    def __matmul__(self, other: Matrix) -> Matrix:
        """Matrix multiplication: A @ B"""
        if isinstance(other, Matrix):
            if self.cols != other.rows:
                raise ValueError(
                    f"Shape mismatch: ({self.rows}×{self.cols}) @ ({other.rows}×{other.cols})"
                )
            result = Matrix.zeros(self.rows, other.cols)
            for i in range(self.rows):
                for j in range(other.cols):
                    result.data[i][j] = sum(
                        self.data[i][k] * other.data[k][j]
                        for k in range(self.cols)
                    )
            return result
        return NotImplemented

    def __add__(self, other: Matrix) -> Matrix:
        """Element-wise addition: A + B"""
        if isinstance(other, Matrix):
            if (self.rows, self.cols) != (other.rows, other.cols):
                raise ValueError("Shape mismatch for addition")
            return Matrix([
                [self.data[i][j] + other.data[i][j] for j in range(self.cols)]
                for i in range(self.rows)
            ])
        return NotImplemented

    def __sub__(self, other: Matrix) -> Matrix:
        if isinstance(other, Matrix):
            if (self.rows, self.cols) != (other.rows, other.cols):
                raise ValueError("Shape mismatch for subtraction")
            return Matrix([
                [self.data[i][j] - other.data[i][j] for j in range(self.cols)]
                for i in range(self.rows)
            ])
        return NotImplemented

    def __mul__(self, scalar) -> Matrix:
        """Scalar multiplication: A * k"""
        if isinstance(scalar, (int, float)):
            return Matrix([[x * scalar for x in row] for row in self.data])
        return NotImplemented

    def __rmul__(self, scalar) -> Matrix:
        """Scalar multiplication from left: k * A"""
        return self.__mul__(scalar)   # commutative

    def __neg__(self) -> Matrix:
        return Matrix([[-x for x in row] for row in self.data])

    def __pos__(self) -> Matrix:
        return Matrix([list(row) for row in self.data])   # copy

    def __eq__(self, other) -> bool:
        if isinstance(other, Matrix):
            return self.data == other.data
        return NotImplemented

    def transpose(self) -> Matrix:
        return Matrix([
            [self.data[j][i] for j in range(self.rows)]
            for i in range(self.cols)
        ])

    def __repr__(self) -> str:
        rows_str = ", ".join(str(row) for row in self.data)
        return f"Matrix([{rows_str}])"

    def __str__(self) -> str:
        width = max(len(f"{x:.2f}") for row in self.data for x in row)
        rows = [" ".join(f"{x:{width}.2f}" for x in row) for row in self.data]
        return "\n".join(rows)

A = Matrix([[1, 2], [3, 4]])
B = Matrix([[5, 6], [7, 8]])

print("A @ B (matrix multiply):")
print(A @ B)
# [[19, 22], [43, 50]]

print("\nA + B:")
print(A + B)

print("\n3 * A (scalar):")
print(3 * A)


# =============================================================================
# EXAMPLE 2: Polynomial — + * and evaluation with ()
# =============================================================================

class Polynomial:
    """
    Polynomial with overloaded +, -, *, ** and callable evaluation.
    Demonstrates combining arithmetic and __call__.
    """

    def __init__(self, *coefficients: float):
        # coefficients[i] is the coefficient of x^i
        # Polynomial(1, 2, 3) → 1 + 2x + 3x²
        self.coeffs = list(coefficients)
        # Remove trailing zeros:
        while len(self.coeffs) > 1 and self.coeffs[-1] == 0:
            self.coeffs.pop()

    def degree(self) -> int:
        return len(self.coeffs) - 1

    def __call__(self, x: float) -> float:
        """Evaluate at x using Horner's method."""
        result = 0.0
        for coeff in reversed(self.coeffs):
            result = result * x + coeff
        return result

    def __add__(self, other: Polynomial) -> Polynomial:
        if isinstance(other, (int, float)):
            other = Polynomial(other)
        if isinstance(other, Polynomial):
            n = max(len(self.coeffs), len(other.coeffs))
            a = self.coeffs + [0] * (n - len(self.coeffs))
            b = other.coeffs + [0] * (n - len(other.coeffs))
            return Polynomial(*(x + y for x, y in zip(a, b)))
        return NotImplemented

    def __radd__(self, other): return self.__add__(other)

    def __sub__(self, other: Polynomial) -> Polynomial:
        if isinstance(other, (int, float)):
            other = Polynomial(other)
        if isinstance(other, Polynomial):
            n = max(len(self.coeffs), len(other.coeffs))
            a = self.coeffs + [0] * (n - len(self.coeffs))
            b = other.coeffs + [0] * (n - len(other.coeffs))
            return Polynomial(*(x - y for x, y in zip(a, b)))
        return NotImplemented

    def __mul__(self, other: Polynomial) -> Polynomial:
        if isinstance(other, (int, float)):
            return Polynomial(*(c * other for c in self.coeffs))
        if isinstance(other, Polynomial):
            n = len(self.coeffs) + len(other.coeffs) - 1
            result = [0.0] * n
            for i, a in enumerate(self.coeffs):
                for j, b in enumerate(other.coeffs):
                    result[i+j] += a * b
            return Polynomial(*result)
        return NotImplemented

    def __rmul__(self, other): return self.__mul__(other)

    def __pow__(self, n: int) -> Polynomial:
        if not isinstance(n, int) or n < 0:
            raise ValueError("Power must be non-negative integer")
        result = Polynomial(1)
        for _ in range(n):
            result = result * self
        return result

    def __neg__(self): return Polynomial(*(-c for c in self.coeffs))

    def __eq__(self, other):
        if isinstance(other, Polynomial):
            return self.coeffs == other.coeffs
        return NotImplemented

    def __repr__(self) -> str:
        return f"Polynomial({', '.join(str(c) for c in self.coeffs)})"

    def __str__(self) -> str:
        if not self.coeffs:
            return "0"
        terms = []
        for i, c in enumerate(self.coeffs):
            if c == 0:
                continue
            if i == 0:
                terms.append(str(c))
            elif i == 1:
                terms.append(f"{c}x" if c != 1 else "x")
            else:
                terms.append(f"{c}x^{i}" if c != 1 else f"x^{i}")
        return " + ".join(reversed(terms)) if terms else "0"

# 3 + 2x + x²
p = Polynomial(3, 2, 1)
print(f"p(x) = {p}")
print(f"p(2) = {p(2)}")   # 3 + 4 + 4 = 11

q = Polynomial(1, 1)      # 1 + x
print(f"p + q = {p + q}")
print(f"p * q = {p * q}")
print(f"q**3  = {q**3}")  # (1+x)^3 = 1 + 3x + 3x² + x³


# =============================================================================
# EXAMPLE 3: Pipe operator for function composition
# =============================================================================

class Pipe:
    """
    Uses | operator to compose functions into a pipeline.
    Demonstrates __or__ and __ror__ for chaining.
    """

    def __init__(self, *funcs):
        self.funcs = list(funcs)

    def __or__(self, func):
        """pipe | func → new Pipe with func added"""
        if callable(func):
            return Pipe(*self.funcs, func)
        return NotImplemented

    def __ror__(self, value):
        """value | pipe → apply pipeline to value"""
        result = value
        for f in self.funcs:
            result = f(result)
        return result

    def __call__(self, value):
        return value | self

    def __len__(self):
        return len(self.funcs)

    def __repr__(self):
        names = [getattr(f, '__name__', str(f)) for f in self.funcs]
        return f"Pipe({' | '.join(names)})"

# Build a text processing pipeline:
clean = Pipe() | str.strip | str.lower | str.split

print(clean("  Hello World  "))   # ['hello', 'world']

# Or use as a pipeline step:
process = (
    Pipe()
    | (lambda s: s.strip())
    | str.upper
    | (lambda s: f"[{s}]")
)
print(process("  hello  "))   # [HELLO]


# =============================================================================
# EXAMPLE 4: Bitwise operators for flag/permission systems
# =============================================================================

class Permission:
    """
    File permission flags using bitwise operators.
    Demonstrates __or__, __and__, __xor__, __invert__.
    """

    READ    = 4
    WRITE   = 2
    EXECUTE = 1

    def __init__(self, value: int = 0):
        self.value = value & 0b111   # only 3 bits

    def __or__(self, other: Permission) -> Permission:
        """Combine permissions: p | Permission(2)"""
        if isinstance(other, Permission):
            return Permission(self.value | other.value)
        if isinstance(other, int):
            return Permission(self.value | other)
        return NotImplemented

    def __and__(self, other: Permission) -> Permission:
        """Intersect permissions"""
        if isinstance(other, Permission):
            return Permission(self.value & other.value)
        if isinstance(other, int):
            return Permission(self.value & other)
        return NotImplemented

    def __xor__(self, other: Permission) -> Permission:
        """Toggle permissions"""
        if isinstance(other, Permission):
            return Permission(self.value ^ other.value)
        return NotImplemented

    def __invert__(self) -> Permission:
        """Invert all permission bits"""
        return Permission(~self.value & 0b111)

    def __contains__(self, perm: int) -> bool:
        """Check if permission is set: Permission.READ in p"""
        return bool(self.value & perm)

    def __bool__(self) -> bool:
        return bool(self.value)

    def __eq__(self, other):
        if isinstance(other, Permission):
            return self.value == other.value
        return NotImplemented

    def __repr__(self) -> str:
        parts = []
        if Permission.READ    in self: parts.append("READ")
        if Permission.WRITE   in self: parts.append("WRITE")
        if Permission.EXECUTE in self: parts.append("EXECUTE")
        return f"Permission({' | '.join(parts) or 'NONE'})"

NONE    = Permission(0)
READ    = Permission(4)
WRITE   = Permission(2)
EXECUTE = Permission(1)

p = READ | WRITE
print(p)                            # Permission(READ | WRITE)
print(Permission.READ in p)         # True
print(Permission.EXECUTE in p)      # False
print(p & READ)                     # Permission(READ)
print(~EXECUTE)                     # Permission(READ | WRITE)


# =============================================================================
# PRACTICE PROBLEMS
# =============================================================================

# ── Problem 1 ──────────────────────────────────────────────────────────────
# Implement a Interval class for numeric ranges [lo, hi] with:
#   - & for intersection: [1,5] & [3,8] = [3,5]
#   - | for union: [1,3] | [5,8] = [1,8] (bounding box)
#   - in operator: 3 in Interval(1,5) → True
#   - len(): hi - lo
#   - __bool__: False if empty (lo > hi)
# Tests:
#   a, b = Interval(1, 5), Interval(3, 8)
#   a & b == Interval(3, 5)
#   5 in a → True
#   len(Interval(2, 7)) → 5

# ── Problem 2 ──────────────────────────────────────────────────────────────
# Build a Money class (amount + currency) with:
#   - +/- between same currencies
#   - * with scalar (Money * 3)
#   - raise CurrencyMismatch if currencies differ
#   - __format__: f"{m:$}" → "$12.50", f"{m:EUR}" → "EUR 12.50"
#   - __round__: round(m, 2)

# ── Problem 3 ──────────────────────────────────────────────────────────────
# Create a BitField class that:
#   - stores an integer bit pattern
#   - supports << and >> (shift), & (mask), | (set bits), ^ (toggle), ~
#   - supports len() → number of set bits (popcount)
#   - supports iteration: yields positions of set bits
#   - supports [n] getter/setter for individual bits
# Tests:
#   b = BitField(0b1010)
#   len(b) == 2        # 2 bits set
#   list(b) == [1, 3]  # positions of set bits
#   b[0] = 1           # set bit 0
#   b >> 1             # BitField(0b101)


# =============================================================================
# SOLUTION: Interval
# =============================================================================

@total_ordering
class Interval:
    def __init__(self, lo: float, hi: float):
        self.lo = lo
        self.hi = hi

    def __and__(self, other: Interval) -> Interval:
        if isinstance(other, Interval):
            lo = max(self.lo, other.lo)
            hi = min(self.hi, other.hi)
            return Interval(lo, hi)
        return NotImplemented

    def __or__(self, other: Interval) -> Interval:
        if isinstance(other, Interval):
            return Interval(min(self.lo, other.lo), max(self.hi, other.hi))
        return NotImplemented

    def __contains__(self, value: float) -> bool:
        return self.lo <= value <= self.hi

    def __len__(self) -> int:
        return max(0, int(self.hi - self.lo))

    def __bool__(self) -> bool:
        return self.lo <= self.hi

    def __eq__(self, other):
        if isinstance(other, Interval):
            return self.lo == other.lo and self.hi == other.hi
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Interval):
            return self.lo < other.lo
        return NotImplemented

    def __hash__(self):
        return hash((self.lo, self.hi))

    def __repr__(self):
        return f"Interval({self.lo}, {self.hi})"

a, b = Interval(1, 5), Interval(3, 8)
assert (a & b) == Interval(3, 5),  f"Got {a & b}"
assert 5 in a
assert len(Interval(2, 7)) == 5
print("Interval tests passed!")
