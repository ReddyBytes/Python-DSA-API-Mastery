# Sorting — Common Mistakes & Error Prevention

A focused guide on the bugs that appear repeatedly in sorting problems during interviews and production code. Each mistake includes a broken implementation, an explanation of why it fails, and a corrected version with test cases that expose the bug.

---

## Mistake 1: Sorting a Copy vs Sorting In-Place

### The Confusion

`sorted()` returns a **new list** and leaves the original unchanged.
`.sort()` modifies the list **in-place** and returns `None`.

Mixing these up produces subtle bugs — especially when the caller holds a reference to the original list and expects one behaviour while your function delivers the other.

### Wrong Code — In-Place Required, But You Return a Copy

```python
# WRONG: Problem asks to sort the list in-place.
# The caller's reference to `nums` still points to the original unsorted list.
def sort_in_place_wrong(nums):
    nums = sorted(nums)   # creates a NEW list; rebinds the local name only
    # The original list the caller passed is untouched.

# --- Test that exposes the bug ---
data = [3, 1, 2]
sort_in_place_wrong(data)
print(data)   # [3, 1, 2]  <-- BUG: still unsorted
```

### Wrong Code — New Sorted List Required, But You Mutate the Original

```python
# WRONG: Caller needs the original list untouched AND a sorted version.
def get_sorted_wrong(nums):
    nums.sort()           # mutates the caller's list as a side-effect
    return nums

# --- Test that exposes the bug ---
original = [3, 1, 2]
result = get_sorted_wrong(original)
print(result)    # [1, 2, 3]  — looks right
print(original)  # [1, 2, 3]  <-- BUG: original was destroyed
```

### Correct Code

```python
def sort_in_place_correct(nums):
    nums.sort()           # modifies the list the caller holds a reference to

def get_sorted_correct(nums):
    return sorted(nums)   # original untouched; new sorted list returned

# --- Tests ---
data = [3, 1, 2]
sort_in_place_correct(data)
print(data)   # [1, 2, 3]  -- correct in-place sort

original = [3, 1, 2]
result = get_sorted_correct(original)
print(result)    # [1, 2, 3]  -- sorted copy
print(original)  # [3, 1, 2]  -- original preserved
```

### Quick Reference

| Function     | Modifies original | Returns          |
|--------------|-------------------|------------------|
| `list.sort()`| YES               | `None`           |
| `sorted()`   | NO                | new sorted list  |

---

## Mistake 2: Custom Comparator — Wrong Return Values with `cmp_to_key`

### The Confusion

Python 3 removed the `cmp=` argument. You must use `key=` or `functools.cmp_to_key`.
A comparator passed to `cmp_to_key` must return:

- **negative** if `a` should come **before** `b`
- **0** if they are equal
- **positive** if `a` should come **after** `b`

Returning `True`/`False` (i.e., `1`/`0`) means "equal" and "before" only — **"after" is never returned** — so the sort order is wrong.

### Wrong Code

```python
from functools import cmp_to_key

# WRONG: returns True/False (1/0) instead of -1/0/1
# True == 1 means "a comes after b"
# False == 0 means "a == b" (never says a comes first)
def bad_comparator(a, b):
    return a > b   # returns True or False, never -1

nums = [3, 1, 4, 1, 5, 9, 2, 6]
result = sorted(nums, key=cmp_to_key(bad_comparator))
print(result)   # Unpredictable / wrong order

# --- Test that exposes the bug ---
data = [5, 3, 1]
result = sorted(data, key=cmp_to_key(bad_comparator))
print(result)   # [5, 3, 1] — may look right by accident
# but try:
data2 = [1, 5, 3]
result2 = sorted(data2, key=cmp_to_key(bad_comparator))
print(result2)  # [1, 5, 3] — BUG: not sorted descending as intended
```

### Correct Code

```python
from functools import cmp_to_key

# CORRECT: returns -1, 0, or 1
def good_comparator_desc(a, b):
    if a > b:
        return -1   # a comes before b (descending)
    elif a < b:
        return 1    # a comes after b
    else:
        return 0

nums = [3, 1, 4, 1, 5, 9, 2, 6]
result = sorted(nums, key=cmp_to_key(good_comparator_desc))
print(result)   # [9, 6, 5, 4, 3, 2, 1, 1]  -- correct descending order

# Simpler alternative: use key= directly when possible
result_simple = sorted(nums, key=lambda x: -x)
print(result_simple)   # [9, 6, 5, 4, 3, 2, 1, 1]

# --- Tests ---
assert sorted([3, 1, 2], key=cmp_to_key(good_comparator_desc)) == [3, 2, 1]
assert sorted([1, 1, 1], key=cmp_to_key(good_comparator_desc)) == [1, 1, 1]
print("All comparator tests passed.")
```

---

## Mistake 3: Assuming Stability (Python vs Java)

### The Confusion

**Python's Timsort is stable** — equal elements retain their original relative order.
**Java's `Arrays.sort` for primitive types uses dual-pivot quicksort — which is NOT stable.**

This becomes a real bug when you sort by a secondary field and rely on a previous sort to have preserved the primary field's order.

### Demonstrating Python Stability

```python
# Python sort IS stable — safe to do multi-pass "sort by secondary, then by primary"
students = [
    ("Alice", 90),
    ("Bob",   85),
    ("Carol", 90),
    ("Dave",  85),
]

# Sort by grade descending first, then by name — using two stable passes
students.sort(key=lambda s: s[0])          # pass 1: sort by name (alphabetical)
students.sort(key=lambda s: s[1], reverse=True)  # pass 2: sort by grade descending

print(students)
# [('Alice', 90), ('Carol', 90), ('Bob', 85), ('Dave', 85)]
# Alice and Carol both have 90; alphabetical order is preserved within the tie — CORRECT

# --- Test ---
assert students[0][0] == "Alice"   # Alice before Carol (same grade, alphabetical)
assert students[2][0] == "Bob"     # Bob before Dave (same grade, alphabetical)
print("Stability test passed.")
```

### The Gotcha — Java Pseudocode Translated Naively to Python

```python
# WRONG assumption: "sort is unstable, so I must sort once with a compound key"
# This is necessary in Java for primitives, but in Python a second .sort() pass
# on an already-partially-sorted list works BECAUSE Python's sort is stable.

# Problematic if you port Java logic and add unnecessary compound keys that
# actually CHANGE the intended order:
records = [(1, "b"), (1, "a"), (2, "c")]

# Wrong: using a compound key that sorts ties by second element when you
# actually want to preserve insertion order for ties
wrong = sorted(records, key=lambda x: (x[0], x[1]))
print(wrong)   # [(1, 'a'), (1, 'b'), (2, 'c')]  -- changed tie order!

# Correct: rely on Python's stability — sort only by the field you care about
correct = sorted(records, key=lambda x: x[0])
print(correct)  # [(1, 'b'), (1, 'a'), (2, 'c')]  -- insertion order preserved for ties
```

---

## Mistake 4: Sorting Strings Numerically

### The Confusion

String comparison is **lexicographic**. `"10" < "2"` because `"1" < "2"` at the first character.
When your data is numeric strings, you must convert to `int` (or `float`) for correct ordering.

### Wrong Code

```python
# WRONG: lexicographic order — "10" < "2" because "1" < "2"
numbers = ["10", "1", "2", "20", "3"]
wrong = sorted(numbers)
print(wrong)   # ['1', '10', '2', '20', '3']  <-- BUG

# --- Test that exposes the bug ---
assert wrong == ["1", "10", "2", "20", "3"]   # passes, confirming the wrong order
```

### Correct Code

```python
# CORRECT: use key=int to sort numerically
numbers = ["10", "1", "2", "20", "3"]
correct = sorted(numbers, key=int)
print(correct)   # ['1', '2', '3', '10', '20']  -- correct numeric order

# --- Tests ---
assert correct == ["1", "2", "3", "10", "20"]

# Edge case: mixed leading zeros
padded = ["02", "010", "1", "9"]
assert sorted(padded, key=int) == ["1", "02", "9", "010"]
# Note: key=int strips leading zeros for comparison but original strings are returned

print("Numeric string sort tests passed.")
```

---

## Mistake 5: "Largest Number" — Sorting Integers Directly

### The Confusion

**LeetCode 179 — Largest Number**: Given a list of non-negative integers, arrange them to form the largest number.

Naive approach: sort in descending order. This fails for `[3, 30]`:
- Descending by value: `[3, 30]` → `"330"` — correct by luck here
- But `[30, 3]` descending: `[30, 3]` → `"303"` — wrong! `"330"` is larger

The fix: compare `str(a) + str(b)` vs `str(b) + str(a)` as strings.

### Wrong Code

```python
# WRONG: sort by integer value descending
def largest_number_wrong(nums):
    nums.sort(reverse=True)
    return "".join(map(str, nums))

# --- Tests that expose the bug ---
print(largest_number_wrong([3, 30, 34, 5, 9]))   # "9534303"  -- wrong
# Correct answer is                                 "9534330"

print(largest_number_wrong([10, 2]))   # "210"  -- correct by coincidence
print(largest_number_wrong([3, 30]))   # "330"  -- correct by coincidence
print(largest_number_wrong([30, 3]))   # "303"  -- BUG: should be "330"
```

### Correct Code

```python
from functools import cmp_to_key

def largest_number_correct(nums):
    def comparator(a, b):
        # Compare which concatenation is larger
        if str(a) + str(b) > str(b) + str(a):
            return -1   # a should come before b
        elif str(a) + str(b) < str(b) + str(a):
            return 1    # b should come before a
        else:
            return 0

    nums.sort(key=cmp_to_key(comparator))
    result = "".join(map(str, nums))
    # Edge case: all zeros
    return "0" if result[0] == "0" else result

# --- Tests ---
assert largest_number_correct([3, 30, 34, 5, 9]) == "9534330"
assert largest_number_correct([10, 2])            == "210"
assert largest_number_correct([3, 30])            == "330"
assert largest_number_correct([30, 3])            == "330"   # was "303" before fix
assert largest_number_correct([0, 0])             == "0"     # all-zeros edge case
assert largest_number_correct([1])                == "1"
print("Largest number tests passed.")
```

### Why String Comparison Works

```
Comparing 3 and 30:
  "3" + "30" = "330"
  "30" + "3" = "303"
  "330" > "303"  →  3 should come before 30  ✓

Comparing 9 and 34:
  "9" + "34" = "934"
  "34" + "9" = "349"
  "934" > "349"  →  9 should come before 34  ✓
```

---

## Mistake 6: Modifying a List While Iterating Over It

### The Confusion

Sorting and removing duplicates in the wrong order, or iterating and removing elements from the same list, causes skipped elements or index errors.

### Wrong Code

```python
# WRONG: removing elements while iterating by index — skips elements
def remove_duplicates_wrong(nums):
    nums.sort()
    for i in range(len(nums) - 1):
        if nums[i] == nums[i + 1]:
            nums.pop(i)   # shifts everything left — next iteration skips an element
    return nums

# --- Test that exposes the bug ---
data = [3, 1, 2, 1, 3, 2]
print(remove_duplicates_wrong(data))
# Expected: [1, 2, 3]
# Actual:   [1, 2, 3, 3]  or IndexError depending on data — BUG

# WRONG version 2: building result while checking against a simultaneously-modified list
def dedup_wrong_v2(nums):
    nums.sort()
    for num in nums:          # iterating over nums
        if nums.count(num) > 1:
            nums.remove(num)  # modifying nums during iteration — unpredictable skips
    return nums

data2 = [1, 1, 2, 2, 3]
print(dedup_wrong_v2(data2))   # [1, 2, 3] — may APPEAR correct on some inputs
data3 = [1, 1, 1, 2]
print(dedup_wrong_v2(data3))   # [1, 2]  -- BUG: one duplicate 1 survives
```

### Correct Code

```python
# CORRECT approach 1: build a new list (never mutate while iterating)
def remove_duplicates_correct(nums):
    nums.sort()
    result = []
    for num in nums:
        if not result or result[-1] != num:
            result.append(num)
    return result

# CORRECT approach 2: use dict.fromkeys or set (for unordered uniqueness)
def remove_duplicates_set(nums):
    return sorted(set(nums))

# CORRECT approach 3: in-place two-pointer (LeetCode 26 style)
def remove_duplicates_inplace(nums):
    if not nums:
        return 0
    nums.sort()
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[read - 1]:
            nums[write] = nums[read]
            write += 1
    return write  # first `write` elements are unique

# --- Tests ---
assert remove_duplicates_correct([3, 1, 2, 1, 3, 2]) == [1, 2, 3]
assert remove_duplicates_correct([1, 1, 1])           == [1]
assert remove_duplicates_correct([])                  == []
assert remove_duplicates_correct([1, 2, 3])           == [1, 2, 3]

assert remove_duplicates_set([3, 1, 2, 1, 3, 2])     == [1, 2, 3]

nums = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
k = remove_duplicates_inplace(nums)
assert k == 5
assert nums[:k] == [0, 1, 2, 3, 4]

print("Deduplication tests passed.")
```

---

## Summary Table

| # | Mistake                                        | Root Cause                              | Fix                                            |
|---|------------------------------------------------|-----------------------------------------|------------------------------------------------|
| 1 | `sorted()` vs `.sort()` confusion              | Forgetting return value semantics       | `sorted()` for copy, `.sort()` for in-place    |
| 2 | Comparator returns `True`/`False`              | Python 3 removed `cmp=`; needs -1/0/1  | Return `-1`, `0`, or `1` from comparator       |
| 3 | Assuming instability                           | Porting Java habits to Python           | Python sort is stable; Java primitives are not |
| 4 | Sorting numeric strings lexicographically      | String `<` is character-by-character    | `key=int` to convert before comparison         |
| 5 | Largest number: sorting by integer value       | Magnitude does not reflect concatenation| Custom comparator on `str(a)+str(b)`           |
| 6 | Modifying a list while iterating over it       | Index shifting corrupts traversal       | Collect to new list; never mutate mid-iteration|
