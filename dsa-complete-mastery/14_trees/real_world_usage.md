# Trees — Real-World Usage

Trees are everywhere in production systems. Every file system, every web page, every
compiled program, and every machine learning model you have ever used is backed by a
tree data structure. This file walks through six concrete production examples with
working Python code.

---

## 1. File System — Directories and Files

Every operating system represents storage as a tree. A directory is an internal node;
a file is a leaf. Linux's `ext4`, macOS's APFS, and Windows's NTFS all store metadata
in B-trees, but the logical shape you interact with is a general tree.

**Real company example:** GitHub's file browser, VS Code's Explorer panel, and macOS
Finder all traverse this tree to render their UI. When you run `du -sh ~/Downloads`
on macOS, the OS does a post-order traversal to sum sizes bottom-up.

```python
import os
from pathlib import Path


# --- DFS: find all files matching an extension ---
def find_files(root_dir: str, extension: str) -> list[str]:
    """
    Depth-first search through a directory tree.
    Mirrors what 'find /path -name "*.py"' does internally.

    Time:  O(N) — every node visited once
    Space: O(H) — call stack depth = directory depth H
    """
    results = []

    def dfs(path: str) -> None:
        try:
            entries = os.scandir(path)
        except PermissionError:
            return
        for entry in entries:
            if entry.is_file() and entry.name.endswith(extension):
                results.append(entry.path)
            elif entry.is_dir(follow_symlinks=False):
                dfs(entry.path)  # recurse into subdirectory

    dfs(root_dir)
    return results


# --- Post-order traversal: compute total directory size ---
def directory_size(path: str) -> int:
    """
    Post-order: process children before the parent.
    Must know children's sizes before you can sum the parent.

    Returns total bytes consumed under `path`.
    """
    if os.path.isfile(path):
        return os.path.getsize(path)

    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_symlink():
                continue
            total += directory_size(entry.path)  # children first
    except PermissionError:
        pass
    return total  # then the parent


# --- How os.walk() does it (BFS-like, but uses a stack internally) ---
def show_os_walk_dfs(root: str, max_files: int = 5) -> None:
    """
    os.walk() is a generator that does DFS under the hood.
    topdown=True  → pre-order  (parent before children)
    topdown=False → post-order (children before parent)
    """
    print(f"Walking '{root}' (post-order, topdown=False):\n")
    count = 0
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        for fname in filenames:
            full = os.path.join(dirpath, fname)
            print(f"  {full}")
            count += 1
            if count >= max_files:
                print("  ... (truncated)")
                return


# Quick demo — point at any directory you like
if __name__ == "__main__":
    home = str(Path.home())
    py_files = find_files(home, ".py")
    print(f"Found {len(py_files)} .py files under {home}")

    size = directory_size(home)
    print(f"Total size of home: {size / 1_000_000:.1f} MB")
```

Key insight: `os.walk(topdown=False)` is exactly the post-order traversal you need
when you want to delete a directory tree — you must remove the children before you
can remove the parent.

---

## 2. HTML/DOM — Every Webpage Is a Tree

When a browser parses HTML it builds the **Document Object Model** — a tree of
nodes. JavaScript's `document.getElementById()` is a tree search. CSS selectors like
`div > p.intro` describe paths in that tree. React's virtual DOM is a shadow copy of
the same tree for efficient diffing.

**Real company example:** Scrapy (used by Airbnb, Trivago) and BeautifulSoup (used
by virtually every Python web scraper) both walk the DOM tree to extract data.

```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DOMNode:
    tag: str
    attrs: dict = field(default_factory=dict)
    text: str = ""
    children: list["DOMNode"] = field(default_factory=list)

    def add_child(self, node: "DOMNode") -> "DOMNode":
        self.children.append(node)
        return node


# --- Build a tiny DOM in memory ---
def build_sample_dom() -> DOMNode:
    html = DOMNode("html")
    head = html.add_child(DOMNode("head"))
    head.add_child(DOMNode("title", text="My Page"))

    body = html.add_child(DOMNode("body"))
    div = body.add_child(DOMNode("div", attrs={"id": "main", "class": "container"}))
    div.add_child(DOMNode("h1", text="Hello World"))
    p1 = div.add_child(DOMNode("p", attrs={"class": "intro"}, text="First paragraph."))
    p2 = div.add_child(DOMNode("p", text="Second paragraph."))

    footer = body.add_child(DOMNode("footer"))
    footer.add_child(DOMNode("p", text="Footer text."))
    return html


# --- querySelector: find all nodes with a given tag (BFS) ---
def find_all_by_tag(root: DOMNode, tag: str) -> list[DOMNode]:
    """
    Mimics document.querySelectorAll('p') — returns every node
    with the matching tag. Uses BFS so results come in document order.

    This is exactly what BeautifulSoup's .find_all() does.
    """
    results = []
    queue = [root]
    while queue:
        node = queue.pop(0)
        if node.tag == tag:
            results.append(node)
        queue.extend(node.children)
    return results


# --- getElementById: stop at first match (DFS) ---
def get_by_id(root: DOMNode, target_id: str) -> Optional[DOMNode]:
    """Short-circuits as soon as the element is found."""
    if root.attrs.get("id") == target_id:
        return root
    for child in root.children:
        result = get_by_id(child, target_id)
        if result:
            return result
    return None


# --- Serialize back to HTML string ---
def to_html(node: DOMNode, indent: int = 0) -> str:
    pad = "  " * indent
    attr_str = "".join(f' {k}="{v}"' for k, v in node.attrs.items())
    if not node.children and not node.text:
        return f"{pad}<{node.tag}{attr_str} />"
    lines = [f"{pad}<{node.tag}{attr_str}>"]
    if node.text:
        lines.append(f"{pad}  {node.text}")
    for child in node.children:
        lines.append(to_html(child, indent + 1))
    lines.append(f"{pad}</{node.tag}>")
    return "\n".join(lines)


if __name__ == "__main__":
    dom = build_sample_dom()
    paragraphs = find_all_by_tag(dom, "p")
    print(f"Found {len(paragraphs)} <p> tags:")
    for p in paragraphs:
        print(f"  text='{p.text}'")

    main_div = get_by_id(dom, "main")
    print(f"\ngetById('main') → tag={main_div.tag}, class={main_div.attrs.get('class')}")
```

---

## 3. JSON / XML Parsing — Nested Documents Are Trees

`json.loads()` builds a Python dict/list tree in memory. Every API response you have
ever consumed is a tree. AWS CloudFormation templates, Kubernetes manifests, and
GitHub Actions workflows are all YAML/JSON trees that tooling traverses recursively.

**Real company example:** Datadog's agent parses JSON config files; AWS CDK walks a
CloudFormation JSON tree to plan deployments.

```python
import json


SAMPLE_JSON = """
{
  "name": "warehouse-api",
  "version": "2.1.0",
  "dependencies": {
    "fastapi": {"version": "0.110.0", "optional": false},
    "sqlalchemy": {
      "version": "2.0.0",
      "extras": {"asyncio": true, "postgresql": true}
    }
  },
  "config": {
    "database": {"host": "db.prod", "port": 5432},
    "cache":    {"host": "redis.prod", "port": 6379}
  }
}
"""


def count_depth(obj, current: int = 0) -> int:
    """
    Returns the maximum nesting depth of a JSON document.
    Depth 0 = scalar, depth 1 = flat dict/list, etc.

    Used in schema validators (e.g. Pydantic v2) to catch
    pathologically nested payloads before they blow the stack.
    """
    if isinstance(obj, dict):
        if not obj:
            return current
        return max(count_depth(v, current + 1) for v in obj.values())
    if isinstance(obj, list):
        if not obj:
            return current
        return max(count_depth(item, current + 1) for item in obj)
    return current  # scalar leaf


def find_keys(obj, target: str) -> list:
    """
    Finds all values whose key matches `target`, anywhere in the tree.
    Same logic as jq's recursive-descent operator `..`.

    Example: find_keys(data, "host") returns all host values.
    """
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == target:
                results.append(v)
            results.extend(find_keys(v, target))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_keys(item, target))
    return results


def flatten(obj, prefix: str = "") -> dict:
    """
    Flattens a nested JSON document into dot-notation keys.
    This is what AWS Parameter Store and HashiCorp Consul do when
    you store nested config as flat key-value pairs.

    {"database": {"host": "db.prod"}} → {"database.host": "db.prod"}
    """
    flat = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}.{k}" if prefix else k
            flat.update(flatten(v, new_key))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            flat.update(flatten(item, f"{prefix}[{i}]"))
    else:
        flat[prefix] = obj
    return flat


if __name__ == "__main__":
    data = json.loads(SAMPLE_JSON)

    print(f"Document depth: {count_depth(data)}")

    hosts = find_keys(data, "host")
    print(f"All 'host' values: {hosts}")

    flat = flatten(data)
    for k, v in flat.items():
        print(f"  {k} = {v}")
```

---

## 4. Decision Trees in Machine Learning

Scikit-learn's `DecisionTreeClassifier` is literally a binary tree stored in arrays.
Every prediction is a path from root to leaf. Random Forest builds hundreds of these
trees and aggregates their votes.

**Real company example:** Spotify uses gradient-boosted trees (XGBoost) for playlist
recommendations. Fraud detection at Stripe and PayPal relies heavily on decision tree
ensembles because they are explainable.

```python
# pip install scikit-learn numpy
import numpy as np
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, export_text


def train_and_inspect() -> None:
    iris = load_iris()
    X, y = iris.data, iris.target

    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(X, y)

    # The tree structure lives in clf.tree_ — a set of parallel arrays.
    # node_count, children_left, children_right, feature, threshold, value
    tree = clf.tree_
    print(f"Nodes in tree: {tree.node_count}")
    print(f"Max depth:     {tree.max_depth}")
    print(f"N leaves:      {tree.n_leaves}")

    # Print the learned rules (this is what you ship to a rules engine)
    print("\nLearned decision rules:")
    print(export_text(clf, feature_names=list(iris.feature_names)))


def trace_prediction(clf, feature_names, class_names, sample: np.ndarray) -> None:
    """
    Walk the tree manually — shows exactly which conditions fire.
    This is how LIME and SHAP generate explanations for tree models.
    """
    tree = clf.tree_
    node = 0  # start at root

    print(f"Tracing prediction for: {dict(zip(feature_names, sample))}\n")
    depth = 0
    while tree.children_left[node] != -1:  # -1 means leaf
        feat = tree.feature[node]
        thresh = tree.threshold[node]
        indent = "  " * depth
        if sample[feat] <= thresh:
            print(f"{indent}{feature_names[feat]} = {sample[feat]:.2f} <= {thresh:.2f}  → go LEFT")
            node = tree.children_left[node]
        else:
            print(f"{indent}{feature_names[feat]} = {sample[feat]:.2f} >  {thresh:.2f}  → go RIGHT")
            node = tree.children_right[node]
        depth += 1

    class_idx = np.argmax(tree.value[node])
    print(f"\nLeaf node {node}: predicted class = '{class_names[class_idx]}'")


if __name__ == "__main__":
    iris = load_iris()
    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(iris.data, iris.target)

    train_and_inspect()

    sample = np.array([5.1, 3.5, 1.4, 0.2])  # classic setosa
    trace_prediction(clf, iris.feature_names, iris.target_names, sample)
```

---

## 5. Expression Trees — Compilers and Calculators

When Python parses `3 + 4 * 2`, it builds an **Abstract Syntax Tree** (AST) where
`*` is a child of `+` to encode operator precedence. The `ast` module exposes this
tree directly. Compilers walk expression trees to generate bytecode; spreadsheet
engines walk them to evaluate formulas.

**Real company example:** Google Sheets formula engine, Python's own `compile()`
built-in, and ORMs like SQLAlchemy all build expression trees before generating
SQL or bytecode.

```python
import ast
import operator as op
from dataclasses import dataclass
from typing import Union


# --- Our own mini expression tree ---
@dataclass
class Num:
    value: float

@dataclass
class BinOp:
    left:  Union["BinOp", Num]
    right: Union["BinOp", Num]
    op_symbol: str


OPS = {"+": op.add, "-": op.sub, "*": op.mul, "/": op.truediv}


def evaluate(node: Union[BinOp, Num]) -> float:
    """Post-order evaluation: children must be evaluated before the parent."""
    if isinstance(node, Num):
        return node.value
    left_val  = evaluate(node.left)
    right_val = evaluate(node.right)
    return OPS[node.op_symbol](left_val, right_val)


def to_infix(node: Union[BinOp, Num]) -> str:
    """In-order traversal reproduces the original expression."""
    if isinstance(node, Num):
        return str(node.value)
    return f"({to_infix(node.left)} {node.op_symbol} {to_infix(node.right)})"


# Build:  3 + 4 * 2  →  tree encodes precedence
#         +
#        / \
#       3   *
#          / \
#         4   2
expr = BinOp(
    left=Num(3),
    right=BinOp(left=Num(4), right=Num(2), op_symbol="*"),
    op_symbol="+"
)

print(f"Expression:  {to_infix(expr)}")
print(f"Result:      {evaluate(expr)}")   # 11.0


# --- Python's own AST for comparison ---
def eval_with_python_ast(expr_str: str) -> float:
    """
    Walk Python's real AST — the same tree Python itself builds.
    Safe alternative to eval() — only allows arithmetic.
    """
    tree = ast.parse(expr_str, mode="eval")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            ops_map = {
                ast.Add: op.add, ast.Sub: op.sub,
                ast.Mult: op.mul, ast.Div: op.truediv,
            }
            return ops_map[type(node.op)](_eval(node.left), _eval(node.right))
        raise ValueError(f"Unsupported node: {type(node)}")

    return _eval(tree)


print(f"\nPython AST eval('3 + 4 * 2') = {eval_with_python_ast('3 + 4 * 2')}")
print(f"Python AST eval('(1+2)*(3+4)') = {eval_with_python_ast('(1+2)*(3+4)')}")
```

---

## 6. Huffman Encoding — Optimal Compression via a Binary Tree

Huffman coding assigns shorter bit strings to more frequent characters, building the
code from a binary tree. It is the backbone of DEFLATE, which powers `.zip`, `.gz`,
PNG images, and HTTP `Content-Encoding: gzip`. Every file you have ever downloaded
compressed was (partly) Huffman-encoded.

**Real company example:** zlib (used by Python, nginx, Git object storage) uses
Huffman trees as its entropy coder. JPEG uses a variant for quantised DCT coefficients.

```python
import heapq
from dataclasses import dataclass, field
from typing import Optional


@dataclass(order=True)
class HuffNode:
    freq:  int
    char:  Optional[str]   = field(compare=False, default=None)
    left:  Optional["HuffNode"] = field(compare=False, default=None)
    right: Optional["HuffNode"] = field(compare=False, default=None)

    @property
    def is_leaf(self) -> bool:
        return self.char is not None


def build_huffman(text: str) -> tuple[HuffNode, dict[str, str]]:
    """
    Build the Huffman tree and return (root, codebook).

    Algorithm:
      1. Count character frequencies.
      2. Push each character as a leaf into a min-heap (lowest freq = highest priority).
      3. Repeatedly merge the two lowest-frequency nodes into a new internal node.
      4. The last node in the heap is the root.

    Time: O(N log N) where N = number of unique characters.
    """
    from collections import Counter
    freq = Counter(text)
    heap = [HuffNode(f, ch) for ch, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left  = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)

    root = heap[0]
    codebook: dict[str, str] = {}

    def _build_codes(node: HuffNode, prefix: str) -> None:
        if node.is_leaf:
            codebook[node.char] = prefix or "0"  # handle single-char edge case
            return
        _build_codes(node.left,  prefix + "0")
        _build_codes(node.right, prefix + "1")

    _build_codes(root, "")
    return root, codebook


def encode(text: str, codebook: dict[str, str]) -> str:
    return "".join(codebook[ch] for ch in text)


def decode(bits: str, root: HuffNode) -> str:
    result = []
    node = root
    for bit in bits:
        node = node.left if bit == "0" else node.right
        if node.is_leaf:
            result.append(node.char)
            node = root
    return "".join(result)


if __name__ == "__main__":
    text = "this is an example of huffman encoding"
    root, codebook = build_huffman(text)

    print("Huffman codebook (char → bits):")
    for ch, code in sorted(codebook.items(), key=lambda x: len(x[1])):
        label = repr(ch)
        print(f"  {label:5s} → {code:10s}  (freq={text.count(ch)})")

    encoded = encode(text, codebook)
    decoded = decode(encoded, root)

    original_bits = len(text) * 8
    compressed_bits = len(encoded)
    ratio = compressed_bits / original_bits

    print(f"\nOriginal:   {original_bits} bits")
    print(f"Compressed: {compressed_bits} bits")
    print(f"Ratio:      {ratio:.2%}")
    print(f"Lossless:   {decoded == text}")
```

---

## Summary Table

| Use Case | Tree Type | Traversal Used | Real Product |
|---|---|---|---|
| File system | General tree | DFS / Post-order | macOS Finder, VS Code Explorer |
| HTML/DOM | General tree (n-ary) | BFS (querySelector) | Chrome, BeautifulSoup, Scrapy |
| JSON parsing | General tree | DFS (recursive) | AWS CDK, Datadog agent |
| Decision trees | Binary tree | Root-to-leaf path | Stripe fraud, Spotify recs |
| Expression trees | Binary tree | Post-order (eval) | Python AST, SQLAlchemy |
| Huffman encoding | Binary tree | Pre-order (codes) | zlib, gzip, PNG, JPEG |

The common thread: **whenever data has a natural parent-child hierarchy, a tree is
the right structure**, and DFS / BFS gives you a systematic way to process every node.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Patterns](./patterns.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
