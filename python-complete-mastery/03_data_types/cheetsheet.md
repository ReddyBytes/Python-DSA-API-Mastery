# ⚡ Data Types — Cheatsheet

## 🗂️ Which Type Should I Use?

```
One value:
  Whole number    →  int        42, -7, 0
  Decimal         →  float      3.14, -0.5
  Yes/No          →  bool       True, False
  Text            →  str        "hello"
  Nothing         →  None       None

Many values:
  Ordered + can change   →  list       [1, 2, 3]
  Ordered + never change →  tuple      (1, 2, 3)
  Unique only, fast find →  set        {1, 2, 3}
  Label → Value pairs    →  dict       {"name": "Alice"}
```

---

## 🔢 int
```python
17 // 5   → 3      # floor division (whole number)
17 %  5   → 2      # modulo (remainder)
17 /  5   → 3.4    # true division (always float)
2 ** 10   → 1024   # power
abs(-5)   → 5      # absolute value

bin(255)  → '0b11111111'
oct(255)  → '0o377'
hex(255)  → '0xff'
```

## 🌊 float
```python
0.1 + 0.2 ≠ 0.3          # precision issue!
round(0.1 + 0.2, 2)       # fix for display
(5.0).is_integer() → True # check if whole number
```

## ✅ bool
```python
# Falsy:  0, 0.0, "", [], {}, (), set(), None, False
# Truthy: everything else (including "0", [False], -1)

True + True  → 2     # bool IS an int
sum([True, False, True])  → 2   # count Trues!
```

---

## 🔤 str
```python
s = "Python"
s[0]      → 'P'       s[-1]     → 'n'
s[1:4]    → 'yth'     s[::-1]   → 'nohtyP'
len(s)    → 6

s.upper() / s.lower() / s.title()
s.strip() / s.split(",") / ",".join(lst)
s.replace(old, new)
s.find("y")       → 1   (or -1 if not found)
s.count("t")      → 1
"y" in s          → True
s.startswith("Py") → True
s.isdigit() / s.isalpha() / s.isalnum()

f"Name: {name}, Age: {age}"       # f-string
f"{3.14:.2f}"  → "3.14"
f"{1234:,}"    → "1,234"
```

---

## 📋 list
```python
lst = [1, 2, 3]
lst.append(4)          # [1,2,3,4]
lst.insert(0, 0)       # [0,1,2,3,4]
lst.extend([5,6])      # adds each item
lst.remove(3)          # by value
lst.pop()              # last item → returns it
lst.pop(0)             # by index → returns it
del lst[0]             # by index, no return

len(lst) / sum(lst) / min(lst) / max(lst)
lst.count(2)           # occurrences
lst.sort()             # in-place, returns None!
sorted(lst)            # new list, original safe
lst.copy() / lst[:]    # real copy (not b = a!)
```

---

## 📦 tuple
```python
t = (1, 2, 3)
t = 1, 2, 3          # same thing
single = (42,)        # ← comma needed for 1 item!

a, b, c = t           # unpack
a, b = b, a           # swap using tuple
```

---

## 🎯 set
```python
s = {1, 2, 3}
empty = set()         # NOT {} — that's a dict!

s.add(4)
s.discard(10)         # safe — no error if missing
s.remove(3)           # KeyError if missing

3 in s               # O(1) — very fast!

A | B   → union            (all)
A & B   → intersection     (both)
A - B   → difference       (in A, not B)
A ^ B   → symmetric diff   (one or other, not both)
```

---

## 🗂️ dict
```python
d = {"key": "value"}

d["key"]              # KeyError if missing
d.get("key")          # None if missing ← safer!
d.get("key", "default")  # custom default

d["new"] = val        # add
d.update({"a":1})     # add/update multiple
del d["key"]          # remove
d.pop("key", None)    # remove safely

for k in d:                # keys
for v in d.values():       # values
for k, v in d.items():     # both ← most common

"key" in d           # True/False — checks keys
```

---

## 🔄 Type Conversion
```python
int("42")    → 42       int(3.9)   → 3  # truncates!
float("3.14")→ 3.14    str(42)    → "42"
bool(0)      → False    bool("")   → False
list("abc")  → ['a','b','c']
set([1,2,2]) → {1,2}   # removes dupes
```

---

## ⚠️ Gotchas
```
{}         → empty dict (not set!)
set()      → empty set
(42)       → int 42 (not tuple!)
(42,)      → tuple with one item
b = a      → alias, NOT a copy (for lists/dicts!)
b = a.copy()→ real copy
int(3.9)   → 3, not 4  (truncates)
0.1+0.2 ≠ 0.3 → float precision
list.sort() → returns None, sorts in place
sorted(list)→ returns new list
```

---

## ⚡ Speed Reference
```
Lookup in list   → O(n)  — checks one by one
Lookup in set    → O(1)  — instant via hash  ← use for large data!
Lookup in dict   → O(1)  — instant via hash
```

---

## 🧭 Navigation

| | |
|---|---|
| ⬅️ Previous | [02 — Control Flow](../02_control_flow/README.md) |
| 📖 Theory | [README.md](./README.md) |
| 💻 Practice | [practice.py](./practice.py) |
| 🌍 Examples | [examples.py](./examples.py) |
| 🎤 Interview | [interview.md](./interview.md) |
| ➡️ Next | [04 — Functions](../04_functions/README.md) |
| 🏠 Home | [python-complete-mastery](../README.md) |