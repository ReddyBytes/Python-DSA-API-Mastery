# 🎯 GroupBy Advanced — Aggregating, Transforming, and Ranking Groups

> GroupBy is like sorting mail into labeled bins, then doing math on each bin independently. The key question is: do you want one result per bin, or one result per original letter?

`groupby` is one of the most powerful operations in Pandas, but also the most misused. Most people know the basic `groupby('col').sum()` pattern. What separates a beginner from a practitioner is knowing when to use `agg()` vs `transform()`, how to compute running totals within groups, how to rank rows relative to their peers, and how to group by time periods with `pd.Grouper`. These patterns appear constantly in feature engineering, leaderboard calculations, and user behavior analysis.

---

## The Core Mental Model — Aggregate vs Transform

This is the single most important distinction in GroupBy:

- **`.agg()`** — reduces each group to one row. Output is smaller than input.
- **`.transform()`** — applies a function per group but keeps the original shape. Output is the same size as input, aligned row-for-row.

```python
import pandas as pd

df = pd.DataFrame({
    "user_id": ["A", "A", "B", "B", "B"],
    "score":   [80,  90,  70,  85,  95],
})

# agg: one row per user (2 rows out)
user_means = df.groupby("user_id")["score"].agg("mean")
# user_id
# A    85.0
# B    83.33

# transform: same shape as df (5 rows out), each row gets its group mean
df["group_mean"] = df.groupby("user_id")["score"].transform("mean")
# df now has a new column where A rows = 85.0, B rows = 83.33
```

The power of `transform`: you can subtract the group mean from each row in one line — the basis of **group normalization**.

---

## Normalizing Scores Within Each Group

Where `agg()` collapses rows, **`transform()`** broadcasts — it computes a group statistic and maps it back to every row in that group. This is how you compute "what fraction of the group's total does this row represent?" in a single operation.

```python
# Z-score within each user group
df["score_normalized"] = df.groupby("user_id")["score"].transform(
    lambda x: (x - x.mean()) / x.std()
)

# Min-max normalize within group
df["score_minmax"] = df.groupby("user_id")["score"].transform(
    lambda x: (x - x.min()) / (x.max() - x.min())
)
```

This is used in ML pipelines to prevent a single user's high absolute scores from dominating a model that should compare users against their own baselines.

---

## Cumulative Operations Per Group

**Cumulative operations** answer "what was the running total at each point in time, restarted per group?"

```python
# Sort first — cumulative operations are order-sensitive
df = df.sort_values(["user_id", "timestamp"])

# Running total of API calls per user
df["cumulative_calls"] = df.groupby("user_id")["request_count"].cumsum()

# Cumulative count: effectively the row number within each group (1-indexed)
df["event_number"] = df.groupby("user_id").cumcount() + 1  # ← +1 makes it 1-indexed

# Running minimum/maximum
df["best_score_so_far"] = df.groupby("user_id")["score"].cummax()
```

---

## Ranking Within a Group

**Rank within group** answers "where does this row stand relative to others in the same group?" — without sorting the DataFrame.

```python
# Rank scores within each user group (highest score = rank 1)
df["rank_in_group"] = df.groupby("user_id")["score"].rank(
    method="dense",      # ← dense: no gaps in ranks (1,2,2,3 not 1,2,2,4)
    ascending=False      # ← highest value = rank 1
)

# method options:
# "average" — tied rows get averaged rank (default)
# "min"     — tied rows get the minimum rank
# "max"     — tied rows get the maximum rank
# "dense"   — no rank gaps for ties (most intuitive)
# "first"   — tied rows get rank in order of appearance
```

---

## Filtering Groups by Size

Sometimes you want to drop groups that are too small to be statistically meaningful. **`.filter()`** on a GroupBy object removes entire groups.

```python
# Keep only users with at least 10 events
df_filtered = df.groupby("user_id").filter(lambda x: len(x) >= 10)

# Keep groups where mean score is above threshold
df_high = df.groupby("user_id").filter(lambda x: x["score"].mean() > 75)

# Check group sizes first
group_sizes = df.groupby("user_id").size().sort_values(ascending=False)
print(group_sizes.head(10))
```

---

## Multiple Aggregations with Named Outputs

**Named aggregations** let you define the output column name and aggregation function together in a single `.agg()` call, making the intent of each summary column explicit. This is the preferred pattern over the older dict-of-lists syntax, and it composes cleanly with custom lambda functions.

```python
summary = df.groupby("user_id").agg(
    mean_score=("score", "mean"),          # ← named output columns
    max_score=("score", "max"),
    total_requests=("request_id", "count"),
    first_seen=("timestamp", "min"),
    last_seen=("timestamp", "max"),
)

# Custom aggregation function
summary = df.groupby("user_id")["score"].agg([
    ("p25", lambda x: x.quantile(0.25)),
    ("p75", lambda x: x.quantile(0.75)),
    ("iqr", lambda x: x.quantile(0.75) - x.quantile(0.25)),
])
```

---

## pd.Grouper — Time-Based Grouping

**`pd.Grouper`** is the bridge between GroupBy and time series. It lets you group by time frequency AND another column simultaneously.

```python
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.set_index("timestamp")

# Requests per user per hour
hourly_per_user = df.groupby(
    [pd.Grouper(freq="h"), "user_id"]  # ← group by hour AND user
)["request_id"].count().reset_index()

# Daily error rate per endpoint
daily_errors = df.groupby(
    [pd.Grouper(freq="D"), "endpoint"]
).agg(
    error_count=("is_error", "sum"),
    total_requests=("request_id", "count"),
).reset_index()

daily_errors["error_rate"] = daily_errors["error_count"] / daily_errors["total_requests"]
```

---

## Real Use — Normalize Scores Within Each User Group

This end-to-end example combines the key GroupBy tools: filter by group size to remove unreliable groups, z-score normalize within each group, rank within group, and compute a running best-so-far. Each step builds on the previous, producing a DataFrame that is ready for downstream ML feature extraction.

```python
import pandas as pd

# Scenario: leaderboard where users have vastly different score ranges.
# Raw scores are not comparable across users — a "90" from a hard grader
# is not the same as a "90" from an easy one. Normalize within each group.

df = pd.read_csv("user_scores.csv")

# 1. Flag small groups (too few samples for reliable normalization)
group_sizes = df.groupby("user_id").transform("count")["score"]
df = df[group_sizes >= 5]  # ← require at least 5 samples per group

# 2. Z-score normalization per user
df["score_z"] = df.groupby("user_id")["score"].transform(
    lambda x: (x - x.mean()) / x.std()
)

# 3. Rank within group (1 = best)
df["rank"] = df.groupby("user_id")["score"].rank(method="dense", ascending=False)

# 4. Cumulative best per user over time
df = df.sort_values(["user_id", "date"])
df["best_so_far"] = df.groupby("user_id")["score"].cummax()

# 5. Summary table per user
summary = df.groupby("user_id").agg(
    n_samples=("score", "count"),
    raw_mean=("score", "mean"),
    z_mean=("score_z", "mean"),   # should be ~0 after normalization
    top_score=("score", "max"),
)

print(summary)
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Module Home | [theory.md](./README.md) |
