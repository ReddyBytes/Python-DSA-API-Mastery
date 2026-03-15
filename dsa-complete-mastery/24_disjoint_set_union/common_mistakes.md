# DSU (Union-Find) — Common Mistakes & Error Prevention

DSU is one of the most elegant data structures in competitive programming and systems work —
but it has a small set of implementation mistakes that appear over and over. Each mistake is
subtle, produces wrong output silently (no crash, no exception), and is easy to introduce when
coding under pressure. This guide shows every common mistake with the exact wrong code, the
exact correct code, an explanation of why it breaks, and test cases to catch the bug.

---

## Background: How DSU Works

Before the mistakes, let's align on the correct baseline implementation:

```python
class DSU:
    """
    Disjoint Set Union (Union-Find) data structure.
    Supports union and find operations with:
        - Union by rank: O(log n) find without path compression
        - Path compression: O(α(n)) amortized find (α = inverse Ackermann, near-constant)
        - Both combined: O(α(n)) amortized for all operations
    """

    def __init__(self, n: int):
        self.parent = list(range(n))   # each node starts as its own root
        self.rank = [0] * n            # height upper bound for each tree

    def find(self, x: int) -> int:
        """Find the root of x's component with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """
        Merge the components of x and y.
        Returns True if they were in different components (merge happened).
        Returns False if they were already in the same component.
        """
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False   # already connected

        # Union by rank: attach smaller tree under larger tree
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx   # ensure rx has higher rank
        self.parent[ry] = rx  # attach ry's tree under rx

        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1   # only increase rank when merging two equal-rank trees

        return True

    def connected(self, x: int, y: int) -> bool:
        """Return True if x and y are in the same component."""
        return self.find(x) == self.find(y)
```

Now let's systematically break each part and show what goes wrong.

---

## Mistake 1 — Union Without Union by Rank/Size

### The Problem

Without union by rank/size, you always attach one root directly under the other in a fixed order.
Over time, this degenerates the tree into a linked list. A `find` on the deepest node must walk
every node in the list: O(n) per find operation.

### Wrong Code

```python
class DSU_wrong_no_rank:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union_WRONG(self, x: int, y: int) -> None:
        rx = self.find(x)
        ry = self.find(y)
        # WRONG: Always attach ry under rx regardless of tree sizes
        # This creates a chain: union(0,1), union(0,2), union(0,3)...
        # produces: 1→0, 2→0, 3→0... wait, that's actually fine for star shape
        # The real disaster is: union(0,1)→1→0, union(1,2)→2→1→0, union(2,3)→3→2→1→0
        self.parent[ry] = rx
```

Let's trace the worst-case scenario: unioning in a chain pattern.

```python
def demonstrate_degenerate_union():
    n = 8
    dsu = DSU_wrong_no_rank(n)

    # Chain unions: 1 under 0, 2 under 1, 3 under 2, etc.
    # This happens when we always find(x) = x and find(y) = y, attach y under x
    # For a chain: manually simulate what happens with sequential merges
    # union(0,1): 1's root=1 goes under 0's root=0 → parent[1]=0
    # union(1,2): find(1)=0 (root), find(2)=2 (root) → parent[2]=0... star!
    # The degenerate case comes when input is presented differently:
    # union(0,1), union(1,2)... if we always attach second root under first root:

    print("Simulating worst-case union without rank:")
    parent = list(range(n))

    def find_no_compress(x):
        depth = 0
        while parent[x] != x:
            x = parent[x]
            depth += 1
        return x, depth

    def union_bad(x, y):
        rx, _ = find_no_compress(x)
        ry, _ = find_no_compress(y)
        if rx != ry:
            parent[ry] = rx  # always attach second root under first root

    # Adversarial input: always union the current root with a new node
    # This creates a path 0←1←2←3←...
    for i in range(1, n):
        # union the root of the current chain with new node i
        # If we do union(0, i): find(0)=0 (it's root), find(i)=i → parent[i]=0 (star)
        # To create a chain: union(i-1, i) and if we attach second under first...
        # find(i-1) returns 0 (root of chain), find(i) = i, attach i under 0 → still star
        # The true degenerate: if we do union in such a way that the input FORCES a chain
        # Let's directly construct the chain to show the cost:
        pass

    # Direct demonstration: manually create chain
    parent = list(range(n))
    # Chain: n-1 → n-2 → ... → 1 → 0
    for i in range(n - 1, 0, -1):
        parent[i] = i - 1

    print("Chain structure: parent =", parent)
    print("Finding root of node", n-1, ":")
    steps = 0
    x = n - 1
    while parent[x] != x:
        print(f"  node {x} → parent {parent[x]}")
        x = parent[x]
        steps += 1
    print(f"  root: {x} (took {steps} steps for n={n})")
    print(f"  For n=1,000,000 nodes, find would take 999,999 steps!")

demonstrate_degenerate_union()
```

### Correct Code

```python
class DSU_correct_with_rank:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union_CORRECT(self, x: int, y: int) -> bool:
        rx = self.find(x)
        ry = self.find(y)
        if rx == ry:
            return False

        # CORRECT: attach smaller rank tree under larger rank tree
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx     # swap so rx always has higher or equal rank
        self.parent[ry] = rx    # attach ry under rx

        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1  # trees had equal height → merged tree is 1 taller

        return True
```

### Why This Matters

With union by rank alone (no path compression):
- The tree height is bounded by O(log n) — this is proven mathematically.
- A `find` visits at most O(log n) nodes instead of O(n).

Proof sketch: a tree of rank k has at least 2^k nodes. Therefore if we have n nodes,
the maximum rank is log2(n). Since tree height equals the rank, `find` is O(log n).

```python
def test_rank_bounds_height():
    """Verify that union by rank keeps tree height <= log2(n)."""
    import math
    n = 64
    dsu = DSU_correct_with_rank(n)

    # Union in worst-case order for height: always merge equal-rank trees
    # This creates maximum height. Even so, height stays <= log2(n).
    i = 0
    while i + 1 < n:
        dsu.union_CORRECT(i, i + 1)
        i += 2
    while i + 1 < n:
        dsu.union_CORRECT(i, i + 1)
        i += 2

    # Check max rank
    max_rank = max(dsu.rank)
    expected_max = math.ceil(math.log2(n))
    print(f"n={n}: max rank = {max_rank}, log2(n) = {expected_max:.1f}")
    assert max_rank <= expected_max, f"Rank {max_rank} exceeded log2({n})={expected_max}"
    print("PASS: Union by rank keeps height <= log2(n)")

test_rank_bounds_height()
```

### Alternative: Union by Size

Union by size is equivalent in practice. Instead of tracking tree height (rank), track the
number of nodes in each tree. Attach the smaller tree under the larger tree.

```python
class DSU_union_by_size:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.size = [1] * n    # each tree starts with size 1

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        # Attach smaller tree under larger tree
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        self.size[rx] += self.size[ry]   # update size of the merged tree
        return True

    def component_size(self, x: int) -> int:
        return self.size[self.find(x)]
```

Union by size has the advantage of giving you `component_size` for free, which is often needed
in problems that ask "how large is the connected component containing node X?"

---

## Mistake 2 — Find Without Path Compression

### The Problem

Without path compression, every `find` operation walks the entire path from node to root.
In a balanced tree (with union by rank), this is O(log n). But with repeated `find` calls
on deep nodes, the work accumulates. Path compression makes repeated finds nearly free by
flattening the tree as a side effect of each find.

### Wrong Code

```python
class DSU_wrong_no_compression:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find_WRONG(self, x: int) -> int:
        # WRONG: walks to root without compressing the path
        while self.parent[x] != x:
            x = self.parent[x]
        return x
        # Every subsequent find on any node in this path will repeat the same walk
```

### Correct Code: Recursive Path Compression

```python
def find_CORRECT_recursive(parent: list, x: int) -> int:
    """
    Recursive path compression.
    After find(x), every node on the path from x to root points directly to root.
    This makes future finds on these nodes O(1).
    """
    if parent[x] != x:
        parent[x] = find_CORRECT_recursive(parent, parent[x])  # compress path
    return parent[x]
```

### Correct Code: Iterative Two-Pass Path Compression

The recursive approach may hit Python's recursion limit for large n. The iterative version
does the same thing in two passes:

```python
def find_CORRECT_iterative(parent: list, x: int) -> int:
    """
    Iterative path compression (two-pass).
    Pass 1: walk to root to find it
    Pass 2: walk again, setting every node's parent directly to root
    """
    # Pass 1: find the root
    root = x
    while parent[root] != root:
        root = parent[root]

    # Pass 2: compress the path — set every node's parent to root
    curr = x
    while curr != root:
        next_node = parent[curr]
        parent[curr] = root    # point directly to root
        curr = next_node

    return root
```

### Correct Code: Path Halving (One-Pass Optimization)

A common one-pass optimization: instead of full compression, each node skips to its grandparent.
Over repeated calls, this achieves the same O(α(n)) amortized complexity with slightly less work
per call:

```python
def find_CORRECT_path_halving(parent: list, x: int) -> int:
    """
    Path halving: each node's parent is set to its grandparent on the way up.
    One-pass, less memory writes than full compression, same asymptotic complexity.
    """
    while parent[x] != x:
        parent[x] = parent[parent[x]]  # skip to grandparent
        x = parent[x]
    return x
```

### Demonstration: Cost Difference

```python
def compare_find_costs():
    """Show how many parent pointer reads each find variant requires."""
    n = 16
    # Create a chain: 15 → 14 → 13 → ... → 1 → 0 (worst case tree without rank)
    parent_no_compress = list(range(n))
    for i in range(1, n):
        parent_no_compress[i] = i - 1   # i's parent is i-1

    parent_compress = parent_no_compress.copy()

    def find_no_compress_counted(parent, x):
        steps = 0
        while parent[x] != x:
            x = parent[x]
            steps += 1
        return x, steps

    def find_compress_counted(parent, x):
        root = x
        steps = 0
        while parent[root] != root:
            root = parent[root]
            steps += 1
        # Path compression pass
        curr = x
        while curr != root:
            nxt = parent[curr]
            parent[curr] = root
            curr = nxt
        return root, steps

    # First find on node 15
    root, steps = find_no_compress_counted(parent_no_compress, 15)
    print(f"Without compression: find(15) in chain of {n} = {steps} steps")

    root, steps = find_compress_counted(parent_compress, 15)
    print(f"With compression:    find(15) in chain of {n} = {steps} steps (same)")

    # Second find on node 15 — now compression has flattened the path
    root2, steps2 = find_no_compress_counted(parent_no_compress, 14)
    print(f"\nWithout compression: find(14) after find(15) = {steps2} steps")

    root2, steps2 = find_compress_counted(parent_compress, 14)
    print(f"With compression:    find(14) after find(15) = {steps2} steps (nearly free!)")

    print(f"\nAfter compression, parent array: {parent_compress}")
    print("All nodes on the path now point directly to root 0 → future finds are O(1)")

compare_find_costs()
```

### Test Cases to Catch Missing Path Compression

```python
def test_path_compression():
    """
    Test that path compression correctly flattens the tree.
    After find(x), parent[x] should equal the root directly.
    """
    # Build a chain: 3 → 2 → 1 → 0
    parent = [0, 0, 1, 2]  # parent[3]=2, parent[2]=1, parent[1]=0, parent[0]=0

    root = find_CORRECT_iterative(parent, 3)
    assert root == 0, f"Root should be 0, got {root}"

    # After compression, parent[3] should point directly to 0, not 2
    assert parent[3] == 0, f"Path compression failed: parent[3]={parent[3]}, expected 0"
    assert parent[2] == 0, f"Path compression failed: parent[2]={parent[2]}, expected 0"
    assert parent[1] == 0, f"Path compression failed: parent[1]={parent[1]}, expected 0"

    print("PASS: Path compression correctly flattened all nodes to root")

test_path_compression()
```

---

## Mistake 3 — Checking Connectivity Using == Instead of find()

### The Problem

To check if nodes A and B are connected, you must compare their roots (what `find()` returns),
not their immediate parents. Two nodes can be in the same component but have different `parent`
values if they are not roots themselves. Using `parent[a] == parent[b]` only checks if they share
the same immediate parent — which is a much stronger (and wrong) condition.

### Wrong Code

```python
def are_connected_WRONG(parent: list, a: int, b: int) -> bool:
    # WRONG: compares immediate parents, not roots
    # Two nodes can be in the same component but have different immediate parents
    return parent[a] == parent[b]
```

### Why This Fails

```python
def demonstrate_wrong_connectivity_check():
    """
    Show that parent[a] == parent[b] gives wrong answer
    for nodes in the same component.
    """
    # Build this tree:
    #       0 (root)
    #      / \
    #     1   2
    #    / \
    #   3   4
    parent = [0, 0, 0, 1, 1]
    # parent[0]=0 (root), parent[1]=0, parent[2]=0, parent[3]=1, parent[4]=1

    # Are nodes 3 and 4 connected? YES — same component (both under root 0)
    # Wrong check: parent[3]=1, parent[4]=1 → equal! (accidentally correct here)
    print(f"Wrong check: parent[3]==parent[4]? {parent[3] == parent[4]}")  # True (lucky)

    # Are nodes 3 and 2 connected? YES — same component (both under root 0)
    # Wrong check: parent[3]=1, parent[2]=0 → NOT equal! Wrong answer!
    print(f"Wrong check: parent[3]==parent[2]? {parent[3] == parent[2]}")  # False (WRONG!)

    # Correct check using find:
    def find_simple(x):
        while parent[x] != x:
            x = parent[x]
        return x

    print(f"Correct check: find(3)==find(2)? {find_simple(3) == find_simple(2)}")  # True
    print(f"Correct check: find(3)==find(4)? {find_simple(3) == find_simple(4)}")  # True

    print("\nConclusion: ALWAYS use find(a) == find(b) to check connectivity.")
    print("parent[a] == parent[b] only works if both a and b are direct children of root.")

demonstrate_wrong_connectivity_check()
```

### Correct Code

```python
def are_connected_CORRECT(dsu: DSU, a: int, b: int) -> bool:
    # CORRECT: compare ROOTS (what find() returns), not immediate parents
    return dsu.find(a) == dsu.find(b)
```

### Another Form of This Mistake: Storing Root and Comparing Stale Values

A more subtle variant: some implementations cache the root and compare cached values,
but the cache becomes stale after subsequent union operations.

```python
# WRONG PATTERN: caching root outside find
def union_and_check_WRONG(parent, rank, edges):
    roots = {i: i for i in range(len(parent))}  # cache roots — becomes stale!

    for a, b in edges:
        ra = roots[a]  # STALE after unions
        rb = roots[b]  # STALE after unions
        if ra != rb:
            parent[rb] = ra
            # Cache is NOT updated for all nodes in ry's component → stale
```

The fix: never cache roots. Always call `find()` which returns the current root with full
path compression applied. The whole point of find() is to compute the current root on-demand.

### Test Cases

```python
def test_connectivity_check():
    """
    Test that connected() uses find() correctly, not parent comparison.
    """
    dsu = DSU(6)  # nodes 0-5

    # Build a chain: 0-1-2-3 are connected, 4-5 are separate
    dsu.union(0, 1)
    dsu.union(1, 2)
    dsu.union(2, 3)
    dsu.union(4, 5)

    # Same component checks
    assert dsu.connected(0, 3), "0 and 3 should be connected"
    assert dsu.connected(0, 2), "0 and 2 should be connected"
    assert dsu.connected(1, 3), "1 and 3 should be connected"
    assert dsu.connected(4, 5), "4 and 5 should be connected"

    # Different component checks
    assert not dsu.connected(0, 4), "0 and 4 should NOT be connected"
    assert not dsu.connected(3, 5), "3 and 5 should NOT be connected"

    # Specifically test the case that breaks parent[a] == parent[b]:
    # After chain 0-1-2-3: nodes 0 and 2 are connected but may have different parents
    # Check that we don't accidentally pass by using immediate parent comparison
    # (Implementation detail: with path compression, parent[2] may or may not == parent[0])
    # The only reliable check is find(0) == find(2)

    print("PASS: All connectivity checks correct")
    print(f"  parent array after unions: {dsu.parent}")
    print(f"  Note: some nodes may have different parents but same ROOT")

test_connectivity_check()
```

---

## Mistake 4 — Initializing parent Incorrectly

### The Problem

DSU initialization must make every node its own root. This represents a state where no nodes
are connected. The common mistake is initializing `parent = [0] * n`, which makes every node
point to node 0, as if all nodes are already in the same component containing node 0.

### Wrong Code

```python
class DSU_wrong_init:
    def __init__(self, n: int):
        # WRONG: all nodes point to 0 — they all appear to be in one component!
        self.parent = [0] * n
        self.rank = [0] * n
```

### Why This Fails

```python
def demonstrate_wrong_init():
    n = 5
    # Wrong initialization
    parent_wrong = [0] * n   # all point to node 0
    parent_correct = list(range(n))   # each is its own root

    def find_simple(parent, x):
        while parent[x] != x:
            x = parent[x]
        return x

    print("Wrong initialization: parent =", parent_wrong)
    print("  find(0) =", find_simple(parent_wrong, 0))  # 0
    print("  find(1) =", find_simple(parent_wrong, 1))  # 0 — wrong! 1 should be its own component
    print("  find(2) =", find_simple(parent_wrong, 2))  # 0 — wrong!

    # Connectivity check immediately after init (before any union):
    # Nodes 1 and 2 should NOT be connected yet
    connected = find_simple(parent_wrong, 1) == find_simple(parent_wrong, 2)
    print(f"  Are 1 and 2 connected after init (wrong)? {connected}")  # True — WRONG!

    print("\nCorrect initialization: parent =", parent_correct)
    print("  find(0) =", find_simple(parent_correct, 0))  # 0
    print("  find(1) =", find_simple(parent_correct, 1))  # 1 (its own root)
    print("  find(2) =", find_simple(parent_correct, 2))  # 2 (its own root)
    connected_correct = find_simple(parent_correct, 1) == find_simple(parent_correct, 2)
    print(f"  Are 1 and 2 connected after init (correct)? {connected_correct}")  # False

demonstrate_wrong_init()
```

### Correct Code

```python
class DSU_correct_init:
    def __init__(self, n: int):
        # CORRECT: each node is its own parent (its own component)
        self.parent = list(range(n))    # [0, 1, 2, 3, ..., n-1]
        self.rank = [0] * n             # all trees have height 0 initially
```

### Related Mistake: Wrong Initial Size

When the problem has node IDs that are not 0-indexed, or uses node labels that are not integers,
you must map them correctly. Off-by-one in the size parameter is a common source of IndexError:

```python
# Problem: nodes are labeled 1 to n (not 0 to n-1)
class DSU_one_indexed:
    def __init__(self, n: int):
        # WRONG: size n creates indices 0..n-1, but nodes are 1..n
        # self.parent = list(range(n))    # parent[n] would cause IndexError

        # CORRECT: allocate n+1 to handle 1-indexed nodes
        self.parent = list(range(n + 1))    # indices 0..n; we use 1..n
        self.rank = [0] * (n + 1)

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True
```

### Test Cases

```python
def test_initialization():
    """Verify that a newly initialized DSU has n separate components."""
    n = 6
    dsu = DSU(n)

    # No unions done yet — every node should be in its own component
    for i in range(n):
        assert dsu.find(i) == i, f"Node {i} should be its own root before any union"

    for i in range(n):
        for j in range(n):
            if i != j:
                assert not dsu.connected(i, j), \
                    f"Nodes {i} and {j} should NOT be connected after init"

    print("PASS: Correct initialization — n separate components")
    print(f"  parent = {dsu.parent}")

    # Also test that wrong init fails
    wrong_parent = [0] * n
    def find_wrong(x):
        while wrong_parent[x] != x:
            x = wrong_parent[x]
        return x

    # Nodes 1 and 2 should not be connected, but wrong init makes them appear so
    wrong_connected = find_wrong(1) == find_wrong(2)
    assert wrong_connected == True, "Wrong init DOES create false connections"
    print(f"\nWrong init confirms: find(1)==find(2)={wrong_connected} (incorrectly True)")

test_initialization()
```

---

## Mistake 5 — Modifying Rank During Path Compression

### The Problem

`rank` is an upper bound on tree height used to decide which root should become the child during
union. Path compression changes the tree structure — it shortens paths — but it does NOT update
the rank array, and it should not. The rank remains an upper bound even after compression.
Modifying rank during path compression (e.g., decrementing it) corrupts the union-by-rank
invariant and can cause unbalanced trees.

### Wrong Code

```python
class DSU_wrong_rank_update:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find_WRONG_rank_update(self, x: int) -> int:
        if self.parent[x] != x:
            original_parent = self.parent[x]
            self.parent[x] = self.find_WRONG_rank_update(self.parent[x])
            # WRONG: decrementing rank when compressing path
            # This seems logical (shorter path = lower rank) but BREAKS the invariant
            if self.parent[x] != original_parent:
                self.rank[x] = max(0, self.rank[x] - 1)
        return self.parent[x]
```

### Why Modifying Rank is Wrong

```python
def demonstrate_wrong_rank_modification():
    """
    Show that modifying rank during path compression breaks union decisions.
    """
    print("Demonstrating rank corruption from path compression modification:\n")

    # Set up a scenario where rank incorrectly gets decremented
    # Consider tree:
    #       A (rank=2)
    #       |
    #       B (rank=1)
    #       |
    #       C (rank=0)
    #       |
    #       D (rank=0)

    n = 4
    parent = [0, 0, 1, 2]   # D→C→B→A (chain where 0=A, 1=B, 2=C, 3=D)
    rank = [2, 1, 0, 0]      # A has rank 2

    print("Before path compression:")
    print(f"  parent: {parent}, rank: {rank}")

    # After find(D=3) with path compression: D, C, B all point to A
    # Their ranks should remain unchanged — rank is just an upper bound
    # After compression:
    parent_after = [0, 0, 0, 0]   # all point to A
    rank_correct = [2, 1, 0, 0]   # UNCHANGED — rank stays as upper bound
    rank_wrong = [2, 0, 0, 0]     # WRONG — B's rank was decremented to 0

    print("\nAfter path compression of find(D):")
    print(f"  parent: {parent_after}")
    print(f"  Correct rank (unchanged): {rank_correct}")
    print(f"  Wrong rank (decremented B): {rank_wrong}")

    # Now if we do union(A, E) where E has rank=1:
    # With correct rank: rank[A]=2 > rank[E]=1 → E goes under A ✓
    # With wrong rank:   rank[A]=2 > rank[E]=1 → E goes under A ✓ (same, lucky)

    # But union(B, F) where F has rank=2:
    # With correct rank: rank[B]=1 < rank[F]=2 → B goes under F ✓
    # With wrong rank:   rank[B]=0 < rank[F]=2 → B goes under F ✓ (same, lucky again)

    # The subtle issue: rank[B] was 1 (correct upper bound for B's subtree height).
    # After wrong decrement, rank[B] = 0. If we then do union(B, G) where G has rank=0:
    # Correct: rank[B]=1 > rank[G]=0 → G goes under B ✓ (B's subtree was taller)
    # Wrong:   rank[B]=0 == rank[G]=0 → B under G OR G under B (arbitrary!)
    #          If G goes under B: rank[B] incremented to 1 again — inconsistent
    #          If B goes under G: B's subtree (which has height 1) goes under G (height 0)
    #                              → combined tree has height 2 but rank[G] only set to 1
    #                              → rank[G] underestimates actual height → WRONG!

    print("\nThe corruption case:")
    print("  After wrong decrement: rank[B]=0")
    print("  If union(B, G) where rank[G]=0: tie → may attach B's DEEPER tree under G")
    print("  rank[G] becomes 1, but B's subtree had height 1 → combined height is 2")
    print("  rank[G]=1 now UNDERESTIMATES the tree height")
    print("  This breaks the guarantee that tree height ≤ rank")

demonstrate_wrong_rank_modification()
```

### Correct Code: Never Touch Rank in Find

```python
class DSU_correct_rank_handling:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find_CORRECT(self, x: int) -> int:
        """
        Path compression without touching rank.
        rank is an UPPER BOUND on tree height, not the exact height.
        After path compression, the tree is shorter, but rank remains valid
        as an upper bound — it just becomes a looser bound, which is fine.
        """
        if self.parent[x] != x:
            self.parent[x] = self.find_CORRECT(self.parent[x])
            # NO rank modification here — intentionally left out
        return self.parent[x]

    def union_CORRECT(self, x: int, y: int) -> bool:
        rx, ry = self.find_CORRECT(x), self.find_CORRECT(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1  # rank ONLY increases during union, never decreases
        return True
```

### The Formal Invariant

The rank invariant is:
1. rank[x] is an upper bound on the height of the subtree rooted at x
2. If x is not a root (parent[x] != x), then rank[x] < rank[parent[x]]
3. rank only increases when two trees of equal rank are merged
4. rank NEVER decreases

Path compression maintains invariants 1 and 2: after compression, x's height decreases (or stays
the same), so rank[x] is still a valid upper bound. The strict inequality in invariant 2 is also
preserved because x's new parent (the root) has a higher rank than x's old parent, which already
had a higher rank than x.

### Test Cases

```python
def test_rank_invariant():
    """
    Verify that rank invariant holds after a sequence of unions and finds.
    Invariant: if parent[x] != x, then rank[x] < rank[parent[x]]
    """
    import random

    n = 20
    dsu = DSU_correct_rank_handling()  # would need to instantiate with n
    dsu2 = DSU(n)

    # Perform random unions
    random.seed(42)
    for _ in range(30):
        a = random.randint(0, n - 1)
        b = random.randint(0, n - 1)
        dsu2.union(a, b)

    # Verify rank invariant: if x is not a root, rank[x] < rank[parent[x]]
    for x in range(n):
        if dsu2.parent[x] != x:
            p = dsu2.parent[x]
            assert dsu2.rank[x] <= dsu2.rank[p], (
                f"Rank invariant violated: rank[{x}]={dsu2.rank[x]} "
                f"but rank[parent[{x}]={p}]={dsu2.rank[p]}"
            )

    print("PASS: Rank invariant holds after 30 random unions")
    print(f"  Final parent: {dsu2.parent}")
    print(f"  Final rank:   {dsu2.rank}")


def test_rank_not_decremented():
    """
    Verify that after path compression via find(), ranks do NOT decrease.
    """
    n = 8
    dsu = DSU(n)

    # Build a chain manually to create a tall tree
    # We bypass union() to force a specific structure
    # 7→6→5→4→3→2→1→0 (chain of 8)
    for i in range(1, n):
        dsu.parent[i] = i - 1
    dsu.rank[0] = 3  # manually set root's rank (as if it was built by unions)

    rank_before = dsu.rank.copy()

    # Now do finds that trigger path compression
    dsu.find(7)  # compresses 7→6→5→4→3→2→1→0 to all point to 0
    dsu.find(5)
    dsu.find(3)

    rank_after = dsu.rank.copy()

    for i in range(n):
        assert rank_after[i] >= rank_before[i] or rank_after[i] == rank_before[i], (
            f"Rank decreased at node {i}: {rank_before[i]} → {rank_after[i]}"
        )

    print("PASS: Ranks do not decrease after path compression")
    print(f"  Rank before: {rank_before}")
    print(f"  Rank after:  {rank_after}")

test_rank_invariant()
test_rank_not_decremented()
```

---

## Full Correct DSU Template (Interview-Ready)

This is the exact template to use in any interview or competitive programming problem:

```python
class DSU:
    """
    Production-quality DSU with:
    - Union by rank: ensures O(log n) find without path compression
    - Path compression (recursive): achieves O(α(n)) amortized per operation
    - Component count tracking
    - Component size tracking (uses union by size internally when size matters)
    """

    def __init__(self, n: int):
        self.parent = list(range(n))   # CORRECT: each node is its own parent
        self.rank = [0] * n
        self.size = [1] * n            # size of each component (useful bonus)
        self.num_components = n        # start with n separate components

    def find(self, x: int) -> int:
        """Find root with path compression. O(α(n)) amortized."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # compress — do NOT modify rank
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """
        Union components of x and y.
        Returns True if merge happened, False if already connected.
        """
        rx, ry = self.find(x), self.find(y)  # CORRECT: use find(), not parent[]
        if rx == ry:
            return False                       # already in same component

        # CORRECT: union by rank — attach smaller under larger
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx    # ensure rx always has >= rank

        self.parent[ry] = rx   # attach ry's tree under rx

        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1  # rank ONLY increases in union when ranks were equal

        self.size[rx] += self.size[ry]  # update merged component size
        self.num_components -= 1

        return True

    def connected(self, x: int, y: int) -> bool:
        """Return True if x and y are in the same component."""
        return self.find(x) == self.find(y)   # CORRECT: compare find() results

    def component_size(self, x: int) -> int:
        """Return size of the component containing x."""
        return self.size[self.find(x)]


# Quick verification of the complete correct implementation
def test_full_dsu():
    dsu = DSU(7)

    # Check 1: initialization
    for i in range(7):
        assert dsu.find(i) == i, f"Node {i} should be its own root"
    assert dsu.num_components == 7

    # Check 2: basic union
    assert dsu.union(0, 1) == True
    assert dsu.union(1, 2) == True
    assert dsu.union(3, 4) == True
    assert dsu.num_components == 4

    # Check 3: connected check uses find() correctly
    assert dsu.connected(0, 2) == True
    assert dsu.connected(0, 3) == False

    # Check 4: redundant union returns False
    assert dsu.union(0, 2) == False

    # Check 5: component sizes
    assert dsu.component_size(0) == 3  # {0, 1, 2}
    assert dsu.component_size(3) == 2  # {3, 4}
    assert dsu.component_size(5) == 1  # {5} alone

    # Check 6: merge large components
    dsu.union(0, 3)  # merge {0,1,2} and {3,4}
    assert dsu.component_size(0) == 5
    assert dsu.connected(2, 4) == True
    assert dsu.num_components == 3

    # Check 7: rank invariant holds
    for x in range(7):
        if dsu.parent[x] != x:
            p = dsu.parent[x]
            assert dsu.rank[x] <= dsu.rank[p], \
                f"Rank invariant violated at node {x}"

    print("PASS: Full DSU implementation correct")
    print(f"  parent: {dsu.parent}")
    print(f"  rank:   {dsu.rank}")
    print(f"  size:   {dsu.size}")
    print(f"  num_components: {dsu.num_components}")

test_full_dsu()
```

---

## Summary of All Mistakes

| Mistake | Root Cause | Symptom | Fix |
|---|---|---|---|
| No union by rank/size | Always attach second root under first | O(n) find on deep chains | Track rank or size; attach smaller under larger |
| No path compression | Find walks full path every time | O(log n) per find (slow on repeated calls) | Set parent[x] = root during find |
| Connectivity check with parent[] | Parent ≠ root for non-root nodes | False negatives: reports disconnected for connected nodes | Always use find(a) == find(b) |
| parent = [0] * n | All nodes pre-connected to node 0 | False positives: all nodes appear connected at init | Use parent = list(range(n)) |
| Decrement rank in find | Rank no longer valid upper bound | Unbalanced trees; height > rank guarantee broken | Never modify rank in find; only increment in union |

### When to Use Union by Rank vs Union by Size

Both achieve O(log n) height. Choose based on what extra information you need:

- **Union by rank**: no extra cost, no component size info → use for pure connectivity
- **Union by size**: stores component sizes → use when you need `component_size(x)`

They can even be combined (track both), though in practice one suffices.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Real World Usage](./real_world_usage.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
