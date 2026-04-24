# 🎯 Pandas Performance Optimization — Faster Code, Less Memory

A restaurant that takes each order one at a time, walks to the fridge, and comes back before taking the next order is slow. One that takes all orders first, makes a single fridge run, and preps everything in batch is fast. Python loops over DataFrames are the first restaurant. Vectorized Pandas operations are the second. The gap in speed is often 100×.

---

## 🐢 Section 1: The apply() Trap — When to Avoid It

Think of `apply()` as hiring a single contractor who personally visits every row of your DataFrame, applies your function, and moves to the next. It looks clean in code, but under the hood it is a Python-speed loop — and Python loops are slow because they carry the full overhead of the interpreter on every iteration. NumPy and Pandas, by contrast, hand the work off to pre-compiled C code that processes entire arrays in a single pass.

**`apply()`** runs a Python function row-by-row. **Vectorized operations** operate on the entire column at C-level speed. When a built-in vectorized equivalent exists, `apply()` is always the worse choice.

```python
# SLOW — apply() with Python function:
df['result'] = df['value'].apply(lambda x: x * 2 + 1)  # ← Python loop under the hood

# FAST — vectorized:
df['result'] = df['value'] * 2 + 1  # ← C-level NumPy operation

# When apply() IS the right choice:
# - Custom string parsing with complex logic
# - When no vectorized equivalent exists
# - Row-wise operations involving multiple columns with complex conditions
df['label'] = df.apply(lambda row: classify(row['text'], row['score']), axis=1)  # ← necessary
```

---

## 🔤 Section 2: .str Methods vs apply for Strings

String operations are a common place where engineers reach for `apply()` out of habit. Imagine you have a million email addresses to clean — doing it one at a time with a Python function is like hand-washing a million dishes. The **`.str` accessor** in Pandas is the dishwasher: it hands the entire column to optimized C code in a single batch call.

Every **`.str` method** (`.str.lower()`, `.str.strip()`, `.str.contains()`, etc.) runs at vectorized speed and also handles `NaN` values gracefully without extra guard logic.

```python
# SLOW:
df['clean'] = df['text'].apply(lambda x: x.strip().lower())  # ← Python loop per row

# FAST — .str accessor runs vectorized C code:
df['clean'] = df['text'].str.strip().str.lower()  # ← single batched operation

# .str.contains vs apply for filtering:
mask = df['email'].str.contains('@gmail.com', na=False)   # ← vectorized, handles NaN
# vs df['email'].apply(lambda x: '@gmail.com' in str(x))  # ← Python loop, misses NaN safety
```

---

## 🗂️ Section 3: Categorical Dtype — The Memory Multiplier

Imagine a spreadsheet column that says "active", "inactive", or "pending" for one million rows. Under the default `object` dtype, Pandas stores the full string for every single row — a million copies of the same three words. **Categorical dtype** works like a lookup table: it stores the three unique strings once, then records a small integer per row pointing to which one applies. One million rows of three words becomes one million tiny integers plus a three-entry dictionary.

The savings are dramatic for **low-cardinality columns** — columns where the number of unique values is small relative to total rows. As a rule of thumb, if `nunique()` is less than 50% of total rows, categorical is worth considering. It also speeds up `groupby()` operations significantly because Pandas can group by integer codes rather than string comparison.

```python
# When a column has few unique values (< 50% unique), use categorical dtype
df['status'].nunique()   # ← check: 3 unique values out of 1 million rows

# BEFORE: object dtype stores full string per row
df['status'].dtype                          # object
df['status'].memory_usage(deep=True)        # ← 8 bytes per reference + string content

# AFTER: categorical stores integers + lookup table
df['status'] = df['status'].astype('category')
df['status'].memory_usage(deep=True)        # ← ~1/50 the memory for low-cardinality columns

# Set dtype at read time (best practice for large CSVs):
df = pd.read_csv('data.csv', dtype={'status': 'category', 'region': 'category'})
```

---

## ⚡ Section 4: Vectorized Operations and Avoiding Loops

Every `for` loop over DataFrame rows is a performance red flag. The pattern `for i, row in df.iterrows()` feels natural if you think of a DataFrame like a list of dictionaries — but that mental model costs you dearly. **`iterrows()`** reconstructs a full Python object for every row, adding overhead on top of an already slow loop. The correct mental model is: a DataFrame is a collection of columns, and operations happen across entire columns at once.

**`assign()`** enables clean method chaining for multi-step column creation without intermediate variables. It is both readable and keeps all operations vectorized.

```python
# WRONG — Python loop over rows:
results = []
for i, row in df.iterrows():
    results.append(row['price'] * row['quantity'])  # ← constructs Python dict per row
df['revenue'] = results  # ← 100-1000x slower than vectorized

# RIGHT — vectorized column operations:
df['revenue'] = df['price'] * df['quantity']   # ← C-level, fast

# ALSO WRONG — itertuples() is faster than iterrows() but still a loop:
for row in df.itertuples():
    pass  # ← avoid unless truly unavoidable

# For complex multi-column ops, use assign() for chaining:
df = (df
    .assign(revenue=df['price'] * df['quantity'])      # ← step 1: vectorized
    .assign(tax=lambda x: x['revenue'] * 0.1)          # ← step 2: builds on step 1
    .assign(total=lambda x: x['revenue'] + x['tax'])   # ← step 3: fully chained
)
```

---

## 💾 Section 5: Memory Optimization — Dtypes at Load Time

Most engineers load a CSV and never think about what Pandas chose for each column's dtype. But Pandas is conservative: it defaults to `int64` for integers and `float64` for floats even when the data fits in `int8`. For a model-training pipeline processing tens of millions of rows, that default choice can silently consume 4–8× more memory than necessary. The fix is to **downcast** numeric columns to the smallest type that still fits the data, and to specify dtypes at read time rather than converting after the fact.

**`memory_usage(deep=True)`** is the diagnostic tool — it shows actual bytes consumed per column, including the content of object columns, not just the pointer size.

```python
# Check memory usage per column:
df.memory_usage(deep=True)            # ← shows bytes per column
df.memory_usage(deep=True).sum()      # ← total memory in bytes
df.info(memory_usage='deep')          # ← full report with dtypes and non-null counts

# Downcast numeric types:
df['age'] = pd.to_numeric(df['age'], downcast='integer')    # ← int64 → int8/int16/int32
df['score'] = pd.to_numeric(df['score'], downcast='float')  # ← float64 → float32

# Read only needed columns:
df = pd.read_csv('big_file.csv', usecols=['id', 'price', 'date'])  # ← skip unneeded columns at source

# Read in chunks for files that don't fit in memory:
chunks = []
for chunk in pd.read_csv('huge.csv', chunksize=100_000):  # ← process 100k rows at a time
    chunk = chunk[chunk['status'] == 'active']             # ← filter before accumulating
    chunks.append(chunk)
df = pd.concat(chunks)  # ← combine only the filtered rows
```

---

## 🔍 Section 6: eval() and query() for Large DataFrames

When you write `df['revenue'] = df['price'] * df['quantity']`, Pandas creates a full temporary array for `df['price'] * df['quantity']` before assigning it. For a DataFrame with millions of rows and multiple chained operations, those temporary arrays stack up in memory. **`eval()`** compiles the expression and executes it in a single pass, skipping the intermediate allocations. It becomes meaningful at roughly 10,000+ rows.

**`query()`** provides the same benefit for filtering: it parses a string expression into an optimized internal representation rather than creating boolean mask arrays as intermediate objects.

```python
# For large DataFrames (>10k rows), eval() can be faster than direct operations
# because it avoids creating intermediate arrays
df.eval('revenue = price * quantity', inplace=True)   # ← single pass, no temp arrays

# Multi-step eval — all computed in one compiled expression:
df.eval('''
    revenue = price * quantity
    tax     = revenue * 0.1
    total   = revenue + tax
''', inplace=True)

# query() for fast filtering:
df.query('price > 100 and status == "active"')   # ← often faster than boolean indexing for large dfs

# Reference Python variables inside query() with @:
threshold = 100
df.query('price > @threshold')   # ← @ prefix injects a local Python variable
```

---

## 🔬 Section 7: Profiling — Find the Bottleneck First

Optimizing without measuring is guessing. The most important rule in performance work is: profile first, optimize second. A fix applied to the wrong bottleneck wastes time and adds complexity. Pandas work in Jupyter pairs naturally with **`%timeit`** for speed measurement and **`tracemalloc`** for memory tracking. Both give you a before/after number, which is the only honest way to know whether a change helped.

**`%timeit`** runs the expression multiple times and reports average and standard deviation — much more reliable than a single `time.time()` call. **`tracemalloc`** tracks peak memory allocation during a block of code, not just the final allocation.

```python
# Time a single operation:
import timeit
%timeit df['col'].apply(lambda x: x * 2)    # ← Jupyter magic: runs N times, reports avg
%timeit df['col'] * 2                        # ← compare directly in the same cell

# Check memory before and after:
import tracemalloc
tracemalloc.start()
result = df.groupby('category')['value'].sum()   # ← operation to measure
current, peak = tracemalloc.get_traced_memory()  # ← current and peak allocation in bytes
tracemalloc.stop()
print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")

# Quick summary of all dtypes and memory:
def df_report(df):
    print(df.dtypes)                                                          # ← all column types
    print(f"Total memory: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")  # ← MB total
    print(f"Shape: {df.shape}")                                               # ← rows × columns
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⬅️ Prev Topic | [08_data_validation.md](./08_data_validation.md) |
| ➡️ Next Topic | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
