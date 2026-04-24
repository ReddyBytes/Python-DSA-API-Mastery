# 🎯 String Operations — Turning Raw Text Into Clean Features

> Raw text in a dataset is like ore in a mine. The `.str` accessor is the smelter — it turns messy, inconsistent strings into structured data a model can actually use.

Text data almost never arrives clean. Product names have inconsistent capitalization, emails have trailing spaces, user inputs mix formats. Before feeding text to a model or joining on a string key, you need to normalize, extract, and filter. Pandas handles all of this through the **`.str` accessor** — a vectorized layer that applies standard Python string methods (and regex) to an entire column at once, without a single Python loop. The difference in speed between `df['col'].apply(lambda x: x.strip())` and `df['col'].str.strip()` is the difference between C-speed and Python-speed across millions of rows.

---

## The .str Accessor — Vectorized String Power

In Python, string methods live on individual strings: `"hello".upper()`. Pandas wraps all of these — and adds regex power — behind the **`.str` accessor**, which applies the operation to every row at once without a loop.

```python
import pandas as pd

df = pd.DataFrame({
    "raw_text": ["  Hello World  ", "hello world", "HELLO WORLD", None]
})

df["lower"]   = df["raw_text"].str.lower()
df["upper"]   = df["raw_text"].str.upper()
df["stripped"] = df["raw_text"].str.strip()   # ← removes leading/trailing whitespace
df["length"]  = df["raw_text"].str.len()
```

Note: `.str` operations propagate `NaN` — a `None` input produces `NaN` output, not an error.

---

## .str.contains — Filtering by Pattern

**`.str.contains()`** returns a boolean Series — `True` if the pattern is found in that row. It's the vectorized version of `"pattern" in text`.

```python
# Find rows where text mentions a model name
mask = df["model_output"].str.contains("GPT", case=False, na=False)
                                                # ↑ na=False treats NaN as non-match
df_gpt = df[mask]

# Regex patterns work too
df["has_url"] = df["text"].str.contains(r"https?://\S+", regex=True, na=False)

# Negate: rows that do NOT contain a pattern
df_clean = df[~df["text"].str.contains(r"<[^>]+>", regex=True, na=False)]  # ← strip HTML rows
```

---

## .str.replace — Cleaning and Normalizing

**`.str.replace()`** substitutes patterns. With `regex=True` it becomes a full regex substitution — the most powerful string cleaning tool in Pandas.

```python
# Remove HTML tags from scraped training data
df["clean"] = df["raw"].str.replace(r"<[^>]+>", "", regex=True)

# Normalize whitespace (collapse multiple spaces to one)
df["clean"] = df["clean"].str.replace(r"\s+", " ", regex=True).str.strip()

# Replace literal string (no regex needed)
df["text"] = df["text"].str.replace("N/A", "", regex=False)

# Remove non-alphanumeric characters
df["clean"] = df["text"].str.replace(r"[^a-zA-Z0-9\s]", "", regex=True)
```

---

## .str.extract — Pulling Structure Out of Text

**`.str.extract()`** applies a regex with **capture groups** and returns the captured content as new columns. This is the bridge from unstructured text to structured features.

```python
# Extract version numbers from strings like "model-v2.3.1"
df["version"] = df["model_name"].str.extract(r"v(\d+\.\d+\.\d+)")
#                                               ↑ capture group returns the match

# Named groups → named columns (cleanest pattern)
pattern = r"(?P<endpoint>/\S+)\s+(?P<status_code>\d{3})\s+(?P<latency_ms>\d+)ms"
extracted = df["log_line"].str.extract(pattern)
# extracted now has columns: endpoint, status_code, latency_ms

df = pd.concat([df, extracted], axis=1)
```

Named groups with `(?P<name>...)` syntax are the preferred pattern — they self-document and produce correctly named DataFrame columns automatically.

---

## .str.findall — Extracting Multiple Matches

Where `.str.extract()` gets the first match, **`.str.findall()`** returns a list of ALL matches in each row. The result is a Series of lists.

```python
# Find all hashtags in social media posts
df["hashtags"] = df["post"].str.findall(r"#\w+")
# Result: each cell is a list like ["#ai", "#llm", "#python"]

# Count how many matches per row
df["hashtag_count"] = df["hashtags"].str.len()

# Extract all URLs from text
df["urls"] = df["text"].str.findall(r"https?://\S+")
```

---

## .str.split — Splitting Into Multiple Columns

**`.str.split()`** with `expand=True` turns a delimited string into multiple columns rather than a list. Essential for parsing structured fields stored as strings.

```python
# Split "first_name last_name" into two columns
df[["first", "last"]] = df["full_name"].str.split(" ", expand=True)
#                                        ↑ expand=True → DataFrame instead of list Series

# Split on delimiter — e.g., "category:subcategory:item"
df[["cat", "subcat", "item"]] = df["path"].str.split(":", n=2, expand=True)
#                                                     ↑ n=2 limits to 2 splits

# When number of parts varies: use without expand, then normalize
parts = df["tags"].str.split(",")  # each row is a list
exploded = df.assign(tag=parts).explode("tag")  # ← one row per tag
```

---

## Real Use — Extract and Clean Text for LLM Fine-Tuning

The following pipeline applies every `.str` technique to prepare a raw JSONL dataset for LLM fine-tuning: normalize whitespace, strip HTML artifacts, extract structured metadata with named capture groups, filter by quality score, and flag rows that contain PII patterns. Each step is a single vectorized operation — no loops, no `apply()`.

```python
import pandas as pd
import re

df = pd.read_json("raw_finetune_data.jsonl", lines=True)

# Step 1: Normalize whitespace in prompts
df["prompt"] = (
    df["prompt"]
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# Step 2: Remove HTML artifacts from scraped responses
df["completion"] = df["completion"].str.replace(r"<[^>]+>", "", regex=True)

# Step 3: Extract named metadata from source strings
# Source format: "domain=news | date=2024-03-15 | quality=4"
meta_pattern = r"domain=(?P<domain>\w+).*?date=(?P<date>[\d-]+).*?quality=(?P<quality>\d)"
meta = df["source_meta"].str.extract(meta_pattern)
df = pd.concat([df, meta], axis=1)

# Step 4: Filter to quality >= 3
df = df[df["quality"].astype(int) >= 3]

# Step 5: Flag rows with suspicious patterns
df["has_pii"] = df["completion"].str.contains(
    r"\b\d{3}-\d{2}-\d{4}\b",  # ← SSN pattern
    regex=True, na=False
)
df = df[~df["has_pii"]]

# Step 6: Check token length proxy (rough character estimate)
df["approx_tokens"] = df["completion"].str.len() / 4  # ← ~4 chars per token
df = df[df["approx_tokens"] <= 512]

# Export clean dataset
df[["prompt", "completion"]].to_json(
    "clean_finetune.jsonl", orient="records", lines=True
)
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Module Home | [theory.md](./README.md) |
