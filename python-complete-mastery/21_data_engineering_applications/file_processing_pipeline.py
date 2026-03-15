"""
21_data_engineering_applications/file_processing_pipeline.py
==============================================================
CONCEPT: File processing pipeline — read raw files, validate, transform,
and write clean output. The "Transform" and "Load" phases of ETL.
WHY THIS MATTERS: Data engineers regularly process thousands of CSV/JSON/log
files. The key skills are: streaming (not loading all into RAM), error handling
at row level without failing the whole job, and idempotent output.

Prerequisite: Modules 01–13 (especially generators, file handling, OOP)
"""

import csv
import json
import time
import logging
import tempfile
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional, Any
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO, format="  %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# =============================================================================
# SECTION 1: Data model and validation
# =============================================================================

print("=== Section 1: Data Models and Validation ===")


@dataclass
class RawRecord:
    """Represents one unvalidated row from a source file."""
    source_file: str
    line_number: int
    raw_data:    dict


@dataclass
class CleanRecord:
    """Validated and transformed record ready for output."""
    user_id:    int
    name:       str
    email:      str
    score:      float
    category:   str
    source_file: str = ""

    def to_dict(self) -> dict:
        return {
            "user_id":  self.user_id,
            "name":     self.name,
            "email":    self.email,
            "score":    self.score,
            "category": self.category,
        }


@dataclass
class ValidationResult:
    """Outcome of validating one raw record."""
    record:  Optional[CleanRecord]
    errors:  list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def validate_and_transform(raw: RawRecord) -> ValidationResult:
    """
    Validate one raw record and transform it to CleanRecord.
    Returns ValidationResult with either a clean record OR error messages.
    NEVER raises — errors are collected, not propagated.
    """
    errors = []
    d      = raw.raw_data

    # Validate user_id
    try:
        user_id = int(d.get("user_id", ""))
        if user_id <= 0:
            errors.append(f"user_id must be positive, got {user_id}")
    except (ValueError, TypeError):
        errors.append(f"user_id not an integer: {d.get('user_id')!r}")
        user_id = -1

    # Validate name
    name = str(d.get("name", "")).strip()
    if len(name) < 2:
        errors.append(f"name too short: {name!r}")

    # Validate email
    email = str(d.get("email", "")).strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        errors.append(f"invalid email: {email!r}")

    # Validate score
    try:
        score = float(d.get("score", ""))
        if not (0.0 <= score <= 100.0):
            errors.append(f"score out of range [0,100]: {score}")
    except (ValueError, TypeError):
        errors.append(f"score not a number: {d.get('score')!r}")
        score = 0.0

    # Derive category from score
    if score >= 90:   category = "A"
    elif score >= 80: category = "B"
    elif score >= 70: category = "C"
    else:             category = "F"

    if errors:
        return ValidationResult(record=None, errors=errors)

    return ValidationResult(
        record=CleanRecord(
            user_id=user_id, name=name, email=email,
            score=score, category=category,
            source_file=raw.source_file,
        ),
        errors=[],
    )


# Test validation
samples = [
    {"user_id": "1", "name": "Alice Smith", "email": "alice@example.com", "score": "92.5"},
    {"user_id": "bad", "name": "B", "email": "not-an-email", "score": "150"},
    {"user_id": "3", "name": "Carol Davis", "email": "carol@example.com", "score": "78"},
]

for sample in samples:
    raw = RawRecord("test.csv", 1, sample)
    result = validate_and_transform(raw)
    if result.is_valid:
        print(f"  OK:  {result.record.name} → {result.record.category} ({result.record.score})")
    else:
        print(f"  ERR: {sample.get('name')!r}: {result.errors}")


# =============================================================================
# SECTION 2: Generator-based CSV pipeline
# =============================================================================

print("\n=== Section 2: Streaming CSV Pipeline ===")

def read_csv_records(filepath: Path) -> Iterator[RawRecord]:
    """
    Lazy CSV reader — yields one RawRecord per row.
    Keeps only ONE row in memory at a time regardless of file size.
    """
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line_num, row in enumerate(reader, start=2):   # start=2 (header=1)
            yield RawRecord(
                source_file=str(filepath.name),
                line_number=line_num,
                raw_data=dict(row),
            )


def validate_records(records: Iterator[RawRecord]) -> Iterator[tuple[RawRecord, ValidationResult]]:
    """Validate each record, yield (raw, result) tuple for both valid and invalid."""
    for raw in records:
        yield raw, validate_and_transform(raw)


def filter_valid(pairs: Iterator[tuple]) -> Iterator[CleanRecord]:
    """Yield only valid CleanRecords from (raw, result) pairs."""
    for raw, result in pairs:
        if result.is_valid:
            yield result.record
        else:
            log.warning(f"  Skipping {raw.source_file}:{raw.line_number} — {result.errors}")


# Create a test CSV file
tmp_dir = Path(tempfile.mkdtemp())
csv_file = tmp_dir / "users.csv"

test_rows = [
    "user_id,name,email,score",
    "1,Alice Smith,alice@example.com,92.5",
    "2,Bob Jones,bob@example.com,85.0",
    "bad,X,not-email,999",         # invalid row
    "4,Carol Davis,carol@example.com,78.0",
    "5,David Lee,david@example.com,95.5",
    ",empty name,,",               # multiple invalid fields
]
csv_file.write_text("\n".join(test_rows))

# Wire the pipeline — nothing processes until we consume
raw_records  = read_csv_records(csv_file)
validated    = validate_records(raw_records)
clean_stream = filter_valid(validated)

# Consume: collect all valid records
clean_records = list(clean_stream)
print(f"  Processed {len(test_rows)-1} rows → {len(clean_records)} valid records")
for r in clean_records:
    print(f"    user_{r.user_id}: {r.name} score={r.score} ({r.category})")


# =============================================================================
# SECTION 3: Multi-file batch processing with progress tracking
# =============================================================================

print("\n=== Section 3: Batch File Processing ===")

def create_test_batch(directory: Path, num_files: int = 5, rows_per_file: int = 20) -> list[Path]:
    """Create a batch of test CSV files."""
    import random
    random.seed(42)
    names  = ["Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Henry"]
    files  = []

    for i in range(num_files):
        filepath = directory / f"batch_{i+1:03d}.csv"
        with open(filepath, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["user_id", "name", "email", "score"])
            w.writeheader()
            for j in range(rows_per_file):
                uid  = i * rows_per_file + j + 1
                name = random.choice(names)
                w.writerow({
                    "user_id": uid,
                    "name":    f"{name}_{uid}",
                    "email":   f"user{uid}@example.com",
                    "score":   round(random.uniform(55, 100), 1),
                })
        files.append(filepath)
    return files


@dataclass
class BatchStats:
    total_files:    int = 0
    total_rows:     int = 0
    valid_rows:     int = 0
    invalid_rows:   int = 0
    processing_time: float = 0.0

    @property
    def valid_rate(self) -> float:
        return self.valid_rows / max(self.total_rows, 1) * 100


def process_batch(files: list[Path], output_file: Path) -> BatchStats:
    """
    Process a batch of CSV files into a single clean output file.
    Streams records — memory usage is O(1) relative to file sizes.
    """
    stats = BatchStats(total_files=len(files))
    start = time.perf_counter()

    with open(output_file, "w", newline="") as out_f:
        writer = None

        for filepath in files:
            log.info(f"Processing {filepath.name}...")

            for raw, result in validate_records(read_csv_records(filepath)):
                stats.total_rows += 1

                if result.is_valid:
                    stats.valid_rows += 1
                    record_dict = result.record.to_dict()

                    # Initialize writer on first valid record
                    if writer is None:
                        writer = csv.DictWriter(out_f, fieldnames=list(record_dict.keys()))
                        writer.writeheader()

                    writer.writerow(record_dict)
                else:
                    stats.invalid_rows += 1

    stats.processing_time = time.perf_counter() - start
    return stats


batch_dir = tmp_dir / "batch"
batch_dir.mkdir()
batch_files  = create_test_batch(batch_dir, num_files=5, rows_per_file=20)
output_path  = tmp_dir / "clean_output.csv"

stats = process_batch(batch_files, output_path)
print(f"\n  Batch results:")
print(f"    Files:       {stats.total_files}")
print(f"    Total rows:  {stats.total_rows}")
print(f"    Valid:       {stats.valid_rows} ({stats.valid_rate:.1f}%)")
print(f"    Invalid:     {stats.invalid_rows}")
print(f"    Time:        {stats.processing_time*1000:.1f} ms")
print(f"    Output size: {output_path.stat().st_size:,} bytes")


# =============================================================================
# SECTION 4: Idempotent processing — skip already-processed files
# =============================================================================

# CONCEPT: Idempotency means running the pipeline twice produces the same
# result as running it once. Achieved by checksumming input files and skipping
# files whose checksum is already in the "processed" registry.

print("\n=== Section 4: Idempotent File Processing ===")

class ProcessingRegistry:
    """
    Tracks which files have been processed (by content hash).
    Enables idempotent re-runs — same file processed only once.
    """

    def __init__(self, registry_path: Path):
        self._path = registry_path
        self._processed = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._processed, indent=2))

    @staticmethod
    def file_hash(filepath: Path) -> str:
        """MD5 hash of file content — unique ID for a specific version of a file."""
        h = hashlib.md5()
        h.update(filepath.read_bytes())
        return h.hexdigest()

    def is_processed(self, filepath: Path) -> bool:
        file_hash = self.file_hash(filepath)
        return file_hash in self._processed

    def mark_processed(self, filepath: Path, records_written: int) -> None:
        file_hash = self.file_hash(filepath)
        self._processed[file_hash] = {
            "filename":        filepath.name,
            "processed_at":    time.time(),
            "records_written": records_written,
        }
        self._save()


registry = ProcessingRegistry(tmp_dir / "registry.json")

print("Processing files (first run):")
for filepath in batch_files[:3]:
    if registry.is_processed(filepath):
        print(f"  SKIP (already processed): {filepath.name}")
    else:
        # Simulate processing
        records = list(filter_valid(validate_records(read_csv_records(filepath))))
        registry.mark_processed(filepath, len(records))
        print(f"  PROCESSED: {filepath.name} → {len(records)} records")

print("\nRe-running same files (idempotent):")
for filepath in batch_files[:3]:
    if registry.is_processed(filepath):
        print(f"  SKIP (already processed): {filepath.name}")
    else:
        print(f"  WOULD PROCESS: {filepath.name}")


print("\n=== File processing pipeline complete ===")
print("Key patterns:")
print("  Generator pipeline  → O(1) memory regardless of file count or size")
print("  Row-level errors    → collect, log, skip — don't abort the whole job")
print("  Atomic output       → write temp file, rename when complete")
print("  Idempotency         → content hash registry prevents double-processing")
