# ⚡ Cheatsheet: Python Fundamentals

```
┌─────────────────────────────────────────────────────────────────────┐
│                     QUICK REFERENCE CARD                            │
└─────────────────────────────────────────────────────────────────────┘
```

## 📝 Variables & Types

```python
x = 42              # int
y = 3.14            # float
s = "hello"         # str
b = True            # bool
n = None            # NoneType
c = 3 + 4j          # complex

type(x)             # <class 'int'>
isinstance(x, int)  # True
```

## ➕ Operators

```python
# Arithmetic
+  -  *  /  //  %  **
# /  → always float | // → floor division | % → remainder | ** → power

# Comparison  (return bool)
==  !=  >  <  >=  <=  is  is not  in  not in

# Logical
and  or  not

# Assignment shortcuts
x += 1   x -= 1   x *= 2   x /= 2   x //= 2   x **= 2   x %= 2
```

## 🖨️ print()

```python
print("hello")                    # hello
print("a", "b", sep="-")          # a-b
print("hi", end="!")              # hi! (no newline)
print(f"name={name!r}")           # name='Alice'
print(f"{3.14159:.2f}")           # 3.14
print(f"{1000000:,}")             # 1,000,000
print(f"{'left':<10}|")          # left       |
print(f"{'right':>10}|")         #      right |
```

## 🔄 Type Conversion

```python
int("42")       → 42
int(3.9)        → 3  (truncates!)
float("3.14")   → 3.14
str(100)        → "100"
bool(0)         → False
bool("")        → False
bool([])        → False
bool(None)      → False
```

## 🔤 String Quick Ops

```python
s = "Hello World"
s[0]         # 'H'
s[-1]        # 'd'
s[1:5]       # 'ello'
s[::-1]      # 'dlroW olleH'
len(s)       # 11
s.upper()    # 'HELLO WORLD'
s.lower()    # 'hello world'
s.strip()    # remove whitespace
s.split()    # ['Hello', 'World']
s.replace("World", "Python")
",".join(["a","b","c"])  # 'a,b,c'
s.startswith("Hello")   # True
s.endswith("World")     # True
"o" in s                # True
```

## ⌨️ Input

```python
name = input("Enter name: ")          # always string!
age  = int(input("Enter age: "))      # convert!
price = float(input("Enter price: ")) # convert!
```

## 🧮 Useful Built-ins

```python
abs(-5)         # 5
round(3.7)      # 4
round(3.14159, 2)  # 3.14
min(1, 2, 3)    # 1
max(1, 2, 3)    # 3
pow(2, 10)      # 1024 (same as 2**10)
divmod(10, 3)   # (3, 1) → quotient and remainder
id(x)           # memory address of x
```

## 💡 Comments

```python
# Single line comment

"""
Multi-line comment
(technically a docstring)
"""

# Useful tags
# TODO: — something to implement
# FIXME: — known bug
# NOTE: — important info
# HACK: — temporary workaround
```

## ⚠️ Common Gotchas

```python
0.1 + 0.2 != 0.3           # float precision!
int(3.9) == 3              # truncates, not rounds!
"5" + 5  → TypeError       # no implicit conversion
-7 // 2 == -4              # floors toward -infinity
-5 % 3 == 1                # modulo is always non-negative
True + True == 2           # bool is subclass of int!
1_000_000 == 1000000       # underscores in numbers ok
```

## 🏷️ Naming Conventions

```python
variable_name     # snake_case
CONSTANT_VALUE    # UPPER_SNAKE_CASE
ClassName         # PascalCase
_private_var      # prefix _ = convention for private
__name_mangled    # prefix __ = name mangling in class
__dunder__        # double underscore both sides = special
```

## 🔍 Truthiness Summary

```
Falsy:  0, 0.0, 0j, "", [], {}, set(), None, False
Truthy: everything else (including "0", [False], -1)
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Interview Q&A](./interview.md)
