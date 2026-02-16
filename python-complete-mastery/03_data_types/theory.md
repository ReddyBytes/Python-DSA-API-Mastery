# 📦 03 — Python Data Types (Beginner → Advanced → Professional Level)



# 🧠 First Understand WHY Data Types Exist

Imagine you are building a school management system.

You need to store:

- Student name
- Student marks
- Student subjects
- Whether student passed
- Student profile details

Now think carefully:

Would you store everything in same format?

No.

Because:
- Name is text
- Marks are numbers
- Subjects are multiple values
- Passed is True/False
- Profile is structured data

👉 That decision is called **choosing correct data type**.

A 5-year experienced developer doesn’t just code.
He chooses the correct container.

---

# 🏗️ Complete Classification

```
Data Types
│
├── Numeric
│     ├── int
│     ├── float
│     └── complex
│
├── Boolean
│
├── Sequence Types
│     ├── str
│     ├── list
│     ├── tuple
│     └── range
│
├── Set Types
│     ├── set
│     └── frozenset
│
├── Mapping Type
│     └── dict
│
└── NoneType
```

---

# 1️⃣ NUMERIC TYPES

## 🔵 int

Whole numbers.

```
age = 25
```

Internally:
- Immutable
- Stored as objects
- Python reuses small integers (-5 to 256)

Important methods:

```
abs(x)
pow(x, y)
int("10")
```

---

## 🔵 float

Decimal numbers.

```
price = 10.5
```

Important:
- Floating precision issues
- Use `decimal` module for financial apps

Methods:

```
round(x)
float("10.5")
```

---

## 🔵 complex

```
x = 3 + 4j
```

Mostly scientific usage.

---

# 2️⃣ BOOLEAN

Only:

```
True
False
```

Used in:
- Conditions
- Flags
- Authentication
- Feature toggles

Important concept:

Everything in Python has truth value.

```
bool(0) → False
bool("") → False
bool([]) → False
```

Empty means False.

---

# 3️⃣ STRING (str)

Text data.

```
name = "Rahul"
```

---

## 🔹 What does Ordered mean?

Imagine:

```
R A H U L
0 1 2 3 4
```

Each character has position.
That position is called index.

---

## 🔹 Immutable Meaning

Once created,
you cannot modify individual character.

```
name[0] = "M" ❌
```

Because Python creates new object instead.

---

## 🔹 Important String Methods

### Case Handling

```
upper()
lower()
title()
capitalize()
swapcase()
```

### Searching

```
find()
index()
startswith()
endswith()
count()
```

### Cleaning

```
strip()
lstrip()
rstrip()
replace()
```

### Splitting & Joining

```
split()
join()
```

Example:

```
"apple,banana".split(",")
```

### Checking

```
isalpha()
isdigit()
isalnum()
isspace()
```

---

## 🧠 Professional Insight

Strings are heavily optimized in Python.
Avoid multiple concatenations in loops.

Instead use:

```
"".join(list_of_strings)
```

Because:
String is immutable → each concat creates new object.

---

# 4️⃣ LIST (Most Used Collection)

```
fruits = ["apple", "banana", "mango"]
```

Think like:
Shopping cart.

---

## 🔹 Properties

- Ordered
- Mutable
- Allows duplicates
- Indexed

---

## 🔹 Important List Methods

### Adding

```
append()
extend()
insert()
```

### Removing

```
remove()
pop()
clear()
```

### Searching

```
index()
count()
```

### Sorting

```
sort()
reverse()
```

---

## 🧠 Performance Insight

| Operation | Time Complexity |
|------------|----------------|
| Append | O(1) |
| Insert middle | O(n) |
| Access by index | O(1) |
| Search | O(n) |

---

## 🧠 Professional Usage

Use list when:
- Order matters
- You need duplicates
- Frequent appending

Avoid list when:
- Need fast lookup → use set or dict

---

# 5️⃣ TUPLE

```
coordinates = (10, 20)
```

Like:
Permanent data.

---

## 🔹 Properties

- Ordered
- Immutable
- Allows duplicates

---

## 🔹 Important Methods

Very limited:

```
count()
index()
```

---

## 🧠 Why Use Tuple?

- Faster than list
- Safe from accidental modification
- Used as dictionary keys
- Used in returning multiple values

---

# 6️⃣ SET

```
numbers = {1, 2, 3}
```

Think:
Unique collection.

---

## 🔹 Properties

- Unordered
- No duplicates
- Mutable

---

## 🔹 Important Methods

```
add()
remove()
discard()
union()
intersection()
difference()
```

---

## 🧠 Performance

Lookup in set:

O(1)

Very fast.

Use when:
- Need uniqueness
- Need fast membership testing

---

# 7️⃣ DICTIONARY

```
student = {
    "name": "Ravi",
    "age": 20
}
```

Key → Value storage.

---

## 🔹 Properties

- Key-value pair
- Mutable
- Keys must be immutable

---

## 🔹 Important Methods

```
get()
keys()
values()
items()
update()
pop()
clear()
```

---

## 🧠 Performance

Lookup by key:

O(1)

Very fast.

Used in:
- Databases
- APIs
- JSON
- Configuration

---

# 8️⃣ NONE TYPE

```
data = None
```

Means:
No value yet.

Used in:
- Default parameters
- Placeholder
- Checking absence

---

# 🔥 MUTABLE vs IMMUTABLE (VERY IMPORTANT)

Immutable:
- int
- float
- str
- tuple
- frozenset

Mutable:
- list
- dict
- set

---

# 🧠 Memory Understanding

Immutable objects:
Changing value → new object created.

Mutable objects:
Changing value → same object modified.

---

# 🎯 Senior Developer Thinking

Before choosing data type, ask:

1. Will data change?
2. Do I need order?
3. Do I need uniqueness?
4. Do I need fast lookup?
5. Will this be used as key?

That is architectural thinking.

---

# 📊 Decision Flow

```
Single value?
    └── Yes → int/float/str/bool

Multiple values?
    └── Need key-value? → dict
    └── Need uniqueness? → set
    └── Should not change? → tuple
    └── Default? → list
```

---

# 🚀 Final Understanding

Data types are not basic topic.

They affect:

- Performance
- Memory
- Readability
- Maintainability
- Architecture

Choosing wrong data type = future technical debt.

Choosing correct data type = clean design.

---



# 🔁 Navigation

[Memory Management](/python-complete-mastery/07_memory_management/theory.md)  
[Control Flow Statements](/python-complete-mastery/02_control_flow/theory.md)  
[Interview Questions](/python-complete-mastery/03_data_types/interview.md)

---