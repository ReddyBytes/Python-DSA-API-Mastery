# Two Pointers — Cheatsheet

---

## Pattern Overview Table

| Pattern         | Setup                     | Movement                        | Use Case                                 |
|-----------------|---------------------------|---------------------------------|------------------------------------------|
| Opposite Ends   | left=0, right=n-1         | Move one or both inward         | Sorted pair sum, palindrome, container   |
| Same Direction  | slow=0, fast=0 or fast=1  | Fast always advances, slow cond | Remove dups, move zeros, partition       |
| Fast / Slow     | slow=head, fast=head      | Slow +1, fast +2                | Cycle detect, find middle, Nth from end  |

---

## Complexity

| Pattern        | Time   | Space  |
|----------------|--------|--------|
| Opposite ends  | O(n)   | O(1)   |
| Same direction | O(n)   | O(1)   |
| Fast / slow    | O(n)   | O(1)   |

---

## Pattern 1: Opposite Ends

```
[ 1,  2,  4,  7,  9 ]
  ^               ^
 left           right
```

### Template — Sorted Pair Sum

```python
def two_sum_sorted(arr, target):
    left, right = 0, len(arr) - 1
    while left < right:
        s = arr[left] + arr[right]
        if s == target:
            return [left, right]        # found
        elif s < target:
            left += 1                   # need larger sum
        else:
            right -= 1                  # need smaller sum
    return []
```

### Template — Container With Most Water

```python
def max_water(height):
    left, right = 0, len(height) - 1
    res = 0
    while left < right:
        h = min(height[left], height[right])
        res = max(res, h * (right - left))
        if height[left] < height[right]:
            left += 1                   # move the shorter side
        else:
            right -= 1
    return res
```

### Recognition Signals
- Sorted array + find pair/triplet with sum constraint
- "Find two numbers that add to target"
- Palindrome check
- Trap water / container problems

---

## Pattern 2: Same Direction (Slow / Fast)

```
[ 1,  1,  2,  3,  3 ]
  s
  f  →  →  →  →
```

### Template — Remove Duplicates (sorted)

```python
def remove_duplicates(nums):
    if not nums:
        return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:    # found new unique
            slow += 1
            nums[slow] = nums[fast]     # overwrite next position
    return slow + 1                     # length of deduped array
```

### Template — Move Zeros to End

```python
def move_zeros(nums):
    slow = 0                            # insertion pointer
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1
    # zeros are now all at the end
```

### Template — Three Sum (sort + opposite ends inside loop)

```python
def three_sum(nums):
    nums.sort()
    res = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue                    # skip duplicate i
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                res.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left+1]:
                    left += 1           # skip duplicate left
                while left < right and nums[right] == nums[right-1]:
                    right -= 1          # skip duplicate right
                left += 1
                right -= 1
            elif s < 0:
                left += 1
            else:
                right -= 1
    return res
```

---

## Pattern 3: Fast / Slow (Floyd's)

```
head → 1 → 2 → 3 → 4 → 5
       s
       f

After 1: s=2, f=3
After 2: s=3, f=5
After 3: s=4, f=2  ← cycle detected when s==f
```

### Template — Detect Cycle

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

### Template — Find Middle of Linked List

```python
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow                         # slow is at middle
# Odd length  → exact middle
# Even length → second of two middles (use fast.next check to get first)
```

### Template — Find Cycle Entry Point

```python
def detect_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            # Phase 2: move one pointer to head
            slow2 = head
            while slow2 != slow:
                slow = slow.next
                slow2 = slow2.next
            return slow                 # cycle entry node
    return None
```

### Template — Nth Node From End

```python
def nth_from_end(head, n):
    fast = slow = head
    for _ in range(n):
        fast = fast.next               # advance fast by n
    while fast:
        fast = fast.next
        slow = slow.next
    return slow                        # slow is n from end
```

---

## When to Reach for Two Pointers

```
Is the array/list SORTED (or can be sorted)?        → Opposite ends
Need to find pair/triplet with sum property?         → Opposite ends
Need to partition in-place (O(1) space)?             → Same direction
Need to remove/filter elements in-place?             → Same direction (slow/fast index)
Linked list: cycle, middle, palindrome check?        → Fast/slow pointers
```

---

## Key Problems by Pattern

### Opposite Ends
| Problem                         | Trick                                  |
|---------------------------------|----------------------------------------|
| Two Sum II (sorted array)       | Standard opposite ends                 |
| 3Sum                            | Fix one, opposite ends for rest        |
| 4Sum                            | Fix two, opposite ends for rest        |
| Container With Most Water       | Move shorter-height pointer inward     |
| Trapping Rain Water             | Track max left, max right              |
| Valid Palindrome                | Skip non-alphanumeric, compare         |

### Same Direction
| Problem                           | Trick                                |
|-----------------------------------|--------------------------------------|
| Remove Duplicates from Sorted Arr | slow = write ptr, fast = read ptr    |
| Remove Element                    | Same pattern, different condition    |
| Move Zeros                        | Swap non-zero to slow position       |
| Sort Colors (Dutch Flag)          | Three pointers: low/mid/high         |

### Fast / Slow
| Problem                           | Trick                                |
|-----------------------------------|--------------------------------------|
| Linked List Cycle                 | Floyd's — meet inside cycle          |
| Linked List Cycle II (entry)      | Phase 2 from head                    |
| Middle of Linked List             | fast reaches end, slow = middle      |
| Palindrome Linked List            | Find mid, reverse second half        |
| Happy Number                      | Cycle in sequence — fast/slow        |

---

## Dutch National Flag (Three Pointers)

```python
def sort_colors(nums):
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1; mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1               # don't advance mid — newly swapped val unchecked
```

---

## Common Mistakes

| Mistake                                    | Fix                                              |
|--------------------------------------------|--------------------------------------------------|
| Moving both pointers when only one needed  | Only move the pointer that violates the condition|
| `left < right` vs `left <= right`          | Use `<` to avoid processing same element twice  |
| Not skipping duplicates in 3Sum            | Inner while loops after recording answer         |
| Fast/slow starting at same vs diff node    | For cycle: same. For Nth from end: same then gap |
| Forgetting `fast.next` check               | `while fast and fast.next` — prevents None.next  |
| Mutating array while iterating             | Two-pointer writes to slow, reads from fast      |

---

## Python Notes

```python
# Reverse in-place with opposite ends
def reverse(arr):
    l, r = 0, len(arr) - 1
    while l < r:
        arr[l], arr[r] = arr[r], arr[l]
        l += 1; r -= 1

# Check palindrome string
def is_palindrome(s):
    l, r = 0, len(s) - 1
    while l < r:
        if s[l] != s[r]: return False
        l += 1; r -= 1
    return True

# bisect not needed — two pointers are already O(n)
# For sorted input, always consider two pointers BEFORE hashmap
# Two pointers uses O(1) space — hashmap uses O(n)
```

---

## Interview Decision Tree

```
Subarray/pair problem?
├── Sorted? → Two Pointers (opposite ends)
├── Unsorted + unique constraint? → Hash Set + two pointers
├── Remove/filter in place? → Same direction (slow/fast index)
└── Linked List? → Fast/slow pointer
```
