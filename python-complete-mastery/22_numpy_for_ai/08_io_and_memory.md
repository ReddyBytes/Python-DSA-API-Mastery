# 🎯 I/O and Memory — Saving, Loading, and Working with Large Arrays

> An array that lives only in RAM dies when your process does. `np.save` is the difference between losing hours of computation and picking up exactly where you left off.

---

## Why NumPy I/O Matters

You've just computed BERT embeddings for 2 million documents — that took 4 hours on a GPU. Tomorrow you run the same pipeline again and it takes 4 hours again because you didn't save them. `np.save` would have made the reload take 2 seconds. NumPy's native formats — `.npy` and `.npz` — store arrays exactly as they are in memory, with full precision and shape metadata, and reload them in milliseconds.

---

## Saving and Loading Single Arrays — `.npy`

You ran inference on a test set of 50,000 images and need to save the feature vectors for downstream experiments. One `np.save` call, one 147MB file, and every future script loads in under a second.

The **`.npy` format** is a binary file that stores exactly one array: its dtype, shape, byte-order, and raw data. It is the fastest way to persist a NumPy array to disk.

```python
import numpy as np

rng = np.random.default_rng(0)
embeddings = rng.normal(0, 1, size=(50000, 768)).astype(np.float32)
# 50k embeddings, BERT-style — 50000 * 768 * 4 bytes ≈ 147 MB

# Save — creates embeddings.npy
np.save("embeddings.npy", embeddings)

# Load — returns the exact same array
loaded = np.load("embeddings.npy")
print(loaded.shape)             # (50000, 768)
print(loaded.dtype)             # float32
print(np.allclose(embeddings, loaded))  # True

# allow_pickle=False is safer for untrusted files (default is True in older NumPy)
loaded_safe = np.load("embeddings.npy", allow_pickle=False)
```

The `.npy` file stores a small header (128 bytes) with format version, dtype string, and shape tuple, followed by the raw array bytes. No compression — pure speed.

---

## Saving Multiple Arrays — `.npz`

Your training pipeline produces features, labels, and split indices — three separate arrays that always travel together. Saving them as three `.npy` files means three file handles, three load calls, and three places to get the filenames wrong. `.npz` keeps them in one archive.

**`.npz`** is a ZIP archive containing multiple `.npy` files. Use it when you need to save a group of related arrays together — training data, labels, metadata — in a single file.

```python
rng = np.random.default_rng(1)
X_train = rng.normal(0, 1, (10000, 64)).astype(np.float32)
y_train = rng.integers(0, 10, size=10000)
X_val   = rng.normal(0, 1, (2000, 64)).astype(np.float32)
y_val   = rng.integers(0, 10, size=2000)

# Save uncompressed — fast, larger file
np.savez("dataset.npz", X_train=X_train, y_train=y_train,
                         X_val=X_val,   y_val=y_val)

# Save compressed — slower to write/read, smaller file (good for archiving)
np.savez_compressed("dataset_compressed.npz",
                    X_train=X_train, y_train=y_train,
                    X_val=X_val,     y_val=y_val)

# Load — returns a lazy NpzFile object (arrays not loaded until accessed)
archive = np.load("dataset.npz")
print(archive.files)                        # ['X_train', 'y_train', 'X_val', 'y_val']
X = archive["X_train"]                     # ← loaded on demand
y = archive["y_train"]
archive.close()                             # ← important: release file handle

# Context manager — safer pattern
with np.load("dataset.npz") as archive:
    X_train_loaded = archive["X_train"]    # ← copy made before close
    y_train_loaded = archive["y_train"]
# archive is closed here — but the arrays are already in memory
```

---

## Saving Text Arrays — `savetxt` / `loadtxt`

You need to hand off results to a colleague who uses R, or submit predictions to a Kaggle competition that requires a CSV. Binary formats won't help here — text format is the universal handshake.

Use text format only when you need human-readable output or interoperability with tools that cannot read `.npy`. It is 5-10x slower and uses more disk space.

```python
data = np.array([[1.1, 2.2, 3.3],
                 [4.4, 5.5, 6.6]])

# Save as CSV-style text
np.savetxt("data.csv", data, delimiter=",", fmt="%.4f",
           header="col1,col2,col3", comments="")   # ← comments="" removes '#' prefix

# Load
data_loaded = np.loadtxt("data.csv", delimiter=",", skiprows=1)  # ← skip header row
print(data_loaded)

# For large CSVs, np.genfromtxt handles missing values
data_with_missing = np.genfromtxt("data.csv", delimiter=",",
                                  skip_header=1,
                                  filling_values=0.0)   # ← fill NaN positions
```

---

## Memory-Mapped Files — `np.memmap`

You have a 40GB dataset of audio spectrograms. Your machine has 16GB of RAM. Loading it all would crash the process — but you only need 256 rows at a time for each training batch. A **memory-mapped file** (`memmap`) is the solution to the "my dataset is larger than RAM" problem. Instead of loading the entire array into memory, NumPy maps the file into virtual address space. You can read and write any slice — the OS loads only the pages you actually touch.

Think of it as a file that pretends to be an array: you index it like an array, but the data lives on disk and flows into RAM only as needed.

```python
# Create a large memmap file (does NOT load into RAM)
fp = np.memmap("large_array.dat", dtype=np.float32, mode="w+",
               shape=(1_000_000, 256))  # ← 1M rows × 256 cols ≈ 1 GB on disk

# Write data in chunks (only this chunk is in RAM at a time)
chunk_size = 10000
for i in range(0, 1_000_000, chunk_size):
    fp[i : i + chunk_size] = rng.normal(0, 1, (chunk_size, 256))

# Flush writes to disk
fp.flush()
del fp   # ← release the mapping
```

```python
# Open existing memmap for reading (no RAM for full array)
fp = np.memmap("large_array.dat", dtype=np.float32, mode="r",
               shape=(1_000_000, 256))

# Access any slice — OS loads only those pages
row_100 = fp[100]          # ← loads 1 row (1 KB) from disk
batch   = fp[0:1000]       # ← loads 1000 rows (1 MB) into RAM
print(f"Row 100 mean: {row_100.mean():.4f}")

# Slices are still memmap objects — operations on them materialize into RAM
batch_copy = np.array(batch)   # ← explicit copy to regular RAM array if needed
```

**Mode options for `np.memmap`:**

| Mode | Behavior |
|---|---|
| `"r"` | Read-only. File must exist. |
| `"r+"` | Read-write. File must exist. Changes written to disk. |
| `"w+"` | Read-write. Creates/overwrites file. |
| `"c"` | Copy-on-write. Reads from disk; writes stay in RAM only. |

---

## Memmap for Mini-Batch Training

The canonical use case: you have 10M training samples that don't fit in RAM, stored in a memmap file. At each step you draw a batch index and access only those rows.

```python
# Assume large_embeddings.dat exists from a preprocessing step
N = 1_000_000
D = 128

# Open without loading
X_mmap = np.memmap("large_embeddings.dat", dtype=np.float32,
                   mode="r", shape=(N, D))

batch_size = 256
n_batches = N // batch_size

batch_rng = np.random.default_rng(42)

for step in range(100):   # simulated training steps
    # Draw random batch indices
    idx = batch_rng.integers(0, N, size=batch_size)
    idx_sorted = np.sort(idx)             # ← sorting indices improves sequential disk access

    # Load only this batch into RAM
    X_batch = np.array(X_mmap[idx_sorted])   # ← np.array forces materialization
    # ... compute loss, gradients, update weights

X_mmap._mmap.close()   # ← explicitly close the mapping when done
```

---

## Comparing Formats — When to Use What

| Format | Speed | File Size | Use Case |
|---|---|---|---|
| `.npy` | Fastest | Large (no compression) | Single arrays, fast reload |
| `.npz` (uncompressed) | Fast | Large | Multiple arrays, fast reload |
| `.npz_compressed` | Slow write/read | Small | Archiving, distributing |
| `.csv` / `.txt` | Slowest | Largest | Human-readable, interop |
| `memmap` | Instant open, paged reads | Same as `.npy` | Arrays larger than RAM |

---

## Practical: Caching Preprocessed Features

A real-world pattern: preprocess once, cache, reload instantly in subsequent runs.

```python
import os

cache_path = "features_cache.npz"

if not os.path.exists(cache_path):
    print("Cache miss — running preprocessing...")
    # ... expensive feature extraction
    X = rng.normal(0, 1, (50000, 512)).astype(np.float32)   # placeholder
    y = rng.integers(0, 100, size=50000)
    np.savez(cache_path, X=X, y=y)
    print(f"Saved to {cache_path}")
else:
    print("Cache hit — loading from disk...")
    with np.load(cache_path) as cache:
        X = cache["X"]      # ← sub-millisecond for typical research datasets
        y = cache["y"]
    print(f"Loaded: X={X.shape}, y={y.shape}")
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Module Home | [theory.md](./README.md) |
| Random and Sampling | [03_random_and_sampling.md](./03_random_and_sampling.md) |
| Linear Algebra (Advanced) | [06_linear_algebra_advanced.md](./06_linear_algebra_advanced.md) |
| Einsum and Performance | [07_einsum_and_performance.md](./07_einsum_and_performance.md) |
| Statistics and Distributions | [05_statistics_and_distributions.md](./05_statistics_and_distributions.md) |
