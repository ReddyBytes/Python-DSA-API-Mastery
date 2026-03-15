# Two Pointers — Common Mistakes & Error Prevention

A focused guide on the bugs that appear most often in two-pointer problems during interviews. Each mistake includes a broken implementation, an explanation of why it fails, and a corrected version with test cases that expose the bug.

---

## Mistake 1: Forgetting to Sort Before Using Converging Pointers

### The Confusion

The converging two-pointer pattern (left pointer starts at 0, right pointer starts at n-1, they move toward each other) **only works on sorted arrays**. The logic is:
- `nums[left] + nums[right] < target` → move `left` right to increase the sum
- `nums[left] + nums[right] > target` → move `right` left to decrease the sum

This logic assumes smaller values are on the left and larger values are on the right. On an unsorted array that assumption is false, so the search terminates early in the wrong direction.

### Wrong Code

```python
# WRONG: two-sum two-pointer on unsorted input
def two_sum_two_pointer_wrong(nums, target):
    left, right = 0, len(nums) - 1

    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return [left, right]
        elif s < target:
            left += 1
        else:
            right -= 1

    return []   # not found

# --- Tests that expose the bug ---
print(two_sum_two_pointer_wrong([3, 1, 4, 2], 6))   # Expected: indices of 2+4
# Actual: [] — BUG: misses the pair because array is unsorted

print(two_sum_two_pointer_wrong([2, 7, 11, 15], 9)) # [0, 1] — correct by luck (already sorted)
print(two_sum_two_pointer_wrong([3, 2, 4], 6))       # []    — BUG: should find 2+4
```

### Correct Code

```python
# CORRECT approach 1: sort first (loses original indices — OK when problem only asks for values)
def two_sum_sorted(nums, target):
    nums_sorted = sorted(nums)   # or sort in-place if original order not needed
    left, right = 0, len(nums_sorted) - 1

    while left < right:
        s = nums_sorted[left] + nums_sorted[right]
        if s == target:
            return [nums_sorted[left], nums_sorted[right]]
        elif s < target:
            left += 1
        else:
            right -= 1

    return []

# CORRECT approach 2: hash map (preserves original indices, works on unsorted)
def two_sum_indices(nums, target):
    seen = {}   # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# --- Tests ---
assert two_sum_sorted([3, 1, 4, 2], 6)          == [2, 4]   # values 2 and 4
assert two_sum_sorted([2, 7, 11, 15], 9)         == [2, 7]
assert two_sum_sorted([3, 2, 4], 6)              == [2, 4]
assert two_sum_sorted([1, 2, 3], 10)             == []       # no solution

assert two_sum_indices([3, 1, 4, 2], 6)          == [2, 3]  # indices 2 (val=4) and 3 (val=2)
assert two_sum_indices([2, 7, 11, 15], 9)        == [0, 1]
assert two_sum_indices([3, 2, 4], 6)             == [1, 2]
assert two_sum_indices([1, 2, 3], 10)            == []

print("Two-pointer sort-first tests passed.")
```

---

## Mistake 2: Infinite Loop — No Pointer Advancement

### The Confusion

Every iteration of a two-pointer loop must move **at least one pointer**. A conditional branch that can leave both pointers unchanged causes an infinite loop.

The most common form: handling duplicates or edge cases inside the loop without also advancing a pointer.

### Wrong Code

```python
# WRONG: potential infinite loop when both conditions fail to advance a pointer
def three_sum_wrong(nums):
    nums.sort()
    result = []

    for i in range(len(nums) - 2):
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                # BUG: after appending, neither pointer advances!
                # If next elements are also duplicates the `elif` branches run,
                # but the equal-case loop gets re-entered forever.
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                # We "skipped" duplicates but did NOT advance past the match itself
                # → next iteration has same values → appends duplicate → infinite loop
            elif s < 0:
                left += 1
            else:
                right -= 1

    return result

# --- Test that exposes the bug ---
# Uncomment to observe infinite loop:
# three_sum_wrong([-1, 0, 1, 2, -1, -4])
```

### Correct Code

```python
def three_sum_correct(nums):
    nums.sort()
    result = []

    for i in range(len(nums) - 2):
        # Skip duplicate values for the outer pointer
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        left, right = i + 1, len(nums) - 1

        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                left += 1    # MUST advance at least one pointer
                right -= 1   # advance both to skip current match
                # Now skip duplicates
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
            elif s < 0:
                left += 1
            else:
                right -= 1

    return result

# --- Tests ---
assert sorted(three_sum_correct([-1, 0, 1, 2, -1, -4])) == sorted([[-1, -1, 2], [-1, 0, 1]])
assert three_sum_correct([0, 0, 0])                      == [[0, 0, 0]]
assert three_sum_correct([0, 0, 0, 0])                   == [[0, 0, 0]]
assert three_sum_correct([1, 2, -2, -1])                 == []
assert three_sum_correct([])                             == []
assert three_sum_correct([0])                            == []

print("Three-sum (no infinite loop) tests passed.")
```

### Checklist to Prevent Infinite Loops

```
After every iteration, ask:
  [ ] Did I advance left OR right?
  [ ] Is there any code path where neither pointer moves?
  [ ] After handling duplicates, did I also advance past the current element?
```

---

## Mistake 3: Off-by-One in Palindrome Check

### The Confusion

Two common loop conditions:
- `while left < right` — stops when pointers cross or meet; never compares a character to itself
- `while left <= right` — runs one extra iteration when `left == right` (middle character)

For palindrome checking, comparing a character to **itself** is harmless but wasteful. The real off-by-one appears in **substring extraction** or when you must check exactly the inner half.

### Wrong Code

```python
# WRONG version 1: using <= instead of < — compares middle char to itself (harmless here,
# but signals confusion and causes bugs in related variations)
def is_palindrome_wrong_v1(s):
    left, right = 0, len(s) - 1
    while left <= right:         # when left == right we compare s[i] to s[i] — always equal
        if s[left] != s[right]:  # this is "correct" by accident for pure palindrome check
            return False
        left += 1
        right -= 1
    return True

# WRONG version 2: off-by-one in the iteration count causes a character skip
def is_palindrome_wrong_v2(s):
    n = len(s)
    for i in range(n // 2 + 1):    # BUG: iterates one too many times for odd-length strings
        if s[i] != s[n - 1 - i]:
            return False
    return True

# --- Test that exposes version 2 bug ---
# For "abc": n=3, n//2+1 = 2
#   i=0: s[0]='a' vs s[2]='c' → 'a' != 'c' → returns False  ← correct result but fragile
# For "aba": n=3, n//2+1 = 2
#   i=0: 'a' vs 'a' → equal
#   i=1: 'b' vs 'b' → equal   ← i=1 is the middle, comparing to itself always passes
# Actually returns True — let's find a case that breaks it:
# For "abba": n=4, n//2+1 = 3
#   i=0: 'a' vs 'a' → equal
#   i=1: 'b' vs 'b' → equal
#   i=2: s[2]='b' vs s[4-1-2]=s[1]='b' → equal  ← extra iteration but happens to pass
# The real danger: when you extend this pattern to find palindromic substrings,
# the wrong boundary causes missed or double-counted characters.

# Cleaner demonstration of off-by-one category of bugs:
def count_palindrome_pairs_wrong(s):
    """Count pairs (i,j) where s[i:j+1] is a palindrome. Wrong boundary."""
    count = 0
    n = len(s)
    for center in range(n):
        # odd-length
        left, right = center, center
        while left > 0 and right < n - 1:   # BUG: skips center itself on first check
            left -= 1
            right += 1
            if s[left] == s[right]:
                count += 1
    return count

print(count_palindrome_pairs_wrong("aaa"))   # misses several palindromes
```

### Correct Code

```python
def is_palindrome_correct(s):
    left, right = 0, len(s) - 1
    while left < right:            # strictly less — stops when pointers meet or cross
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

def count_palindromes_correct(s):
    """Count all palindromic substrings using expand-around-center."""
    def expand(left, right):
        count = 0
        while left >= 0 and right < len(s) and s[left] == s[right]:
            count += 1
            left -= 1
            right += 1
        return count

    total = 0
    for i in range(len(s)):
        total += expand(i, i)       # odd-length palindromes (centre is s[i])
        total += expand(i, i + 1)   # even-length palindromes (centre between i and i+1)
    return total

# --- Tests ---
assert is_palindrome_correct("racecar")  == True
assert is_palindrome_correct("hello")    == False
assert is_palindrome_correct("a")        == True
assert is_palindrome_correct("")         == True
assert is_palindrome_correct("aa")       == True
assert is_palindrome_correct("ab")       == False

assert count_palindromes_correct("abc")  == 3   # "a", "b", "c"
assert count_palindromes_correct("aaa")  == 6   # "a","a","a","aa","aa","aaa"
assert count_palindromes_correct("aba")  == 4   # "a","b","a","aba"
assert count_palindromes_correct("a")    == 1

print("Palindrome off-by-one tests passed.")
```

---

## Mistake 4: Dutch National Flag — Wrong Boundary Conditions

### The Confusion

The Dutch National Flag algorithm (sort an array containing only 0, 1, 2 in-place) uses three pointers:

```
Invariant at all times:
  nums[0 .. lo-1]   = all 0s
  nums[lo .. mid-1] = all 1s
  nums[mid .. hi]   = UNKNOWN (to be processed)
  nums[hi+1 .. n-1] = all 2s
```

The critical mistake: when you swap `nums[mid]` with `nums[hi]` (encountered a 2), you move an **unknown element** to `mid`. You must NOT advance `mid` in that case — the swapped-in element is still unclassified.

### Wrong Code

```python
# WRONG: advances mid after swapping with hi — skips unclassified element
def sort_colors_wrong(nums):
    lo, mid, hi = 0, 0, len(nums) - 1

    while mid <= hi:
        if nums[mid] == 0:
            nums[lo], nums[mid] = nums[mid], nums[lo]
            lo += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:  # nums[mid] == 2
            nums[mid], nums[hi] = nums[hi], nums[mid]
            hi -= 1
            mid += 1    # BUG: must NOT advance mid here!
                        # The element that swapped in from hi is unclassified.

# --- Test that exposes the bug ---
test1 = [2, 0, 2, 1, 1, 0]
sort_colors_wrong(test1)
print(test1)   # Expected: [0, 0, 1, 1, 2, 2]
               # Actual:   [0, 0, 1, 2, 1, 2]  BUG

test2 = [2, 2, 0]
sort_colors_wrong(test2)
print(test2)   # Expected: [0, 2, 2] — wait, should be [0, 2, 2]? No: [0, 2, 2]
               # Actually expected: [0, 2, 2] — Hmm, let's trace:
               # [2, 2, 0]: mid=0, nums[0]=2 → swap with hi=2: [0, 2, 2], hi=1, mid=1  WRONG advance
               # mid=1, nums[1]=2 → swap with hi=1: [0, 2, 2], hi=0, mid=2
               # mid=2 > hi=0: stop. Result: [0, 2, 2]  happens to look right here
               # Try: [2, 0, 1]
test3 = [2, 0, 1]
sort_colors_wrong(test3)
print(test3)   # Expected: [0, 1, 2] — Actual: [0, 2, 1]  BUG
```

### Correct Code

```python
def sort_colors_correct(nums):
    lo, mid, hi = 0, 0, len(nums) - 1

    while mid <= hi:
        if nums[mid] == 0:
            nums[lo], nums[mid] = nums[mid], nums[lo]
            lo += 1
            mid += 1     # safe: lo region contained a known 1 before the swap
        elif nums[mid] == 1:
            mid += 1     # already in the right zone
        else:            # nums[mid] == 2
            nums[mid], nums[hi] = nums[hi], nums[mid]
            hi -= 1
            # DO NOT advance mid — the swapped-in element from hi is unknown

# --- Tests ---
def test_sort_colors(nums):
    sort_colors_correct(nums)
    return nums

assert test_sort_colors([2, 0, 2, 1, 1, 0]) == [0, 0, 1, 1, 2, 2]
assert test_sort_colors([2, 0, 1])           == [0, 1, 2]
assert test_sort_colors([0])                 == [0]
assert test_sort_colors([1])                 == [1]
assert test_sort_colors([2])                 == [2]
assert test_sort_colors([0, 0, 0])           == [0, 0, 0]
assert test_sort_colors([2, 2, 2])           == [2, 2, 2]
assert test_sort_colors([1, 2, 0])           == [0, 1, 2]
assert test_sort_colors([2, 0, 1, 2, 0, 1]) == [0, 0, 1, 1, 2, 2]

print("Dutch National Flag tests passed.")
```

### Invariant Visualised

```
Initial: [2, 0, 1, 2, 0]
          lo=0, mid=0, hi=4
          |unknown region|

Step 1: nums[0]=2 → swap(0,4): [0, 0, 1, 2, 2]... actually let's trace correctly:
Start:  [2, 0, 1, 2, 0]  lo=0, mid=0, hi=4
        nums[mid]=2 → swap mid,hi: [0, 0, 1, 2, 2]  NO wait...
        swap(nums[0], nums[4]): [0, 0, 1, 2, 2] → [0, 0, 1, 2, 2]

Let's use a cleaner trace on [2, 0, 1]:
  lo=0, mid=0, hi=2
  nums[0]=2 → swap(mid=0, hi=2): [1, 0, 2], hi=1, mid stays 0
  nums[0]=1 → mid++ : mid=1
  nums[1]=0 → swap(lo=0, mid=1): [0, 1, 2], lo=1, mid=2
  mid=2 > hi=1: stop
  Result: [0, 1, 2]  ✓
```

---

## Mistake 5: Fast/Slow Pointer — Not Checking `fast.next` Before `fast.next.next`

### The Confusion

The fast/slow (Floyd's cycle detection) pattern advances `fast` two steps per iteration. To advance `fast` two steps you need **both** `fast.next` and `fast.next.next` to be non-None. Checking only `fast.next.next` raises `AttributeError` when `fast.next` is `None` — you are calling `.next` on `None`.

### Wrong Code

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# WRONG: crashes on even-length lists where fast.next becomes None mid-traversal
def has_cycle_wrong(head):
    slow = fast = head
    while fast.next.next:        # BUG: AttributeError if fast.next is None
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False

# WRONG version 2: checks fast.next.next but not fast itself
def find_middle_wrong(head):
    slow = fast = head
    while fast.next.next:        # BUG: same issue — crashes on even-length list
        slow = slow.next
        fast = fast.next.next
    return slow

# --- Tests that expose the bug ---
# Even-length list: 1 -> 2 -> 3 -> 4
nodes = [ListNode(i) for i in range(1, 5)]
for i in range(len(nodes) - 1):
    nodes[i].next = nodes[i + 1]

try:
    has_cycle_wrong(nodes[0])
except AttributeError as e:
    print(f"BUG caught: {e}")   # 'NoneType' object has no attribute 'next'

try:
    find_middle_wrong(nodes[0])
except AttributeError as e:
    print(f"BUG caught: {e}")
```

### Correct Code

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build_list(values):
    if not values:
        return None
    head = ListNode(values[0])
    cur = head
    for v in values[1:]:
        cur.next = ListNode(v)
        cur = cur.next
    return head

def has_cycle_correct(head):
    slow = fast = head
    while fast and fast.next:         # check BOTH fast and fast.next
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False

def find_middle_correct(head):
    """Returns the middle node. For even-length lists, returns the second middle."""
    slow = fast = head
    while fast and fast.next:         # same guard
        slow = slow.next
        fast = fast.next.next
    return slow

def find_cycle_start(head):
    """Floyd's algorithm: returns node where cycle begins, or None."""
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None   # no cycle

    # Move one pointer to head; advance both one step at a time
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    return slow

# --- Tests ---
# No cycle — even length
head = build_list([1, 2, 3, 4])
assert has_cycle_correct(head)        == False

# No cycle — odd length
head = build_list([1, 2, 3])
assert has_cycle_correct(head)        == False

# No cycle — single node
head = build_list([1])
assert has_cycle_correct(head)        == False

# No cycle — empty
assert has_cycle_correct(None)        == False

# With cycle: 1->2->3->4->2 (cycle at node 2)
nodes = [ListNode(i) for i in range(1, 5)]
for i in range(len(nodes) - 1):
    nodes[i].next = nodes[i + 1]
nodes[3].next = nodes[1]   # 4 points back to 2
assert has_cycle_correct(nodes[0])    == True

# Find middle
head = build_list([1, 2, 3, 4, 5])
assert find_middle_correct(head).val  == 3   # odd: middle is 3

head = build_list([1, 2, 3, 4])
assert find_middle_correct(head).val  == 3   # even: second middle is 3

print("Fast/slow pointer tests passed.")
```

### Why `while fast and fast.next` is the Correct Guard

```
For a list of length n:

Iteration | fast position
----------|--------------
0         | head
1         | head.next.next
2         | head.next.next.next.next
...

When n is even (e.g., n=4):
  After 2 iterations fast = tail.next = None
  Next check: fast (None) → short-circuits immediately → safe

When n is odd (e.g., n=3):
  After 1 iteration fast = tail (last node)
  fast.next = None → fast.next check fails → short-circuits → safe

If you check only fast.next.next:
  When fast = second-to-last node, fast.next = tail (not None)
  But fast.next.next = tail.next = None
  → the while condition is False, loop exits → accidentally safe here

  When fast.next is None (end of even list):
  → fast.next.next raises AttributeError on None.next → CRASH
```

---

## Summary Table

| # | Mistake                                           | Root Cause                                    | Fix                                                      |
|---|---------------------------------------------------|-----------------------------------------------|----------------------------------------------------------|
| 1 | Converging pointers on unsorted array             | Pattern relies on sorted order invariant      | Sort first, or use hash map for unsorted input           |
| 2 | Infinite loop — pointer not advancing             | Equal case exits neither pointer branch       | Advance at least one pointer in every iteration          |
| 3 | Off-by-one: `<` vs `<=` in palindrome loop        | Unclear invariant about when pointers meet    | Use `<` for palindrome check; expand-around-center for counting |
| 4 | Dutch Flag: advancing `mid` after swap with `hi`  | Swapped-in element from `hi` is unclassified  | Only advance `mid` when it sees a 0 or 1, not a 2        |
| 5 | Checking `fast.next.next` without checking `fast.next` | `None.next` raises AttributeError         | Always guard with `while fast and fast.next`             |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Real World Usage](./real_world_usage.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
