# 🎯 NumPy dtypes and Precision — Memory, Speed, and ML

A factory stores inventory in different container sizes — some items need a 64-litre drum, others fit in an 8-litre bucket. Using the wrong container wastes shelf space or causes overflow. **NumPy dtypes** are the same idea: every element in an array gets stored in a container of a fixed size, and choosing the right container size directly affects memory usage, computation speed, and numerical stability.

---

## 🗂️ Section 1: What is a dtype?

Think of a dtype as a stamp on every slot in an array: "this slot holds a 32-bit floating-point number." That stamp controls three things at once — the kind of number, the number of bits used to represent it, and therefore the memory consumed per element.

Every NumPy array carries exactly one **dtype** (data type descriptor) shared by all its elements. Mixed types inside one array are not allowed — that is what Python lists are for.

| dtype | bits | range / precision | common use case |
|---|---|---|---|
| `float64` | 64 | default Python float | general computation, prototyping |
| `float32` | 32 | ±3.4×10³⁸, ~7 sig. digits | GPU training, ML models |
| `float16` | 16 | ±65504, ~3 sig. digits | inference, mixed-precision training |
| `int64` | 64 | ±9.2×10¹⁸ | large indices, timestamps |
| `int32` | 32 | ±2.1×10⁹ | token IDs, class labels |
| `int8` | 8 | -128 to 127 | quantized model weights |
| `bool` | 1 (stored as 1 byte) | True / False | attention masks, boolean filters |

---

## 🔬 Section 2: Creating arrays with specific dtypes

When you let NumPy infer the dtype from Python literals, it defaults to `float64` for floats and `int64` for integers on most platforms — the safest choices, but not always the most efficient.

You can declare the container size upfront, the same way a warehouse manager specifies which bin size to requisition before stock arrives.

```python
import numpy as np

arr = np.array([1.0, 2.0, 3.0], dtype=np.float32)  # ← explicit dtype at creation
arr = np.zeros((1000, 768), dtype=np.float32)        # ← 3 MB instead of 6 MB for float64

arr.dtype      # dtype('float32')   ← confirm the dtype
arr.itemsize   # 4                  ← bytes per single element
arr.nbytes     # total bytes = itemsize × number of elements
```

Key attributes for inspecting memory:

- `arr.dtype` — the dtype object (readable label + size info)
- `arr.itemsize` — bytes for a single element
- `arr.nbytes` — total bytes consumed by the array buffer

---

## 🔄 Section 3: Casting dtypes

Casting is changing the container after the fact — like transferring goods from a large drum into smaller cans. Moving to a larger container (**upcasting**) is safe: no information is lost. Moving to a smaller container (**downcasting**) risks overflow or precision loss.

```python
arr = np.array([1.5, 2.7], dtype=np.float32)

arr_f64 = arr.astype(np.float64)   # ← upcast: safe, gains precision headroom
arr_f16 = arr.astype(np.float16)   # ← downcast: may lose precision, possible overflow
arr_int = arr.astype(np.int32)     # ← truncates decimal: 1.5 → 1, 2.7 → 2

# Check cast safety before committing:
np.can_cast(np.float32, np.float16)    # False — range and precision may be lost
np.can_cast(np.float32, np.float64)    # True  — safe upcast
np.can_cast(np.int32,   np.int64)      # True  — safe upcast
```

`np.can_cast` is your pre-flight checklist: query it before any downcast in production code.

---

## ⚖️ Section 4: float16 vs float32 vs float64 — real ML impact

The choice of float precision in ML is a trade-off between three resources: memory, compute speed, and numerical stability. Think of it as choosing between a high-resolution photograph (float64), a standard digital photo (float32), and a compressed thumbnail (float16).

**float64** — the default in pure Python and NumPy. Most precise, but doubles memory vs float32 and is slower on modern GPUs that are optimised for 32-bit or 16-bit operations.

**float32** — the workhorse of ML training. PyTorch and TensorFlow default to float32 on GPU. Half the memory of float64 with sufficient precision for gradient descent.

**float16** — used in inference and mixed-precision training (e.g. `torch.cuda.amp`). Quarter the memory of float64. The limited range (max ~65504) means gradient values can overflow during training without careful loss scaling.

**int8** — used for quantized inference (LLM quantization via GPTQ, AWQ, bitsandbytes). Weights are stored as 8-bit integers, reducing a float32 model to one quarter its size at the cost of some accuracy.

Memory comparison for one million 768-dimension embeddings (a common vector store scenario):

```python
# 1 million embedding vectors of dimension 768
embeddings_f64 = np.zeros((1_000_000, 768), dtype=np.float64)  # ← ~6.1 GB
embeddings_f32 = np.zeros((1_000_000, 768), dtype=np.float32)  # ← ~3.0 GB
embeddings_f16 = np.zeros((1_000_000, 768), dtype=np.float16)  # ← ~1.5 GB
```

Halving dtype precision halves memory — that is often the difference between fitting a workload in RAM or spilling to disk.

---

## ⚠️ Section 5: Overflow and precision loss — the silent danger

Overflow is the factory container analogy made literal: you try to pour 70,000 litres into a drum rated for 65,504 litres, and the result is not an error — it silently becomes infinity. This is one of the most dangerous failure modes in ML pipelines because the code keeps running and produces garbage results.

```python
x = np.float16(70000)    # ← inf! float16 max is 65504 — silent overflow
x = np.float16(0.0001)   # ← 9.999e-05 (rounds, but stays finite)
x = np.float16(1e-8)     # ← 0.0 — underflow, rounds to zero

# Query the safe range before casting:
info = np.finfo(np.float16)
info.max   # 65504.0
info.min   # -65504.0
info.eps   # 0.000977 — smallest representable difference from 1.0

# Safe downcast pattern:
MAX_F16 = np.finfo(np.float16).max
if arr.max() <= MAX_F16 and arr.min() >= -MAX_F16:
    arr = arr.astype(np.float16)   # ← only cast when range is safe
else:
    print("Values out of float16 range — keeping float32")
```

Use `np.finfo` for float types and `np.iinfo` for integer types to inspect range limits before any downcast.

---

## 🤖 Section 6: dtype in AI workflows

Different components of an AI pipeline have different dtype requirements, just as different departments in a factory use different container standards.

**Attention masks** — use `bool` dtype. A boolean mask stores True/False per token. Using `int32` for the same data wastes 32× more memory per element.

```python
mask = np.ones((batch_size, seq_len), dtype=np.bool_)   # ← 1 byte per element
mask[padding_positions] = False                           # ← mark padding tokens
```

**Token IDs** — use `int32`. GPT-4's vocabulary has ~100,000 tokens, well within int32's range of ±2.1 billion. Using int64 doubles memory for no benefit.

```python
token_ids = np.array(tokenizer.encode(text), dtype=np.int32)   # ← sufficient for all vocab sizes
```

**Model weights** — `float32` for training (full precision gradients), `int8` for quantized inference (post-training quantization).

**Embeddings** — store in `float16` to minimise index size, but load and compute similarity in `float32` to avoid precision loss in dot products.

```python
# Real use: load embeddings in float16 for storage, compute in float32 for accuracy
stored_embeddings = np.load("embeddings.npy").astype(np.float16)  # ← ~1.5 GB for 1M vectors

def cosine_similarity(a, b):
    a32 = a.astype(np.float32)   # ← upcast before computation
    b32 = b.astype(np.float32)
    return np.dot(a32, b32) / (np.linalg.norm(a32) * np.linalg.norm(b32))
```

The pattern — store small, compute with enough precision — is the same trade-off a financial system makes when archiving compressed records but loading them fully before calculations.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⬅️ Prev Topic | [theory.md](./README.md) |
| ➡️ Next Topic | [02_views_and_copies.md](./02_views_and_copies.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
