# 🔢 NumPy for AI

---

You're working on a RAG system.

You have 10,000 document embeddings — each is a list of 1536 numbers. You need to find which documents are most similar to a user's query. With plain Python lists, comparing one query to 10,000 documents takes 3 seconds. With NumPy, it takes 3 milliseconds. That's the difference between a usable product and a broken one. NumPy is how AI actually runs fast.

This module teaches you NumPy from scratch — not as a math library, but as the engine behind every embedding, every neural network, and every similarity search you will ever build.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Array creation · Indexing and slicing · Broadcasting · Vectorized operations · `np.array` dtype · `reshape` / `flatten`

**Should Learn** — Important for real projects, comes up regularly:
Linear algebra (`np.linalg`) · `np.random` · Boolean indexing · Fancy indexing · `np.where` / `np.select` · Memory layout (C vs F order)

**Good to Know** — Useful in specific situations:
`np.einsum` · Stride tricks · Masked arrays · `np.memmap` for large files · Structured arrays

**Reference** — Know it exists, look up when needed:
FFT (`np.fft`) · Custom ufuncs · `nditer` · Array interface protocol · `numexpr`

---

## 1️⃣ What is NumPy and Why AI Needs It

NumPy stands for Numerical Python.

It is a library for working with arrays of numbers.

That sounds boring. Here's why it isn't.

Every AI model — GPT, Stable Diffusion, a recommendation engine — stores its data as giant tables of numbers. Weight matrices. Embedding vectors. Activation maps. All of it is just numbers in arrays.

The question is: how fast can you work with those numbers?

**Python lists are slow for numbers.**

```python
# Python list — slow
a = [1.0, 2.0, 3.0, 4.0]
b = [5.0, 6.0, 7.0, 8.0]

# Add them element-by-element
result = [a[i] + b[i] for i in range(len(a))]
```

For 4 elements: fine.
For 1,536,000 elements: catastrophic.

**Why Python lists are slow:**

- Each number in a Python list is a full Python object with overhead.
- A Python `int` is not just 4 bytes — it carries type info, reference count, etc. About 28 bytes per number.
- A list of a million floats occupies ~8 MB just for pointers, plus millions of individual objects.
- Operations require a Python loop, which hits the interpreter overhead on every step.

**Why NumPy arrays are fast:**

- All elements are the same type, stored in a single contiguous block of memory.
- A NumPy array of a million float32 values occupies exactly 4 MB.
- Operations are implemented in C and FORTRAN, running outside the Python interpreter.
- One NumPy call does what a million Python iterations would do.

```python
import numpy as np

a = np.array([1.0, 2.0, 3.0, 4.0])
b = np.array([5.0, 6.0, 7.0, 8.0])

result = a + b  # No loop. Runs in C. Blazing fast.
print(result)   # [6. 8. 10. 12.]
```

**Memory comparison:**

```python
import sys
import numpy as np

py_list = list(range(1_000_000))
np_array = np.arange(1_000_000)

print(sys.getsizeof(py_list))          # ~8 MB for pointers alone
print(np_array.nbytes)                 # 4 MB (int32) or 8 MB (int64)
```

For AI work, NumPy is not optional. It is the foundation.

---

## 2️⃣ Creating Arrays

There are many ways to create NumPy arrays. Each has its purpose.

**From a Python list:**

```python
import numpy as np

v = np.array([1, 2, 3, 4, 5])
print(v)         # [1 2 3 4 5]
print(v.dtype)   # int64
```

**Specify dtype explicitly (important for memory in AI):**

```python
v = np.array([1.0, 2.0, 3.0], dtype=np.float32)
print(v.dtype)   # float32  — uses 4 bytes instead of 8
```

AI models almost always use `float32`. GPT embeddings from OpenAI come as `float32`. Using `float64` doubles your memory for no benefit.

**All zeros (used to initialize weight matrices):**

```python
zeros = np.zeros((3, 4))       # 3 rows, 4 columns of 0.0
print(zeros)
# [[0. 0. 0. 0.]
#  [0. 0. 0. 0.]
#  [0. 0. 0. 0.]]
```

**All ones:**

```python
ones = np.ones((2, 3), dtype=np.float32)
print(ones)
# [[1. 1. 1.]
#  [1. 1. 1.]]
```

**Range of values (like Python's range):**

```python
r = np.arange(0, 10, 2)   # start, stop, step
print(r)   # [0 2 4 6 8]
```

**Evenly spaced values over an interval:**

```python
ls = np.linspace(0, 1, 5)   # 5 evenly spaced points from 0 to 1
print(ls)   # [0.   0.25 0.5  0.75 1.  ]
```

`linspace` is used when you need exactly N points between two values. Common in signal processing and plotting.

**Random arrays (used to initialize neural network weights):**

```python
rng = np.random.default_rng(seed=42)  # reproducible randomness

# Uniform random between 0 and 1
rand = rng.random((3, 3))

# Normal distribution (Gaussian) — most common for weight init
normal = rng.standard_normal((3, 3))

# Random integers
ints = rng.integers(0, 10, size=(2, 5))
```

Always use `np.random.default_rng(seed=...)` for reproducible experiments. The old `np.random.seed()` is global state — messy in real projects.

**Identity matrix (used in linear algebra):**

```python
eye = np.eye(4)   # 4x4 identity matrix
```

---

## 3️⃣ Array Shapes and Dimensions

This is where beginners get confused. Take your time here.

An array's **shape** tells you how many elements it has in each dimension.

**1D array — a vector:**

```python
v = np.array([1, 2, 3, 4])
print(v.shape)   # (4,)
print(v.ndim)    # 1
```

In AI: a single embedding is a 1D vector. `text-embedding-3-small` from OpenAI gives you shape `(1536,)`.

**2D array — a matrix:**

```python
m = np.array([[1, 2, 3],
              [4, 5, 6]])
print(m.shape)   # (2, 3)  — 2 rows, 3 columns
print(m.ndim)    # 2
```

In AI: a batch of embeddings is a 2D matrix. 100 documents × 1536 dimensions = shape `(100, 1536)`.

**3D array — a batch of matrices:**

```python
t = np.zeros((32, 10, 512))
print(t.shape)   # (32, 10, 512)
print(t.ndim)    # 3
```

In AI: attention scores in a transformer. 32 batch size × 10 tokens × 512 dimensions.

**Shape vocabulary you must know:**

```python
arr = np.zeros((batch_size, seq_len, d_model))
#                   32         10      512

arr.shape[0]   # 32  — batch size
arr.shape[1]   # 10  — sequence length
arr.shape[-1]  # 512 — last dimension (feature size)
arr.size       # 32 * 10 * 512 = 163840 — total elements
arr.nbytes     # total bytes in memory
```

**Checking dtype and size together:**

```python
embeddings = np.random.standard_normal((10_000, 1536)).astype(np.float32)
print(embeddings.shape)   # (10000, 1536)
print(embeddings.dtype)   # float32
print(embeddings.nbytes / 1e6, "MB")   # ~61 MB
```

---

## 4️⃣ Indexing and Slicing

**Basic indexing — works like Python lists:**

```python
v = np.array([10, 20, 30, 40, 50])

v[0]     # 10
v[-1]    # 50
v[1:4]   # [20 30 40]
v[::-1]  # [50 40 30 20 10]
```

**2D indexing:**

```python
m = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

m[0, 0]    # 1  — row 0, col 0
m[1, 2]    # 6  — row 1, col 2
m[0]       # [1 2 3]  — entire row 0
m[:, 1]    # [2 5 8]  — entire column 1
m[0:2, 1:3]  # [[2 3] [5 6]] — submatrix
```

**Boolean indexing — extremely useful for filtering:**

```python
scores = np.array([0.2, 0.8, 0.6, 0.1, 0.9])

# Which scores are above threshold?
mask = scores > 0.5
print(mask)    # [False  True  True False  True]

# Get only those values
print(scores[mask])   # [0.8 0.6 0.9]

# One-liner
print(scores[scores > 0.5])   # [0.8 0.6 0.9]
```

In AI: filtering similarity scores above a threshold, finding all tokens above attention threshold.

**Fancy indexing — select by index list:**

```python
arr = np.array([100, 200, 300, 400, 500])

indices = [0, 2, 4]
print(arr[indices])   # [100 300 500]
```

In AI: selecting top-k document indices after argsort.

```python
similarities = np.array([0.3, 0.9, 0.1, 0.7, 0.8])

# Get indices of top 3
top_k_indices = np.argsort(similarities)[-3:][::-1]
print(top_k_indices)           # [1 4 3]
print(similarities[top_k_indices])   # [0.9 0.8 0.7]
```

---

## 5️⃣ Broadcasting

This is NumPy's most powerful concept. Read it twice.

Broadcasting lets NumPy apply operations between arrays of different shapes — without copying data.

**Simple example — add scalar to array:**

```python
a = np.array([1, 2, 3])
result = a + 10
print(result)   # [11 12 13]
```

NumPy did not loop. It understood: "add 10 to every element."

**Add a row vector to a matrix:**

```python
m = np.array([[1, 2, 3],
              [4, 5, 6]])   # shape (2, 3)

bias = np.array([10, 20, 30])   # shape (3,)

result = m + bias
print(result)
# [[11 22 33]
#  [14 25 36]]
```

`bias` was broadcast across both rows automatically.

In AI: adding a bias vector to every sample in a batch. This is literally what a neural network layer does.

**The broadcasting rule:**

Two shapes are compatible if, going from right to left:
- The dimensions are equal, OR
- One of them is 1 (it gets stretched to match the other)

```python
# Shape (4, 1) + shape (1, 3) → broadcasts to (4, 3)
a = np.ones((4, 1))
b = np.ones((1, 3))
print((a + b).shape)   # (4, 3)
```

**Common AI use case — subtract mean embedding:**

```python
embeddings = np.random.standard_normal((100, 512))   # 100 documents

mean = embeddings.mean(axis=0)   # shape (512,)
normalized = embeddings - mean   # shape (100, 512) - (512,) → broadcasts correctly
```

Broadcasting is what makes "no loop" operations possible at scale.

---

## 6️⃣ Vectorized Operations

Vectorized means: apply the operation to the whole array at once, in C, without a Python loop.

**Element-wise arithmetic:**

```python
a = np.array([1.0, 2.0, 3.0])
b = np.array([4.0, 5.0, 6.0])

a + b    # [5. 7. 9.]
a * b    # [4. 10. 18.]
a ** 2   # [1. 4. 9.]
a / b    # [0.25  0.4  0.5]
```

**Math functions (all vectorized):**

```python
angles = np.array([0, np.pi/2, np.pi])

np.sin(angles)    # [0. 1. 0.]
np.cos(angles)    # [1. 0. -1.]
np.exp(angles)    # exponential of each element
np.log(angles + 1)  # natural log
np.sqrt(np.array([4., 9., 16.]))  # [2. 3. 4.]
```

**The softmax function — implemented with vectorized ops:**

```python
def softmax(x):
    e_x = np.exp(x - np.max(x))   # subtract max for numerical stability
    return e_x / e_x.sum()

logits = np.array([2.0, 1.0, 0.1])
probs = softmax(logits)
print(probs)           # [0.659 0.242 0.099]
print(probs.sum())     # 1.0
```

This is the softmax every transformer uses. Zero Python loops. Pure NumPy.

**Clip — useful for numerical stability:**

```python
values = np.array([-2.0, 0.5, 3.0, -1.5])
clipped = np.clip(values, 0, 1)
print(clipped)   # [0.  0.5 1.  0. ]
```

---

## 7️⃣ Matrix Operations

Matrix operations are the heart of AI. Every neural network layer is `output = input @ weights + bias`.

**Dot product — two vectors:**

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

dot = np.dot(a, b)
print(dot)   # 1*4 + 2*5 + 3*6 = 32
```

In AI: dot product measures how aligned two embedding vectors are.

**Matrix multiplication:**

```python
A = np.array([[1, 2],
              [3, 4]])   # shape (2, 2)

B = np.array([[5, 6],
              [7, 8]])   # shape (2, 2)

C = A @ B   # @ operator — matrix multiply
print(C)
# [[19 22]
#  [43 50]]

# Also valid:
C = np.matmul(A, B)
```

**A neural network forward pass:**

```python
# Input: batch of 4 samples, each with 3 features
X = np.random.standard_normal((4, 3))       # shape (4, 3)

# Weight matrix: 3 input features → 5 output neurons
W = np.random.standard_normal((3, 5))       # shape (3, 5)

# Bias: one per output neuron
b = np.zeros(5)                              # shape (5,)

output = X @ W + b   # shape (4, 5) — broadcasting adds bias to each row
```

That is literally a dense layer in a neural network.

**Transpose:**

```python
m = np.array([[1, 2, 3],
              [4, 5, 6]])   # shape (2, 3)

print(m.T)   # shape (3, 2)
# [[1 4]
#  [2 5]
#  [3 6]]
```

Transpose is used constantly — to align dimensions for matrix multiply.

**Why shapes must be compatible:**

- `(4, 3) @ (3, 5)` → OK, output is `(4, 5)`
- `(4, 3) @ (4, 5)` → ERROR — inner dimensions don't match
- Rule: `(m, k) @ (k, n)` → `(m, n)`

---

## 8️⃣ Aggregations

Aggregations collapse an array to a scalar or smaller array.

**Basic aggregations:**

```python
arr = np.array([[1, 2, 3],
                [4, 5, 6]])

np.sum(arr)      # 21 — total sum
np.mean(arr)     # 3.5 — average
np.min(arr)      # 1
np.max(arr)      # 6
np.std(arr)      # standard deviation
np.var(arr)      # variance
```

**The axis parameter — this trips up beginners:**

`axis=0` means "collapse rows, keep columns" — operates down each column.
`axis=1` means "collapse columns, keep rows" — operates across each row.

```python
arr = np.array([[1, 2, 3],
                [4, 5, 6]])

np.sum(arr, axis=0)   # [5 7 9]  — sum each column
np.sum(arr, axis=1)   # [6 15]   — sum each row

np.mean(arr, axis=0)  # [2.5 3.5 4.5] — mean of each column
np.mean(arr, axis=1)  # [2.  5. ]     — mean of each row
```

**In AI:** when you have a batch of embeddings with shape `(100, 1536)`, use `axis=0` to get the mean across documents, `axis=1` to get the mean per document.

**argmax and argmin — index of the extreme value:**

```python
scores = np.array([0.3, 0.9, 0.1, 0.7])

print(np.argmax(scores))   # 1  — index of highest score
print(np.argmin(scores))   # 2  — index of lowest score
```

In AI: argmax gives you the predicted class label.

**argsort — indices that would sort the array:**

```python
scores = np.array([0.3, 0.9, 0.1, 0.7])
order = np.argsort(scores)
print(order)               # [2 0 3 1]  — ascending

top_k = np.argsort(scores)[-3:][::-1]
print(top_k)               # [1 3 0]    — top 3 descending
```

---

## 9️⃣ Reshaping and Stacking

**reshape — change shape without changing data:**

```python
v = np.arange(12)         # shape (12,)
m = v.reshape((3, 4))     # shape (3, 4)
m = v.reshape((2, 2, 3))  # shape (2, 2, 3)

# Use -1 to let NumPy infer one dimension
m = v.reshape((3, -1))    # NumPy figures out columns: 12/3 = 4
```

**flatten — any array back to 1D:**

```python
m = np.array([[1, 2], [3, 4]])
flat = m.flatten()   # [1 2 3 4]
```

**ravel — same as flatten but may return a view (faster):**

```python
flat = m.ravel()
```

**concatenate — join arrays along existing axis:**

```python
a = np.array([[1, 2], [3, 4]])   # shape (2, 2)
b = np.array([[5, 6]])            # shape (1, 2)

c = np.concatenate([a, b], axis=0)   # stack vertically → (3, 2)
```

**vstack and hstack — shortcuts:**

```python
top = np.array([1, 2, 3])
bottom = np.array([4, 5, 6])

v = np.vstack([top, bottom])   # [[1 2 3] [4 5 6]]  shape (2, 3)
h = np.hstack([top, bottom])   # [1 2 3 4 5 6]      shape (6,)
```

**stack — create a new axis:**

```python
a = np.array([1, 2, 3])   # shape (3,)
b = np.array([4, 5, 6])   # shape (3,)

s = np.stack([a, b], axis=0)   # shape (2, 3)
s = np.stack([a, b], axis=1)   # shape (3, 2)
```

In AI: stacking individual embedding vectors into a matrix before batch processing.

**expand_dims — add a new axis:**

```python
v = np.array([1, 2, 3])   # shape (3,)
v2d = np.expand_dims(v, axis=0)   # shape (1, 3) — batch of one
```

---

## 🔟 Embeddings in NumPy

This is what you actually build with.

An embedding is a dense vector of floating point numbers that represents meaning. A sentence, a word, a product, a user — all can be represented as a vector.

**What a single embedding looks like:**

```python
# A fake 8-dimensional embedding for the word "apple"
embedding = np.array([0.21, -0.45, 0.13, 0.88, -0.12, 0.56, -0.77, 0.34])
print(embedding.shape)   # (8,)
print(embedding.dtype)   # float64
```

Real embeddings from OpenAI `text-embedding-3-small` have shape `(1536,)`.

**What a database of embeddings looks like:**

```python
# 1000 documents, each with a 1536-dimensional embedding
doc_embeddings = np.random.standard_normal((1000, 1536)).astype(np.float32)
print(doc_embeddings.shape)   # (1000, 1536)
```

**Cosine similarity from scratch:**

Cosine similarity measures the angle between two vectors. If two vectors point in exactly the same direction, similarity = 1. Opposite directions = -1. Perpendicular = 0.

```
cosine_similarity(a, b) = (a · b) / (||a|| * ||b||)
```

```python
def cosine_similarity(a, b):
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot / (norm_a * norm_b)

query = np.array([1.0, 0.0, 0.0])
doc   = np.array([0.8, 0.6, 0.0])

print(cosine_similarity(query, doc))   # 0.8
```

**A normalized vector — shortcut when working at scale:**

If you normalize all vectors to unit length first, cosine similarity becomes just a dot product. This is a major optimization.

```python
def normalize(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)

q_norm = normalize(query_embedding)         # shape (1536,)
d_norm = normalize(doc_embeddings)          # shape (1000, 1536)

# All cosine similarities at once — no loop
similarities = d_norm @ q_norm              # shape (1000,)
```

---

## 1️⃣1️⃣ np.linalg

`np.linalg` is NumPy's linear algebra module.

**Vector norm — the "length" of a vector:**

```python
v = np.array([3.0, 4.0])

np.linalg.norm(v)          # 5.0  — L2 norm (Euclidean distance)
np.linalg.norm(v, ord=1)   # 7.0  — L1 norm (Manhattan distance)
```

In AI: normalizing embeddings to unit vectors for cosine similarity.

**Dot product:**

```python
np.dot(a, b)   # same as a @ b for 1D vectors
```

**Solving a linear equation Ax = b:**

```python
A = np.array([[2, 1],
              [1, 3]])
b = np.array([5, 10])

x = np.linalg.solve(A, b)
print(x)   # [1. 3.]  — solution to the system
```

**Eigenvalues and eigenvectors (used in PCA):**

```python
M = np.array([[4, 2],
              [1, 3]])

eigenvalues, eigenvectors = np.linalg.eig(M)
```

**Singular Value Decomposition (SVD) — used in topic modeling:**

```python
U, S, Vt = np.linalg.svd(M)
```

**Matrix inverse:**

```python
inv_A = np.linalg.inv(A)
```

---

## 1️⃣2️⃣ Real AI Example: Cosine Similarity Search

You have 1000 document embeddings. A user sends a query. You need the top-5 most similar documents. No loops.

```python
import numpy as np
import time

# --- Setup ---
np.random.seed(42)
dim = 1536

# Simulate 1000 document embeddings
doc_embeddings = np.random.standard_normal((1000, dim)).astype(np.float32)

# Simulate one query embedding
query_embedding = np.random.standard_normal((dim,)).astype(np.float32)

# --- NumPy approach: vectorized, no loop ---
def cosine_search_numpy(query, docs, top_k=5):
    # Normalize query
    query_norm = query / np.linalg.norm(query)

    # Normalize all docs at once — shape (1000, 1536)
    doc_norms = np.linalg.norm(docs, axis=1, keepdims=True)   # shape (1000, 1)
    docs_normalized = docs / doc_norms                          # shape (1000, 1536)

    # Dot product of query with every doc — shape (1000,)
    similarities = docs_normalized @ query_norm

    # Get top-k indices (descending)
    top_k_indices = np.argsort(similarities)[-top_k:][::-1]
    top_k_scores  = similarities[top_k_indices]

    return top_k_indices, top_k_scores

# --- Plain Python loop approach ---
def cosine_search_loop(query, docs, top_k=5):
    def cos_sim(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    scores = [(i, cos_sim(query, docs[i])) for i in range(len(docs))]
    scores.sort(key=lambda x: x[1], reverse=True)
    top = scores[:top_k]
    return [i for i, _ in top], [s for _, s in top]

# --- Benchmark ---
start = time.perf_counter()
for _ in range(100):
    indices, scores = cosine_search_numpy(query_embedding, doc_embeddings)
numpy_time = (time.perf_counter() - start) / 100

start = time.perf_counter()
for _ in range(100):
    indices_loop, scores_loop = cosine_search_loop(query_embedding, doc_embeddings)
loop_time = (time.perf_counter() - start) / 100

print(f"NumPy  : {numpy_time * 1000:.3f} ms per query")
print(f"Loop   : {loop_time * 1000:.3f} ms per query")
print(f"Speedup: {loop_time / numpy_time:.1f}x")
print(f"Top-5 indices: {indices}")
print(f"Top-5 scores:  {scores.round(4)}")
```

This is the exact pattern used inside vector databases like Chroma, Pinecone, and Weaviate — before they add their index structures for even larger scale.

The NumPy version is typically 50–200x faster than the Python loop version, depending on hardware and array size.

---

## Summary

NumPy is not just a math library. It is the execution layer for AI workloads.

Every embedding, every weight matrix, every similarity score, every activation — all of it flows through NumPy-compatible arrays.

Once you understand:
- How arrays are shaped
- How broadcasting works
- How to use vectorized operations instead of loops
- How to use matrix multiply for batch operations

You can implement any AI algorithm from scratch, and you can understand what libraries like PyTorch and TensorFlow are doing under the hood. They are NumPy with gradients and GPU support.
## 🔁 Navigation

Previous: `21_typing_and_pydantic/theory.md`
Next: `23_pandas_for_ai/theory.md`

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Data Engineering Applications — Interview Q&A](../21_data_engineering_applications/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)

---

---

## 🗺️ NumPy Learning Path — Topic Files

Study these in order after completing this theory file:

| Order | Topic | File |
|---|---|---|
| 01 | dtypes, float16 vs float32, int8 quantization | [01_dtype_and_precision.md](./01_dtype_and_precision.md) |
| 02 | Views vs copies — the #1 source of silent bugs | [02_views_and_copies.md](./02_views_and_copies.md) |
| 03 | Random number generation, seeding, sampling, weight init | [03_random_and_sampling.md](./03_random_and_sampling.md) |
| 04 | Conditional ops: `np.where`, `np.select`, `np.clip` | [04_conditional_operations.md](./04_conditional_operations.md) |
| 05 | Percentiles, quantiles, histograms, correlation, covariance | [05_statistics_and_distributions.md](./05_statistics_and_distributions.md) |
| 06 | Least squares, QR decomposition, condition number, SVD | [06_linear_algebra_advanced.md](./06_linear_algebra_advanced.md) |
| 07 | `np.einsum`, batch matmul, Transformer attention, performance | [07_einsum_and_performance.md](./07_einsum_and_performance.md) |
| 08 | `.npy`/`.npz` save/load, memory-mapped files for large arrays | [08_io_and_memory.md](./08_io_and_memory.md) |
