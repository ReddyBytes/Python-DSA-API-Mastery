"""
21_data_engineering_applications/api_data_collector.py
=========================================================
CONCEPT: Production-grade API data collector — the "Extract" phase of ETL.
Pulls data from paginated REST APIs, handles authentication, retries on failure,
and writes raw responses to a local staging area.
WHY THIS MATTERS: Data engineers spend most of their time extracting data
from external APIs. Real APIs fail, paginate, rate-limit, and return partial
data. This module shows how to handle all of it robustly.

Prerequisite: Modules 01–13 (especially threading, context managers, file handling)
"""

import json
import time
import random
import logging
import threading
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional
import tempfile

# =============================================================================
# SECTION 1: API Client with retry, auth, and rate-limit handling
# =============================================================================

print("=== Section 1: Robust API Client ===")

logging.basicConfig(level=logging.INFO, format="  %(levelname)s %(message)s")
log = logging.getLogger(__name__)


@dataclass
class APIConfig:
    base_url:      str
    api_key:       str
    timeout:       float = 30.0
    max_retries:   int   = 3
    retry_backoff: float = 2.0   # exponential backoff base
    rate_limit_rps: float = 10.0  # requests per second


class SimulatedAPIServer:
    """
    Simulates an external REST API with realistic failure modes:
    - 5% of requests return 429 (rate limited)
    - 3% return 500 (server error, should retry)
    - 2% return 503 (transient, should retry)
    - Paginated endpoints return up to 3 pages of data
    """

    def __init__(self, failure_rate: float = 0.1):
        self.failure_rate = failure_rate
        self._call_count = 0

    def get(self, path: str, params: dict = None) -> dict:
        self._call_count += 1
        params = params or {}
        time.sleep(random.uniform(0.01, 0.05))   # simulate latency

        # Simulate failures
        roll = random.random()
        if roll < 0.05:
            return {"status": 429, "body": None, "headers": {"Retry-After": "1"}}
        if roll < 0.08:
            return {"status": 500, "body": None, "headers": {}}
        if roll < 0.10:
            return {"status": 503, "body": None, "headers": {}}

        # Paginated response
        page      = int(params.get("page", 1))
        page_size = int(params.get("page_size", 10))
        total     = 25   # total records available
        offset    = (page - 1) * page_size
        items     = [
            {"id": offset + i, "value": (offset + i) * 2, "label": f"item_{offset+i}"}
            for i in range(min(page_size, max(0, total - offset)))
        ]

        return {
            "status": 200,
            "body": {
                "data":       items,
                "page":       page,
                "page_size":  page_size,
                "total":      total,
                "has_more":   offset + page_size < total,
            },
            "headers": {},
        }


class APICollector:
    """
    Paginated API collector with retry + exponential backoff.
    Yields records one page at a time — memory-efficient even for huge datasets.
    """

    RETRYABLE_STATUSES = {429, 500, 502, 503, 504}

    def __init__(self, config: APIConfig, server: SimulatedAPIServer):
        self.config     = config
        self.server     = server
        self._token_bucket = TokenBucketThrottle(config.rate_limit_rps)
        self.stats      = defaultdict(int)

    def _request_with_retry(self, path: str, params: dict) -> Optional[dict]:
        """Make one HTTP request with exponential backoff on transient errors."""
        for attempt in range(1, self.config.max_retries + 1):
            self._token_bucket.acquire()   # rate limit before request

            response = self.server.get(path, params)
            self.stats["total_requests"] += 1

            if response["status"] == 200:
                self.stats["successes"] += 1
                return response["body"]

            if response["status"] in self.RETRYABLE_STATUSES:
                wait = self.config.retry_backoff ** attempt
                if response["status"] == 429:
                    wait = float(response["headers"].get("Retry-After", wait))
                log.warning(f"HTTP {response['status']} on {path} — "
                            f"retry {attempt}/{self.config.max_retries} in {wait:.1f}s")
                self.stats[f"http_{response['status']}"] += 1
                time.sleep(wait)
                continue

            # Non-retryable error
            self.stats["errors"] += 1
            log.error(f"HTTP {response['status']} on {path} — not retrying")
            return None

        self.stats["exhausted_retries"] += 1
        return None

    def paginate(self, endpoint: str, page_size: int = 10) -> Iterator[list]:
        """
        Generator that yields pages of records from a paginated API.
        Handles pagination automatically — caller just iterates.
        """
        page = 1
        while True:
            params = {"page": page, "page_size": page_size}
            body   = self._request_with_retry(endpoint, params)

            if body is None:
                log.error(f"Failed to fetch page {page} of {endpoint}")
                break

            yield body["data"]
            self.stats["pages_fetched"] += 1

            if not body.get("has_more"):
                break
            page += 1

    def collect_all(self, endpoint: str, page_size: int = 10) -> list:
        """Collect ALL records from a paginated endpoint into a list."""
        all_records = []
        for page in self.paginate(endpoint, page_size):
            all_records.extend(page)
        return all_records


class TokenBucketThrottle:
    """Simple token bucket for outgoing request rate limiting."""

    def __init__(self, rate: float):
        self._rate      = rate
        self._tokens    = rate
        self._last      = time.time()
        self._lock      = threading.Lock()

    def acquire(self) -> None:
        with self._lock:
            now          = time.time()
            self._tokens = min(self._rate, self._tokens + (now - self._last) * self._rate)
            self._last   = now
            if self._tokens >= 1:
                self._tokens -= 1
            else:
                wait = (1 - self._tokens) / self._rate
                time.sleep(wait)
                self._tokens = 0


# Run the collector
random.seed(42)
config  = APIConfig(base_url="https://api.example.com", api_key="sk_test_abc123",
                    max_retries=3, rate_limit_rps=50.0)
server  = SimulatedAPIServer(failure_rate=0.1)
collector = APICollector(config, server)

log.info("Collecting /api/records with pagination...")
records = collector.collect_all("/api/records", page_size=10)

log.info(f"Collected {len(records)} records")
print(f"\n  Records: {len(records)}")
print(f"  Stats: {dict(collector.stats)}")
print(f"  First 3: {records[:3]}")


# =============================================================================
# SECTION 2: Writing collected data to staging (raw JSON files)
# =============================================================================

print("\n=== Section 2: Staging — Writing Raw Data ===")

@contextmanager
def staging_writer(output_dir: Path, batch_name: str):
    """
    Context manager for writing a batch of collected data.
    Writes to a temp file first, then renames atomically — prevents
    partial files from being picked up by downstream processors.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    final_path = output_dir / f"{batch_name}.json"
    tmp_path   = output_dir / f"{batch_name}.json.tmp"

    print(f"  Writing to staging: {final_path.name}")
    with open(tmp_path, "w") as f:
        yield f   # caller writes records here

    # Atomic rename — downstream never sees a partial file
    tmp_path.rename(final_path)
    print(f"  Committed: {final_path.name}  ({final_path.stat().st_size:,} bytes)")


staging_dir = Path(tempfile.mkdtemp()) / "staging"

with staging_writer(staging_dir, "records_batch_001") as f:
    json.dump({"source": "/api/records", "collected_at": time.time(),
               "records": records}, f, indent=2)

with staging_writer(staging_dir, "records_batch_002") as f:
    # Simulate a second run with fresh data
    more_records = [{"id": 100 + i, "value": i * 3} for i in range(5)]
    json.dump({"source": "/api/records", "collected_at": time.time(),
               "records": more_records}, f, indent=2)

# List staged files
staged = sorted(staging_dir.glob("*.json"))
print(f"\n  Staged files ({len(staged)}):")
for f in staged:
    data = json.loads(f.read_text())
    print(f"    {f.name}: {len(data['records'])} records")


print("\n=== API data collector complete ===")
print("Key patterns:")
print("  Retry with backoff  → handle transient 5xx/429 errors")
print("  Token bucket        → respect API rate limits")
print("  Generator pagination→ O(1) memory regardless of dataset size")
print("  Atomic staging      → no partial files seen by downstream")
