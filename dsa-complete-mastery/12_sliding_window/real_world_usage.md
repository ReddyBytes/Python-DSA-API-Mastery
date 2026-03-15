# Sliding Window — Real-World Usage

The sliding window technique maintains a running view over a contiguous
subarray or substring, adding elements on the right and removing elements on
the left without recomputing from scratch. It reduces O(n * k) brute-force
approaches to O(n). It is everywhere in production: monitoring dashboards,
API gateways, financial analytics, search engines, bioinformatics pipelines,
and log analysis systems.

---

## 1. Network Monitoring — Average Latency Over Last N Requests

### The Production Problem

Observability platforms (Datadog, New Relic, Prometheus) compute rolling
averages of response latency continuously. A naive implementation recomputes
the sum of the last N values from scratch on every new reading — O(k) per
update. The sliding window maintains a running sum: add the new value, subtract
the value that just left the window. This is O(1) per update, which matters at
thousands of requests per second.

```python
from collections import deque
import time
import random

# -----------------------------------------------------------------------
# Fixed-size sliding window for rolling statistics
# -----------------------------------------------------------------------

class NetworkMonitor:
    """
    Real-time network latency monitor using a fixed sliding window.
    Maintains rolling average, min, max, and p95 over the last N requests.

    This is how APM (Application Performance Monitoring) tools like
    Datadog, New Relic, and AWS CloudWatch compute rolling metrics
    without storing the full history of every request.
    """

    def __init__(self, window_size: int):
        self.window_size  = window_size
        self._window      = deque(maxlen=window_size)  # last N latencies
        self._running_sum = 0.0
        self._total_count = 0
        self._alert_threshold_ms = 200.0

    def add_latency(self, latency_ms: float) -> None:
        """
        Record a new latency measurement.
        O(1): add to right of deque, sum update is constant time.
        When window is full, deque automatically evicts the oldest value.
        """
        if len(self._window) == self.window_size:
            # Remove the oldest reading from the running sum before eviction
            self._running_sum -= self._window[0]

        self._window.append(latency_ms)
        self._running_sum += latency_ms
        self._total_count += 1

    def get_avg_latency(self) -> float:
        """Rolling average over current window. O(1)."""
        if not self._window:
            return 0.0
        return self._running_sum / len(self._window)

    def get_min_latency(self) -> float:
        """O(k) — in production, a monotonic deque gives O(1)."""
        return min(self._window) if self._window else 0.0

    def get_max_latency(self) -> float:
        return max(self._window) if self._window else 0.0

    def get_p95_latency(self) -> float:
        """95th percentile over current window."""
        if not self._window:
            return 0.0
        sorted_window = sorted(self._window)
        idx = int(0.95 * len(sorted_window))
        return sorted_window[min(idx, len(sorted_window) - 1)]

    def is_degraded(self) -> bool:
        """Return True if rolling average exceeds alert threshold."""
        return self.get_avg_latency() > self._alert_threshold_ms

    def get_stats(self) -> dict:
        return {
            "window_size"     : self.window_size,
            "samples_in_window": len(self._window),
            "total_requests"  : self._total_count,
            "avg_ms"          : round(self.get_avg_latency(), 2),
            "min_ms"          : round(self.get_min_latency(), 2),
            "max_ms"          : round(self.get_max_latency(), 2),
            "p95_ms"          : round(self.get_p95_latency(), 2),
            "status"          : "DEGRADED" if self.is_degraded() else "OK",
        }


# -----------------------------------------------------------------------
# Demo: simulate a microservice with a latency spike
# -----------------------------------------------------------------------

random.seed(42)
monitor = NetworkMonitor(window_size=100)

print("Simulating 300 requests to api.example.com/v1/users")
print(f"Window size: {monitor.window_size} requests\n")
print(f"{'Request':>8}  {'Latency':>10}  {'Roll.Avg':>10}  {'P95':>10}  {'Status'}")
print("-" * 60)

for i in range(1, 301):
    # Simulate a latency spike between requests 150-200 (e.g., DB overload)
    if 150 <= i <= 200:
        latency = random.gauss(400, 50)   # degraded: avg 400ms
    else:
        latency = random.gauss(80, 15)    # normal: avg 80ms

    monitor.add_latency(max(1.0, latency))

    if i % 50 == 0 or (145 <= i <= 155) or (195 <= i <= 205):
        stats = monitor.get_stats()
        print(f"{i:>8}  {latency:>9.1f}ms  {stats['avg_ms']:>9.1f}ms"
              f"  {stats['p95_ms']:>9.1f}ms  {stats['status']}")

print(f"\nFinal stats: {monitor.get_stats()}")
```

---

## 2. Rate Limiting — Sliding Window Rate Limiter

### The Production Problem

Every production API (Stripe, GitHub, Twitter/X, Cloudflare) enforces rate
limits: "at most N requests per time window per user." Naive fixed-window rate
limiting (reset counter at the start of each second) has a boundary problem: a
user can send N requests at 00:59 and N more at 01:01 and receive 2N requests
in 2 seconds. The sliding window approach timestamps each request and counts
only requests in the last T seconds, solving the boundary problem exactly.
This is what Cloudflare, NGINX's `limit_req`, and Redis-backed rate limiters use.

```python
from collections import deque
import time as time_module

# -----------------------------------------------------------------------
# Sliding window rate limiter using a timestamped deque
# -----------------------------------------------------------------------

class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter — allows at most `max_requests` in any
    rolling window of `window_seconds` seconds.

    Algorithm:
    1. Maintain a deque of timestamps of past requests for each client.
    2. On each new request, evict timestamps older than (now - window).
    3. If remaining count < max_requests, allow and record the timestamp.
    4. Otherwise, deny and return the retry-after time.

    This is the algorithm used by:
      - Redis with sorted sets (ZADD + ZCOUNT + ZREMRANGEBYSCORE)
      - Nginx `limit_req_zone` with leaky bucket variant
      - Cloudflare's rate limiting product
      - GitHub API's rate limiter (5000 req/hour per token)

    Space: O(max_requests) per client — bounded by the window size.
    Time:  O(1) amortized per request (each timestamp added and removed once).
    """

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests    = max_requests
        self.window_seconds  = window_seconds
        # Per-client request history: client_id -> deque of timestamps
        self._clients: dict[str, deque] = {}

    def allow_request(self, client_id: str, current_time: float = None) -> tuple[bool, dict]:
        """
        Check if a request from `client_id` should be allowed.

        Returns (allowed: bool, info: dict) where info contains:
          - remaining: requests left in this window
          - reset_in:  seconds until the window resets (oldest request expires)
          - retry_after: seconds to wait if denied
        """
        now = current_time if current_time is not None else time_module.time()

        if client_id not in self._clients:
            self._clients[client_id] = deque()

        timestamps = self._clients[client_id]
        window_start = now - self.window_seconds

        # Evict timestamps outside the current window (sliding window shrinks on left)
        while timestamps and timestamps[0] <= window_start:
            timestamps.popleft()

        current_count = len(timestamps)

        if current_count < self.max_requests:
            # Allow: record this request's timestamp
            timestamps.append(now)
            remaining = self.max_requests - current_count - 1
            reset_in  = (timestamps[0] + self.window_seconds - now) if timestamps else self.window_seconds
            return True, {
                "allowed"    : True,
                "remaining"  : remaining,
                "used"       : current_count + 1,
                "reset_in"   : round(reset_in, 2),
                "retry_after": 0,
            }
        else:
            # Deny: calculate when the oldest request will expire
            retry_after = timestamps[0] + self.window_seconds - now
            return False, {
                "allowed"    : False,
                "remaining"  : 0,
                "used"       : current_count,
                "reset_in"   : round(retry_after, 2),
                "retry_after": round(retry_after, 2),
            }

    def get_usage(self, client_id: str, current_time: float = None) -> dict:
        """Get current rate limit status without making a request."""
        now = current_time if current_time is not None else time_module.time()
        if client_id not in self._clients:
            return {"used": 0, "remaining": self.max_requests}

        timestamps = self._clients[client_id]
        window_start = now - self.window_seconds
        active = sum(1 for t in timestamps if t > window_start)
        return {"used": active, "remaining": self.max_requests - active}


# -----------------------------------------------------------------------
# Demo: simulate burst traffic and rate limiting
# -----------------------------------------------------------------------

limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60.0)

print("Rate Limiter: 10 requests per 60 seconds")
print("Simulating burst traffic from two clients\n")

# Simulate time manually for deterministic demo
t = 0.0

print("=== Client alice@example.com ===")
for i in range(15):
    t_request = t + i * 3.0  # one request every 3 seconds
    allowed, info = limiter.allow_request("alice", t_request)
    status = "ALLOWED" if allowed else "DENIED "
    print(f"  t={t_request:5.1f}s  Request #{i+1:2d}: {status}  "
          f"(used={info['used']}/{limiter.max_requests}, "
          f"retry_after={info['retry_after']}s)")

print("\n=== Client bob@example.com (burst — 15 requests at t=0) ===")
for i in range(15):
    allowed, info = limiter.allow_request("bob", current_time=0.0)
    status = "ALLOWED" if allowed else "DENIED "
    print(f"  t=0.0s   Request #{i+1:2d}: {status}  "
          f"(used={info['used']}/{limiter.max_requests}, "
          f"retry_after={info['retry_after']}s)")

# Show that bob's window resets after 60 seconds
print(f"\n  [60 seconds later]")
for i in range(3):
    allowed, info = limiter.allow_request("bob", current_time=61.0 + i)
    status = "ALLOWED" if allowed else "DENIED "
    print(f"  t=61.0s  Request #{i+1}: {status}  (used={info['used']}/{limiter.max_requests})")
```

---

## 3. Stock Market Analysis — Maximum Profit in Any K Consecutive Days

### The Production Problem

Quantitative trading firms compute the maximum achievable return in any
consecutive K-day window across a stock's full price history. Risk analysts use
this to measure maximum short-term drawdown potential. The sliding window
approach: maintain a running sum of daily returns, slide the window across all
possible K-day periods, track the maximum. This is O(n) vs O(n * k) brute force.

```python
from typing import Optional
import random

# -----------------------------------------------------------------------
# Maximum profit over any K consecutive days using sliding window
# -----------------------------------------------------------------------

def max_profit_k_days(
    prices: list[float],
    k: int
) -> tuple[float, int, int, list[float]]:
    """
    Find the maximum total return (sum of daily price changes) in any
    consecutive window of k days.

    This is not the same as "buy and sell once" — it's the maximum
    cumulative gain from holding a position for exactly k consecutive days.

    Used by quantitative analysts for:
      - Backtesting momentum strategies
      - Computing maximum drawdown over rolling windows
      - Identifying historically optimal entry windows

    Returns: (max_profit, start_day, end_day, prices_in_window)
    Time:  O(n)
    Space: O(k)
    """
    if len(prices) < k + 1:
        raise ValueError(f"Need at least {k+1} prices for a {k}-day window")

    # Convert prices to daily returns (price changes)
    daily_returns = [prices[i] - prices[i - 1] for i in range(1, len(prices))]

    # Initialize the first window
    window_sum = sum(daily_returns[:k])
    max_sum    = window_sum
    max_start  = 0   # index into daily_returns
    cur_start  = 0

    # Slide the window
    for i in range(k, len(daily_returns)):
        # Add the new day's return, remove the oldest day's return
        window_sum += daily_returns[i] - daily_returns[cur_start]
        cur_start  += 1

        if window_sum > max_sum:
            max_sum   = window_sum
            max_start = cur_start

    # Convert back to price indices (daily_returns[i] = prices[i+1] - prices[i])
    price_start = max_start           # buy at close of this day
    price_end   = max_start + k       # sell at close of this day

    return (
        round(max_sum, 4),
        price_start,
        price_end,
        prices[price_start : price_end + 1]
    )


def rolling_returns(prices: list[float], k: int) -> list[tuple[float, int, int]]:
    """
    Compute the return for every k-day window.
    Returns list of (return, start_day, end_day) for plotting.
    """
    if len(prices) < k + 1:
        return []

    daily_returns = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    results = []
    window_sum = sum(daily_returns[:k])
    results.append((round(window_sum, 4), 0, k))

    for i in range(k, len(daily_returns)):
        window_sum += daily_returns[i] - daily_returns[i - k]
        results.append((round(window_sum, 4), i - k + 1, i + 1))

    return results


# -----------------------------------------------------------------------
# Demo: analyze Apple-like stock with known profitable periods
# -----------------------------------------------------------------------

random.seed(2024)

# Simulate 365 days of stock price with a known bull run between days 100-130
base_price = 150.0
prices = [base_price]
for day in range(365):
    if 100 <= day <= 130:
        daily_change = random.gauss(2.5, 1.5)   # bull run: avg +$2.50/day
    elif 200 <= day <= 230:
        daily_change = random.gauss(-1.5, 1.2)  # bear period
    else:
        daily_change = random.gauss(0.2, 1.8)   # normal: slight upward drift
    prices.append(max(1.0, prices[-1] + daily_change))

print("Stock analysis: 365 days of simulated price data")
print(f"Start price: ${prices[0]:.2f}  |  End price: ${prices[-1]:.2f}\n")

for k in [5, 10, 21, 30]:  # 1-week, 2-week, 1-month, 6-week windows
    profit, start, end, window_prices = max_profit_k_days(prices, k)
    start_price = window_prices[0]
    end_price   = window_prices[-1]
    pct_return  = (profit / start_price) * 100

    print(f"  Best {k:2d}-day window: Day {start:3d} → Day {end:3d}")
    print(f"    Buy at: ${start_price:.2f}  |  Sell at: ${end_price:.2f}")
    print(f"    Profit: ${profit:.2f}  ({pct_return:.1f}% return)\n")

# Show the distribution of all 30-day window returns
all_returns = rolling_returns(prices, 30)
returns_only = [r for r, _, _ in all_returns]
positive_windows = sum(1 for r in returns_only if r > 0)

print(f"30-day rolling window statistics:")
print(f"  Total windows : {len(returns_only)}")
print(f"  Positive      : {positive_windows} ({100*positive_windows/len(returns_only):.0f}%)")
print(f"  Average return: ${sum(returns_only)/len(returns_only):.2f}")
print(f"  Best  window  : ${max(returns_only):.2f}")
print(f"  Worst window  : ${min(returns_only):.2f}")
```

---

## 4. Text Analytics — Most Frequent Word in Any Window of K Words

### The Production Problem

Social media trend detection (Twitter/X trending topics, Reddit's hot algorithm,
news aggregators) needs to find what word or hashtag appears most often in any
sliding window of K consecutive words or posts. The naive approach recomputes
word frequencies from scratch for each window — O(k) per slide, O(n*k) total.
The sliding window maintains a frequency dictionary: add the incoming word,
remove the outgoing word, track the current maximum. This is O(n) total.

```python
from collections import defaultdict

# -----------------------------------------------------------------------
# Most frequent word in any K-word sliding window
# -----------------------------------------------------------------------

def most_frequent_word_in_window(
    words: list[str],
    k: int
) -> tuple[str, int, int, int]:
    """
    Find the word with the highest frequency in any window of k consecutive words.

    Used in:
      - Trending topic detection in social media pipelines
      - Keyword density analysis in SEO tools
      - Hotspot detection in log streams

    Returns: (word, frequency, window_start, window_end)
    Time:  O(n)  — each word is added and removed from the frequency map exactly once
    Space: O(k)  — at most k distinct words in the window at any time
    """
    if not words or k <= 0 or k > len(words):
        raise ValueError("Invalid input")

    freq: dict[str, int] = defaultdict(int)
    max_freq = 0
    best_word = ""
    best_start = 0

    # Initialize first window
    for i in range(k):
        freq[words[i]] += 1
        if freq[words[i]] > max_freq:
            max_freq  = freq[words[i]]
            best_word = words[i]

    # Slide the window
    for right in range(k, len(words)):
        left = right - k

        # Add new word entering the window
        new_word = words[right]
        freq[new_word] += 1
        if freq[new_word] > max_freq:
            max_freq   = freq[new_word]
            best_word  = new_word
            best_start = left + 1

        # Remove old word leaving the window
        old_word = words[left]
        freq[old_word] -= 1
        if freq[old_word] == 0:
            del freq[old_word]

        # Note: if the removed word was the max, we may need to rescan.
        # For O(n) amortized, track max lazily and rescan only when needed.
        if old_word == best_word and freq.get(old_word, 0) < max_freq:
            # Rescan current window for true max — O(k) worst case but rare
            max_freq  = max(freq.values()) if freq else 0
            best_word = max(freq, key=freq.get) if freq else ""
            best_start = left + 1

    return best_word, max_freq, best_start, best_start + k - 1


def sliding_window_word_frequencies(
    words: list[str],
    k: int,
    top_n: int = 3
) -> list[tuple[int, list[tuple[str, int]]]]:
    """
    For each position of the k-word window, return the top-N most frequent words.
    Used for generating trend timelines.
    """
    freq: dict[str, int] = defaultdict(int)
    results = []

    for i in range(k):
        freq[words[i]] += 1

    def top_words():
        return sorted(freq.items(), key=lambda x: -x[1])[:top_n]

    results.append((0, top_words()))

    for right in range(k, len(words)):
        left = right - k
        freq[words[right]] += 1
        freq[words[left]]  -= 1
        if freq[words[left]] == 0:
            del freq[words[left]]
        results.append((left + 1, top_words()))

    return results


# -----------------------------------------------------------------------
# Demo: trending word detection on a stream of social media posts
# -----------------------------------------------------------------------

# Simulate a stream of words from social media posts about a tech announcement
import random

random.seed(2024)
base_words = ["the", "a", "is", "in", "to", "and", "of", "for", "with", "on"]
tech_words = ["python", "ai", "model", "release", "claude", "gpt", "llm", "agent"]
trending   = ["announcement", "launch", "new", "feature", "update"]

# Create a word stream where "claude" trends strongly between positions 200-400
word_stream = []
for i in range(600):
    if 200 <= i < 400:
        # Trending period: "claude" appears frequently
        pool = base_words * 3 + ["claude"] * 8 + tech_words + trending
    else:
        pool = base_words * 5 + tech_words * 2 + ["claude"] * 1
    word_stream.append(random.choice(pool))

print(f"Word stream length: {len(word_stream)} words")
print(f"Total unique words: {len(set(word_stream))}\n")

# Find globally most frequent word in any 50-word window
word, freq, start, end = most_frequent_word_in_window(word_stream, k=50)
print(f"Most frequent word in any 50-word window:")
print(f"  Word: {word!r}  |  Frequency: {freq}x  |  Window: [{start}, {end}]\n")

# Show trending topics over time using 100-word windows
print("Trending word at each 100-position window (showing every 50th):")
timeline = sliding_window_word_frequencies(word_stream, k=100, top_n=3)
for pos in range(0, len(timeline), 50):
    window_start, top = timeline[pos]
    top_str = ", ".join(f"{w}({c})" for w, c in top)
    print(f"  Position {window_start:3d}-{window_start+99:3d}: {top_str}")
```

---

## 5. Substring Problems in Bio — Minimum DNA Window

### The Production Problem

In computational biology and genomics, a common query is: "find the shortest
contiguous region of a DNA sequence that contains all of a set of required
nucleotides or gene markers." This is used to identify minimal promoter
regions, find restriction enzyme recognition sites, and design PCR primers.
The minimum window substring algorithm (variable sliding window) solves this
in O(n) — a core tool in bioinformatics pipelines (BWA, GATK, Bowtie use
variants of this for sequence alignment scoring).

```python
from collections import Counter

# -----------------------------------------------------------------------
# Minimum window containing all required nucleotides/markers
# -----------------------------------------------------------------------

def min_dna_window(
    sequence: str,
    required_nucleotides: str
) -> tuple[str, int, int]:
    """
    Find the minimum-length contiguous window in `sequence` that contains
    at least the counts of each character in `required_nucleotides`.

    This is the classic "minimum window substring" problem, applied to
    DNA sequence analysis.

    Used in:
      - Finding minimal promoter regions (smallest region containing all
        required transcription factor binding motifs)
      - PCR primer design: shortest sequence containing all required markers
      - Sequence assembly: minimum overlap containing all required k-mers

    Algorithm: variable sliding window with two pointers.
      - right expands to meet the requirement.
      - Once satisfied, left contracts to minimize the window.
      - Track the minimum satisfying window seen.

    Time:  O(n)  — each character enters and leaves the window at most once
    Space: O(|alphabet|)  — at most 4 characters for DNA (A, C, G, T)

    Returns: (window, start_index, end_index) or ("", -1, -1) if impossible
    """
    if not sequence or not required_nucleotides:
        return "", -1, -1

    need   = Counter(required_nucleotides)   # required counts
    have   = Counter()                        # current window counts
    formed = 0                                # number of requirements met
    required_types = len(need)                # number of distinct characters needed

    best_len   = float("inf")
    best_start = 0
    best_end   = 0

    left = 0

    for right in range(len(sequence)):
        char = sequence[right]
        have[char] += 1

        # Check if this character's requirement is now satisfied
        if char in need and have[char] == need[char]:
            formed += 1

        # Contract from the left while all requirements are still met
        while formed == required_types and left <= right:
            window_len = right - left + 1
            if window_len < best_len:
                best_len   = window_len
                best_start = left
                best_end   = right

            # Remove the leftmost character and advance left
            left_char = sequence[left]
            have[left_char] -= 1
            if left_char in need and have[left_char] < need[left_char]:
                formed -= 1  # requirement no longer met
            left += 1

    if best_len == float("inf"):
        return "", -1, -1

    return sequence[best_start : best_end + 1], best_start, best_end


def find_all_minimal_windows(
    sequence: str,
    required: str,
    max_results: int = 10
) -> list[tuple[str, int, int]]:
    """
    Find all minimal windows of minimum length containing all required characters.
    Useful for finding all equivalent minimal binding sites.
    """
    if not sequence or not required:
        return []

    _, _, _ = min_dna_window(sequence, required)
    min_window, _, _ = min_dna_window(sequence, required)
    if not min_window:
        return []

    min_len = len(min_window)
    need = Counter(required)
    results = []

    for start in range(len(sequence) - min_len + 1):
        if len(results) >= max_results:
            break
        window = sequence[start : start + min_len]
        window_counts = Counter(window)
        if all(window_counts[c] >= need[c] for c in need):
            results.append((window, start, start + min_len - 1))

    return results


# -----------------------------------------------------------------------
# Demo 1: Find minimal promoter region in a gene sequence
# -----------------------------------------------------------------------

# Simulated gene upstream region
# We're looking for the minimal region containing all of: A, T, G, C
# (i.e., the shortest region with all four DNA bases — simplified example)
gene_region = "AATCCGGTTAACGCTATGCAATCGATCGATCG"

required = "ATGC"   # need at least one of each nucleotide
window, start, end = min_dna_window(gene_region, required)

print("DNA Minimum Window Search")
print(f"Sequence: {gene_region}")
print(f"Required: {required}")
print(f"Minimum window: {window!r}  at positions [{start}, {end}]")
print(f"Window length: {len(window)}\n")

# -----------------------------------------------------------------------
# Demo 2: Find binding motif regions
# -----------------------------------------------------------------------

import random
random.seed(42)

# 200bp simulated regulatory sequence
bases = "ACGT"
long_seq = "".join(random.choices(bases, weights=[0.25, 0.25, 0.25, 0.25], k=200))

print(f"Regulatory sequence (200bp):")
print(f"  {long_seq[:80]}...")
print(f"  {long_seq[80:160]}...")

for required_motif in ["AATTCCGG", "GCGCATCG", "AAACCCGGG"]:
    window, start, end = min_dna_window(long_seq, required_motif)
    if window:
        print(f"\nMinimum region containing {required_motif!r}:")
        print(f"  Window: {window!r}  ({len(window)}bp)  at [{start}, {end}]")
    else:
        print(f"\nRequired motif {required_motif!r} not fully present in sequence")

# -----------------------------------------------------------------------
# Demo 3: Performance on a full chromosome simulation
# -----------------------------------------------------------------------

import time

random.seed(99)
chromosome = "".join(random.choices("ACGT", k=1_000_000))  # 1Mbp

start_time = time.perf_counter()
window, w_start, w_end = min_dna_window(chromosome, "AAACCCGGGTTT")
elapsed_ms = (time.perf_counter() - start_time) * 1000

print(f"\nChromosome scan: 1,000,000 bp")
print(f"Required motif: 'AAACCCGGGTTT' (12 specific bases)")
print(f"Minimum window: {len(window)}bp at position [{w_start}, {w_end}]")
print(f"Scan time: {elapsed_ms:.1f} ms  (O(n) — single pass)")
```

---

## 6. Log Analysis — Longest Period with No Errors

### The Production Problem

SRE (Site Reliability Engineering) teams measure system reliability by finding
the longest stretch of time with no error-level log events. This is the "uptime
streak" metric. It uses a variable sliding window: expand the right pointer to
include new log events, and whenever an error is encountered, shrink the left
pointer to just past the last error. This finds the longest clean period in O(n).

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import random

class LogLevel(Enum):
    DEBUG = 0
    INFO  = 1
    WARN  = 2
    ERROR = 3
    FATAL = 4

@dataclass
class LogEvent:
    timestamp: float   # Unix timestamp
    level: LogLevel
    service: str
    message: str

    def is_error(self) -> bool:
        return self.level in (LogLevel.ERROR, LogLevel.FATAL)

    def __repr__(self):
        t = int(self.timestamp)
        return f"[{t}] {self.level.name:5s} {self.service}: {self.message}"


def longest_clean_period(
    log_entries: list[LogEvent]
) -> tuple[float, int, int, Optional[LogEvent], Optional[LogEvent]]:
    """
    Find the longest contiguous period with no ERROR or FATAL events.
    Uses variable sliding window: expand right until an error is found,
    then advance left to just after the error.

    This is the algorithm SRE dashboards use to compute "longest incident-free
    streak" — a key reliability metric (MTBF: Mean Time Between Failures).

    Returns:
        (duration_seconds, start_index, end_index, first_event, last_event)
    Time:  O(n)
    Space: O(1)
    """
    if not log_entries:
        return 0.0, -1, -1, None, None

    best_duration = 0.0
    best_start    = 0
    best_end      = 0
    window_start  = 0  # left pointer (index of window's first event)

    for right in range(len(log_entries)):
        if log_entries[right].is_error():
            # Error found — the clean window ends at right-1
            # Advance left pointer to just after this error
            window_start = right + 1
        else:
            # No error — the current clean window is [window_start, right]
            start_ts   = log_entries[window_start].timestamp
            end_ts     = log_entries[right].timestamp
            duration   = end_ts - start_ts

            if duration > best_duration:
                best_duration = duration
                best_start    = window_start
                best_end      = right

    if best_start > best_end:
        return 0.0, -1, -1, None, None

    return (
        best_duration,
        best_start,
        best_end,
        log_entries[best_start],
        log_entries[best_end],
    )


def analyze_service_reliability(log_entries: list[LogEvent]) -> dict:
    """
    Compute full reliability metrics for a service from its log history.
    Used to generate SLA reports and incident timelines.
    """
    if not log_entries:
        return {}

    total_duration = log_entries[-1].timestamp - log_entries[0].timestamp
    error_events   = [e for e in log_entries if e.is_error()]
    error_count    = len(error_events)

    duration, start_idx, end_idx, first, last = longest_clean_period(log_entries)

    # Compute all clean periods (for MTBF calculation)
    clean_periods = []
    window_start  = 0
    for i, event in enumerate(log_entries):
        if event.is_error():
            if window_start < i:
                period_duration = log_entries[i-1].timestamp - log_entries[window_start].timestamp
                clean_periods.append(period_duration)
            window_start = i + 1

    if window_start < len(log_entries):
        period_duration = log_entries[-1].timestamp - log_entries[window_start].timestamp
        clean_periods.append(period_duration)

    mtbf = sum(clean_periods) / len(error_events) if error_events else total_duration

    return {
        "total_duration_hours"    : round(total_duration / 3600, 2),
        "total_log_events"        : len(log_entries),
        "error_events"            : error_count,
        "error_rate_per_hour"     : round(error_count / (total_duration / 3600), 2),
        "longest_clean_period_h"  : round(duration / 3600, 2),
        "longest_clean_start_idx" : start_idx,
        "longest_clean_end_idx"   : end_idx,
        "mtbf_hours"              : round(mtbf / 3600, 2),
        "availability_pct"        : round((total_duration - sum(0 for e in error_events)) / total_duration * 100, 4),
    }


# -----------------------------------------------------------------------
# Demo: analyze 72 hours of microservice logs
# -----------------------------------------------------------------------

random.seed(2024)

def generate_service_logs(
    service_name: str,
    duration_hours: int,
    events_per_hour: int,
    error_probability: float
) -> list[LogEvent]:
    messages = {
        LogLevel.DEBUG : ["Cache lookup", "Query plan evaluated", "Connection reused"],
        LogLevel.INFO  : ["Request processed", "User authenticated", "Job completed"],
        LogLevel.WARN  : ["Slow query detected", "Retry attempt", "Cache miss"],
        LogLevel.ERROR : ["Database connection failed", "Timeout exceeded", "Service unavailable"],
        LogLevel.FATAL : ["Out of memory", "Disk full", "Unhandled exception"],
    }
    entries = []
    base_time = 1_700_000_000.0  # Unix timestamp

    for hour in range(duration_hours):
        for event_num in range(events_per_hour):
            t = base_time + hour * 3600 + (event_num / events_per_hour) * 3600

            # Inject an outage between hours 24-26
            if 24 <= hour < 26:
                if random.random() < 0.4:
                    level = random.choice([LogLevel.ERROR, LogLevel.FATAL])
                else:
                    level = random.choice([LogLevel.INFO, LogLevel.WARN])
            elif random.random() < error_probability:
                level = random.choice([LogLevel.ERROR, LogLevel.WARN])
            else:
                level = random.choice([LogLevel.DEBUG, LogLevel.INFO, LogLevel.INFO])

            message = random.choice(messages[level])
            entries.append(LogEvent(t, level, service_name, message))

    return entries

logs = generate_service_logs(
    service_name="api-gateway",
    duration_hours=72,
    events_per_hour=600,
    error_probability=0.02
)

print(f"Log analysis for: api-gateway")
print(f"Total events: {len(logs):,}  |  Duration: 72 hours\n")

metrics = analyze_service_reliability(logs)
for key, val in metrics.items():
    print(f"  {key:<30s}: {val}")

duration, s_idx, e_idx, first_event, last_event = longest_clean_period(logs)
if first_event and last_event:
    print(f"\nLongest clean period details:")
    print(f"  Started  : {first_event}")
    print(f"  Ended    : {last_event}")
    print(f"  Duration : {duration/3600:.2f} hours ({int(e_idx - s_idx):,} events)")
```

---

## Summary Table

| Use Case | Window Type | Key Operation | Complexity |
|---|---|---|---|
| Network monitoring | Fixed (last N) | Running sum O(1) update | O(1) per update |
| Rate limiting | Time-based sliding | Evict expired timestamps | O(1) amortized |
| Stock analysis | Fixed K days | Sum of daily returns | O(n) |
| Text trending | Fixed K words | Frequency map add/remove | O(n) |
| DNA window | Variable expand/contract | Requirement counter | O(n) |
| Log clean period | Variable expand/contract | Error triggers reset | O(n) |

The sliding window's power comes from a single invariant: **every element is
added to the window exactly once and removed from the window at most once**,
giving O(n) total work regardless of window size.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Patterns](./patterns.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
