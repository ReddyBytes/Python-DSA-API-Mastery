# NumPy for AI — Practice

## Quick Index

| Q | Topic | Difficulty |
|---|---|---|
| [Q1](#q1--dtype-and-precision--float32-vs-float64) | dtype and precision — float32 vs float64 | 🟢 |
| [Q2](#q2--dtype-and-precision--inspecting-memory) | dtype and precision — inspecting memory | 🟢 |
| [Q3](#q3--dtype-and-precision--safe-downcast-pattern) | dtype and precision — safe downcast pattern | 🟡 |
| [Q4](#q4--dtype-and-precision--astype-and-overflow) | dtype and precision — astype and overflow | 🟡 |
| [Q5](#q5--dtype-and-precision--ai-pipeline-dtypes) | dtype and precision — AI pipeline dtypes | 🟡 |
| [Q6](#q6--views-and-copies--identify-view-or-copy) | views and copies — identify view or copy | 🟢 |
| [Q7](#q7--views-and-copies--base-attribute) | views and copies — .base attribute | 🟢 |
| [Q8](#q8--views-and-copies--accidental-mutation-fix) | views and copies — accidental mutation fix | 🟡 |
| [Q9](#q9--views-and-copies--writeable-flag-and-memory-layout) | views and copies — writeable flag and memory layout | 🟠 |
| [Q10](#q10--random-and-sampling--default_rng-and-reproducibility) | random and sampling — default_rng and reproducibility | 🟢 |
| [Q11](#q11--random-and-sampling--integers-and-normal) | random and sampling — integers and normal | 🟢 |
| [Q12](#q12--random-and-sampling--choice-with-and-without-replacement) | random and sampling — choice with and without replacement | 🟡 |
| [Q13](#q13--random-and-sampling--shuffle-paired-arrays) | random and sampling — shuffle paired arrays | 🟡 |
| [Q14](#q14--conditional-operations--npwhere-relu) | conditional operations — np.where ReLU | 🟢 |
| [Q15](#q15--conditional-operations--npselect-multi-branch) | conditional operations — np.select multi-branch | 🟡 |
| [Q16](#q16--conditional-operations--npclip-safe-cross-entropy) | conditional operations — np.clip safe cross-entropy | 🟡 |
| [Q17](#q17--conditional-operations--safe-divide-pattern) | conditional operations — safe divide pattern | 🟠 |
| [Q18](#q18--statistics-and-distributions--percentile-and-iqr) | statistics and distributions — percentile and IQR | 🟢 |
| [Q19](#q19--statistics-and-distributions--nan-safe-functions) | statistics and distributions — nan-safe functions | 🟡 |
| [Q20](#q20--statistics-and-distributions--histogram-bins) | statistics and distributions — histogram bins | 🟡 |
| [Q21](#q21--statistics-and-distributions--correlation-matrix) | statistics and distributions — correlation matrix | 🟠 |
| [Q22](#q22--linear-algebra--matmul-vs-dot) | linear algebra — matmul vs dot | 🟢 |
| [Q23](#q23--linear-algebra--solve-linear-system) | linear algebra — solve linear system | 🟡 |
| [Q24](#q24--linear-algebra--svd-and-low-rank-approximation) | linear algebra — SVD and low-rank approximation | 🟠 |
| [Q25](#q25--linear-algebra--lstsq-regression) | linear algebra — lstsq regression | 🟠 |
| [Q26](#q26--einsum-and-performance--basic-notation) | einsum and performance — basic notation | 🟢 |
| [Q27](#q27--einsum-and-performance--trace-and-outer-product) | einsum and performance — trace and outer product | 🟡 |
| [Q28](#q28--einsum-and-performance--batch-matrix-multiply) | einsum and performance — batch matrix multiply | 🟡 |
| [Q29](#q29--einsum-and-performance--attention-scores) | einsum and performance — attention scores | 🟠 |
| [Q30](#q30--einsum-and-performance--optimizeTrue-and-path-precompute) | einsum and performance — optimize=True and path precompute | 🟠 |
| [Q31](#q31--io-and-memory--save-and-load-npy) | I/O and memory — save and load .npy | 🟢 |
| [Q32](#q32--io-and-memory--savez-multiple-arrays) | I/O and memory — savez multiple arrays | 🟡 |
| [Q33](#q33--io-and-memory--savetxt-and-loadtxt) | I/O and memory — savetxt and loadtxt | 🟡 |
| [Q34](#q34--io-and-memory--memmap-for-large-arrays) | I/O and memory — memmap for large arrays | 🟠 |
| [Q35](#q35--io-and-memory--cache-pattern-with-npz) | I/O and memory — cache pattern with npz | 🟠 |

Difficulty: 🟢 Basic / 🟡 Intermediate / 🟠 Advanced

---

### Q1 · dtype and precision — float32 vs float64 🟢

Create two arrays containing the values `[1.0, 2.0, 3.0]` — one as `float32` and one as `float64`. Print the `dtype`, `itemsize`, and `nbytes` for each. Confirm that `float32` uses half the memory of `float64`.

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `dtype=np.float32` and `dtype=np.float64` at creation. Check `.itemsize` (bytes per element) and `.nbytes` (total bytes).
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

arr32 = np.array([1.0, 2.0, 3.0], dtype=np.float32)
arr64 = np.array([1.0, 2.0, 3.0], dtype=np.float64)

print(arr32.dtype, arr32.itemsize, arr32.nbytes)   # float32  4  12
print(arr64.dtype, arr64.itemsize, arr64.nbytes)   # float64  8  24
```

**Why:** `float32` uses 4 bytes per element vs 8 for `float64`. For a million embedding vectors this difference is ~3 GB of RAM.
</details>

---

### Q2 · dtype and precision — inspecting memory 🟢

Create a `float32` array of shape `(1000, 768)` (typical embedding batch). Print its total size in megabytes. Then do the same for `float64` and `float16`. Confirm the 2x ratio between consecutive precisions.

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `.nbytes / 1e6` to convert bytes to megabytes.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

for dt in [np.float64, np.float32, np.float16]:
    arr = np.zeros((1000, 768), dtype=dt)
    print(f"{dt.__name__}: {arr.nbytes / 1e6:.2f} MB")
# float64: 6.14 MB
# float32: 3.07 MB
# float16: 1.54 MB
```

**Why:** Each halving of bit-width halves memory. At one million rows the difference is gigabytes.
</details>

---

### Q3 · dtype and precision — safe downcast pattern 🟡

You have a `float32` array with values ranging from -500 to 500. Write the safe downcast pattern using `np.finfo` and `np.can_cast` to decide whether it is safe to cast to `float16`. Then try an array with a value of 70000 and show what happens if you cast unsafely.

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `np.finfo(np.float16).max` to get the float16 ceiling (65504). Cast only when `arr.max() <= max_f16`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

arr = np.array([-500.0, 0.0, 500.0], dtype=np.float32)
MAX_F16 = np.finfo(np.float16).max   # 65504.0

if arr.max() <= MAX_F16 and arr.min() >= -MAX_F16:
    arr_f16 = arr.astype(np.float16)
    print("Cast safe:", arr_f16)
else:
    print("Values out of float16 range — keeping float32")

# Unsafe example — silent overflow:
bad = np.float16(70000)   # ← inf, no error raised
print("Unsafe cast:", bad)  # inf
```

**Why:** `float16` silently produces `inf` for values above 65504. Always query `np.finfo` before downcasting in production pipelines.
</details>

---

### Q4 · dtype and precision — astype and overflow 🟡

Create an array `[1.5, 2.7, 3.9]` as `float32`. Cast it to `int32` and observe what happens to the decimal parts. Also demonstrate `np.can_cast(np.float32, np.float16)` and `np.can_cast(np.int32, np.int64)`.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`astype(np.int32)` truncates — it does not round. `np.can_cast` returns True/False for safe casts.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

arr = np.array([1.5, 2.7, 3.9], dtype=np.float32)
print(arr.astype(np.int32))   # [1 2 3] — truncated, not rounded

print(np.can_cast(np.float32, np.float16))  # False — range/precision loss
print(np.can_cast(np.int32,   np.int64))    # True  — safe upcast
print(np.can_cast(np.float32, np.float64))  # True  — safe upcast
```

**Why:** `astype` truncates floats to integers — 1.9 becomes 1. `np.can_cast` is the pre-flight check before any downcast.
</details>

---

### Q5 · dtype and precision — AI pipeline dtypes 🟡

Write code showing three dtype decisions from a real AI pipeline: (a) a boolean attention mask for a batch of 4 sequences of length 8, (b) token IDs for a vocabulary of 100k tokens as `int32`, and (c) the store-small / compute-big pattern — store embeddings as `float16` but upcast to `float32` before computing cosine similarity.

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Boolean mask uses `dtype=np.bool_`. Upcast with `.astype(np.float32)` before the dot product. `np.dot` on float16 loses precision.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

# (a) Boolean attention mask
mask = np.ones((4, 8), dtype=np.bool_)
mask[0, 6:] = False   # last 2 positions are padding
print(mask.dtype, mask.nbytes)   # bool  32 bytes (vs 128 for int32)

# (b) Token IDs — int32 covers all vocab sizes up to ~2 billion
token_ids = np.array([101, 2023, 2003, 102], dtype=np.int32)

# (c) Store small, compute big
stored = np.random.default_rng(0).standard_normal((5, 128)).astype(np.float16)
a32 = stored[0].astype(np.float32)   # upcast for computation
b32 = stored[1].astype(np.float32)
sim = np.dot(a32, b32) / (np.linalg.norm(a32) * np.linalg.norm(b32))
print(f"Cosine sim: {sim:.4f}")
```

**Why:** `bool_` uses 1 byte vs 4 for `int32` — a 32x saving for attention masks. Always upcast float16 before dot products to avoid precision loss.
</details>

---

### Q6 · views and copies — identify view or copy 🟢

Given `a = np.arange(10)`, create `b = a[2:7]` and `c = a[[2, 4, 6]]`. For each: (1) check `.base` to determine view vs copy, (2) mutate the first element, and (3) print `a` to confirm whether it changed.

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Slicing returns a view (`b.base is a` → True). Fancy indexing returns a copy (`c.base is None`).
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

a = np.arange(10)

b = a[2:7]         # slice — view
print(b.base is a) # True
b[0] = 99
print(a)           # [0 1 99 3 4 5 6 7 8 9] — a changed

a = np.arange(10)  # reset
c = a[[2, 4, 6]]   # fancy indexing — copy
print(c.base)      # None
c[0] = 99
print(a)           # unchanged
```

**Why:** Slicing is O(1) — NumPy just creates a new descriptor pointing at the same buffer. Fancy indexing must gather non-contiguous values, so it always allocates a new array.
</details>

---

### Q7 · views and copies — .base attribute 🟢

Create a chain: `a = np.arange(12)`, `b = a[::2]` (every other element), `c = b[1:]` (drop first). Check `c.base is a` and `c.base is b`. What does this tell you about multi-level view chains?

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`.base` always chains back to the original owner, skipping intermediate views.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

a = np.arange(12)
b = a[::2]    # view of a — elements 0,2,4,6,8,10
c = b[1:]     # view of b — but c.base is a, not b

print(c.base is a)  # True — traces back to root owner
print(c.base is b)  # False — b is not the root
```

**Why:** NumPy always traces `.base` back to the original owner. Intermediate views are not stored in the chain — only the root allocation matters.
</details>

---

### Q8 · views and copies — accidental mutation fix 🟡

The function below silently modifies the caller's array. Identify the bug, then write two fixed versions: one using a non-in-place operator, one copying at the start.

```python
def normalize(arr):
    arr /= arr.max()
    return arr
```

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`/=` is an in-place operator — it modifies the array's buffer. Use `arr / arr.max()` (creates a new array) or `arr = arr.copy(); arr /= arr.max()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

# Bug: /= mutates in-place. If caller passed a view, caller's data changes.
data = np.array([1.0, 2.0, 4.0, 8.0])
subset = data[1:3]   # view
normalize_bug = lambda arr: (arr.__itruediv__(arr.max()), arr)[1]

# Fix 1: non-in-place operator (creates new array)
def normalize_safe(arr):
    return arr / arr.max()   # ← new array, caller untouched

# Fix 2: explicit copy at start
def normalize_copy(arr):
    arr = arr.copy()
    arr /= arr.max()
    return arr

data2 = np.array([1.0, 2.0, 4.0, 8.0])
result = normalize_safe(data2[1:3])
print(data2)   # unchanged: [1. 2. 4. 8.]
```

**Why:** In-place operators (`/=`, `*=`, `+=`) modify the underlying buffer regardless of whether the array is a view. This is the most common view-related bug in numerical code.
</details>

---

### Q9 · views and copies — writeable flag and memory layout 🟠

Create a 2D `float64` array `a` of shape `(3, 4)`. Check its `C_CONTIGUOUS` and `F_CONTIGUOUS` flags. Then take `a.T` and check again. Explain why `a.T` is not C-contiguous. Finally, create a C-contiguous copy of `a.T` using `np.ascontiguousarray` and verify.

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`.T` returns a view with swapped strides — no data is moved, so the memory layout does not change. `np.ascontiguousarray` creates a new C-order allocation.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

a = np.zeros((3, 4), dtype=np.float64)
print(a.flags['C_CONTIGUOUS'])      # True  — rows are contiguous
print(a.flags['F_CONTIGUOUS'])      # False

t = a.T
print(t.flags['C_CONTIGUOUS'])      # False — transpose just swaps strides
print(t.flags['F_CONTIGUOUS'])      # True  — column-major view of a

t_c = np.ascontiguousarray(t)       # fresh C-contiguous allocation
print(t_c.flags['C_CONTIGUOUS'])    # True
print(t_c.base is None)             # True — owns its data (copy, not view)

# Strides show the byte step per axis
print(a.strides)    # (32, 8) — 32 bytes to next row, 8 bytes to next col
print(t.strides)    # (8, 32) — transposed: column step is now fast
```

**Why:** Transpose is O(1) — it swaps strides, not data. BLAS routines and some C extensions require C-contiguous input; `np.ascontiguousarray` is the fix.
</details>

---

### Q10 · random and sampling — default_rng and reproducibility 🟢

Create two separate `default_rng` generators with seeds 0 and 99. Generate 5 floats from each. Show that calling them in any order does not affect the other generator's sequence (isolated state). Then confirm the same seed always produces the same output.

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.random.default_rng(seed)` creates an isolated generator. Each instance has completely independent state.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng_a = np.random.default_rng(seed=0)
rng_b = np.random.default_rng(seed=99)

a1 = rng_a.random(5)
_ = rng_b.random(100)   # consume 100 values from b — should not affect a
a2 = rng_a.random(5)    # continues from where rng_a left off, unaffected by rng_b

# Reproducibility: same seed always gives same sequence
rng_check = np.random.default_rng(seed=0)
a_repro = rng_check.random(5)
print(np.allclose(a1, a_repro))  # True — same seed, same output
```

**Why:** Unlike the old `np.random.seed()` global, `default_rng` gives each generator its own isolated state. This prevents cross-contamination between training shuffles, weight initialisation, and data augmentation.
</details>

---

### Q11 · random and sampling — integers and normal 🟢

Using `rng = np.random.default_rng(42)`, generate: (a) 50 random class labels in [0, 10), (b) weight initialisation values for a layer with `fan_in=512, fan_out=256` using He init (normal with `std = sqrt(2/fan_in)`), and (c) a dropout mask (80% keep rate) using `binomial`.

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `rng.integers(low, high, size)`, `rng.normal(loc, scale, size)`, and `rng.binomial(n=1, p=keep_rate, size)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(42)

# (a) Class labels
labels = rng.integers(low=0, high=10, size=(50,))
print("Labels sample:", labels[:5])

# (b) He weight init
fan_in, fan_out = 512, 256
std = np.sqrt(2.0 / fan_in)
weights = rng.normal(loc=0.0, scale=std, size=(fan_in, fan_out))
print(f"Weights shape: {weights.shape}, std: {weights.std():.4f}")

# (c) Dropout mask (1=keep, 0=drop)
mask = rng.binomial(n=1, p=0.8, size=(100,))
print(f"Keep rate: {mask.mean():.2f}")  # approx 0.80
```

**Why:** He initialisation (`std = sqrt(2/fan_in)`) is designed for ReLU layers. `binomial(n=1, p)` is an exact Bernoulli draw — the right tool for dropout masks.
</details>

---

### Q12 · random and sampling — choice with and without replacement 🟡

Given a population array `[10, 20, 30, 40, 50, 60, 70, 80]`, demonstrate: (a) sampling 4 elements without replacement, (b) sampling 10 elements with replacement (showing repeats are possible), and (c) weighted sampling where the first two elements are 5x more likely than the rest.

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`rng.choice(population, size, replace=False/True, p=weights)`. Weights must sum to 1.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(5)
pop = np.array([10, 20, 30, 40, 50, 60, 70, 80])

# (a) Without replacement — each element at most once
s1 = rng.choice(pop, size=4, replace=False)
print("No replace:", s1)

# (b) With replacement — repeats allowed
s2 = rng.choice(pop, size=10, replace=True)
print("With replace:", s2)

# (c) Weighted — 10 and 20 appear far more often
w = np.array([0.3, 0.3, 0.05, 0.05, 0.1, 0.1, 0.05, 0.05])
s3 = rng.choice(pop, size=20, replace=True, p=w)
print("Weighted:", s3)
```

**Why:** Bootstrap sampling (ensemble methods) uses `replace=True`. Weighted sampling models prior-biased draws. The key difference: without replacement guarantees each element appears at most once.
</details>

---

### Q13 · random and sampling — shuffle paired arrays 🟡

You have `X` (10 samples × 2 features) and `y` (10 labels). Show the wrong way to shuffle (independently, breaking pairing), then the correct way using a shared index permutation. Verify the pairing is preserved after the correct shuffle.

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Use `rng.permutation(len(y))` to get a shuffled index array, then apply it to both `X` and `y` with fancy indexing.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(7)
X = np.arange(20).reshape(10, 2)  # each row: [2i, 2i+1]
y = np.arange(10)                  # y[i] = i

# WRONG — shuffle independently, breaks X[i] ↔ y[i] pairing
# rng.shuffle(X); rng.shuffle(y)  ← DO NOT do this

# CORRECT — shared index permutation
idx = rng.permutation(len(y))
X_shuffled = X[idx]
y_shuffled = y[idx]

# Verify: X_shuffled[i][0] should always be 2 * y_shuffled[i]
for xi, yi in zip(X_shuffled[:5], y_shuffled[:5]):
    assert xi[0] == 2 * yi, "Pairing broken!"
print("Pairing preserved.")
```

**Why:** Shuffling X and y independently is one of the most common and painful bugs in ML code — the model silently trains on mismatched (features, label) pairs with no error message.
</details>

---

### Q14 · conditional operations — np.where ReLU 🟢

Implement ReLU two ways: (a) using `np.where(x > 0, x, 0)` and (b) using `np.maximum(x, 0)`. Apply both to `x = np.array([-2.0, 1.5, -0.3, 0.0, 4.0])`. Confirm results match and explain which is preferred.

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.maximum` is the preferred ReLU — it is self-documenting and avoids the eager branch evaluation issue in `np.where`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

x = np.array([-2.0, 1.5, -0.3, 0.0, 4.0])

relu_where = np.where(x > 0, x, 0)          # works but evaluates both branches
relu_max   = np.maximum(x, 0)               # preferred — clean and idiomatic

print(relu_where)   # [0.  1.5 0.  0.  4. ]
print(relu_max)     # [0.  1.5 0.  0.  4. ]
print(np.allclose(relu_where, relu_max))   # True
```

**Why:** `np.where(cond, A, B)` evaluates both `A` and `B` as full arrays before applying the condition. For `np.where(denom != 0, num/denom, 0)` this still computes `num/denom` everywhere, causing division-by-zero. `np.maximum(x, 0)` has no such issue.
</details>

---

### Q15 · conditional operations — np.select multi-branch 🟡

Given a scores array `[45, 72, 88, 55, 93, 60]`, use `np.select` to assign letter grades: A (≥90), B (≥70), C (≥50), else F. Then do the same for class confidence labels: high_conf (≥0.8), medium_conf (≥0.5), low_conf (≥0.3), else very_low.

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.select(conditions, choices, default)` evaluates conditions in order — first match wins, like an if/elif chain.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

scores = np.array([45, 72, 88, 55, 93, 60])
grades = np.select(
    [scores >= 90, scores >= 70, scores >= 50],
    ['A', 'B', 'C'],
    default='F'
)
print(grades)  # ['F' 'B' 'B' 'C' 'A' 'C']

probs = np.array([0.05, 0.45, 0.72, 0.91, 0.38])
labels = np.select(
    [probs >= 0.8, probs >= 0.5, probs >= 0.3],
    ['high_conf', 'medium_conf', 'low_conf'],
    default='very_low'
)
print(labels)  # ['very_low' 'low_conf' 'medium_conf' 'high_conf' 'low_conf']
```

**Why:** `np.select` is the vectorized if/elif/else for more than two outcomes. The first matching condition wins — order matters.
</details>

---

### Q16 · conditional operations — np.clip safe cross-entropy 🟡

Implement stable binary cross-entropy loss. The trap: `log(0)` produces `-inf`, breaking training. Use `np.clip` to keep probabilities in `(1e-7, 1 - 1e-7)`, then compute loss. Also demonstrate gradient clipping by capping a gradient array at `[-1.0, 1.0]`.

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.clip(probs, 1e-7, 1 - 1e-7)` prevents zeros and ones. Then `-np.log(clipped)` is always finite.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

# Cross-entropy: clip to avoid log(0) = -inf
probs = np.array([0.0, 0.3, 1.0, 0.7])
safe_probs = np.clip(probs, 1e-7, 1 - 1e-7)
loss = -np.log(safe_probs)
print(loss)   # finite values — no -inf

# Gradient clipping: prevent exploding gradients
grads = np.array([-5.0, 0.2, 8.3, -1.1, 0.7])
clipped_grads = np.clip(grads, -1.0, 1.0)
print(clipped_grads)   # [-1.   0.2  1.  -1.   0.7]
```

**Why:** `log(0) = -inf` produces NaN gradients and kills training. `np.clip` is the standard guard. Gradient clipping (capping gradient magnitude) prevents the exploding gradient problem in RNNs and deep networks.
</details>

---

### Q17 · conditional operations — safe divide pattern 🟠

Implement safe element-wise division that avoids `inf`/`NaN` when the denominator is zero, using the double `np.where` pattern (no Python loop, fully vectorized). Test with `num = [1, 2, 3, 4]`, `denom = [0, 2, 0, 4]`. Result should be `[0, 1, 0, 1]`.

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

<details>
<summary>💡 Hint</summary>
First use `np.where(denom != 0, denom, 1)` to make a safe denominator, then use `np.where(denom != 0, num / safe_denom, 0.0)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

numerator   = np.array([1.0, 2.0, 3.0, 4.0])
denominator = np.array([0.0, 2.0, 0.0, 4.0])

# Step 1: replace zeros in denominator with 1 (temporary — prevents div/0)
safe_denom = np.where(denominator != 0, denominator, 1)
# Step 2: divide, but output 0 wherever denominator was 0
result = np.where(denominator != 0, numerator / safe_denom, 0.0)
print(result)   # [0. 1. 0. 1.]
```

**Why:** `np.where(cond, A, B)` evaluates both `A` and `B` eagerly. Without step 1, `numerator / denominator` computes the division for all elements first (including the zeros), generating `inf`. The double-`where` trick avoids this while staying fully vectorized.
</details>

---

### Q18 · statistics and distributions — percentile and IQR 🟢

Generate 10,000 samples from an exponential distribution (scale=2.0, seed=42). Compute: the median, IQR (Q75 - Q25), the five-number summary, and identify outliers using Tukey fences (Q1 - 1.5×IQR, Q3 + 1.5×IQR).

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.percentile(data, [25, 50, 75])` returns all three at once. Tukey fences: lower = Q1 - 1.5×IQR, upper = Q3 + 1.5×IQR.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(42)
data = rng.exponential(scale=2.0, size=10000)

p25, p50, p75 = np.percentile(data, [25, 50, 75])
iqr = p75 - p25

summary = np.percentile(data, [0, 25, 50, 75, 100])
print(f"Five-number summary: {summary.round(3)}")

lower_fence = p25 - 1.5 * iqr
upper_fence = p75 + 1.5 * iqr
outliers = data[(data < lower_fence) | (data > upper_fence)]
print(f"Outlier count: {len(outliers)} ({len(outliers)/len(data)*100:.1f}%)")
```

**Why:** Percentiles expose skewed distributions where the mean is misleading (e.g. P99 latency spikes). IQR-based outlier detection is distribution-free — it works for skewed data where standard deviation would under- or over-count.
</details>

---

### Q19 · statistics and distributions — nan-safe functions 🟡

Create an array `[1.0, 2.0, np.nan, 4.0, np.nan, 6.0]`. Show what happens when you call `np.mean` on it (NaN propagation). Then use `np.nanmean`, `np.nanstd`, and `np.nanpercentile` to get results that ignore NaNs. Finally, check with `np.isnan` and `np.isfinite`.

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.mean` with any NaN returns NaN. `np.nanmean` skips NaN positions. `np.isnan(arr).sum()` counts NaN occurrences.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

arr = np.array([1.0, 2.0, np.nan, 4.0, np.nan, 6.0])

print(np.mean(arr))       # nan — propagates
print(np.nanmean(arr))    # 3.25 — ignores NaN
print(np.nanstd(arr))     # ~1.92
print(np.nanpercentile(arr, 50))  # 3.0

print(np.isnan(arr).sum())     # 2 — count of NaN
print(np.isfinite(arr).all())  # False — not all finite
```

**Why:** NaN propagation is silent — a single corrupted value poisons the entire computation. Always run `np.isnan(X).any()` at pipeline entry points to catch data quality issues early.
</details>

---

### Q20 · statistics and distributions — histogram bins 🟡

Generate 10,000 samples from a standard normal distribution (seed=0). Compute a 50-bin histogram and extract bin centers. Then compute a normalised density histogram (`density=True`) and verify it integrates to approximately 1.0. Show the 2D histogram signature for two correlated features.

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.histogram` returns `(counts, bin_edges)` — note there is one more edge than count. Bin centers = `(edges[:-1] + edges[1:]) / 2`. Density integrates to 1: `(density * bin_width).sum() ≈ 1.0`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(0)
data = rng.standard_normal(10000)

counts, edges = np.histogram(data, bins=50)
centers = (edges[:-1] + edges[1:]) / 2   # midpoint of each bin

density, d_edges = np.histogram(data, bins=50, density=True)
bin_width = d_edges[1] - d_edges[0]
print(f"Density integrates to: {(density * bin_width).sum():.4f}")  # ~1.0

# 2D histogram for correlated features
x = rng.normal(0, 1, 5000)
y = x * 0.8 + rng.normal(0, 0.6, 5000)
H, xedges, yedges = np.histogram2d(x, y, bins=20)
print(f"2D histogram shape: {H.shape}")  # (20, 20)
```

**Why:** `density=True` converts raw counts to a probability density — useful for overlaying a theoretical distribution. Note `bin_edges` has `n_bins + 1` values; forgetting this causes off-by-one errors.
</details>

---

### Q21 · statistics and distributions — correlation matrix 🟠

Create three features: `x1` (500 normal samples), `x2 = x1 * 0.9 + noise` (highly correlated with x1), and `x3` (independent normal). Compute the Pearson correlation matrix with `np.corrcoef`. Extract the upper-triangle correlations with `np.triu_indices`. Flag any pair with |corr| > 0.8.

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.corrcoef` expects shape `(n_vars, n_observations)` — use `np.vstack`. `np.triu_indices(n, k=1)` gives upper-triangle indices excluding the diagonal.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(3)
x1 = rng.normal(0, 1, 500)
x2 = x1 * 0.9 + rng.normal(0, 0.44, 500)
x3 = rng.normal(0, 1, 500)

features = np.vstack([x1, x2, x3])   # shape (3, 500)
corr = np.corrcoef(features)         # shape (3, 3)
print(corr.round(3))

# Upper triangle (exclude diagonal)
idx = np.triu_indices(3, k=1)
for i, j in zip(*idx):
    if abs(corr[i, j]) > 0.8:
        print(f"High correlation: features {i} and {j}: {corr[i,j]:.3f}")
```

**Why:** Features with correlation > 0.95 add no new information — keeping both wastes compute and can destabilise gradient descent. The correlation matrix is the first audit to run on any new feature set.
</details>

---

### Q22 · linear algebra — matmul vs dot 🟢

Explain and demonstrate the difference between `np.dot`, `np.matmul` (`@`), and `np.einsum("ij,jk->ik", A, B)` for 2D matrix multiplication. Use `A` of shape `(3, 4)` and `B` of shape `(4, 5)`. Confirm all three give the same result. Then show how `np.dot` behaves differently for higher-dimensional arrays.

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

<details>
<summary>💡 Hint</summary>
For 2D arrays all three are equivalent. For 3D, `np.matmul` does batch multiply while `np.dot` does something more complex (sum over last axis of first and second-to-last of second).
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(0)
A = rng.normal(0, 1, (3, 4))
B = rng.normal(0, 1, (4, 5))

r1 = np.dot(A, B)
r2 = np.matmul(A, B)        # same as A @ B
r3 = np.einsum("ij,jk->ik", A, B)

print(np.allclose(r1, r2))  # True
print(np.allclose(r1, r3))  # True

# For 3D: matmul is batch matmul; dot is more complex
C3 = rng.normal(0, 1, (2, 3, 4))
D3 = rng.normal(0, 1, (2, 4, 5))
print(np.matmul(C3, D3).shape)  # (2, 3, 5) — batch matmul
# np.dot(C3, D3) would give shape (2, 3, 2, 5) — NOT batch matmul
```

**Why:** Use `@` for 2D matrix multiply (clean, Pythonic). Use `np.einsum` for batch or multi-head operations. Avoid `np.dot` for arrays with more than 2 dimensions — the semantics are confusing.
</details>

---

### Q23 · linear algebra — solve linear system 🟡

Solve the system `Ax = b` where `A = [[3, 1], [1, 2]]` and `b = [9, 8]` using `np.linalg.solve`. Verify the solution by computing `A @ x` and checking it matches `b`. Also compute `det(A)` and explain what a zero determinant would mean.

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.linalg.solve(A, b)` is numerically stable (uses LU decomposition). If `det(A) ≈ 0`, the matrix is singular and the system has no unique solution.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

A = np.array([[3.0, 1.0],
              [1.0, 2.0]])
b = np.array([9.0, 8.0])

x = np.linalg.solve(A, b)
print(f"Solution: x = {x}")          # [2. 3.5]? Verify:
print(np.allclose(A @ x, b))         # True

det = np.linalg.det(A)
print(f"det(A) = {det:.2f}")         # 5.0 — non-zero, invertible

# Near-singular matrix
B = np.array([[1.0, 2.0], [2.0, 4.0]])  # row 2 = 2 * row 1
print(f"det(B) ≈ {np.linalg.det(B):.6f}")  # ≈ 0.0 — singular
```

**Why:** A determinant of zero means the matrix is singular — it squashes some dimension to zero, and the inverse does not exist. This corresponds to a system of equations with no unique solution (either no solution or infinitely many).
</details>

---

### Q24 · linear algebra — SVD and low-rank approximation 🟠

Create a `(50, 10)` matrix `A`. Compute the full SVD with `np.linalg.svd`. Reconstruct `A` from `U`, `s`, `Vt` and verify with `np.allclose`. Then build a rank-3 approximation and print the percentage of variance explained by the top 3 singular values.

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.linalg.svd(A, full_matrices=False)` returns economy SVD. Reconstruction: `U @ np.diag(s) @ Vt`. Explained variance: `(s[:k]**2).sum() / (s**2).sum()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(0)
A = rng.normal(0, 1, (50, 10))

U, s, Vt = np.linalg.svd(A, full_matrices=False)
# U: (50, 10)  s: (10,)  Vt: (10, 10)

A_reconstructed = U @ np.diag(s) @ Vt
print(np.allclose(A, A_reconstructed))   # True

# Rank-3 approximation
k = 3
A_lowrank = U[:, :k] @ np.diag(s[:k]) @ Vt[:k, :]
var_explained = (s[:k]**2).sum() / (s**2).sum()
print(f"Top-{k} explain {var_explained*100:.1f}% of variance")
```

**Why:** SVD is the backbone of PCA, recommendation systems, and dimensionality reduction. The explained variance ratio tells you how much information is retained by the low-rank approximation.
</details>

---

### Q25 · linear algebra — lstsq regression 🟠

Generate 100 training samples with 3 features plus a bias column. True weights are `[0, 2.0, -1.5, 0.8]` (bias + 3 feature weights). Solve with `np.linalg.lstsq`. Print recovered weights and compare to true weights. Explain why `lstsq` is preferred over computing `(XᵀX)⁻¹ Xᵀy` directly.

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Add a bias column of ones with `np.column_stack([np.ones(n), X_raw])`. `lstsq` uses SVD internally and handles ill-conditioned matrices gracefully.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(42)
X_raw = rng.normal(0, 1, (100, 3))
true_w = np.array([2.0, -1.5, 0.8])
y = X_raw @ true_w + rng.normal(0, 0.1, 100)

X = np.column_stack([np.ones(100), X_raw])  # add bias column

w, residuals, rank, sv = np.linalg.lstsq(X, y, rcond=None)
print(f"Recovered: {w[1:].round(3)}")   # close to [2.0, -1.5, 0.8]
print(f"Bias:      {w[0]:.4f}")
print(f"Rank:      {rank}")
```

**Why:** Directly inverting `XᵀX` fails silently when features are correlated (ill-conditioned matrix). `lstsq` uses SVD which degrades gracefully, returning the minimum-norm solution rather than garbage.
</details>

---

### Q26 · einsum and performance — basic notation 🟢

Use `np.einsum` to perform: (a) dot product of two 1D vectors `a` and `b`, (b) matrix multiplication of `A (3×4)` and `B (4×5)`, (c) transpose of `A`. For each, verify against the equivalent NumPy function (`np.dot`, `@`, `.T`).

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Dot product: `"i,i->"` (scalar output — no output index). Matmul: `"ij,jk->ik"`. Transpose: `"ij->ji"`. Index that disappears from output gets summed.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(0)
a = rng.normal(0, 1, (4,))
b = rng.normal(0, 1, (4,))
A = rng.normal(0, 1, (3, 4))
B = rng.normal(0, 1, (4, 5))

# (a) Dot product — no output index means scalar sum
dot_ein = np.einsum("i,i->", a, b)
print(np.isclose(dot_ein, np.dot(a, b)))   # True

# (b) Matrix multiply
C_ein = np.einsum("ij,jk->ik", A, B)
print(np.allclose(C_ein, A @ B))           # True

# (c) Transpose
At_ein = np.einsum("ij->ji", A)
print(np.allclose(At_ein, A.T))            # True
```

**Why:** Learning einsum notation unlocks the ability to read and write complex tensor operations in PyTorch and TensorFlow, not just NumPy. The rule: any index absent from the output gets summed.
</details>

---

### Q27 · einsum and performance — trace and outer product 🟡

Use `np.einsum` to compute: (a) the trace of a 4×4 matrix (sum of diagonal), (b) the outer product of two vectors of length 4, and (c) element-wise (Hadamard) product of two 3×4 matrices. Verify all three against NumPy equivalents.

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)

<details>
<summary>💡 Hint</summary>
Trace: `"ii->"` (same index on both axes, scalar output). Outer product: `"i,j->ij"` (no contraction). Hadamard: `"ij,ij->ij"` (same indices in, same out).
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(1)
M = rng.normal(0, 1, (4, 4))
a = rng.normal(0, 1, (4,))
b = rng.normal(0, 1, (4,))
A = rng.normal(0, 1, (3, 4))
B = rng.normal(0, 1, (3, 4))

# (a) Trace
trace_ein = np.einsum("ii->", M)
print(np.isclose(trace_ein, np.trace(M)))   # True

# (b) Outer product
outer_ein = np.einsum("i,j->ij", a, b)
print(np.allclose(outer_ein, np.outer(a, b)))   # True

# (c) Hadamard product
had_ein = np.einsum("ij,ij->ij", A, B)
print(np.allclose(had_ein, A * B))              # True
```

**Why:** These patterns cover a majority of tensor operations. Once you see how `ii->` means "only diagonal elements" and `i,j->ij` means "no contraction", you can construct almost any tensor expression.
</details>

---

### Q28 · einsum and performance — batch matrix multiply 🟡

Implement batch matrix multiply for 32 pairs of matrices: `A_batch (32, 64, 128)` and `B_batch (32, 128, 64)`. Use `np.einsum("bmk,bkn->bmn", ...)` and verify it matches `np.matmul(A_batch, B_batch)`. Explain which index gets contracted and which is preserved.

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`b` is the batch index (preserved), `k` is the contracted dimension, `m` and `n` are the output matrix dimensions.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(0)
A_b = rng.normal(0, 1, (32, 64, 128))
B_b = rng.normal(0, 1, (32, 128, 64))

# b=batch (preserved), k=contracted, m and n=output dims
C_ein = np.einsum("bmk,bkn->bmn", A_b, B_b)   # shape (32, 64, 64)
C_np  = np.matmul(A_b, B_b)

print(C_ein.shape)                   # (32, 64, 64)
print(np.allclose(C_ein, C_np))      # True
```

**Why:** Batch matrix multiply is the most common einsum in deep learning — it is the core computation in multi-head attention. `k` disappears from the output because all values along that axis are summed (contracted).
</details>

---

### Q29 · einsum and performance — attention scores 🟠

Implement the first step of scaled dot-product attention: compute attention scores for `Q` and `K` of shape `(batch=2, heads=4, seq=16, head_dim=32)`. Use einsum `"bhqd,bhkd->bhqk"` to get scores of shape `(2, 4, 16, 16)`. Scale by `1/sqrt(head_dim)` and verify output shape.

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`"bhqd,bhkd->bhqk"` — `b` and `h` are preserved (batch, heads), `d` is contracted (head_dim), `q` and `k` are query and key positions (both appear in output).
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(42)
B, H, S, D = 2, 4, 16, 32
Q = rng.normal(0, 1, (B, H, S, D))
K = rng.normal(0, 1, (B, H, S, D))

# "bhqd,bhkd->bhqk": for each (b,h), compute q×k dot products over head_dim d
scores = np.einsum("bhqd,bhkd->bhqk", Q, K)
scores = scores / np.sqrt(D)   # ← scale to prevent softmax saturation

print(scores.shape)   # (2, 4, 16, 16) — each of 2 batches, 4 heads, 16q x 16k
```

**Why:** This single einsum replaces a nested loop over batch and head dimensions. The `d` axis (head_dim) is contracted because attention scores are dot products — they sum over the embedding dimension.
</details>

---

### Q30 · einsum and performance — optimize=True and path precompute 🟠

Compare einsum with and without `optimize=True` for a chain of three matrices: `A (100×200)`, `B (200×300)`, `C (300×50)`. Then demonstrate precomputing the contraction path with `np.einsum_path` and reusing it in a loop of 100 iterations.

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.einsum_path("ij,jk,kl->il", A, B, C, optimize="optimal")` returns `(path, description)`. Reuse the path as `optimize=path` in repeated calls.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(0)
A = rng.normal(0, 1, (100, 200))
B = rng.normal(0, 1, (200, 300))
C = rng.normal(0, 1, (300, 50))

# Without optimization
r1 = np.einsum("ij,jk,kl->il", A, B, C)

# With optimization — finds best contraction order
r2 = np.einsum("ij,jk,kl->il", A, B, C, optimize=True)
print(np.allclose(r1, r2))   # True — same result

# Precompute path for hot loops
path, info = np.einsum_path("ij,jk,kl->il", A, B, C, optimize="optimal")
print(info)

for _ in range(100):
    result = np.einsum("ij,jk,kl->il", A, B, C, optimize=path)
```

**Why:** For three-matrix contractions, the order of operations dramatically affects FLOP count (associativity). Precomputing the path avoids re-deriving it on every call — important in training loops where the same einsum runs thousands of times.
</details>

---

### Q31 · I/O and memory — save and load .npy 🟢

Create a `float32` array of shape `(1000, 128)`. Save it to `test_embeddings.npy` with `np.save`. Load it back and verify shape, dtype, and values match. Also demonstrate `allow_pickle=False` for safer loading of untrusted files.

> 🛠️ **Solve locally:** [practice_local.py → Q31](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.save("path.npy", arr)` creates the file. `np.load("path.npy")` loads it. `allow_pickle=False` prevents arbitrary Python code execution from malicious `.npy` files.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(0)
embeddings = rng.standard_normal((1000, 128)).astype(np.float32)

np.save("/tmp/test_embeddings.npy", embeddings)

loaded = np.load("/tmp/test_embeddings.npy", allow_pickle=False)
print(loaded.shape)                          # (1000, 128)
print(loaded.dtype)                          # float32
print(np.allclose(embeddings, loaded))       # True
```

**Why:** `.npy` stores exact binary — dtype, shape, byte order, and raw data — with zero precision loss. Reload is measured in milliseconds even for 1GB arrays.
</details>

---

### Q32 · I/O and memory — savez multiple arrays 🟡

Save four arrays (`X_train`, `y_train`, `X_val`, `y_val`) in a single `.npz` archive. Load it back using both direct access and a context manager. Show `archive.files` to list stored array names. Then show `savez_compressed` and explain the trade-off.

> 🛠️ **Solve locally:** [practice_local.py → Q32](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.savez("file.npz", name1=arr1, name2=arr2)` uses keyword arguments as names. Load returns an `NpzFile` lazy object — arrays are loaded on access. Always close with `archive.close()` or use a context manager.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(1)
X_train = rng.normal(0, 1, (1000, 64)).astype(np.float32)
y_train = rng.integers(0, 10, 1000)
X_val   = rng.normal(0, 1, (200, 64)).astype(np.float32)
y_val   = rng.integers(0, 10, 200)

# Save multiple arrays — uncompressed (fast)
np.savez("/tmp/dataset.npz", X_train=X_train, y_train=y_train,
                              X_val=X_val,   y_val=y_val)

# Context manager — arrays copied before close
with np.load("/tmp/dataset.npz") as archive:
    print(archive.files)          # ['X_train', 'y_train', 'X_val', 'y_val']
    Xt = archive["X_train"]
    yt = archive["y_train"]

# Compressed — smaller file, slower I/O
np.savez_compressed("/tmp/dataset_c.npz", X_train=X_train, y_train=y_train,
                                           X_val=X_val, y_val=y_val)
```

**Why:** `.npz` keeps related arrays together in one file handle, one filename, and one `load` call. Compressed saves 30-60% disk space but adds CPU cost on every read/write — good for archiving, bad for hot training loops.
</details>

---

### Q33 · I/O and memory — savetxt and loadtxt 🟡

Save a `(3, 4)` float array as a CSV with `np.savetxt` (comma delimiter, 4 decimal places, with a header). Load it back with `np.loadtxt` (skip header row). Also show `np.genfromtxt` with a missing value filled as 0.0.

> 🛠️ **Solve locally:** [practice_local.py → Q33](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`comments=""` in `savetxt` removes the `#` prefix from the header. Use `skiprows=1` in `loadtxt` to skip the header. `genfromtxt` handles missing values with `filling_values`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

data = np.array([[1.1, 2.2, 3.3, 4.4],
                 [5.5, 6.6, 7.7, 8.8],
                 [9.9, 10.1, 11.1, 12.1]])

np.savetxt("/tmp/data.csv", data, delimiter=",", fmt="%.4f",
           header="a,b,c,d", comments="")

loaded = np.loadtxt("/tmp/data.csv", delimiter=",", skiprows=1)
print(np.allclose(data, loaded))   # True

# genfromtxt for missing values
data2 = np.genfromtxt("/tmp/data.csv", delimiter=",",
                       skip_header=1, filling_values=0.0)
print(data2.shape)   # (3, 4)
```

**Why:** Text formats are 5-10x slower than binary `.npy` and use more disk space. Use them only for interoperability (handing results to R, Excel, or Kaggle submissions).
</details>

---

### Q34 · I/O and memory — memmap for large arrays 🟠

Create a `np.memmap` file at `/tmp/large.dat` with shape `(100000, 128)` of `float32` in write mode. Write random data in chunks of 10000 rows. Then open it in read mode, access one row and a batch of 1000 rows. Explain what "copy-on-write" mode (`"c"`) does.

> 🛠️ **Solve locally:** [practice_local.py → Q34](./practice_local.py)

<details>
<summary>💡 Hint</summary>
`np.memmap(path, dtype, mode="w+", shape)` creates the file. After writing, `fp.flush(); del fp` flushes and releases. Reopen with `mode="r"` for reading. Sorting batch indices improves sequential disk access.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

rng = np.random.default_rng(0)
N, D = 100_000, 128

# Create and write in chunks
fp = np.memmap("/tmp/large.dat", dtype=np.float32, mode="w+", shape=(N, D))
chunk = 10_000
for i in range(0, N, chunk):
    fp[i:i+chunk] = rng.normal(0, 1, (chunk, D))
fp.flush()
del fp   # release mapping

# Read — only requested pages loaded from disk
fp_r = np.memmap("/tmp/large.dat", dtype=np.float32, mode="r", shape=(N, D))
row_0    = fp_r[0]          # loads 1 row (512 bytes)
batch    = np.array(fp_r[0:1000])   # explicit copy for computation
print(f"Row 0 mean: {row_0.mean():.4f}")

# "c" mode: reads from disk, writes stay in RAM (disk unchanged)
fp_cow = np.memmap("/tmp/large.dat", dtype=np.float32, mode="c", shape=(N, D))
fp_cow[0, :] = 999.0   # in RAM only — file on disk unchanged
```

**Why:** memmap is the solution for arrays that exceed available RAM (40GB genomics datasets, large embedding corpora). The OS loads only the pages you touch. "c" mode is useful for read-heavy workloads where you need temporary in-memory modifications without corrupting the source file.
</details>

---

### Q35 · I/O and memory — cache pattern with npz 🟠

Implement a cache-or-compute function that: on first run, generates a `float32` feature matrix of shape `(5000, 512)` and labels (simulating expensive preprocessing) and saves them to `features_cache.npz`; on subsequent runs, loads from the cache. Use `os.path.exists` to check. Add a cache-hit message and verify loaded shapes.

> 🛠️ **Solve locally:** [practice_local.py → Q35](./practice_local.py)

<details>
<summary>💡 Hint</summary>
This is the standard "preprocess once, reload fast" pattern. Use `np.savez` for the cache and `with np.load(...) as cache:` to load safely.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
import os

cache_path = "/tmp/features_cache.npz"

def get_features():
    if not os.path.exists(cache_path):
        print("Cache miss — running preprocessing...")
        rng = np.random.default_rng(0)
        X = rng.normal(0, 1, (5000, 512)).astype(np.float32)
        y = rng.integers(0, 100, size=5000)
        np.savez(cache_path, X=X, y=y)
        print(f"Saved to {cache_path}")
    else:
        print("Cache hit — loading from disk...")

    with np.load(cache_path) as cache:
        return cache["X"], cache["y"]

X, y = get_features()   # first run: computes + saves
X, y = get_features()   # second run: loads from cache
print(f"X: {X.shape} {X.dtype}")   # (5000, 512) float32
print(f"y: {y.shape}")             # (5000,)
```

**Why:** This pattern is ubiquitous in ML pipelines — BERT embeddings, audio spectrograms, and image features take hours to compute. Caching them with `.npz` reduces re-run time from hours to milliseconds.
</details>

---

**[Back to README](./README.md)** | [Cheatsheet](./cheetsheet.md) | [Interview Q&A](./interview.md)
