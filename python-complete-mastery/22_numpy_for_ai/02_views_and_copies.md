# 🎯 NumPy Views vs Copies — The Silent Bug Source

In a shared Google Doc, two people editing the same document both see each other's changes in real time — there is only one underlying document. In a private copy, edits are isolated. **NumPy views** are the shared document: multiple array variables can point at the same block of memory, and a change made through any one of them is visible through all of them. **Copies** are isolated — a separate allocation with its own data.

This distinction is invisible at a glance, which makes it one of the most common sources of subtle bugs in numerical and ML code.

---

## 👁️ Section 1: What is a view?

A **view** is an array object that does not own its data. It holds a pointer into another array's memory buffer, along with shape and stride information describing how to interpret that memory. No new allocation happens. No data is duplicated.

The consequence: mutating a view mutates the original.

```python
import numpy as np

a = np.array([1, 2, 3, 4, 5])
b = a[1:4]         # ← b is a VIEW — same memory, different window
b[0] = 99          # ← writing to b writes through to a's buffer
print(a)           # [1, 99, 3, 4, 5] ← original changed without touching a directly
print(b.base is a) # True — confirms b is a view of a
```

Views are deliberate design. They make slicing O(1) regardless of array size: no data is moved, only a new descriptor is created.

---

## 📋 Section 2: What is a copy?

A **copy** allocates a fresh block of memory and duplicates the data. After that point, the two arrays are completely independent — changes to one have no effect on the other.

```python
a = np.array([1, 2, 3, 4, 5])
b = a[1:4].copy()  # ← .copy() forces a new allocation
b[0] = 99          # ← only b's buffer is modified
print(a)           # [1, 2, 3, 4, 5] ← original unchanged
print(b.base)      # None — b owns its data, it is not a view of anything
```

The price of safety is memory: copying a 1 GB array costs 1 GB of additional RAM. Views cost essentially nothing.

---

## 🔍 Section 3: How to check — view or copy?

NumPy gives you a direct diagnostic: every array has a `.base` attribute.

```python
b.base is a     # True  — b is a view of a (shares a's memory buffer)
b.base is None  # True  — b owns its data (either a copy or the original allocation)
```

For multi-level views (a view of a view), `.base` chains back to the original owner:

```python
a = np.arange(10)
b = a[::2]      # view of a
c = b[1:]       # view of b — but c.base is a, not b
c.base is a     # True — always traces back to the root owner
```

---

## 📊 Section 4: When does NumPy return a view vs copy?

This table is the core reference. Many bugs come from assuming the wrong column.

| Operation | View or Copy? | Why |
|---|---|---|
| Slicing `a[1:4]` | **View** | Contiguous memory window, no copy needed |
| Transpose `a.T` | **View** | Same data, different strides |
| Reshape (compatible) `a.reshape(2,3)` | **View** (usually) | Reinterprets strides; copy if non-contiguous |
| Boolean indexing `a[a > 0]` | **Copy** | Result size unknown until runtime |
| Fancy indexing `a[[0, 2, 4]]` | **Copy** | Non-contiguous selection, must gather |
| `.astype(new_dtype)` | **Copy** | New dtype requires new memory layout |
| `.flatten()` | **Copy** | Always returns a 1D copy |
| `.ravel()` | **View** (when possible) | Returns a view if memory is contiguous |

The key insight: any operation where NumPy cannot know the output size or memory layout at O(1) cost returns a copy.

---

## 🐛 Section 5: Accidental mutation — the real danger

The most common view-related bug is a function that silently modifies its caller's array. Unlike pandas' `SettingWithCopyWarning`, NumPy gives you no warning — the mutation just happens.

In-place operators (`/=`, `*=`, `+=`) are the most frequent culprits because they look like they create a new result but actually modify the array in place.

```python
# ACCIDENTAL mutation via in-place operator:
def normalize(arr):
    arr /= arr.max()   # ← /= modifies arr in-place
    return arr         # if caller passed a view, caller's original is now normalized too

data = np.array([1.0, 2.0, 4.0, 8.0])
subset = data[1:3]     # view of data
normalize(subset)      # mutates data[1] and data[2] without any warning
print(data)            # [1.0, 0.5, 1.0, 8.0] ← data was changed by normalize()

# Fix option 1: avoid in-place operators in functions
def normalize_safe(arr):
    return arr / arr.max()   # ← creates a new array, caller's data untouched

# Fix option 2: copy explicitly at the start of the function
def normalize_copy(arr):
    arr = arr.copy()         # ← local copy, isolate from caller
    arr /= arr.max()
    return arr
```

**Intentional write-back via view** (the flip side — sometimes you want this):

```python
matrix = np.zeros((100, 100))
row = matrix[5]        # ← view of row 5
row[:] = 1.0           # ← writes back into matrix row 5 in-place
# matrix[5] is now all 1.0 — no copy, no reassignment needed
```

The assignment `row[:] = 1.0` (with the slice) writes through the view. The assignment `row = 1.0` (without the slice) would just rebind the Python variable `row` to a scalar — it would not touch the matrix.

---

## 🗃️ Section 6: Memory layout and contiguity

When you create a standard 2D array, NumPy stores rows consecutively in memory — this is called **C-contiguous** (or row-major) layout, named after the C language convention. Accessing a full row is fast because the elements are adjacent in memory. Accessing a full column requires jumping through memory in strides.

**F-contiguous** (Fortran-order, column-major) stores columns consecutively. Useful when passing data to Fortran or LAPACK routines that expect column-major input.

```python
a = np.array([[1, 2, 3],
              [4, 5, 6]])

a.flags['C_CONTIGUOUS']     # True  — rows are laid out consecutively
a.flags['F_CONTIGUOUS']     # False

a.T.flags['C_CONTIGUOUS']   # False — transpose flips strides, not data layout
a.T.flags['F_CONTIGUOUS']   # True  — the transpose is F-contiguous

# Some C extensions (scipy sparse, certain BLAS calls) require contiguous input.
# Force a contiguous copy when needed:
a_contig = np.ascontiguousarray(a.T)   # ← C-contiguous copy of the transpose
```

**Strides** are the byte steps NumPy takes to move one element along each axis. A view changes strides without moving data — that is how transpose and reshape work without copying.

```python
a = np.zeros((3, 4), dtype=np.float64)
a.strides   # (32, 8) — move 32 bytes to next row, 8 bytes to next column
a.T.strides # (8, 32) — transposed: column step is now the fast dimension
```

---

## 📐 Section 7: Practical rules

**Assume slicing returns a view.** Never modify a slice unless you explicitly intend to update the original array. This assumption prevents the majority of accidental mutations.

**Use `.copy()` when:**
- Passing a subset to a function that will modify it in-place.
- Storing a subset long-term while the original array will be discarded or modified.
- After fancy indexing or boolean indexing (these already return copies, but being explicit documents intent).

**Use views intentionally when:**
- Working with large arrays where copying is expensive.
- Writing back to a specific row, column, or region of a larger array.
- Transposing or reshaping for a downstream call that does not modify the data.

**Quick decision checklist:**
1. Will this array be modified by the code that receives it? → `.copy()` first.
2. Is this a slice I will write back to the parent? → View is correct, use `slice[:] = value`.
3. Am I passing to an external library? → Check if it modifies in-place and whether it requires contiguous layout.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⬅️ Prev Topic | [01_dtype_and_precision.md](./01_dtype_and_precision.md) |
| ➡️ Next Topic | [03_random_and_sampling.md](./03_random_and_sampling.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
