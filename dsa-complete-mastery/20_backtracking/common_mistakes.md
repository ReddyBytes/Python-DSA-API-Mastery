# Backtracking — Common Mistakes & Error Prevention

---

## Mistake 1: Not Copying Before Adding to Result — All Results Point to the Same List

### The Bug

In Python, lists are passed and stored by reference. When you do `result.append(current)`, you store a reference to the exact list object `current`. Every time `current` is modified later (more elements added or removed during backtracking), every previously stored reference reflects that change. By the time backtracking finishes, all entries in `result` contain the same (empty or partially filled) list.

### WRONG Code

```python
def subsets_wrong(nums: list[int]) -> list[list[int]]:
    result = []
    current = []

    def backtrack(start: int) -> None:
        result.append(current)          # WRONG: appends a reference to the same list
        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1)
            current.pop()               # when this modifies current, ALL stored refs change

    backtrack(0)
    return result
```

**What actually happens:**

```
nums = [1, 2]
After backtrack completes, current = []
All entries in result point to current = []
result = [[], [], [], []]   ← all point to the same [] object!
Expected = [[], [1], [1,2], [2]]
```

### CORRECT Code

```python
def subsets_correct(nums: list[int]) -> list[list[int]]:
    result = []
    current = []

    def backtrack(start: int) -> None:
        result.append(current[:])       # CORRECT: shallow copy at time of capture
        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1)
            current.pop()

    backtrack(0)
    return result


# Equivalent using list() constructor
def subsets_list_copy(nums: list[int]) -> list[list[int]]:
    result = []
    current = []

    def backtrack(start: int) -> None:
        result.append(list(current))    # list() also creates a shallow copy
        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1)
            current.pop()

    backtrack(0)
    return result
```

### Why Shallow Copy Is Sufficient Here

For lists of integers (or any immutable values), `current[:]` is all you need. A deep copy (`copy.deepcopy`) is only necessary when `current` contains mutable objects (e.g., lists of lists) that themselves change during backtracking.

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_all_point_to_same_list():
    result = subsets_wrong([1, 2])
    # All entries in result are the same object (empty list at the end)
    # Check that they all refer to the same object id
    ids = [id(r) for r in result]
    assert len(set(ids)) == 1, f"WRONG: all {len(result)} entries share the same list object"


def test_wrong_all_empty_at_end():
    result = subsets_wrong([1, 2, 3])
    # After backtracking, current is [] — all refs show []
    for r in result:
        assert r == [], f"WRONG: expected all to be [], got {r}"


def test_correct_subsets_unique_objects():
    result = subsets_correct([1, 2])
    # All entries must be distinct objects
    ids = [id(r) for r in result]
    assert len(set(ids)) == len(result), "Each subset must be a distinct list object"


def test_correct_subsets_values():
    result = subsets_correct([1, 2, 3])
    expected = [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
    assert sorted(result) == sorted(expected)


def test_correct_single_element():
    result = subsets_correct([1])
    assert sorted(result) == [[], [1]]


def test_correct_empty_input():
    result = subsets_correct([])
    assert result == [[]]


def test_correct_subsets_count():
    """For n elements, there should be 2^n subsets."""
    for n in range(5):
        nums = list(range(n))
        result = subsets_correct(nums)
        assert len(result) == 2 ** n, f"Expected {2**n} subsets for n={n}, got {len(result)}"


def test_list_copy_equivalent():
    for nums in [[], [1], [1, 2], [1, 2, 3]]:
        r1 = subsets_correct(nums)
        r2 = subsets_list_copy(nums)
        assert sorted(r1) == sorted(r2)


if __name__ == "__main__":
    print("=== WRONG ===")
    wrong = subsets_wrong([1, 2])
    print(f"result = {wrong}")    # [[], [], [], []] — all point to same []

    print("\n=== CORRECT ===")
    correct = subsets_correct([1, 2])
    print(f"result = {correct}")  # [[], [1], [2], [1, 2]]

    # Demonstrate reference aliasing
    result = []
    current = []
    result.append(current)    # append reference
    current.append(99)        # modify current
    print(f"\nReference aliasing demo: result={result}")  # [[99]] — not [[]]!
```

### Key Takeaway

- **Always copy** before appending to result: `result.append(current[:])`.
- The copy must be made **at the moment of recording** — not at the beginning or end of the function.
- This bug is silent: no error is thrown, but all result entries share state and are corrupted.

---

## Mistake 2: Duplicate Subsets/Permutations — Not Sorting and Skipping Duplicates

### The Bug

When the input contains duplicate values (e.g., `[1, 1, 2]`), the backtracking tree generates duplicate subsets/permutations because the same value appears at multiple positions. Without sorting and explicitly skipping duplicates at the same recursion level, you get two copies of `[1, 2]`.

### WRONG Code

```python
def subsets_with_dup_wrong(nums: list[int]) -> list[list[int]]:
    result = []
    current = []

    def backtrack(start: int) -> None:
        result.append(current[:])
        for i in range(start, len(nums)):
            current.append(nums[i])     # WRONG: no duplicate check
            backtrack(i + 1)
            current.pop()

    backtrack(0)
    return result


def permutations_with_dup_wrong(nums: list[int]) -> list[list[int]]:
    result = []
    current = []
    used = [False] * len(nums)

    def backtrack() -> None:
        if len(current) == len(nums):
            result.append(current[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            current.append(nums[i])     # WRONG: no duplicate check
            used[i] = True
            backtrack()
            used[i] = False
            current.pop()

    backtrack()
    return result
```

### CORRECT Code

```python
def subsets_with_dup_correct(nums: list[int]) -> list[list[int]]:
    nums.sort()                         # STEP 1: sort so duplicates are adjacent
    result = []
    current = []

    def backtrack(start: int) -> None:
        result.append(current[:])
        for i in range(start, len(nums)):
            # STEP 2: skip duplicates at the same recursion level
            if i > start and nums[i] == nums[i - 1]:
                continue
            current.append(nums[i])
            backtrack(i + 1)
            current.pop()

    backtrack(0)
    return result


def permutations_with_dup_correct(nums: list[int]) -> list[list[int]]:
    nums.sort()                         # STEP 1: sort
    result = []
    current = []
    used = [False] * len(nums)

    def backtrack() -> None:
        if len(current) == len(nums):
            result.append(current[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            # STEP 2: skip if same value as previous AND previous was not used
            # (meaning we already explored starting with nums[i-1] at this level)
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue
            current.append(nums[i])
            used[i] = True
            backtrack()
            used[i] = False
            current.pop()

    backtrack()
    return result
```

### Why `i > start` and Not Just `i > 0`

```
nums = [1, 1, 2],  backtrack(start=0)
Iteration:  i=0 → nums[0]=1  (first 1)
            i=1 → nums[1]=1  (second 1)
                  i > start (1 > 0) and nums[1]==nums[0] → SKIP
                  Without this: generates [1,2] twice (once starting with first 1, once with second 1)

backtrack(start=1)  ← called after choosing first 1
Iteration:  i=1 → nums[1]=1  (second 1)
            i=2 → nums[2]=2  (2)
                  i > start (2 > 1) — correct check, prevents skipping legitimate entries

If we used `i > 0` instead:
  backtrack(start=1), i=1: 1 > 0 and nums[1]==nums[0] → WOULD SKIP, missing [1,1,2]!
```

### Test Cases That Expose the Bug

```python
import pytest
from collections import Counter


def test_wrong_subsets_has_duplicates():
    result = subsets_with_dup_wrong([1, 1, 2])
    # Convert to tuples for counting
    as_tuples = [tuple(sorted(r)) for r in result]
    counts = Counter(as_tuples)
    duplicates = {k: v for k, v in counts.items() if v > 1}
    assert duplicates, f"WRONG: expected duplicates, got none (result={result})"


def test_correct_subsets_no_duplicates():
    result = subsets_with_dup_correct([1, 1, 2])
    as_tuples = [tuple(r) for r in result]
    assert len(as_tuples) == len(set(as_tuples)), "No duplicate subsets expected"
    expected = [(), (1,), (1, 1), (1, 1, 2), (1, 2), (2,)]
    assert sorted(as_tuples) == sorted(expected)


def test_wrong_permutations_has_duplicates():
    result = permutations_with_dup_wrong([1, 1, 2])
    as_tuples = [tuple(r) for r in result]
    counts = Counter(as_tuples)
    duplicates = {k: v for k, v in counts.items() if v > 1}
    assert duplicates, f"WRONG: expected duplicates, got none"


def test_correct_permutations_no_duplicates():
    result = permutations_with_dup_correct([1, 1, 2])
    as_tuples = [tuple(r) for r in result]
    assert len(as_tuples) == len(set(as_tuples))
    assert len(result) == 3   # 3!/2! = 3 unique permutations


def test_correct_all_distinct():
    """No duplicates in input — should produce 2^n subsets."""
    result = subsets_with_dup_correct([1, 2, 3])
    assert len(result) == 8


def test_correct_all_same():
    """[1,1,1] — subsets are: [], [1], [1,1], [1,1,1]"""
    result = subsets_with_dup_correct([1, 1, 1])
    as_tuples = sorted([tuple(r) for r in result])
    assert as_tuples == [(), (1,), (1, 1), (1, 1, 1)]


def test_correct_two_pairs():
    result = subsets_with_dup_correct([1, 1, 2, 2])
    as_tuples = [tuple(r) for r in result]
    assert len(as_tuples) == len(set(as_tuples))
    assert len(result) == 9   # (1+1)*(1+1+1) = 9 unique subsets


if __name__ == "__main__":
    print("=== WRONG subsets [1,1,2] ===")
    w = subsets_with_dup_wrong([1, 1, 2])
    print(sorted([tuple(r) for r in w]))   # contains duplicates

    print("\n=== CORRECT subsets [1,1,2] ===")
    c = subsets_with_dup_correct([1, 1, 2])
    print(sorted([tuple(r) for r in c]))   # no duplicates

    print("\n=== WRONG permutations [1,1,2] ===")
    wp = permutations_with_dup_wrong([1, 1, 2])
    print(sorted([tuple(r) for r in wp]))

    print("\n=== CORRECT permutations [1,1,2] ===")
    cp = permutations_with_dup_correct([1, 1, 2])
    print(sorted([tuple(r) for r in cp]))
```

### Key Takeaway

1. Sort the input first so duplicates are adjacent.
2. In the for-loop: `if i > start and nums[i] == nums[i-1]: continue` — skip when we would pick the same value as a sibling branch.
3. The guard is `i > start` (not `i > 0`) so we don't skip the first element of a deeper recursion level.

---

## Mistake 3: Permutations — Using `start` Index Instead of a `used` Array

### The Bug

Combination generation uses a `start` pointer to only move forward through the array, which prevents reusing elements and avoids order duplicates. Permutations require every element to be usable at every position — a `start` pointer enforces a "pick from remaining tail" constraint, which generates combinations (subsets of a fixed size), not permutations.

### WRONG Code

```python
def permutations_wrong(nums: list[int]) -> list[list[int]]:
    result = []
    current = []

    def backtrack(start: int) -> None:  # WRONG: using start like combinations
        if len(current) == len(nums):
            result.append(current[:])
            return
        for i in range(start, len(nums)):   # WRONG: only picks from position 'start' onward
            current.append(nums[i])
            backtrack(i + 1)        # WRONG: advances start — skips earlier elements
            current.pop()

    backtrack(0)
    return result
```

**What the wrong version actually generates for `[1, 2, 3]`:**

```
start=0: picks 1,2,3 (only combinations of length 3 from position 0)
         [1,2,3] only — never generates [3,1,2], [2,1,3], etc.
```

### CORRECT Code

```python
def permutations_correct(nums: list[int]) -> list[list[int]]:
    result = []
    current = []
    used = [False] * len(nums)   # CORRECT: track which elements are already in current

    def backtrack() -> None:    # CORRECT: no start parameter — scan full array each time
        if len(current) == len(nums):
            result.append(current[:])
            return
        for i in range(len(nums)):       # always scan from 0
            if used[i]:
                continue                 # skip elements already in the current permutation
            current.append(nums[i])
            used[i] = True
            backtrack()
            used[i] = False
            current.pop()

    backtrack()
    return result


# Alternative: swap-based permutation (no extra space for used array)
def permutations_swap(nums: list[int]) -> list[list[int]]:
    result = []
    nums = list(nums)   # make a copy since we'll mutate

    def backtrack(start: int) -> None:
        if start == len(nums):
            result.append(nums[:])
            return
        for i in range(start, len(nums)):
            nums[start], nums[i] = nums[i], nums[start]   # swap into position
            backtrack(start + 1)
            nums[start], nums[i] = nums[i], nums[start]   # swap back (undo)

    backtrack(0)
    return result
```

### Combinations vs Permutations — The Core Difference

```
Input: [1, 2, 3]

Combinations (length 2): [1,2], [1,3], [2,3]          — order doesn't matter
  → use start, range(start, n), recurse with i+1

Permutations (length 3): [1,2,3], [1,3,2], [2,1,3],   — order matters
                          [2,3,1], [3,1,2], [3,2,1]
  → use used[], range(0, n), skip used[i]

WRONG permutation using start: only generates [1,2,3] — treats it like combinations!
```

### Test Cases That Expose the Bug

```python
import pytest
from itertools import permutations as itertools_perms


def test_wrong_misses_permutations():
    result = permutations_wrong([1, 2, 3])
    # wrong version with start only generates 1 permutation: [1,2,3]
    assert len(result) == 1, f"WRONG version should produce 1 result, got {len(result)}"
    assert result == [[1, 2, 3]]


def test_correct_count():
    """n=3 → 3! = 6 permutations."""
    result = permutations_correct([1, 2, 3])
    assert len(result) == 6


def test_correct_all_permutations():
    result = permutations_correct([1, 2, 3])
    result_set = {tuple(p) for p in result}
    expected = {tuple(p) for p in itertools_perms([1, 2, 3])}
    assert result_set == expected


def test_swap_all_permutations():
    result = permutations_swap([1, 2, 3])
    result_set = {tuple(p) for p in result}
    expected = {tuple(p) for p in itertools_perms([1, 2, 3])}
    assert result_set == expected


def test_correct_single_element():
    assert permutations_correct([1]) == [[1]]


def test_correct_two_elements():
    result = permutations_correct([1, 2])
    assert sorted(result) == [[1, 2], [2, 1]]


def test_correct_no_duplicates_in_output():
    result = permutations_correct([1, 2, 3, 4])
    result_set = {tuple(p) for p in result}
    assert len(result_set) == len(result) == 24   # 4! = 24


def test_used_array_resets_correctly():
    """Verify used[] is properly reset so each path is independent."""
    result = permutations_correct([1, 2, 3])
    # Every element should appear in every position
    for pos in range(3):
        vals_at_pos = {p[pos] for p in result}
        assert vals_at_pos == {1, 2, 3}


if __name__ == "__main__":
    print("=== WRONG (uses start) ===")
    print(permutations_wrong([1, 2, 3]))   # [[1,2,3]] only

    print("\n=== CORRECT (uses used[]) ===")
    print(permutations_correct([1, 2, 3]))  # all 6 permutations

    print("\n=== CORRECT (swap) ===")
    print(permutations_swap([1, 2, 3]))     # all 6 permutations
```

### Key Takeaway

| Pattern | Use For | Control |
|---|---|---|
| `range(start, n)` + recurse with `i+1` | Combinations / subsets | Picks from remaining tail |
| `range(0, n)` + `used[]` array | Permutations | Picks any unused element |
| Swap approach | Permutations (in-place) | Swaps element into current position |

**The interview signal:** If someone uses a `start` parameter for permutations, they fundamentally confused the two patterns.

---

## Mistake 4: Combination Sum — Not Pruning with Sorted Candidates

### The Bug

In Combination Sum, candidates are reusable and we want all combinations that sum to `target`. Without pruning, if a candidate exceeds the remaining target, we still recurse into it (and all further candidates), wasting O(n * target) extra work. With sorted candidates, the moment `candidates[i] > remaining`, all subsequent candidates are also too large — we can `break` instead of `continue`.

### WRONG Code

```python
def combination_sum_wrong(candidates: list[int], target: int) -> list[list[int]]:
    result = []
    current = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(current[:])
            return
        if remaining < 0:
            return

        for i in range(start, len(candidates)):
            current.append(candidates[i])
            backtrack(i, remaining - candidates[i])   # i not i+1 (reuse allowed)
            current.pop()
        # WRONG: no pruning — if candidates[i] > remaining, we still call backtrack
        # and immediately return remaining < 0, but the call overhead accumulates

    backtrack(0, target)
    return result
```

*Note: The wrong version produces correct results but is slower. The deeper bug is explored in the variant below with unsorted input.*

### WRONG Code — Pruning in Wrong Direction

```python
def combination_sum_wrong_sort(candidates: list[int], target: int) -> list[list[int]]:
    # Doesn't sort — can't use break, must use continue
    result = []
    current = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(current[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                continue   # WRONG: should be `break` after sorting
                            # continue skips but doesn't stop exploring larger candidates
                            # (works but is O(n) per level instead of O(1) average exit)
            current.append(candidates[i])
            backtrack(i, remaining - candidates[i])
            current.pop()

    backtrack(0, target)
    return result
```

### CORRECT Code

```python
def combination_sum_correct(candidates: list[int], target: int) -> list[list[int]]:
    candidates.sort()       # STEP 1: sort to enable early termination
    result = []
    current = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(current[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break       # STEP 2: break (not continue) — all subsequent are also too large
            current.append(candidates[i])
            backtrack(i, remaining - candidates[i])   # i not i+1: reuse allowed
            current.pop()

    backtrack(0, target)
    return result
```

### Performance Impact

```
candidates = [7, 3, 2], target = 18  (unsorted, no pruning)

Without sorting + break:
  At remaining=1: tries 7>1 (skip), 3>1 (skip), 2>1 (skip) — 3 checks, then return
  At remaining=1 this happens O(2^n) times in worst case

With sorting [2,3,7] + break:
  At remaining=1: tries 2>1 → break immediately — 1 check, done
  Worst-case recursion depth reduced significantly
```

### Variants: Combination Sum II (Each Used at Most Once)

```python
def combination_sum_ii(candidates: list[int], target: int) -> list[list[int]]:
    """Each candidate used at most once. Input may have duplicates."""
    candidates.sort()
    result = []
    current = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(current[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break
            if i > start and candidates[i] == candidates[i - 1]:
                continue   # skip duplicates at same level (same as subsets with dup)
            current.append(candidates[i])
            backtrack(i + 1, remaining - candidates[i])   # i+1: no reuse
            current.pop()

    backtrack(0, target)
    return result
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_produces_correct_but_slow():
    """Wrong version is correct but doesn't prune — verify it produces right answer."""
    result = combination_sum_wrong([2, 3, 6, 7], 7)
    result_set = {tuple(sorted(r)) for r in result}
    assert (2, 2, 3) in result_set
    assert (7,) in result_set
    assert len(result) == 2


def test_correct_basic():
    result = combination_sum_correct([2, 3, 6, 7], 7)
    result_set = {tuple(r) for r in result}
    assert (2, 2, 3) in result_set
    assert (7,) in result_set
    assert len(result) == 2


def test_correct_reuse():
    """Elements can be reused."""
    result = combination_sum_correct([2], 6)
    assert result == [[2, 2, 2]]


def test_correct_no_solution():
    result = combination_sum_correct([3, 5], 4)
    assert result == []


def test_correct_single_candidate():
    result = combination_sum_correct([1], 3)
    assert result == [[1, 1, 1]]


def test_correct_target_is_candidate():
    result = combination_sum_correct([2, 3, 5], 5)
    result_set = {tuple(r) for r in result}
    assert (5,) in result_set
    assert (2, 3) in result_set


def test_combination_sum_ii_no_duplicates_in_result():
    result = combination_sum_ii([10, 1, 2, 7, 6, 1, 5], 8)
    result_tuples = [tuple(r) for r in result]
    assert len(result_tuples) == len(set(result_tuples))   # no duplicates
    result_set = {tuple(r) for r in result}
    assert (1, 7) in result_set
    assert (1, 2, 5) in result_set
    assert (2, 6) in result_set
    assert (1, 1, 6) in result_set


def test_correct_break_vs_continue_count():
    """With break after sorting, results should be identical to without."""
    candidates = [2, 3, 5]
    target = 8
    r1 = combination_sum_wrong(candidates[:], target)
    r2 = combination_sum_correct(candidates[:], target)
    assert {tuple(r) for r in r1} == {tuple(r) for r in r2}


if __name__ == "__main__":
    print("combination_sum([2,3,6,7], 7):", combination_sum_correct([2, 3, 6, 7], 7))
    print("combination_sum([2], 6):",       combination_sum_correct([2], 6))
    print("combination_sum_ii([10,1,2,7,6,1,5], 8):", combination_sum_ii([10, 1, 2, 7, 6, 1, 5], 8))
```

### Key Takeaway

1. Sort candidates before backtracking.
2. Use `break` (not `continue`) when `candidates[i] > remaining` — after sorting, all subsequent candidates are also too large.
3. For no-reuse variant (Combination Sum II): use `i + 1` in the recursion and add the `i > start and nums[i] == nums[i-1]: continue` guard.

---

## Mistake 5: N-Queens — O(n) Conflict Check Instead of O(1) with Sets

### The Bug

N-Queens requires checking whether a queen placement conflicts with existing queens. The naive approach scans the entire board (rows and columns already placed) for conflicts — O(n) per placement. A queen attacks along its column, its left diagonal (row - col = constant), and its right diagonal (row + col = constant). Maintaining three sets allows O(1) conflict detection.

### WRONG Code

```python
def solve_n_queens_wrong(n: int) -> list[list[str]]:
    result = []
    board = [["." for _ in range(n)] for _ in range(n)]

    def is_valid_wrong(row: int, col: int) -> bool:
        """O(n) check — scans previously placed queens."""
        # Check column
        for r in range(row):
            if board[r][col] == "Q":
                return False
        # Check top-left diagonal
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0:
            if board[r][c] == "Q":
                return False
            r -= 1
            c -= 1
        # Check top-right diagonal
        r, c = row - 1, col + 1
        while r >= 0 and c < n:
            if board[r][c] == "Q":
                return False
            r -= 1
            c += 1
        return True   # O(n) total work per call

    def backtrack_wrong(row: int) -> None:
        if row == n:
            result.append(["".join(r) for r in board])
            return
        for col in range(n):
            if is_valid_wrong(row, col):
                board[row][col] = "Q"
                backtrack_wrong(row + 1)
                board[row][col] = "."

    backtrack_wrong(0)
    return result
```

### CORRECT Code

```python
def solve_n_queens_correct(n: int) -> list[list[str]]:
    result = []
    cols: set[int] = set()
    diag1: set[int] = set()   # row - col = constant for each '/' diagonal
    diag2: set[int] = set()   # row + col = constant for each '\' diagonal
    queens: list[int] = []    # queens[row] = column of queen in that row

    def backtrack(row: int) -> None:
        if row == n:
            board = []
            for q_col in queens:
                board.append("." * q_col + "Q" + "." * (n - q_col - 1))
            result.append(board)
            return

        for col in range(n):
            # O(1) conflict check using sets
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue

            # Place queen
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            queens.append(col)

            backtrack(row + 1)

            # Remove queen (backtrack)
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)
            queens.pop()

    backtrack(0)
    return result


def count_n_queens(n: int) -> int:
    """Just count solutions without building the board strings."""
    count = 0
    cols: set[int] = set()
    diag1: set[int] = set()
    diag2: set[int] = set()

    def backtrack(row: int) -> None:
        nonlocal count
        if row == n:
            count += 1
            return
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            backtrack(row + 1)
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)

    backtrack(0)
    return count
```

### Diagonal Key Derivation

```
For an n×n board, a queen at (row, col) attacks:
  Column:      col is constant           → store col in cols set
  '\' diagonal: row - col is constant   → store row-col in diag1 set
                (same '\' diagonal has same row-col value)
  '/' diagonal: row + col is constant   → store row+col in diag2 set
                (same '/' diagonal has same row+col value)

Examples (n=4):
  Queen at (0, 1):  col=1, diag1=-1, diag2=1
  Queen at (1, 3):  col=3, diag1=-2, diag2=4
  Does (2, 2) conflict with (0,1)?
    col: 2 not in {1,3} ✓
    diag1: 2-2=0 not in {-1,-2} ✓
    diag2: 2+2=4 in {1,4} ✗ → conflicts on '/' diagonal with (1,3)
```

### Performance Comparison

```python
import time


def benchmark_n_queens(n: int) -> None:
    start = time.perf_counter()
    wrong_result = solve_n_queens_wrong(n)
    wrong_time = time.perf_counter() - start

    start = time.perf_counter()
    correct_result = solve_n_queens_correct(n)
    correct_time = time.perf_counter() - start

    print(f"n={n}: wrong={wrong_time:.4f}s ({len(wrong_result)} solutions), "
          f"correct={correct_time:.4f}s ({len(correct_result)} solutions), "
          f"speedup={wrong_time/correct_time:.1f}x")
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_and_correct_produce_same_results():
    for n in range(1, 9):
        wrong = {tuple(tuple(row) for row in board) for board in solve_n_queens_wrong(n)}
        correct = {tuple(tuple(row) for row in board) for board in solve_n_queens_correct(n)}
        assert wrong == correct, f"n={n}: results differ"


def test_known_solution_counts():
    """Known OEIS sequence A000170."""
    expected = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92}
    for n, expected_count in expected.items():
        assert count_n_queens(n) == expected_count, f"n={n}: expected {expected_count}"


def test_n1():
    result = solve_n_queens_correct(1)
    assert result == [["Q"]]


def test_n4():
    result = solve_n_queens_correct(4)
    assert len(result) == 2
    for board in result:
        assert len(board) == 4
        for row in board:
            assert row.count("Q") == 1   # exactly one queen per row


def test_n4_no_column_conflicts():
    result = solve_n_queens_correct(4)
    for board in result:
        queen_cols = [row.index("Q") for row in board]
        assert len(set(queen_cols)) == 4   # all columns distinct


def test_n4_no_diagonal_conflicts():
    result = solve_n_queens_correct(4)
    for board in result:
        queens = [(r, row.index("Q")) for r, row in enumerate(board)]
        for i in range(len(queens)):
            for j in range(i + 1, len(queens)):
                r1, c1 = queens[i]
                r2, c2 = queens[j]
                assert abs(r1 - r2) != abs(c1 - c2), \
                    f"Diagonal conflict between {queens[i]} and {queens[j]}"


def test_o1_vs_on_same_output():
    for n in [4, 5, 6]:
        r1 = solve_n_queens_wrong(n)
        r2 = solve_n_queens_correct(n)
        assert len(r1) == len(r2)


if __name__ == "__main__":
    for n in range(1, 9):
        count = count_n_queens(n)
        print(f"N={n}: {count} solutions")

    print("\nN=4 solutions:")
    for board in solve_n_queens_correct(4):
        for row in board:
            print(" ", row)
        print()

    benchmark_n_queens(8)
    benchmark_n_queens(10)
```

### Key Takeaway

| Approach | Conflict Check | Time per Placement | Total Complexity |
|---|---|---|---|
| Board scan | O(n) | O(n) | O(n! * n) |
| Three sets | O(1) | O(1) | O(n!) |

- `cols` set: blocks same column.
- `diag1` set: `row - col` value blocks the `\` diagonal.
- `diag2` set: `row + col` value blocks the `/` diagonal.
- Always add to all three sets when placing, remove from all three when backtracking.

---

## Summary Table

| # | Mistake | Root Cause | Fix |
|---|---|---|---|
| 1 | `result.append(current)` | Appends reference, not a copy — all entries mutate together | `result.append(current[:])` |
| 2 | No duplicate skipping | Same value at same recursion level generates identical branches | Sort + `if i > start and nums[i] == nums[i-1]: continue` |
| 3 | `range(start, n)` for permutations | Generates combinations (ordered subsets) not permutations | `used[]` array + `range(0, n)` |
| 4 | No pruning in combination sum | Recurses past impossible candidates | Sort + `if candidates[i] > remaining: break` |
| 5 | O(n) board scan in N-Queens | Rescanning placed queens each time | `cols`, `diag1` (`row-col`), `diag2` (`row+col`) sets for O(1) check |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Real World Usage](./real_world_usage.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
