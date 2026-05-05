"""
21_data_engineering_applications/memory_efficient_etl.py
==========================================================
CONCEPT: Memory-efficient ETL — Extract, Transform, Load without loading
the entire dataset into RAM. Uses generator pipelines and chunked processing.
WHY THIS MATTERS: A data file that fits in memory on a developer's laptop
might be 10x larger in production. Generators and chunked processing make
code that scales from MB to GB without code changes.

Prerequisite: Modules 01–13 (especially generators, file handling, memory management)
"""

import csv
import json
import time
import tempfile
import random
import sys
import gc
from pathlib import Path
from typing import Iterator, Callable, Any
from collections import defaultdict

# =============================================================================
# SECTION 1: The core ETL pipeline as a generator chain
# =============================================================================

# CONCEPT: Each stage of the pipeline is a generator. Records flow through
# the chain one at a time — never accumulating in memory.
# E(xtract) → T(ransform) → T(ransform) → L(oad)
#
# Memory usage: O(1) — only 1 record in memory at any pipeline stage at a time.
# Compare: eager approach O(n) — all records in memory simultaneously.

print("=== Section 1: Generator ETL Chain ===")


# ---- EXTRACT ----
def extract_from_csv(filepath: str) -> Iterator[dict]:
    """
    Extract: read CSV rows lazily, one at a time.
    The file object itself is an iterator — Python does NOT read the whole file.
    """
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield dict(row)


# ---- TRANSFORM ----
def cast_types(records: Iterator[dict]) -> Iterator[dict]:
    """Transform: parse string fields to correct Python types."""
    for r in records:
        try:
            yield {
                "id":     int(r["id"]),
                "name":   r["name"].strip(),
                "score":  float(r["score"]),
                "active": r["active"].lower() == "true",
                "region": r.get("region", "unknown").strip(),
            }
        except (ValueError, KeyError):
            pass   # skip malformed rows silently


def filter_active(records: Iterator[dict]) -> Iterator[dict]:
    """Transform: keep only active records."""
    return (r for r in records if r["active"])


def enrich_with_grade(records: Iterator[dict]) -> Iterator[dict]:
    """Transform: add derived field 'grade' based on score."""
    def grade(score: float) -> str:
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        return "F"

    for r in records:
        r["grade"] = grade(r["score"])
        yield r


def normalize_region(records: Iterator[dict]) -> Iterator[dict]:
    """Transform: standardize region names."""
    REGION_MAP = {
        "us": "US", "usa": "US", "united states": "US",
        "uk": "GB", "britain": "GB", "great britain": "GB",
        "eu": "EU", "europe": "EU",
    }
    for r in records:
        r["region"] = REGION_MAP.get(r["region"].lower(), r["region"].upper())
        yield r


# ---- LOAD ----
def load_to_csv(records: Iterator[dict], output_path: str,
                fields: list) -> int:
    """Load: write records to a CSV file. Returns count of written records."""
    count = 0
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow(record)
            count += 1
    return count


def load_to_json_lines(records: Iterator[dict], output_path: str) -> int:
    """Load: write records as NDJSON (one JSON object per line)."""
    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
            count += 1
    return count


# ----- Run the pipeline -----
# Create a test dataset
tmp_dir = Path(tempfile.mkdtemp())
source  = tmp_dir / "source.csv"

random.seed(42)
regions = ["us", "uk", "EU", "usa", "europe", "APAC"]

with open(source, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "name", "score", "active", "region"])
    for i in range(1, 201):
        w.writerow([
            i,
            f"User_{i}",
            round(random.uniform(40, 100), 1),
            random.choice(["True", "False"]),
            random.choice(regions),
        ])

print(f"  Source: {source.name} ({source.stat().st_size:,} bytes, 200 rows)")

# Wire the pipeline
pipeline = normalize_region(
    enrich_with_grade(
        filter_active(
            cast_types(
                extract_from_csv(str(source))
            )
        )
    )
)

output_csv = tmp_dir / "output.csv"
start      = time.perf_counter()
count      = load_to_csv(pipeline, str(output_csv),
                         fields=["id", "name", "score", "grade", "region", "active"])
elapsed    = time.perf_counter() - start

print(f"  Pipeline result: {count} active records written in {elapsed*1000:.1f}ms")
print(f"  Output: {output_csv.name} ({output_csv.stat().st_size:,} bytes)")


# =============================================================================
# SECTION 2: Chunked processing for aggregations
# =============================================================================

# CONCEPT: Pure streaming can't do aggregations like GROUP BY without seeing
# all records (unless data is pre-sorted). Chunked processing is a middle ground:
# process in batches of N records — bounded memory, still handles large datasets.

print("\n=== Section 2: Chunked Aggregation ===")


def chunk(iterable: Iterator, size: int) -> Iterator[list]:
    """
    Split an iterator into chunks of `size` items.
    Each chunk is a list — the only time memory exceeds O(1).
    Max memory at any time: O(chunk_size), regardless of total dataset size.
    """
    chunk_list = []
    for item in iterable:
        chunk_list.append(item)
        if len(chunk_list) >= size:
            yield chunk_list
            chunk_list = []
    if chunk_list:
        yield chunk_list


def merge_aggregates(aggs: list[dict]) -> dict:
    """Merge multiple partial aggregates into one final aggregate."""
    merged = defaultdict(lambda: {"count": 0, "total_score": 0.0, "min": float("inf"), "max": float("-inf")})
    for agg in aggs:
        for region, data in agg.items():
            merged[region]["count"]       += data["count"]
            merged[region]["total_score"] += data["total_score"]
            merged[region]["min"]          = min(merged[region]["min"], data["min"])
            merged[region]["max"]          = max(merged[region]["max"], data["max"])
    return {
        region: {
            "count":     v["count"],
            "avg_score": round(v["total_score"] / v["count"], 2),
            "min_score": v["min"],
            "max_score": v["max"],
        }
        for region, v in merged.items()
    }


# Re-run extraction for aggregation
all_records_gen = normalize_region(enrich_with_grade(cast_types(extract_from_csv(str(source)))))

chunk_aggs = []
total_processed = 0

for records_chunk in chunk(all_records_gen, size=50):
    # Aggregate within this chunk
    local_agg = defaultdict(lambda: {"count": 0, "total_score": 0.0, "min": float("inf"), "max": float("-inf")})
    for r in records_chunk:
        region = r["region"]
        local_agg[region]["count"]       += 1
        local_agg[region]["total_score"] += r["score"]
        local_agg[region]["min"]          = min(local_agg[region]["min"], r["score"])
        local_agg[region]["max"]          = max(local_agg[region]["max"], r["score"])

    chunk_aggs.append(dict(local_agg))
    total_processed += len(records_chunk)
    print(f"  Chunk: {len(records_chunk)} records ({total_processed} total)")

final_agg = merge_aggregates(chunk_aggs)
print(f"\n  Region aggregates ({len(final_agg)} regions):")
for region, stats in sorted(final_agg.items()):
    print(f"    {region:6}: n={stats['count']:3}, avg={stats['avg_score']}, "
          f"min={stats['min_score']}, max={stats['max_score']}")


# =============================================================================
# SECTION 3: Memory tracking — proving O(1) behavior
# =============================================================================

print("\n=== Section 3: Memory Comparison (Eager vs Lazy) ===")

import tracemalloc

N_RECORDS = 50_000   # larger dataset to show the difference

# Create a large CSV for testing
large_csv = tmp_dir / "large.csv"
with open(large_csv, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "name", "score", "active", "region"])
    for i in range(N_RECORDS):
        w.writerow([i, f"User_{i}", round(random.uniform(40, 100), 1),
                    "True", random.choice(["US", "GB", "EU"])])

def process_eager(filepath: str) -> int:
    """EAGER: load ALL rows into a list first, then process."""
    with open(filepath, newline="") as f:
        all_rows = list(csv.DictReader(f))   # ALL rows in memory
    count = sum(1 for r in all_rows if float(r["score"]) >= 70)
    return count


def process_lazy(filepath: str) -> int:
    """LAZY: generator — only 1 row in memory at a time."""
    with open(filepath, newline="") as f:
        return sum(1 for r in csv.DictReader(f) if float(r["score"]) >= 70)


def measure_peak_memory(func, *args):
    gc.collect()
    tracemalloc.start()
    result = func(*args)
    snap   = tracemalloc.take_snapshot()
    tracemalloc.stop()
    peak = sum(s.size for s in snap.statistics("filename"))
    return result, peak


r_eager, mem_eager = measure_peak_memory(process_eager, str(large_csv))
r_lazy,  mem_lazy  = measure_peak_memory(process_lazy,  str(large_csv))

print(f"  N = {N_RECORDS:,} records")
print(f"  Eager (load all): {mem_eager/1024:.1f} KB  result={r_eager:,}")
print(f"  Lazy  (stream):   {mem_lazy/1024:.1f} KB   result={r_lazy:,}")
print(f"  Memory ratio: {mem_eager/max(mem_lazy,1):.1f}x more for eager approach")
assert r_eager == r_lazy, "Results must match!"


# =============================================================================
# SECTION 4: Parallel pipeline with thread pool (I/O-bound files)
# =============================================================================

print("\n=== Section 4: Parallel File Processing ===")

from concurrent.futures import ThreadPoolExecutor, as_completed


def process_one_file(filepath: Path) -> dict:
    """Process a single file — suitable for ThreadPoolExecutor."""
    pipeline = normalize_region(enrich_with_grade(
        filter_active(cast_types(extract_from_csv(str(filepath))))
    ))
    count = sum(1 for _ in pipeline)
    return {"file": filepath.name, "active_records": count}


# Create multiple small files to process in parallel
file_batch = []
for i in range(8):
    p = tmp_dir / f"parallel_{i+1:02d}.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "score", "active", "region"])
        for j in range(50):
            w.writerow([j+1, f"User_{j}", round(random.uniform(50, 100), 1),
                        random.choice(["True", "False"]), "US"])
    file_batch.append(p)

start = time.perf_counter()
results = []
with ThreadPoolExecutor(max_workers=4, thread_name_prefix="ETL") as pool:
    futures = {pool.submit(process_one_file, fp): fp for fp in file_batch}
    for future in as_completed(futures):
        results.append(future.result())

elapsed = time.perf_counter() - start

results.sort(key=lambda r: r["file"])
for r in results:
    print(f"  {r['file']}: {r['active_records']} active records")

total = sum(r["active_records"] for r in results)
print(f"\n  Total active: {total} across {len(results)} files in {elapsed*1000:.1f}ms")


print("\n=== Memory-efficient ETL complete ===")
print("ETL best practices:")
print("  1. Never load entire dataset — use generator pipelines")
print("  2. Each pipeline stage = one generator function (single responsibility)")
print("  3. Use chunked processing only when aggregation requires seeing groups")
print("  4. Process files in parallel (threads for I/O-bound reading)")
print("  5. Measure memory: tracemalloc proves O(1) behavior")
print("  6. Keep E/T/L separate — testable in isolation with small data")
