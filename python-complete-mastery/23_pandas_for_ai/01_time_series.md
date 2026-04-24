# 🎯 Time Series — Taming Data With a Clock

> A server log without timestamps is just a list of complaints. With timestamps, it becomes a story — when traffic spiked, when errors clustered, when users slept.

Time series data is everywhere in production ML — server logs, sensor readings, user activity streams, financial prices. What makes it different from regular tabular data is the **time dimension**: order matters, adjacent rows are related, and patterns like "what happened in the hour before a spike?" are only visible when you treat timestamps as a first-class axis. Pandas has a dedicated toolkit for this — datetime parsing, resampling, rolling windows, lag features — that turns raw timestamped rows into a rich set of features a model can actually learn from.

---

## DateTime Parsing — Teaching Pandas to Read Clocks

**DateTime parsing** is the act of converting a raw string like `"2024-03-15 14:32:01"` into a Python object that understands concepts like "hour", "day of week", and "3 days later".

```python
import pandas as pd

# pd.to_datetime() is the front door
df["timestamp"] = pd.to_datetime(df["timestamp"])

# When format is ambiguous, be explicit
df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S")

# Parsing directly at load time — most efficient path
df = pd.read_csv("api_logs.csv", parse_dates=["timestamp"])

# Unix epoch integers (common in API logs)
df["timestamp"] = pd.to_datetime(df["ts_epoch"], unit="s")  # ← seconds since 1970
```

The result is a `datetime64[ns]` column — the native Pandas time type. All time-aware operations flow from this.

---

## The .dt Accessor — Your Clock Toolkit

Once a column is `datetime64`, the **`.dt` accessor** unlocks a full set of calendar-aware properties. Think of it as asking "what does this moment look like on a calendar?"

```python
df["hour"]       = df["timestamp"].dt.hour         # 0–23
df["day_of_week"] = df["timestamp"].dt.day_name()  # "Monday", "Tuesday", ...
df["month"]      = df["timestamp"].dt.month        # 1–12
df["date"]       = df["timestamp"].dt.date         # strips time, keeps date
df["week"]       = df["timestamp"].dt.isocalendar().week  # ISO week number
df["quarter"]    = df["timestamp"].dt.quarter       # 1–4

# Is it a weekday? Useful for filtering business hours traffic
df["is_weekday"] = df["timestamp"].dt.dayofweek < 5  # ← Mon=0, Sun=6
```

Real use: add `hour` and `day_of_week` as features for an API latency prediction model.

---

## Setting the Index — Unlocking Time-Aware Operations

**Resampling** and many rolling operations require the DataFrame's index to be the datetime column. This is the setup step most tutorials skip.

```python
df = df.set_index("timestamp")       # make time the row label
df = df.sort_index()                 # always sort — resampling assumes order

# To undo:
df = df.reset_index()
```

---

## Resampling — Changing the Clock Resolution

**Resampling** is like zooming in or out on a timeline. You have per-second data; you want per-hour summaries. That is downsampling.

```python
# Count API requests per hour
hourly_requests = df["request_id"].resample("h").count()

# Average latency per day
daily_latency = df["latency_ms"].resample("D").mean()

# Total errors per week
weekly_errors = df["is_error"].resample("W").sum()

# Multiple aggregations at once
summary = df["latency_ms"].resample("h").agg(["mean", "max", "count"])
```

Common **frequency strings**: `"min"` (minute), `"h"` (hour), `"D"` (day), `"W"` (week), `"ME"` (month end), `"QE"` (quarter end).

---

## Rolling Windows — Smoothing Noise Into Signal

A **rolling window** is a moving calculation — at each row, look back N steps and compute something. Think of it as a "sliding average" that follows you through time.

```python
# 24-hour rolling mean of request count (smooths hourly spikes)
df["rolling_24h_mean"] = df["request_count"].rolling(window=24).mean()

# Rolling max — useful for detecting sustained high latency
df["rolling_max_latency"] = df["latency_ms"].rolling(window=10).max()

# min_periods: compute even when the window isn't full yet
df["rolling_mean"] = df["latency_ms"].rolling(window=7, min_periods=1).mean()
```

The first `window - 1` rows will be `NaN` by default — this is expected. The window "fills up" before producing values.

---

## EWM — Exponentially Weighted Moving Average

**EWM (Exponentially Weighted Moving)** is like a rolling average that cares more about recent values. A data center ops team monitoring API latency uses EWM because a spike 10 minutes ago matters more than one from yesterday.

```python
# span=12 means recent 12 data points get most of the weight
df["ewm_latency"] = df["latency_ms"].ewm(span=12, adjust=False).mean()

# alpha directly controls decay: higher alpha = more weight on recent data
df["ewm_alpha"] = df["latency_ms"].ewm(alpha=0.3, adjust=False).mean()
```

EWM never has `NaN` gaps the way rolling does — it starts computing from row 0.

---

## Time Deltas — Measuring Duration

A **timedelta** is the gap between two timestamps. It's how you answer "how long did this request take from submission to completion?"

```python
df["response_time"] = df["completed_at"] - df["submitted_at"]  # ← timedelta column

# Extract numeric components
df["seconds"] = df["response_time"].dt.total_seconds()
df["minutes"] = df["response_time"].dt.total_seconds() / 60

# Filter by duration
slow_requests = df[df["response_time"] > pd.Timedelta("5s")]

# Add fixed offsets
df["deadline"] = df["submitted_at"] + pd.Timedelta(hours=24)
```

---

## Shift and Lag Features — Teaching the Model What Happened Before

**Lag features** are one of the most powerful tools in time-series ML. The idea: the value at time `t-1` is often a strong predictor of the value at time `t`.

```python
# Lag: previous row's value (shift forward by 1)
df["latency_lag_1"] = df["latency_ms"].shift(1)   # ← value from 1 step ago
df["latency_lag_2"] = df["latency_ms"].shift(2)

# Lead: next row's value (shift backward — for target leakage checks)
df["latency_next"]  = df["latency_ms"].shift(-1)

# Difference from previous row: captures rate of change
df["latency_delta"] = df["latency_ms"].diff(1)     # ← equivalent to value - shift(1)
```

Warning: `shift()` introduces `NaN` in the first (or last) rows. Drop them before training: `df.dropna(inplace=True)`.

---

## Real Use — Analyze API Request Logs by Hour

The following script ties every technique together: parse timestamps at load time, set the datetime index, extract calendar features, compute rolling statistics, build lag features, and resample to hourly summaries. This is the full feature-engineering pipeline you would run before feeding API log data into a latency prediction model.

```python
import pandas as pd

# Load raw API logs
df = pd.read_csv("api_logs.csv", parse_dates=["timestamp"])
df = df.set_index("timestamp").sort_index()

# Feature engineering for a latency model
df["hour"]        = df.index.hour
df["day_of_week"] = df.index.day_name()
df["is_weekend"]  = df.index.dayofweek >= 5

# Rolling baseline: smooth 6-hour window
df["rolling_latency_6h"] = df["latency_ms"].rolling("6h").mean()  # ← time-based window

# Lag feature
df["latency_lag_1h"] = df["latency_ms"].shift(1)

# Hourly summary for visualization
hourly = df["latency_ms"].resample("h").agg(
    mean_latency=("mean"),
    p95_latency=lambda x: x.quantile(0.95),
    request_count=("count"),
)

print(hourly.head(24))
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Module Home | [theory.md](./README.md) |
