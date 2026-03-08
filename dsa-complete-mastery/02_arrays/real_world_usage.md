# Arrays — Real World Usage

Arrays are the most fundamental data structure in computing.
At the hardware level, memory is an array of bytes.
Every abstraction above it — strings, images, neural networks, databases — is built on arrays.

---

## 1. NumPy Arrays — Contiguous Memory vs Python List Overhead

A Python list is an array of pointers. Each element is a Python object stored separately on the heap.
`[1, 2, 3]` in Python: the list stores 3 pointers (8 bytes each), and each integer is a full Python
object (~28 bytes). Total: ~3 * 36 = ~108 bytes for 3 integers.

A NumPy array stores raw numeric data contiguously. `np.array([1, 2, 3], dtype=int32)`:
3 × 4 bytes = 12 bytes. 9x less memory, and CPU cache lines are used efficiently.

Vectorized operations run in compiled C/Fortran, bypassing Python's interpreter loop entirely.

```python
import numpy as np
import time

size = 10_000_000

# Python list approach
py_list = list(range(size))
start = time.time()
result = [x * 2 for x in py_list]
print(f"Python list multiply: {time.time() - start:.3f}s")  # ~0.8s

# NumPy array approach
np_array = np.arange(size, dtype=np.int32)
start = time.time()
result = np_array * 2  # single C-level loop over contiguous memory
print(f"NumPy multiply:       {time.time() - start:.3f}s")  # ~0.01s

# Memory comparison
import sys
print(f"Python list size: {sys.getsizeof(py_list) + size * 28} bytes approx")
print(f"NumPy array size: {np_array.nbytes} bytes")

# Strides — NumPy's way of describing memory layout
matrix = np.array([[1, 2, 3], [4, 5, 6]])
print(f"Shape: {matrix.shape}, Strides: {matrix.strides}")
# Strides: (12, 4) means moving one row = 12 bytes, one column = 4 bytes
# This is how NumPy does slicing without copying data
```

NumPy is the backbone of pandas, scikit-learn, TensorFlow, and PyTorch.
Every ML model you have ever used runs on arrays.

---

## 2. Database Row Storage — Rows as Byte Arrays

In a relational database, each row is stored as a contiguous byte array on disk.
PostgreSQL's heap file format stores rows as `HeapTupleData`: a fixed header followed by
attribute values laid out sequentially in memory.

When PostgreSQL reads a row, it does one seek + one read of ~200 bytes.
Column types with fixed widths (int, float, date) allow direct offset calculation:
`column_value = row_bytes[column_offset : column_offset + column_size]`.

```python
import struct

# Simulating how a database stores a row as a byte array
# Row: (id: int32, age: int16, salary: float32, active: bool)
row_format = "i h f ?"  # struct format: int32, int16, float32, bool
row_data = (1001, 29, 95000.50, True)

# Serialize row to bytes (what a DB writes to disk)
packed = struct.pack(row_format, *row_data)
print(f"Row as bytes ({len(packed)} bytes): {packed.hex()}")

# Deserialize (what a DB does on read)
unpacked = struct.unpack(row_format, packed)
print(f"Deserialized: id={unpacked[0]}, age={unpacked[1]}, salary={unpacked[2]:.2f}")

# Column store (OLAP databases like ClickHouse, Parquet)
# Instead of row-by-row, store each column as its own contiguous array
ids     = [1001, 1002, 1003]
ages    = [29, 34, 41]
salaries = [95000.0, 120000.0, 87000.0]

# Analytical query: average salary — only reads the salary array, not ids/ages
avg_salary = sum(salaries) / len(salaries)
print(f"Avg salary: {avg_salary:.2f}")  # Never touched ids or ages arrays
```

Column stores (Parquet, ClickHouse) outperform row stores for analytics because
reading one column = reading a contiguous byte array. One sequential I/O vs N random I/Os.

---

## 3. Image Processing — Images as 2D and 3D Arrays

A grayscale image is a 2D array of shape `(height, width)`, values 0–255.
A color image is a 3D array of shape `(height, width, 3)` for RGB channels.
A video is a 4D array: `(frames, height, width, channels)`.

Every filter, crop, resize, and neural network convolution operates on these arrays.

```python
import numpy as np

# Create a simple 5x5 grayscale image
image = np.array([
    [10, 20, 30, 40, 50],
    [60, 70, 80, 90, 100],
    [110, 120, 128, 130, 140],
    [150, 160, 170, 180, 190],
    [200, 210, 220, 230, 240],
], dtype=np.uint8)

print(f"Image shape: {image.shape}")  # (5, 5)
print(f"Pixel at (2,2): {image[2, 2]}")  # 128

# Crop: array slicing — O(1), no copy (view)
crop = image[1:4, 1:4]
print(f"Cropped shape: {crop.shape}")  # (3, 3)

# Brightness increase — vectorized operation
brightened = np.clip(image.astype(np.int16) + 50, 0, 255).astype(np.uint8)

# Edge detection — 2D convolution (what Sobel filter does)
# Kernel is a small 2D array; slide it over the image
sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])

def apply_kernel(img, kernel):
    h, w = img.shape
    kh, kw = kernel.shape
    output = np.zeros((h - kh + 1, w - kw + 1))
    for i in range(output.shape[0]):
        for j in range(output.shape[1]):
            output[i, j] = np.sum(img[i:i+kh, j:j+kw] * kernel)
    return output

edges = apply_kernel(image.astype(np.float32), sobel_x)
print(f"Edge map shape: {edges.shape}")  # (3, 3)

# RGB image
rgb_image = np.zeros((100, 100, 3), dtype=np.uint8)
rgb_image[:, :, 0] = 255  # Red channel max
print(f"Red pixel at (0,0): {rgb_image[0, 0]}")  # [255, 0, 0]
```

OpenCV, Pillow, and PyTorch's `torchvision` all represent images as NumPy/tensor arrays.
A ResNet inference pass is matrix multiplications over 3D activation arrays.

---

## 4. Circular Buffers — Audio/Video Streaming and OS I/O

A circular buffer (ring buffer) is a fixed-size array used as a FIFO queue.
The write pointer and read pointer advance modulo the buffer size.
When the write pointer catches the read pointer, the buffer is full.

This is used everywhere:
- Audio drivers: microphone samples are written to a ring buffer; playback reads from it.
- Linux kernel: `pipe`, `kfifo`, network socket receive buffers.
- Video streaming: decoder writes decoded frames; renderer reads them.

```python
class CircularBuffer:
    """Fixed-size ring buffer. O(1) enqueue and dequeue."""

    def __init__(self, capacity: int):
        self.buffer = [None] * capacity
        self.capacity = capacity
        self.read_pos = 0
        self.write_pos = 0
        self.size = 0

    def write(self, value) -> bool:
        """Write a sample. Returns False if buffer is full (overrun)."""
        if self.size == self.capacity:
            return False  # Buffer full — audio overrun / drop frame
        self.buffer[self.write_pos] = value
        self.write_pos = (self.write_pos + 1) % self.capacity
        self.size += 1
        return True

    def read(self) -> object:
        """Read next sample. Returns None if buffer is empty (underrun)."""
        if self.size == 0:
            return None  # Buffer empty — audio underrun / silence
        value = self.buffer[self.read_pos]
        self.read_pos = (self.read_pos + 1) % self.capacity
        self.size -= 1
        return value

    def __len__(self):
        return self.size

# Audio streaming simulation
audio_buffer = CircularBuffer(capacity=4096)

# Producer: audio hardware writes samples at 44100 Hz
for sample in [0.1, 0.3, -0.2, 0.5, 0.8]:
    audio_buffer.write(sample)

# Consumer: audio playback reads samples
while len(audio_buffer) > 0:
    sample = audio_buffer.read()
    print(f"Playing sample: {sample}")
```

The key property: no dynamic memory allocation during operation.
Audio drivers cannot call `malloc` mid-stream (too slow, non-deterministic).
The fixed array guarantees constant memory usage and O(1) operations.

---

## 5. Prefix Sum in Analytics — Range Sum Queries

Analytics dashboards answer questions like: "What is the total revenue between day 30 and day 90?"
Naive: iterate the array from index 30 to 90 = O(n) per query.
With prefix sums: O(n) preprocessing, O(1) per range query.

```python
# E-commerce analytics: daily revenue for a year
import random
random.seed(42)
daily_revenue = [random.randint(10000, 100000) for _ in range(365)]

# Build prefix sum array — O(n) once
prefix = [0] * (len(daily_revenue) + 1)
for i, rev in enumerate(daily_revenue):
    prefix[i + 1] = prefix[i] + rev

def range_sum(start: int, end: int) -> int:
    """Sum of daily_revenue[start..end] inclusive. O(1)."""
    return prefix[end + 1] - prefix[start]

# Dashboard queries — each O(1)
q1_revenue = range_sum(0, 89)    # Jan–Mar
q2_revenue = range_sum(90, 180)  # Apr–Jun
print(f"Q1 revenue: ${q1_revenue:,}")
print(f"Q2 revenue: ${q2_revenue:,}")

# Sliding window average (7-day rolling average)
window = 7
rolling_avg = []
for i in range(window - 1, len(daily_revenue)):
    avg = range_sum(i - window + 1, i) / window
    rolling_avg.append(avg)

print(f"Day 10 rolling avg: ${rolling_avg[9]:,.0f}")

# 2D prefix sums — used in image processing and 2D analytics
# query: sum of any rectangle in a matrix in O(1)
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
rows, cols = len(matrix), len(matrix[0])
p2d = [[0] * (cols + 1) for _ in range(rows + 1)]
for r in range(rows):
    for c in range(cols):
        p2d[r+1][c+1] = matrix[r][c] + p2d[r][c+1] + p2d[r+1][c] - p2d[r][c]

def rect_sum(r1, c1, r2, c2):
    return p2d[r2+1][c2+1] - p2d[r1][c2+1] - p2d[r2+1][c1] + p2d[r1][c1]

print(f"Sum of full matrix: {rect_sum(0, 0, 2, 2)}")  # 45
```

Google BigQuery, ClickHouse, and Redshift use prefix sum techniques internally for
materialized aggregate queries (COUNT, SUM over time ranges).

---

## 6. GPU Programming — CUDA Arrays and Contiguous Memory

A GPU has thousands of cores that execute the same instruction on different array elements
simultaneously (SIMD: Single Instruction, Multiple Data).

For this to work efficiently, data must be in contiguous memory.
Non-contiguous arrays cause cache thrashing — each thread has to fetch from a different
cache line, destroying the memory bandwidth advantage.

```python
# CPU simulation of how GPU CUDA kernels process arrays
import numpy as np

# In CUDA C:
# __global__ void multiply(float* a, float* b, float* c, int n) {
#     int i = blockIdx.x * blockDim.x + threadIdx.x;
#     if (i < n) c[i] = a[i] * b[i];
# }

# Python equivalent — NumPy simulates vectorized CUDA behavior
a = np.random.rand(1_000_000).astype(np.float32)  # contiguous float32 array
b = np.random.rand(1_000_000).astype(np.float32)

# All elements processed "simultaneously" (vectorized in C, parallel on GPU)
c = a * b  # element-wise multiply

# Contiguous check — critical for GPU transfers
print(f"a is C-contiguous: {a.flags['C_CONTIGUOUS']}")  # True = GPU-ready

# Non-contiguous example — every other element (stride = 8 bytes, not 4)
a_strided = a[::2]
print(f"a_strided is C-contiguous: {a_strided.flags['C_CONTIGUOUS']}")  # False
# To send to GPU, must call .copy() first to make contiguous

# PyTorch (GPU tensors) — same principle
# import torch
# tensor = torch.randn(1000, 1000, device="cuda")  # allocated on GPU memory
# result = tensor @ tensor.T  # matrix multiply — thousands of GPU cores in parallel
```

PyTorch's `Tensor.contiguous()` method is called before many GPU operations
precisely because CUDA kernels require contiguous memory layout.

---

## 7. Event Logs and Time Series — Append-Only Arrays

Application logs, metrics, and time-series data are naturally append-only.
New events are always appended to the end. Historical events are never modified.

This makes an array the perfect structure:
- Append: O(1) amortized.
- Read by time range: O(log n) with binary search on sorted timestamps.
- No deletes needed (rotate by truncating the front).

```python
import time
import bisect
from dataclasses import dataclass
from typing import List

@dataclass
class LogEvent:
    timestamp: float
    level: str
    message: str

class AppendOnlyLog:
    """Append-only log with O(log n) time-range queries."""

    def __init__(self):
        self.events: List[LogEvent] = []
        self.timestamps: List[float] = []  # parallel array for binary search

    def append(self, level: str, message: str):
        ts = time.time()
        self.events.append(LogEvent(ts, level, message))
        self.timestamps.append(ts)  # always increasing — sorted automatically

    def query_range(self, start_ts: float, end_ts: float) -> List[LogEvent]:
        """Return all events between start_ts and end_ts. O(log n + k)."""
        left = bisect.bisect_left(self.timestamps, start_ts)
        right = bisect.bisect_right(self.timestamps, end_ts)
        return self.events[left:right]

log = AppendOnlyLog()
log.append("INFO", "Server started")
log.append("INFO", "Request received: GET /api/users")
log.append("ERROR", "Database connection timeout")
log.append("INFO", "Retry successful")

# Query last N seconds
now = time.time()
recent = log.query_range(now - 60, now)
print(f"Events in last 60s: {len(recent)}")
for event in recent:
    print(f"  [{event.level}] {event.message}")
```

Apache Kafka stores events as an append-only array on disk (a commit log).
Prometheus stores time-series metrics in compressed append-only chunks.
LSMT (Log-Structured Merge Trees) in RocksDB/LevelDB use the same idea.

---

## Summary

| Use Case | Array Property Used | Why Arrays |
|---|---|---|
| NumPy / ML | Contiguous memory, vectorized ops | Cache efficiency, SIMD instructions |
| Database rows | Fixed-offset byte layout | O(1) column access by offset |
| Image processing | 2D/3D indexing | Direct pixel addressing |
| Circular buffer | Modulo index arithmetic | O(1) enqueue/dequeue, zero allocation |
| Prefix sum analytics | Cumulative offset lookup | O(1) range queries after O(n) build |
| GPU kernels | Contiguous float32 blocks | Coalesced memory access on GPU |
| Event logs | Append-only, sorted timestamps | O(log n) range queries via binary search |

Arrays are not just a beginner data structure.
They are the foundation of numerical computing, databases, operating systems, and machine learning.
