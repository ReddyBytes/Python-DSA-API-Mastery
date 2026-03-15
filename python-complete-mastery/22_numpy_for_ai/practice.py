# Practice: NumPy for AI

import numpy as np
import time

# ============================================================
# SECTION 1: Array Creation
# ============================================================

print("=" * 50)
print("SECTION 1: Array Creation")
print("=" * 50)

# From a Python list
v = np.array([1, 2, 3, 4, 5])
print("From list:", v)
print("dtype:", v.dtype)

# Specify float32 — what AI models use
v_f32 = np.array([1.0, 2.0, 3.0], dtype=np.float32)
print("float32 array:", v_f32, "dtype:", v_f32.dtype)

# All zeros and ones
zeros = np.zeros((3, 4))
ones  = np.ones((2, 3))
print("zeros shape:", zeros.shape)
print("ones shape:", ones.shape)

# arange and linspace
r = np.arange(0, 10, 2)
ls = np.linspace(0, 1, 5)
print("arange:", r)
print("linspace:", ls)

# Random arrays — reproducible
rng = np.random.default_rng(seed=42)
rand_uniform = rng.random((3, 3))
rand_normal  = rng.standard_normal((3, 3))
print("Uniform random shape:", rand_uniform.shape)
print("Normal random shape:", rand_normal.shape)

# ============================================================
# SECTION 2: Shapes and Dimensions
# ============================================================

print("\n" + "=" * 50)
print("SECTION 2: Shapes and Dimensions")
print("=" * 50)

# 1D — single embedding vector
embedding = np.random.standard_normal(1536).astype(np.float32)
print("Single embedding shape:", embedding.shape)    # (1536,)
print("Single embedding dtype:", embedding.dtype)

# 2D — batch of embeddings (100 documents)
batch = np.random.standard_normal((100, 1536)).astype(np.float32)
print("Batch embeddings shape:", batch.shape)        # (100, 1536)
print("Memory (MB):", batch.nbytes / 1e6)

# 3D — batch of attention matrices
attention = np.zeros((32, 10, 512), dtype=np.float32)
print("Attention tensor shape:", attention.shape)    # (32, 10, 512)
print("ndim:", attention.ndim)

# ============================================================
# SECTION 3: Indexing and Slicing
# ============================================================

print("\n" + "=" * 50)
print("SECTION 3: Indexing and Slicing")
print("=" * 50)

scores = np.array([0.1, 0.8, 0.3, 0.9, 0.5, 0.2])

# Basic
print("scores[0]:", scores[0])         # 0.1
print("scores[-1]:", scores[-1])       # 0.2
print("scores[1:4]:", scores[1:4])     # [0.8 0.3 0.9]

# 2D
m = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

print("m[0]:", m[0])           # [1 2 3] — row 0
print("m[:, 1]:", m[:, 1])     # [2 5 8] — col 1
print("m[0:2, 1:3]:", m[0:2, 1:3])  # submatrix

# Boolean indexing — filter above threshold
above = scores[scores > 0.5]
print("Scores above 0.5:", above)

# Top-k with argsort
top3_indices = np.argsort(scores)[-3:][::-1]
print("Top-3 indices:", top3_indices)
print("Top-3 values:", scores[top3_indices])

# ============================================================
# SECTION 4: Broadcasting Demo
# ============================================================

print("\n" + "=" * 50)
print("SECTION 4: Broadcasting")
print("=" * 50)

# Scalar broadcast
arr = np.array([1.0, 2.0, 3.0, 4.0])
print("arr + 10:", arr + 10)            # [11. 12. 13. 14.]

# Row vector broadcast across matrix
m = np.ones((4, 3))
bias = np.array([10, 20, 30])           # shape (3,)
result = m + bias                        # broadcast: (4,3) + (3,) → (4,3)
print("matrix + row vector:")
print(result)

# Normalize a batch of embeddings (subtract mean, divide by std)
fake_embeddings = rng.standard_normal((10, 5))
mean_vec = fake_embeddings.mean(axis=0)   # shape (5,) — mean per dimension
std_vec  = fake_embeddings.std(axis=0)    # shape (5,)
normalized = (fake_embeddings - mean_vec) / std_vec   # broadcasting both ops
print("Normalized embeddings mean (should be ~0):", normalized.mean(axis=0).round(10))

# ============================================================
# SECTION 5: Matrix Multiply — Neural Network Layer
# ============================================================

print("\n" + "=" * 50)
print("SECTION 5: Matrix Multiply")
print("=" * 50)

# Simulate a dense layer: output = input @ weights + bias
batch_size    = 4
input_features  = 3
output_features = 5

X = rng.standard_normal((batch_size, input_features))   # (4, 3)
W = rng.standard_normal((input_features, output_features))  # (3, 5)
b = np.zeros(output_features)                              # (5,)

output = X @ W + b    # (4, 5) — bias broadcasts across batch
print("Input shape:", X.shape)
print("Weights shape:", W.shape)
print("Output shape:", output.shape)

# Dot product between two vectors
a = np.array([1.0, 2.0, 3.0])
b_vec = np.array([4.0, 5.0, 6.0])
print("Dot product:", np.dot(a, b_vec))   # 32.0

# Transpose
m = np.array([[1, 2, 3], [4, 5, 6]])
print("Original shape:", m.shape)         # (2, 3)
print("Transposed shape:", m.T.shape)     # (3, 2)

# ============================================================
# SECTION 6: Full Cosine Similarity Search
# ============================================================

print("\n" + "=" * 50)
print("SECTION 6: Cosine Similarity Search")
print("=" * 50)

np.random.seed(42)
DIM = 1536
N_DOCS = 1000
TOP_K = 5

# Simulate document embeddings and query
doc_embeddings = np.random.standard_normal((N_DOCS, DIM)).astype(np.float32)
query_embedding = np.random.standard_normal((DIM,)).astype(np.float32)

# --- NumPy vectorized approach (no loop) ---
def cosine_search_numpy(query, docs, top_k=5):
    # Normalize query
    q = query / np.linalg.norm(query)

    # Normalize all docs at once
    # linalg.norm with axis=1 gives one norm per row → shape (n, 1)
    doc_norms    = np.linalg.norm(docs, axis=1, keepdims=True)
    docs_normed  = docs / doc_norms

    # One matrix multiply: dot query with every doc
    similarities = docs_normed @ q   # shape (n_docs,)

    # Get top-k descending
    top_idx    = np.argsort(similarities)[-top_k:][::-1]
    top_scores = similarities[top_idx]
    return top_idx, top_scores


# --- Plain Python loop approach ---
def cosine_sim_single(a, b):
    dot = float(np.dot(a, b))
    norm = float(np.linalg.norm(a) * np.linalg.norm(b))
    return dot / norm

def cosine_search_loop(query, docs, top_k=5):
    results = [(i, cosine_sim_single(query, docs[i])) for i in range(len(docs))]
    results.sort(key=lambda x: x[1], reverse=True)
    top = results[:top_k]
    return [i for i, _ in top], [s for _, s in top]


# Run both once to verify they agree
idx_numpy, scores_numpy = cosine_search_numpy(query_embedding, doc_embeddings, TOP_K)
idx_loop,  scores_loop  = cosine_search_loop(query_embedding, doc_embeddings, TOP_K)

print("NumPy top-5 indices:", idx_numpy)
print("Loop  top-5 indices:", idx_loop)
print("Results agree:", list(idx_numpy) == idx_loop)

# --- Benchmark ---
RUNS = 20

start = time.perf_counter()
for _ in range(RUNS):
    cosine_search_numpy(query_embedding, doc_embeddings, TOP_K)
numpy_ms = (time.perf_counter() - start) / RUNS * 1000

start = time.perf_counter()
for _ in range(RUNS):
    cosine_search_loop(query_embedding, doc_embeddings, TOP_K)
loop_ms = (time.perf_counter() - start) / RUNS * 1000

print(f"\nNumPy  : {numpy_ms:.3f} ms per query")
print(f"Loop   : {loop_ms:.3f} ms per query")
print(f"Speedup: {loop_ms / numpy_ms:.1f}x faster with NumPy")

# ============================================================
# SECTION 7: Softmax from scratch (vectorized)
# ============================================================

print("\n" + "=" * 50)
print("SECTION 7: Softmax (vectorized)")
print("=" * 50)

def softmax(x):
    # Subtract max for numerical stability before exp
    shifted = x - np.max(x)
    e_x = np.exp(shifted)
    return e_x / e_x.sum()

logits = np.array([2.0, 1.0, 0.1])
probs = softmax(logits)
print("Logits:", logits)
print("Softmax:", probs.round(4))
print("Sum of probs:", probs.sum())   # should be exactly 1.0

# ============================================================
# SECTION 8: Reshaping
# ============================================================

print("\n" + "=" * 50)
print("SECTION 8: Reshaping and Stacking")
print("=" * 50)

v = np.arange(12)
print("Original:", v, "shape:", v.shape)

m = v.reshape((3, 4))
print("Reshaped (3,4):\n", m)

m2 = v.reshape((2, -1))   # NumPy infers the second dimension
print("Reshaped (2,-1), shape:", m2.shape)

flat = m.flatten()
print("Flattened:", flat)

# Stacking embedding vectors into a matrix
emb1 = np.array([0.1, 0.2, 0.3])
emb2 = np.array([0.4, 0.5, 0.6])
emb3 = np.array([0.7, 0.8, 0.9])

matrix = np.vstack([emb1, emb2, emb3])
print("Stacked embeddings shape:", matrix.shape)   # (3, 3)
print(matrix)
