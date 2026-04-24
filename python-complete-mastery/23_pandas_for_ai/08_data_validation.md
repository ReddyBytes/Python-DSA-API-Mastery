# 🎯 Data Validation — Catching Problems Before They Reach Your Model

> A model trained on bad data learns bad patterns — and does so confidently. Validation is the quality gate you run before training, not after debugging a mysterious accuracy drop.

A model is only as good as the data it trains on. Silent data quality issues — columns that changed dtype, features whose range doubled, duplicate rows that inflate class counts — are harder to debug than code bugs because they don't raise exceptions. They just silently shift your model's behavior. **Data validation** is the quality gate you run before any training or inference: asserting column schemas, checking null rates, verifying value ranges, and flagging duplicate records. It is the difference between catching a broken data pipeline in minutes and debugging a model degradation for days.

---

## Why Validation Matters in ML Pipelines

Imagine a training pipeline that runs every night. One night, an upstream database migration silently changes a column from integer to string. No error is raised. The model retrains on corrupted data. Accuracy drops by 8 points. You spend three days debugging.

**Data validation** is the practice of asserting properties about your data — schema, ranges, null rates, uniqueness — before passing it downstream. Catching this at ingestion time takes minutes to fix. Catching it after training takes days.

---
## Schema Validation — Checking Column Types and Presence

**Schema validation** checks that the DataFrame has the right columns with the right data types. It's the first gate — if the schema is wrong, nothing else is reliable.

```python
import pandas as pd

def validate_schema(df, expected_schema):
    """
    expected_schema: dict of {column_name: expected_dtype_string}
    Example: {"age": "int64", "score": "float64", "label": "object"}
    
    Returns a list of violations.
    """
    violations = []

    for col, expected_dtype in expected_schema.items():
        if col not in df.columns:
            violations.append(f"MISSING COLUMN: '{col}'")
        elif str(df[col].dtype) != expected_dtype:
            actual = str(df[col].dtype)
            violations.append(
                f"TYPE MISMATCH: '{col}' expected={expected_dtype} actual={actual}"
            )

    extra_cols = set(df.columns) - set(expected_schema.keys())
    if extra_cols:
        violations.append(f"UNEXPECTED COLUMNS: {sorted(extra_cols)}")

    return violations

# Define your expected schema
TRAINING_SCHEMA = {
    "user_id":     "object",
    "age":         "int64",
    "score":       "float64",
    "label":       "int64",
    "source":      "object",
}

violations = validate_schema(df, TRAINING_SCHEMA)
if violations:
    for v in violations:
        print(f"  VIOLATION: {v}")
    raise ValueError(f"Schema validation failed with {len(violations)} violation(s)")
```

---
## Null Rate Audit — Understanding Missingness

Different null rates require different responses: 0% is ideal, <5% can usually be imputed, >30% may mean the column is useless, 100% means a pipeline broke.

```python
def null_rate_audit(df, max_allowed_null_rate=0.05):
    """
    Returns a DataFrame summarizing null rates per column.
    Flags columns above max_allowed_null_rate.
    """
    total = len(df)
    report = pd.DataFrame({
        "null_count": df.isnull().sum(),
        "null_rate":  df.isnull().mean().round(4),
        "dtype":      df.dtypes.astype(str),
    })
    report["flag"] = report["null_rate"] > max_allowed_null_rate

    return report.sort_values("null_rate", ascending=False)

null_report = null_rate_audit(df, max_allowed_null_rate=0.05)
print(null_report)

# Hard assertion: no nulls in critical columns
critical_cols = ["label", "user_id", "score"]
for col in critical_cols:
    null_count = df[col].isnull().sum()
    assert null_count == 0, f"Critical column '{col}' has {null_count} null values"
```

---
## Range Checks With Assert — Enforcing Business Rules

**Range checks** assert that numeric values fall within expected bounds. They catch data entry errors, unit mismatches (milliseconds vs seconds), and upstream schema changes.

```python
# Assert statements are the simplest range checks
# They raise AssertionError immediately if the condition fails

assert df["age"].between(0, 120).all(), \
    f"Age out of range: min={df['age'].min()}, max={df['age'].max()}"

assert df["score"].between(0.0, 1.0).all(), \
    f"Score not normalized: found values outside [0, 1]"

assert (df["probability"] >= 0).all() and (df["probability"] <= 1).all(), \
    "Probability values outside valid range [0, 1]"

# For soft checks (warn but don't fail):
def check_range(series, low, high, column_name, strict=True):
    violations = series[(series < low) | (series > high)]
    if len(violations) > 0:
        msg = f"'{column_name}': {len(violations)} rows outside [{low}, {high}]"
        if strict:
            raise ValueError(msg)
        else:
            print(f"WARNING: {msg}")

check_range(df["latency_ms"], 0, 30_000, "latency_ms", strict=False)
```

---
## Uniqueness Checks — Detecting Accidental Duplicates

**Duplicates** in training data cause a model to see the same example multiple times, which inflates its confidence in those patterns and can cause data leakage if a duplicate straddles train and test.

```python
# Check for fully duplicate rows
n_duplicates = df.duplicated().sum()
assert n_duplicates == 0, f"Found {n_duplicates} fully duplicate rows"

# Check for duplicate primary keys (should be unique per row)
n_dup_ids = df["sample_id"].duplicated().sum()
assert n_dup_ids == 0, f"sample_id has {n_dup_ids} duplicate values"

# Check for near-duplicates in text data (same text, different ID)
duplicate_texts = df["prompt"].duplicated().sum()
if duplicate_texts > 0:
    print(f"WARNING: {duplicate_texts} rows have duplicate 'prompt' values")
    # Show examples
    print(df[df["prompt"].duplicated(keep=False)][["sample_id", "prompt"]].head(5))
```

---
## Value Set Validation — Catching Invalid Categories

**Value set validation** checks that categorical columns only contain expected values. A new category that wasn't in training (e.g., a new region code from an API change) can silently break one-hot encoding.

```python
VALID_LABELS   = {0, 1}
VALID_SOURCES  = {"reddit", "twitter", "news", "academic", "synthetic"}
VALID_LANGUAGES = {"en", "fr", "de", "es", "zh"}

def check_value_set(series, valid_values, column_name):
    """Check that all values in the series are in the valid set."""
    actual_values = set(series.dropna().unique())
    unexpected = actual_values - valid_values
    if unexpected:
        raise ValueError(
            f"'{column_name}' contains unexpected values: {unexpected}"
            f"\n  Expected: {valid_values}"
        )

check_value_set(df["label"],    VALID_LABELS,    "label")
check_value_set(df["source"],   VALID_SOURCES,   "source")
check_value_set(df["language"], VALID_LANGUAGES, "language")

# Soft version: warn and report counts
def audit_value_set(series, valid_values, column_name):
    counts = series.value_counts()
    unexpected = counts[~counts.index.isin(valid_values)]
    if len(unexpected) > 0:
        print(f"WARNING '{column_name}' unexpected values:\n{unexpected}")
    return unexpected
```

---
## Reusable validate_dataset() — A Complete Quality Report

This function runs all checks and returns a structured quality report — designed to be called at the start of every training pipeline run.

```python
import pandas as pd
import numpy as np

def validate_dataset(
    df,
    expected_schema=None,
    critical_cols=None,
    range_checks=None,
    unique_cols=None,
    value_set_checks=None,
    max_null_rate=0.05,
    raise_on_error=True,
):
    """
    Run a full data quality audit and return a quality report dict.

    Parameters
    ----------
    df              : DataFrame to validate
    expected_schema : dict {col: dtype_str} — schema validation
    critical_cols   : list of columns that must have zero nulls
    range_checks    : dict {col: (min, max)} — numeric range validation
    unique_cols     : list of columns that must be fully unique
    value_set_checks: dict {col: set_of_valid_values}
    max_null_rate   : float — flag columns with null rate above this
    raise_on_error  : if True, raises ValueError on any violation

    Returns
    -------
    dict with keys: passed, violations, warnings, stats
    """
    violations = []
    warnings   = []
    stats      = {}

    # ── Basic stats ──────────────────────────────────────────────────────────
    stats["shape"]          = df.shape
    stats["total_rows"]     = len(df)
    stats["total_columns"]  = len(df.columns)
    stats["memory_mb"]      = df.memory_usage(deep=True).sum() / 1e6

    # ── Schema validation ─────────────────────────────────────────────────────
    if expected_schema:
        for col, expected_dtype in expected_schema.items():
            if col not in df.columns:
                violations.append(f"MISSING_COLUMN: '{col}'")
            elif str(df[col].dtype) != expected_dtype:
                violations.append(
                    f"TYPE_MISMATCH: '{col}' expected={expected_dtype} "
                    f"actual={df[col].dtype}"
                )

    # ── Null rate audit ───────────────────────────────────────────────────────
    null_rates = df.isnull().mean()
    stats["null_rates"] = null_rates[null_rates > 0].round(4).to_dict()

    if critical_cols:
        for col in critical_cols:
            if col in df.columns:
                n_nulls = df[col].isnull().sum()
                if n_nulls > 0:
                    violations.append(f"NULL_IN_CRITICAL_COL: '{col}' has {n_nulls} nulls")

    high_null_cols = null_rates[null_rates > max_null_rate].index.tolist()
    if high_null_cols:
        warnings.append(f"HIGH_NULL_RATE (>{max_null_rate:.0%}): {high_null_cols}")

    # ── Range checks ─────────────────────────────────────────────────────────
    if range_checks:
        for col, (low, high) in range_checks.items():
            if col in df.columns:
                out_of_range = df[(df[col] < low) | (df[col] > high)]
                if len(out_of_range) > 0:
                    violations.append(
                        f"RANGE_VIOLATION: '{col}' has {len(out_of_range)} rows "
                        f"outside [{low}, {high}]"
                    )

    # ── Uniqueness checks ─────────────────────────────────────────────────────
    if unique_cols:
        for col in unique_cols:
            if col in df.columns:
                n_dups = df[col].duplicated().sum()
                if n_dups > 0:
                    violations.append(f"DUPLICATE_VALUES: '{col}' has {n_dups} duplicates")

    # ── Duplicate rows ─────────────────────────────────────────────────────────
    n_dup_rows = df.duplicated().sum()
    if n_dup_rows > 0:
        warnings.append(f"DUPLICATE_ROWS: {n_dup_rows} fully duplicate rows found")
    stats["duplicate_rows"] = int(n_dup_rows)

    # ── Value set checks ──────────────────────────────────────────────────────
    if value_set_checks:
        for col, valid_values in value_set_checks.items():
            if col in df.columns:
                unexpected = set(df[col].dropna().unique()) - set(valid_values)
                if unexpected:
                    violations.append(
                        f"INVALID_VALUES: '{col}' contains {unexpected}"
                    )

    # ── Summary ───────────────────────────────────────────────────────────────
    passed = len(violations) == 0
    report = {
        "passed":     passed,
        "violations": violations,
        "warnings":   warnings,
        "stats":      stats,
    }

    # Print summary
    status = "PASSED" if passed else "FAILED"
    print(f"\n=== Data Validation: {status} ===")
    print(f"  Rows: {stats['total_rows']:,} | Columns: {stats['total_columns']}")
    print(f"  Memory: {stats['memory_mb']:.1f} MB")

    if violations:
        print(f"\n  VIOLATIONS ({len(violations)}):")
        for v in violations:
            print(f"    - {v}")

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    - {w}")

    if raise_on_error and not passed:
        raise ValueError(
            f"Dataset validation failed with {len(violations)} violation(s). "
            "Fix violations before proceeding."
        )

    return report


# ── Example usage ─────────────────────────────────────────────────────────────
report = validate_dataset(
    df=df_train,
    expected_schema={
        "user_id": "object",
        "score":   "float64",
        "label":   "int64",
        "source":  "object",
    },
    critical_cols=["label", "score"],
    range_checks={
        "score":       (0.0, 100.0),
        "age":         (0, 120),
        "probability": (0.0, 1.0),
    },
    unique_cols=["sample_id"],
    value_set_checks={
        "label":  {0, 1},
        "source": {"reddit", "news", "academic"},
    },
    max_null_rate=0.05,
    raise_on_error=True,
)

# Access the report programmatically
if report["passed"]:
    print(f"\nDataset validated. Proceeding with {report['stats']['total_rows']:,} rows.")
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Module Home | [theory.md](./README.md) |
