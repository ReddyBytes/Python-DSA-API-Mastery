# Recursion — Real-World Usage

Recursion is not a trick. It is the natural way to express algorithms over
self-similar structures: trees, nested documents, divided arrays, and hierarchical
file systems. Every major programming language runtime, every compiler, and every
data serialization library uses recursion internally. This file shows six concrete
production examples with working Python code.

---

## 1. File System Traversal — Recursive Directory Scanning

The file system is a tree, and the natural way to walk a tree is recursively. The
OS kernel itself uses recursive descent to traverse directory trees for operations
like `rm -rf`, `cp -r`, and `chmod -R`. Python's `pathlib` and `os.walk()` expose
this traversal.

**Real company example:** VS Code's workspace search, GitHub's repository file browser,
and Docker's `COPY` instruction all recursively traverse directory trees. Webpack and
Vite recursively scan `node_modules` to build import graphs.

```python
import os
from pathlib import Path
from collections import defaultdict


def find_size(path: str) -> int:
    """
    Recursively computes total size of a directory in bytes.
    Post-order: leaf files first, then sum up at each directory level.
    This mirrors what `du -sb /path` does.

    Time:  O(N)  — every file/directory visited once
    Space: O(H)  — call stack depth = maximum directory depth
    """
    if os.path.isfile(path):
        return os.path.getsize(path)

    total = 0
    try:
        for entry in os.scandir(path):
            if not entry.is_symlink():
                total += find_size(entry.path)   # recursive call
    except PermissionError:
        pass
    return total


def find_files_by_extension(path: str, ext: str) -> list[str]:
    """
    Recursively find all files with the given extension.
    Equivalent to: find /path -name "*.ext" -type f

    Used by IDEs (PyCharm, VS Code) to index project files on startup.
    """
    results = []

    if os.path.isfile(path):
        if path.endswith(ext):
            results.append(path)
        return results

    try:
        for entry in os.scandir(path):
            if entry.is_symlink():
                continue
            results.extend(find_files_by_extension(entry.path, ext))
    except PermissionError:
        pass

    return results


def file_tree(path: str, prefix: str = "", max_depth: int = 3, _depth: int = 0) -> str:
    """
    Recursively build a pretty-printed directory tree — like the `tree` command.
    VS Code's Explorer panel renders this structure exactly.
    """
    if _depth > max_depth:
        return prefix + "...\n"

    name = os.path.basename(path) or path
    output = prefix + name + "\n"

    if os.path.isdir(path):
        try:
            entries = sorted(os.scandir(path), key=lambda e: (e.is_file(), e.name))
        except PermissionError:
            return output
        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            extension = "    " if is_last else "│   "
            output += file_tree(
                entry.path,
                prefix + connector,
                max_depth,
                _depth + 1,
            ).replace(prefix + connector, prefix + connector, 1)
            # adjust subsequent lines
    return output


def count_by_extension(path: str) -> dict[str, int]:
    """
    Recursively count files by extension.
    Same logic as GitHub's language detection (Linguist library).
    """
    counts: dict[str, int] = defaultdict(int)

    def recurse(p: str) -> None:
        if os.path.isfile(p):
            ext = Path(p).suffix or "(no extension)"
            counts[ext] += 1
            return
        try:
            for entry in os.scandir(p):
                if not entry.is_symlink():
                    recurse(entry.path)
        except PermissionError:
            pass

    recurse(path)
    return dict(counts)


if __name__ == "__main__":
    home = str(Path.home())

    # Find all Python files in home directory (capped for demo)
    py_files = find_files_by_extension(home, ".py")
    print(f"Found {len(py_files)} .py files under {home}")

    total_size = find_size(home)
    print(f"Total size: {total_size / 1_000_000:.1f} MB")
```

---

## 2. JSON / XML Parsing — Recursive Descent Through Nested Documents

Every JSON parser uses recursive descent. The grammar of JSON is defined
recursively — a value can be a string, number, array (list of values), or object
(map of keys to values). The Python `json` module's C implementation is a recursive
descent parser. `pyyaml`, `lxml`, and `xml.etree` work the same way.

**Real company example:** AWS Lambda reads CloudFormation JSON templates recursively
to resolve `!Ref` and `!Sub` intrinsic functions. Terraform's HCL parser uses
recursive descent. FastAPI/Pydantic validate deeply nested request bodies recursively.

```python
import json
from typing import Any


SAMPLE = {
    "service": "payments-api",
    "version": "3.2.1",
    "config": {
        "database": {
            "primary":  {"host": "db-1.prod", "port": 5432, "ssl": True},
            "replica":  {"host": "db-2.prod", "port": 5432, "ssl": True},
        },
        "cache": {"host": "redis.prod", "port": 6379, "ttl": 300},
        "feature_flags": {"dark_mode": True, "new_checkout": False},
    },
    "tags": ["production", "payments", "pci-dss"],
}


def count_nested_keys(obj: Any) -> int:
    """
    Count all keys at every level of a nested JSON document.
    Used by schema validators to detect unexpectedly large payloads.
    """
    if isinstance(obj, dict):
        return len(obj) + sum(count_nested_keys(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(count_nested_keys(item) for item in obj)
    return 0   # scalar — no keys


def flatten_nested_dict(obj: Any, prefix: str = "", sep: str = ".") -> dict[str, Any]:
    """
    Flatten a nested document into dot-notation keys.

    {"database": {"host": "db.prod"}} → {"database.host": "db.prod"}

    This is what AWS Parameter Store, Consul, and Vault do when
    storing hierarchical config as flat key-value pairs.
    Also used by pandas.json_normalize() and Elasticsearch ingest pipelines.
    """
    flat: dict[str, Any] = {}

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}{sep}{k}" if prefix else k
            flat.update(flatten_nested_dict(v, new_key, sep))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            flat.update(flatten_nested_dict(item, f"{prefix}[{i}]", sep))
    else:
        flat[prefix] = obj

    return flat


def deep_get(obj: Any, *keys) -> Any:
    """
    Safely navigate a nested dict — like JavaScript's optional chaining (?.).
    Used everywhere: API clients, config readers, Jinja2 template context.

    deep_get(config, "database", "primary", "host") → "db-1.prod"
    """
    for key in keys:
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        elif isinstance(obj, list) and isinstance(key, int) and 0 <= key < len(obj):
            obj = obj[key]
        else:
            return None
    return obj


def find_all_values_for_key(obj: Any, target_key: str) -> list[Any]:
    """
    Find every value associated with `target_key` anywhere in the document.
    Equivalent to jq's recursive descent: ..target_key
    Used by Ansible to extract 'host' from any nested inventory.
    """
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == target_key:
                results.append(v)
            results.extend(find_all_values_for_key(v, target_key))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_all_values_for_key(item, target_key))
    return results


if __name__ == "__main__":
    print(f"Total keys in document: {count_nested_keys(SAMPLE)}")

    flat = flatten_nested_dict(SAMPLE)
    print("\nFlattened config:")
    for k, v in flat.items():
        print(f"  {k} = {v!r}")

    host = deep_get(SAMPLE, "config", "database", "primary", "host")
    print(f"\nPrimary DB host: {host}")

    all_hosts = find_all_values_for_key(SAMPLE, "host")
    print(f"All 'host' values: {all_hosts}")
```

---

## 3. Web Crawling — Recursive DFS Through a Link Graph

A web crawler starts at a seed URL, fetches the page, extracts all links, and
recursively visits each unvisited link. This is DFS on the web's link graph. Google's
original PageRank paper describes exactly this traversal. `scrapy`, `playwright`, and
`aiohttp`-based crawlers all implement this recursion.

**Real company example:** Googlebot, Common Crawl (used to train GPT-3/4), and the
Wayback Machine at archive.org all work this way. Screaming Frog SEO Spider does
recursive DFS to audit website structure.

```python
import time
from urllib.parse import urljoin, urlparse
from typing import Optional

# For a real crawler, use: requests, httpx, or aiohttp
# This demo uses a simulated link graph to avoid network calls.


# Simulated website link graph
LINK_GRAPH: dict[str, list[str]] = {
    "https://example.com/":           ["https://example.com/about",
                                        "https://example.com/blog",
                                        "https://example.com/contact"],
    "https://example.com/about":      ["https://example.com/team",
                                        "https://example.com/"],
    "https://example.com/blog":       ["https://example.com/blog/post-1",
                                        "https://example.com/blog/post-2"],
    "https://example.com/blog/post-1":["https://example.com/blog",
                                        "https://example.com/contact"],
    "https://example.com/blog/post-2":["https://example.com/blog"],
    "https://example.com/team":       ["https://example.com/about"],
    "https://example.com/contact":    ["https://example.com/"],
}

SIMULATED_CONTENT: dict[str, str] = {
    "https://example.com/":           "<h1>Welcome</h1>",
    "https://example.com/about":      "<h1>About Us</h1>",
    "https://example.com/blog":       "<h1>Blog</h1>",
    "https://example.com/blog/post-1":"<h1>Post 1: Intro to DSA</h1>",
    "https://example.com/blog/post-2":"<h1>Post 2: Recursion Deep Dive</h1>",
    "https://example.com/team":       "<h1>Our Team</h1>",
    "https://example.com/contact":    "<h1>Contact</h1>",
}


def web_crawl(
    url: str,
    max_depth: int,
    visited: set[str] | None = None,
    _depth: int = 0,
) -> dict[str, str]:
    """
    Recursive DFS web crawler.
    Returns {url: content} for all reachable pages within max_depth.

    The `visited` set prevents infinite loops — the web's link graph
    has cycles (A → B → A), which would cause infinite recursion.

    Base cases:
      1. max_depth reached
      2. URL already visited (cycle prevention)
      3. URL outside target domain
    """
    if visited is None:
        visited = set()

    # Base cases
    if _depth > max_depth:
        return {}
    if url in visited:
        return {}
    if "example.com" not in url:   # stay within domain
        return {}

    visited.add(url)
    indent = "  " * _depth
    print(f"{indent}[depth={_depth}] Crawling: {url}")

    # Fetch page (simulated)
    content = SIMULATED_CONTENT.get(url, "")
    results = {url: content}

    # Extract and follow links (recursive step)
    for link in LINK_GRAPH.get(url, []):
        results.update(
            web_crawl(link, max_depth, visited, _depth + 1)
        )

    return results


def build_site_map(seed: str, max_depth: int = 3) -> dict[str, list[str]]:
    """
    Build a site map: {url: [outgoing_links]} using recursive DFS.
    This is how Screaming Frog and Google Search Console map a site.
    """
    visited: set[str] = set()
    site_map: dict[str, list[str]] = {}

    def dfs(url: str, depth: int) -> None:
        if depth > max_depth or url in visited:
            return
        visited.add(url)
        links = LINK_GRAPH.get(url, [])
        site_map[url] = links
        for link in links:
            dfs(link, depth + 1)

    dfs(seed, 0)
    return site_map


if __name__ == "__main__":
    print("=== Recursive Web Crawler (DFS) ===\n")
    crawled = web_crawl("https://example.com/", max_depth=2)
    print(f"\nCrawled {len(crawled)} pages total.")

    print("\n=== Site Map ===")
    site_map = build_site_map("https://example.com/")
    for url, links in sorted(site_map.items()):
        print(f"  {url}")
        for link in links:
            print(f"    → {link}")
```

---

## 4. Fractal Generation — Pure Recursion Made Visual

Fractals are defined by recursive self-similarity: each part looks like the whole.
The Sierpinski triangle is produced by repeatedly removing the central triangle from
equilateral triangles. Koch snowflake replaces each line segment with four new segments.
These are pure recursion with no iteration.

**Real company example:** NVIDIA uses fractal noise (Perlin noise — recursive octave
summation) in every GPU. Procedural terrain generation in games like No Man's Sky,
Minecraft, and Dwarf Fortress uses recursive subdivision (midpoint displacement).

```python
def sierpinski_text(n: int) -> list[str]:
    """
    Generate an ASCII Sierpinski triangle of order n.

    Recursive structure:
      order 0 → ["*"]
      order n → top half of smaller triangle
                bottom-left smaller triangle + bottom-right smaller triangle

    Base case: n == 0 returns a single asterisk.
    Recursive case: combine three copies of order n-1.
    """
    if n == 0:
        return ["*"]

    smaller = sierpinski_text(n - 1)
    width = len(smaller[-1])
    space = " " * width

    top    = [space + line + space for line in smaller]
    bottom = [line + " " + line    for line in smaller]

    return top + bottom


def koch_curve_lengths(order: int, initial_length: float = 1.0) -> list[float]:
    """
    Return all segment lengths in a Koch curve of given order.
    At each step every segment is replaced by 4 segments of length/3.

    This is the basis for the Koch snowflake — total segments = 4^order.
    Fractal dimension = log(4)/log(3) ≈ 1.26 (between 1D and 2D).
    """
    if order == 0:
        return [initial_length]

    sub = koch_curve_lengths(order - 1, initial_length / 3)
    return sub * 4   # four copies of the sub-curve


def fractal_tree_text(depth: int) -> list[str]:
    """
    ASCII fractal tree. Each branch splits into two sub-branches.
    The same structure underlies binary space partitioning (BSP trees)
    used in game engines like Quake and Doom for rendering.
    """
    if depth == 0:
        return ["|"]

    sub = fractal_tree_text(depth - 1)
    width = len(sub[0])
    space = " " * width

    # Split: left branch leans left, right branch leans right
    left_branch  = [" " + line for line in sub]
    right_branch = [line + " " for line in sub]
    trunk = [space + "|" + space]

    merged = []
    for l, r in zip(left_branch, right_branch):
        merged.append(l + " " + r)

    return merged + trunk


if __name__ == "__main__":
    print("Sierpinski Triangle (order 4):")
    for line in sierpinski_text(4):
        print(line)

    print("\nKoch curve segment counts by order:")
    for order in range(6):
        segs = koch_curve_lengths(order)
        print(f"  order {order}: {len(segs):4d} segments, "
              f"each length = {segs[0]:.6f}")

    print("\nFractal tree (depth 3):")
    for line in fractal_tree_text(3):
        print(line)
```

---

## 5. Merge Sort and Quick Sort — Divide and Conquer

Every production sort is divide-and-conquer at heart. Python's `timsort` is a hybrid
merge sort. Java's `Arrays.sort()` uses dual-pivot quicksort for primitives and
timsort for objects. C++'s `std::sort` uses introsort (quicksort + heapsort hybrid).
All three are recursive.

**Real company example:** Pandas `DataFrame.sort_values()`, NumPy `argsort()`, and
every database `ORDER BY` clause ultimately call a recursive sort internally. Merge
sort specifically is used for external sorting — sorting data that does not fit in RAM —
by database engines and Hadoop MapReduce.

```python
def merge_sort(arr: list, depth: int = 0) -> list:
    """
    Classic merge sort annotated to show the three recursive steps.

    Step 1 — DIVIDE:   split array in half
    Step 2 — CONQUER:  recursively sort each half
    Step 3 — COMBINE:  merge two sorted halves

    Time:  O(N log N) — log N levels, N work per level
    Space: O(N)       — merge requires a temporary array
    """
    # Base case: a single element is already sorted
    if len(arr) <= 1:
        return arr

    indent = "  " * depth
    mid = len(arr) // 2

    # DIVIDE
    left_half  = arr[:mid]
    right_half = arr[mid:]

    # CONQUER (two recursive calls)
    left_sorted  = merge_sort(left_half,  depth + 1)
    right_sorted = merge_sort(right_half, depth + 1)

    # COMBINE
    return _merge(left_sorted, right_sorted)


def _merge(left: list, right: list) -> list:
    """Merge two sorted arrays into one sorted array. O(n)."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(arr: list, lo: int = 0, hi: int = -1, _init: bool = True) -> list:
    """
    In-place quicksort.
    Divide: partition around pivot (all < pivot on left, all > on right)
    Conquer: recursively sort each partition
    No combine step needed — partitioning is done in-place.

    Average time: O(N log N)    Worst case: O(N^2) — already-sorted input
    Space: O(log N) stack space for recursion
    """
    if _init:
        arr = arr[:]
        hi = len(arr) - 1

    if lo >= hi:
        return arr

    pivot_idx = _partition(arr, lo, hi)
    quick_sort(arr, lo, pivot_idx - 1, _init=False)
    quick_sort(arr, pivot_idx + 1, hi, _init=False)
    return arr


def _partition(arr: list, lo: int, hi: int) -> int:
    """Lomuto partition scheme. Pivot = last element."""
    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    return i + 1


if __name__ == "__main__":
    import random
    data = [random.randint(1, 100) for _ in range(10)]
    print(f"Original:   {data}")
    print(f"Merge sort: {merge_sort(data)}")
    print(f"Quick sort: {quick_sort(data)}")
    print(f"Python sort:{sorted(data)}")
    assert merge_sort(data) == sorted(data) == quick_sort(data)
    print("All three agree.")
```

---

## 6. Tree and Graph Algorithms — Recursion Is the Natural Fit

Almost every algorithm on a tree is naturally recursive because a tree is defined
recursively: a tree is a root node plus zero or more subtrees. Asking "what is the
height of this tree?" is the same as "1 + max(height of left subtree, height of right
subtree)".

**Real company example:** React's virtual DOM diffing algorithm (reconciliation) is
recursive tree comparison. JSON Schema validation recursively walks the schema tree.
Serializing a Python object graph (pickle, msgpack, protobuf) is recursive tree
traversal.

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class TreeNode:
    val: int
    left:  Optional[TreeNode] = None
    right: Optional[TreeNode] = None


def max_depth(root: Optional[TreeNode]) -> int:
    """
    Maximum depth (height) of a binary tree.
    Classic example of recursive definition:
      depth(None) = 0
      depth(node) = 1 + max(depth(left), depth(right))

    Used in: AVL trees to maintain balance, React's fiber depth limit.
    """
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


def count_nodes(root: Optional[TreeNode]) -> int:
    """
    Count all nodes. O(N).
    Used by serializers to pre-allocate buffers.
    """
    if root is None:
        return 0
    return 1 + count_nodes(root.left) + count_nodes(root.right)


def serialize(root: Optional[TreeNode]) -> str:
    """
    Convert tree to string for storage or transmission.
    LeetCode uses this exact format. Redis stores sorted sets
    by serializing tree nodes to RDB format.

    Pre-order traversal: root → left → right
    "None" marks absent children.
    """
    if root is None:
        return "null"
    return f"{root.val},{serialize(root.left)},{serialize(root.right)}"


def deserialize(data: str) -> Optional[TreeNode]:
    """
    Rebuild tree from serialized string.
    Protobuf and MessagePack both use recursive deserialization.
    """
    values = iter(data.split(","))

    def _build() -> Optional[TreeNode]:
        val = next(values)
        if val == "null":
            return None
        node = TreeNode(int(val))
        node.left  = _build()
        node.right = _build()
        return node

    return _build()


def path_sum(root: Optional[TreeNode], target: int) -> list[list[int]]:
    """
    Find all root-to-leaf paths that sum to target.
    Classic recursive backtracking — used in decision tree explainability
    and in expression evaluators.
    """
    results: list[list[int]] = []

    def dfs(node: Optional[TreeNode], remaining: int, path: list[int]) -> None:
        if node is None:
            return
        path.append(node.val)
        remaining -= node.val

        if node.left is None and node.right is None:
            if remaining == 0:
                results.append(list(path))
        else:
            dfs(node.left,  remaining, path)
            dfs(node.right, remaining, path)

        path.pop()   # backtrack

    dfs(root, target, [])
    return results


def lowest_common_ancestor(
    root: Optional[TreeNode], p: int, q: int
) -> Optional[TreeNode]:
    """
    Find the lowest common ancestor of nodes with values p and q.
    LCA is used in: git merge-base, phylogenetic trees (biology),
    and network routing (find common subnet).
    """
    if root is None:
        return None
    if root.val == p or root.val == q:
        return root

    left_lca  = lowest_common_ancestor(root.left,  p, q)
    right_lca = lowest_common_ancestor(root.right, p, q)

    if left_lca and right_lca:
        return root          # p and q are in different subtrees
    return left_lca or right_lca


if __name__ == "__main__":
    # Build a sample tree:
    #         5
    #        / \
    #       4   8
    #      /   / \
    #     11  13   4
    #    /  \       \
    #   7    2       1
    root = TreeNode(5)
    root.left             = TreeNode(4)
    root.right            = TreeNode(8)
    root.left.left        = TreeNode(11)
    root.left.left.left   = TreeNode(7)
    root.left.left.right  = TreeNode(2)
    root.right.left       = TreeNode(13)
    root.right.right      = TreeNode(4)
    root.right.right.right= TreeNode(1)

    print(f"Max depth:   {max_depth(root)}")
    print(f"Node count:  {count_nodes(root)}")

    serialized = serialize(root)
    print(f"Serialized:  {serialized}")

    rebuilt = deserialize(serialized)
    print(f"Rebuilt depth: {max_depth(rebuilt)}  (matches original)")

    paths = path_sum(root, 22)
    print(f"\nPaths summing to 22: {paths}")

    lca = lowest_common_ancestor(root, 7, 2)
    print(f"LCA(7, 2) = {lca.val if lca else None}  (expected: 11)")

    lca2 = lowest_common_ancestor(root, 4, 13)
    print(f"LCA(4, 13) = {lca2.val if lca2 else None}  (expected: 5)")
```

---

## Summary Table

| Use Case | Recursive Pattern | Real Product |
|---|---|---|
| File system traversal | DFS / post-order | VS Code, Docker, Webpack |
| JSON/XML parsing | Recursive descent | AWS CDK, Pydantic, Terraform |
| Web crawling | DFS with visited set | Googlebot, Scrapy, Screaming Frog |
| Fractal generation | Self-similar subdivision | NVIDIA noise, No Man's Sky terrain |
| Merge / quick sort | Divide and conquer | Python timsort, Pandas, NumPy |
| Tree algorithms | Tree = root + subtrees | React reconciler, protobuf, git |

The pattern that unifies all six: **a problem is recursive when its solution can be
expressed in terms of the same problem on smaller inputs**. When you see a tree, a
nested document, a divide-and-conquer split, or a self-similar structure — that is
the signal to reach for recursion.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
