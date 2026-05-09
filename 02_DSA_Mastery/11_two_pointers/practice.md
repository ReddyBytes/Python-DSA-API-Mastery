# Practice — 11 Two Pointers

> 🟢 Basic · 🟡 Intermediate · 🟠 Advanced

---

## Quick Index

| # | Concept | Difficulty |
|---|---------|------------|
| [Q1](#q1) | valid-palindrome | 🟢 Basic |
| [Q2](#q2) | two-sum-sorted | 🟢 Basic |
| [Q3](#q3) | remove-duplicates | 🟢 Basic |
| [Q4](#q4) | move-zeros | 🟢 Basic |
| [Q5](#q5) | reverse-array | 🟢 Basic |
| [Q6](#q6) | cycle-detection | 🟢 Basic |
| [Q7](#q7) | middle-of-linked-list | 🟢 Basic |
| [Q8](#q8) | when-two-pointers-beats-brute-force | 🟢 Basic |
| [Q9](#q9) | container-with-most-water | 🟡 Intermediate |
| [Q10](#q10) | three-sum | 🟡 Intermediate |
| [Q11](#q11) | remove-element-in-place | 🟡 Intermediate |
| [Q12](#q12) | partition-around-value | 🟡 Intermediate |
| [Q13](#q13) | sort-colors-dutch-flag | 🟡 Intermediate |
| [Q14](#q14) | merge-sorted-arrays | 🟡 Intermediate |
| [Q15](#q15) | intersection-sorted-arrays | 🟡 Intermediate |
| [Q16](#q16) | choosing-pointer-direction | 🟡 Intermediate |
| [Q17](#q17) | cycle-entry-point | 🟡 Intermediate |
| [Q18](#q18) | valid-palindrome-ii | 🟡 Intermediate |
| [Q19](#q19) | two-pointers-vs-hashmap | 🟡 Intermediate |
| [Q20](#q20) | wrong-stop-condition | 🟡 Intermediate |
| [Q21](#q21) | four-sum | 🟠 Advanced |
| [Q22](#q22) | trapping-rain-water | 🟠 Advanced |
| [Q23](#q23) | three-sum-closest | 🟠 Advanced |
| [Q24](#q24) | not-moving-both-pointers-bug | 🟠 Advanced |
| [Q25](#q25) | nth-node-from-end | 🟠 Advanced |

---

<a id="q1"></a>
### Q1 · valid-palindrome — Valid Palindrome 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Given a string `s`, return `True` if it reads the same forwards and backwards (ignore case and non-alphanumeric characters), `False` otherwise.

```
Input:  s = "A man, a plan, a canal: Panama"
Output: True

Input:  s = "race a car"
Output: False
```

<details>
<summary>Hint</summary>
Use opposite-end pointers. Skip characters that are not alphanumeric, compare lowercased characters.
</details>

<details>
<summary>Answer</summary>

```python
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True
```

**Why:** Opposite-end pointers converge inward. Skipping non-alphanumeric chars means we only compare letters and digits. Each pointer moves at most n times.
Time: O(n) · Space: O(1)
</details>

---

<a id="q2"></a>
### Q2 · two-sum-sorted — Two Sum in Sorted Array 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Given a sorted array `numbers` (1-indexed) and a `target`, return the 1-indexed positions of the two numbers that add to `target`. Exactly one solution guaranteed.

```
Input:  numbers = [2, 7, 11, 15], target = 9
Output: [1, 2]

Input:  numbers = [2, 3, 4], target = 6
Output: [1, 3]
```

<details>
<summary>Hint</summary>
Start `left` at 0, `right` at the end. If sum is too big, move right left. If too small, move left right.
</details>

<details>
<summary>Answer</summary>

```python
def two_sum(numbers: list[int], target: int) -> list[int]:
    left, right = 0, len(numbers) - 1
    while left < right:
        s = numbers[left] + numbers[right]
        if s == target:
            return [left + 1, right + 1]
        elif s < target:
            left += 1
        else:
            right -= 1
    return []
```

**Why:** Sorted order lets us use the sum direction as a signal. Too big → reduce by moving right inward. Too small → increase by moving left inward. Each element visited at most once.
Time: O(n) · Space: O(1)
</details>

---

<a id="q3"></a>
### Q3 · remove-duplicates — Remove Duplicates from Sorted Array 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Given a sorted array `nums`, remove duplicates in-place and return the count of unique elements. The first k elements of the array should hold the unique values.

```
Input:  nums = [1, 1, 2]
Output: 2  (nums becomes [1, 2, ...])

Input:  nums = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
Output: 5  (nums becomes [0, 1, 2, 3, 4, ...])
```

<details>
<summary>Hint</summary>
Slow pointer tracks the write position. Fast pointer scans. When fast finds a new unique value, write it at slow+1.
</details>

<details>
<summary>Answer</summary>

```python
def remove_duplicates(nums: list[int]) -> int:
    if not nums:
        return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1
```

**Why:** `slow` is the write pointer — it marks the last confirmed unique position. `fast` reads every element. When a new unique value is found, it gets placed at `slow + 1`. No extra memory needed.
Time: O(n) · Space: O(1)
</details>

---

<a id="q4"></a>
### Q4 · move-zeros — Move Zeros to End 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Given an array `nums`, move all `0`s to the end while maintaining the relative order of non-zero elements. Do it in-place.

```
Input:  nums = [0, 1, 0, 3, 12]
Output: [1, 3, 12, 0, 0]

Input:  nums = [0]
Output: [0]
```

<details>
<summary>Hint</summary>
Use a slow pointer as the insertion position. Whenever fast finds a non-zero, swap it with slow's position.
</details>

<details>
<summary>Answer</summary>

```python
def move_zeros(nums: list[int]) -> None:
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1
```

**Why:** `slow` marks where the next non-zero goes. Swapping instead of overwriting keeps zeros implicitly pushed to the back. Relative order of non-zeros is preserved because `fast` scans left to right.
Time: O(n) · Space: O(1)
</details>

---

<a id="q5"></a>
### Q5 · reverse-array — Reverse an Array In-Place 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Given an array `arr`, reverse it in-place and return it.

```
Input:  arr = [1, 2, 3, 4, 5]
Output: [5, 4, 3, 2, 1]

Input:  arr = [1, 2]
Output: [2, 1]
```

<details>
<summary>Hint</summary>
Classic opposite-end pointer. Swap left and right, then move both inward until they meet.
</details>

<details>
<summary>Answer</summary>

```python
def reverse_array(arr: list[int]) -> list[int]:
    left, right = 0, len(arr) - 1
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]
        left += 1
        right -= 1
    return arr
```

**Why:** Two pointers from each end meet in the middle. Each element is swapped exactly once. Stop condition `left < right` avoids re-swapping on odd-length arrays.
Time: O(n) · Space: O(1)
</details>

---

<a id="q6"></a>
### Q6 · cycle-detection — Linked List Cycle Detection 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Given the head of a linked list, return `True` if there is a cycle, `False` otherwise.

```
Input:  1 -> 2 -> 3 -> 4 -> 2 (cycle back to node 2)
Output: True

Input:  1 -> 2 -> 3 -> None
Output: False
```

<details>
<summary>Hint</summary>
Use Floyd's algorithm. Fast moves 2 steps, slow moves 1. If they ever meet, there is a cycle.
</details>

<details>
<summary>Answer</summary>

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def has_cycle(head: ListNode) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

**Why:** In a cycle, fast eventually laps slow — they must meet. Without a cycle, fast reaches `None` first. The guard `fast and fast.next` prevents `AttributeError` when fast is at the tail.
Time: O(n) · Space: O(1)
</details>

---

<a id="q7"></a>
### Q7 · middle-of-linked-list — Middle of Linked List 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Given the head of a singly linked list, return the middle node. If two middle nodes exist, return the second one.

```
Input:  1 -> 2 -> 3 -> 4 -> 5
Output: node with value 3

Input:  1 -> 2 -> 3 -> 4
Output: node with value 3  (second middle)
```

<details>
<summary>Hint</summary>
When fast reaches the end, slow is at the middle. Same guard as cycle detection: `while fast and fast.next`.
</details>

<details>
<summary>Answer</summary>

```python
def middle_node(head: ListNode) -> ListNode:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

**Why:** Fast travels at 2x speed. When fast reaches the tail (or past it), slow has traveled exactly half the distance — landing at the middle. For even-length lists, this lands on the second middle node.
Time: O(n) · Space: O(1)
</details>

---

<a id="q8"></a>
### Q8 · when-two-pointers-beats-brute-force — Why O(n) Beats O(n²) 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Given a sorted array of 100,000 integers, you want to find if any two elements sum to a target `T`. Your teammate wrote a nested loop solution. Explain the problem and show the two-pointer version.

```
Input:  nums = [1, 3, 5, 7, 10, ...] (100,000 elements), target = 18
Output: True / False
```

<details>
<summary>Hint</summary>
The nested loop makes ~5 billion comparisons for n=100,000. Two pointers makes at most 100,000. Both are correct — the question is which is feasible.
</details>

<details>
<summary>Answer</summary>

```python
# Brute force: O(n²) — too slow for n = 100,000
def has_pair_brute(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return True
    return False

# Two pointers: O(n) — uses sorted order to discard candidates
def has_pair_two_ptr(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return True
        elif s < target:
            left += 1   # current left is too small with any right → discard it
        else:
            right -= 1  # current right is too large with any left → discard it
    return False
```

**Why:** At each step, two pointers eliminate an element permanently. Sorted order guarantees: if `nums[left] + nums[right] < target`, no right pointer can save `nums[left]` — discard it. This is the core insight that converts O(n²) → O(n).
Time: O(n) · Space: O(1)
</details>

---

<a id="q9"></a>
### Q9 · container-with-most-water — Container With Most Water 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Given an array `height` where `height[i]` is the height of a wall at position `i`, find two walls that together form a container holding the most water.

```
Input:  height = [1, 8, 6, 2, 5, 4, 8, 3, 7]
Output: 49

Input:  height = [1, 1]
Output: 1
```

<details>
<summary>Hint</summary>
Area = min(height[left], height[right]) * (right - left). Always move the pointer at the shorter wall — moving the taller one can only decrease or keep the area the same.
</details>

<details>
<summary>Answer</summary>

```python
def max_area(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        area = min(height[left], height[right]) * (right - left)
        best = max(best, area)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best
```

**Why:** We start with maximum width (widest container). To improve area, we need a taller minimum wall — the only candidate is the shorter wall's side. Moving the taller wall inward shrinks width without improving the minimum, so it can't help. The greedy move is always to advance the shorter wall.
Time: O(n) · Space: O(1)
</details>

---

<a id="q10"></a>
### Q10 · three-sum — Three Sum 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Given an integer array `nums`, return all unique triplets `[a, b, c]` such that `a + b + c == 0`. The solution set must not contain duplicate triplets.

```
Input:  nums = [-1, 0, 1, 2, -1, -4]
Output: [[-1, -1, 2], [-1, 0, 1]]

Input:  nums = [0, 0, 0]
Output: [[0, 0, 0]]
```

<details>
<summary>Hint</summary>
Sort first. Fix one element with an outer loop. For each fixed element, use opposite-end two pointers on the rest. Skip duplicates at both the outer and inner level.
</details>

<details>
<summary>Answer</summary>

```python
def three_sum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue  # skip duplicate outer values
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
            elif s < 0:
                left += 1
            else:
                right -= 1
    return result
```

**Why:** Sorting enables two-pointer logic for the inner pair. Deduplication at both levels prevents duplicate triplets. The outer loop runs n times, inner two-pointer runs O(n) per iteration → O(n²) total.
Time: O(n²) · Space: O(1) (excluding output)
</details>

---

<a id="q11"></a>
### Q11 · remove-element-in-place — Remove Element In-Place 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Given an array `nums` and a value `val`, remove all occurrences of `val` in-place. Return the count of elements not equal to `val`.

```
Input:  nums = [3, 2, 2, 3], val = 3
Output: 2  (nums becomes [2, 2, ...])

Input:  nums = [0, 1, 2, 2, 3, 0, 4, 2], val = 2
Output: 5  (nums becomes [0, 1, 3, 0, 4, ...])
```

<details>
<summary>Hint</summary>
Same-direction two pointers. `write` pointer marks where to place the next non-val element. `read` scans all elements.
</details>

<details>
<summary>Answer</summary>

```python
def remove_element(nums: list[int], val: int) -> int:
    write = 0
    for read in range(len(nums)):
        if nums[read] != val:
            nums[write] = nums[read]
            write += 1
    return write
```

**Why:** The write pointer only advances when we find a value to keep. All elements equal to `val` are simply skipped — fast pointer reads them but slow pointer stays put, effectively overwriting them on the next valid element.
Time: O(n) · Space: O(1)
</details>

---

<a id="q12"></a>
### Q12 · partition-around-value — Partition Array Around a Pivot 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Given an array `nums` and a `pivot`, rearrange so all elements less than `pivot` come before elements greater than or equal to `pivot`. Order within each partition does not need to be preserved.

```
Input:  nums = [3, 8, 5, 2, 6, 1], pivot = 5
Output: [3, 1, 2, 5, 6, 8]  (or any valid partition)
```

<details>
<summary>Hint</summary>
This is Lomuto partition. Use a slow pointer to track the boundary between the "less than" and "greater or equal" regions. Fast pointer scans.
</details>

<details>
<summary>Answer</summary>

```python
def partition(nums: list[int], pivot: int) -> list[int]:
    write = 0
    for read in range(len(nums)):
        if nums[read] < pivot:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1
    return nums
```

**Why:** `write` marks the boundary of the "less than pivot" region. When `read` finds an element less than pivot, it swaps that element into the boundary position and expands it. This is the same pattern as remove_element but with a swap instead of overwrite.
Time: O(n) · Space: O(1)
</details>

---

<a id="q13"></a>
### Q13 · sort-colors-dutch-flag — Sort Colors (Dutch National Flag) 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Given an array `nums` containing only 0, 1, and 2, sort it in-place without using any built-in sort. One pass only.

```
Input:  nums = [2, 0, 2, 1, 1, 0]
Output: [0, 0, 1, 1, 2, 2]

Input:  nums = [2, 0, 1]
Output: [0, 1, 2]
```

<details>
<summary>Hint</summary>
Three pointers: `low`, `mid`, `high`. Invariant: everything before `low` is 0, between `low` and `mid` is 1, after `high` is 2. Do NOT advance `mid` after swapping with `high`.
</details>

<details>
<summary>Answer</summary>

```python
def sort_colors(nums: list[int]) -> None:
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:  # nums[mid] == 2
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
            # Do NOT advance mid — the swapped-in element from high is unclassified
```

**Why:** The third case swaps an unknown element from `high` to `mid`. That unknown element still needs to be evaluated — advancing `mid` would skip it. For 0 and 1 cases, the element is known after the swap so `mid` can safely advance.
Time: O(n) · Space: O(1)
</details>

---

<a id="q14"></a>
### Q14 · merge-sorted-arrays — Merge Two Sorted Arrays 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


Given two sorted arrays `arr1` and `arr2`, return a new sorted array containing all elements from both.

```
Input:  arr1 = [1, 3, 5], arr2 = [2, 4, 6]
Output: [1, 2, 3, 4, 5, 6]

Input:  arr1 = [1, 2, 3], arr2 = []
Output: [1, 2, 3]
```

<details>
<summary>Hint</summary>
Two pointers, one per array. At each step, take the smaller element and advance that pointer. Append leftovers from whichever array still has elements.
</details>

<details>
<summary>Answer</summary>

```python
def merge_sorted(arr1: list[int], arr2: list[int]) -> list[int]:
    i, j = 0, 0
    result = []
    while i < len(arr1) and j < len(arr2):
        if arr1[i] <= arr2[j]:
            result.append(arr1[i])
            i += 1
        else:
            result.append(arr2[j])
            j += 1
    result.extend(arr1[i:])
    result.extend(arr2[j:])
    return result
```

**Why:** At each step we take the globally smallest remaining element. Since both arrays are sorted, the smallest remaining is always at one of the two current pointer positions. The extend calls at the end handle whichever array has leftover elements.
Time: O(n + m) · Space: O(n + m)
</details>

---

<a id="q15"></a>
### Q15 · intersection-sorted-arrays — Intersection of Two Sorted Arrays 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


Given two sorted arrays, return the elements that appear in both arrays (no duplicates in output).

```
Input:  arr1 = [1, 2, 4, 5, 6], arr2 = [2, 3, 5, 7]
Output: [2, 5]

Input:  arr1 = [1, 2, 3], arr2 = [4, 5, 6]
Output: []
```

<details>
<summary>Hint</summary>
Two pointers, one per array. When equal, record and advance both. When unequal, advance the pointer at the smaller value to try to catch up.
</details>

<details>
<summary>Answer</summary>

```python
def intersection(arr1: list[int], arr2: list[int]) -> list[int]:
    i, j = 0, 0
    result = []
    while i < len(arr1) and j < len(arr2):
        if arr1[i] == arr2[j]:
            result.append(arr1[i])
            i += 1
            j += 1
        elif arr1[i] < arr2[j]:
            i += 1  # arr1 is behind, advance to catch up
        else:
            j += 1  # arr2 is behind, advance to catch up
    return result
```

**Why:** Sorted order means if `arr1[i] < arr2[j]`, then `arr1[i]` can never match any element in `arr2` from `j` onward (they're all >= arr2[j] > arr1[i]). Safe to discard it — this is the elimination logic that keeps the algorithm O(n+m).
Time: O(n + m) · Space: O(min(n, m))
</details>

---

<a id="q16"></a>
### Q16 · choosing-pointer-direction — Choosing Pointer Movement Direction 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


For each of the following scenarios, state which pointer to move and why:

1. Sorted array two-sum: `nums[left] + nums[right] > target`
2. Container with most water: `height[left] < height[right]`
3. Removing duplicates: `nums[fast] == nums[slow]`
4. Cycle detection in linked list: default step (no condition)

<details>
<summary>Hint</summary>
The key question for each is: "Which pointer, if moved, could lead to a better answer? Which one is definitively exhausted?"
</details>

<details>
<summary>Answer</summary>

```python
# 1. Two-sum sorted: sum too large → move RIGHT left (decrease the big number)
#    Moving left right would make sum even larger — wrong direction
right -= 1

# 2. Container: left is shorter → move LEFT right
#    The area is limited by min(left, right). Moving right (the taller) inward
#    only shrinks width without any chance of improving the min height.
left += 1

# 3. Remove duplicates: duplicate found → move FAST only (slow stays put)
#    Slow marks the last unique written position. Moving slow would create a gap.
fast += 1  # (implicitly — loop continues without advancing slow)

# 4. Cycle detection: always move BOTH — slow by 1, fast by 2
slow = slow.next
fast = fast.next.next
```

**Why:** Every two-pointer decision is rooted in what can be eliminated. If we can prove an element or position cannot contribute to a better answer, we discard it by advancing that pointer. The direction rule follows directly from the problem's monotonic property.
Time: O(1) per decision · Space: O(1)
</details>

---

<a id="q17"></a>
### Q17 · cycle-entry-point — Cycle Entry Point in Linked List 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


Given a linked list with a cycle, return the node where the cycle begins. If there is no cycle, return `None`.

```
Input:  1 -> 2 -> 3 -> 4 -> 5 -> 3 (cycle starts at node 3)
Output: node with value 3
```

<details>
<summary>Hint</summary>
Phase 1: use fast/slow to detect the meeting point. Phase 2: reset one pointer to head, advance both one step at a time — they meet at the cycle entry.
</details>

<details>
<summary>Answer</summary>

```python
def detect_cycle(head: ListNode) -> ListNode:
    slow = fast = head
    # Phase 1: find meeting point
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None  # no cycle

    # Phase 2: find entry point
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    return slow
```

**Why:** Floyd's proof: distance from head to entry equals distance from meeting point to entry (within the cycle). So resetting one pointer to head and advancing both at speed 1 guarantees they meet exactly at the entry node.
Time: O(n) · Space: O(1)
</details>

---

<a id="q18"></a>
### Q18 · valid-palindrome-ii — Valid Palindrome II (One Deletion Allowed) 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Given a string `s`, return `True` if it can become a palindrome by removing at most one character.

```
Input:  s = "abca"
Output: True  (remove 'b' or 'c')

Input:  s = "abc"
Output: False
```

<details>
<summary>Hint</summary>
Use opposite-end pointers. When you find a mismatch, try skipping `s[left]` OR skipping `s[right]` — if either remaining substring is a palindrome, return True.
</details>

<details>
<summary>Answer</summary>

```python
def valid_palindrome(s: str) -> bool:
    def is_pal(l, r):
        while l < r:
            if s[l] != s[r]:
                return False
            l += 1
            r -= 1
        return True

    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            # Try skipping either side
            return is_pal(left + 1, right) or is_pal(left, right - 1)
        left += 1
        right -= 1
    return True
```

**Why:** At the first mismatch, we have exactly two choices for our one deletion. We test both and return True if either works. The helper `is_pal` is a standard opposite-end palindrome check on the subarray.
Time: O(n) · Space: O(1)
</details>

---

<a id="q19"></a>
### Q19 · two-pointers-vs-hashmap — Two Pointers vs Hash Map Decision 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


You are given an unsorted array `nums` and a target. Your teammate says "just use two pointers." Explain when they are wrong and implement both the correct two-pointer solution (if applicable) and the hash map fallback.

```
Input:  nums = [3, 1, 4, 2], target = 6
Output: indices [2, 3]  (values 4 and 2)
```

<details>
<summary>Hint</summary>
Two pointers require sorted order. If you sort an unsorted array to use two pointers, you lose original indices. Hash map preserves indices and handles unsorted input.
</details>

<details>
<summary>Answer</summary>

```python
# Two-pointer approach: works on sorted input, loses original indices
def two_sum_sorted_values(nums, target):
    nums_sorted = sorted(nums)
    left, right = 0, len(nums_sorted) - 1
    while left < right:
        s = nums_sorted[left] + nums_sorted[right]
        if s == target:
            return [nums_sorted[left], nums_sorted[right]]  # values only
        elif s < target:
            left += 1
        else:
            right -= 1
    return []

# Hash map approach: works on unsorted, preserves indices
def two_sum_indices(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Rule:
# Sorted input + only need values → two pointers (O(1) space)
# Unsorted input OR need indices → hash map (O(n) space)
```

**Why:** Two pointers rely on sorted order to know which direction increases or decreases the sum. On unsorted data, that directional guarantee breaks. Hash map trades O(n) space for O(n) time without needing sorted input — it is the right tool when order is not guaranteed.
Time: O(n log n) sort + O(n) scan vs O(n) hash map · Space: O(1) vs O(n)
</details>

---

<a id="q20"></a>
### Q20 · wrong-stop-condition — Wrong Stop Condition Bug 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


The following code is supposed to check if a string is a palindrome, but it has a bug in the stop condition. Identify the bug and explain what goes wrong on a specific input.

```python
def is_palindrome_buggy(s):
    left, right = 0, len(s) - 1
    while left <= right:   # <-- examine this
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
```

<details>
<summary>Hint</summary>
Try running this on `"aba"`. What happens at the final step when `left == right`? Is that comparison meaningful?
</details>

<details>
<summary>Answer</summary>

```python
# The bug: `left <= right` causes one extra comparison when left == right
# For odd-length strings, the middle character is compared to itself.
# This is always True (s[i] == s[i]) so it doesn't cause a wrong answer HERE,
# but it signals conceptual confusion and causes real bugs in variants.

# Example where the confusion causes a real bug:
def is_palindrome_wrong_range(s):
    n = len(s)
    for i in range(n // 2 + 1):   # BUG: one extra iteration
        if s[i] != s[n - 1 - i]:
            return False
    return True

# For "abba" (n=4): n//2+1 = 3 iterations
# i=0: s[0]='a' vs s[3]='a' ok
# i=1: s[1]='b' vs s[2]='b' ok
# i=2: s[2]='b' vs s[1]='b' ok  <-- re-checks already-checked pair!
# Accidentally correct but does redundant work.

# Correct version:
def is_palindrome_correct(s):
    left, right = 0, len(s) - 1
    while left < right:   # strictly < : stops when pointers meet or cross
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

# Rule: use `left < right` for palindrome checks.
# The middle element (when left == right) never needs comparison — it's its own mirror.
```

**Why:** `while left < right` is the correct invariant: we only compare pairs that are true mirrors of each other. When `left == right`, we're at the exact center of an odd-length string — no pair to compare. The `<=` version is harmless in the pure palindrome check but represents a broken mental model that creates real bugs in related problems (substring extraction, counting).
Time: O(n) · Space: O(1)
</details>

---

<a id="q21"></a>
### Q21 · four-sum — Four Sum 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


Given an integer array `nums` and a target integer `target`, return all unique quadruplets `[a, b, c, d]` such that `a + b + c + d == target`.

```
Input:  nums = [1, 0, -1, 0, -2, 2], target = 0
Output: [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]

Input:  nums = [2, 2, 2, 2, 2], target = 8
Output: [[2, 2, 2, 2]]
```

<details>
<summary>Hint</summary>
Extend the 3Sum approach. Fix two elements with nested outer loops, then use opposite-end two pointers for the remaining pair. Skip duplicates at all three levels.
</details>

<details>
<summary>Answer</summary>

```python
def four_sum(nums: list[int], target: int) -> list[list[int]]:
    nums.sort()
    result = []
    n = len(nums)

    for i in range(n - 3):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        for j in range(i + 1, n - 2):
            if j > i + 1 and nums[j] == nums[j - 1]:
                continue
            left, right = j + 1, n - 1
            while left < right:
                s = nums[i] + nums[j] + nums[left] + nums[right]
                if s == target:
                    result.append([nums[i], nums[j], nums[left], nums[right]])
                    while left < right and nums[left] == nums[left + 1]:
                        left += 1
                    while left < right and nums[right] == nums[right - 1]:
                        right -= 1
                    left += 1
                    right -= 1
                elif s < target:
                    left += 1
                else:
                    right -= 1

    return result
```

**Why:** Pattern generalizes from 3Sum. Each outer loop fixes one element and reduces the problem to a smaller k-sum. Two pointers handle the innermost pair in O(n). Duplicate skipping at every level is required to avoid repeated quadruplets. Total: O(n³) — two nested loops × O(n) inner scan.
Time: O(n³) · Space: O(1) (excluding output)
</details>

---

<a id="q22"></a>
### Q22 · trapping-rain-water — Trapping Rain Water 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


Given an elevation map as an array `height`, compute how much water can be trapped after it rains.

```
Input:  height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
Output: 6

Input:  height = [4, 2, 0, 3, 2, 5]
Output: 9
```

<details>
<summary>Hint</summary>
Water above position `i` = `min(max_left, max_right) - height[i]`. Track running left_max and right_max. Move whichever side has the smaller max — that side's water contribution is determined.
</details>

<details>
<summary>Answer</summary>

```python
def trap(height: list[int]) -> int:
    if not height:
        return 0
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    return water
```

**Why:** The water at any position is bounded by `min(max_left, max_right)`. When we move the left pointer (because `height[left] < height[right]`), we know the right side is taller — so `right_max >= height[right] > height[left]`, meaning the water at `left` is purely bounded by `left_max`. We can compute it immediately. Same logic applies symmetrically to the right pointer.
Time: O(n) · Space: O(1)
</details>

---

<a id="q23"></a>
### Q23 · three-sum-closest — Three Sum Closest 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Given an integer array `nums` and an integer `target`, find three integers whose sum is closest to `target`. Return the sum.

```
Input:  nums = [-1, 2, 1, -4], target = 1
Output: 2  (sum of [-1, 2, 1])

Input:  nums = [0, 0, 0], target = 1
Output: 0
```

<details>
<summary>Hint</summary>
Sort the array. For each element, use two pointers for the remaining pair. Track the closest sum seen so far. If exact match found, return immediately.
</details>

<details>
<summary>Answer</summary>

```python
def three_sum_closest(nums: list[int], target: int) -> int:
    nums.sort()
    closest = float('inf')
    for i in range(len(nums) - 2):
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if abs(s - target) < abs(closest - target):
                closest = s
            if s == target:
                return s  # exact match
            elif s < target:
                left += 1
            else:
                right -= 1
    return closest
```

**Why:** Same structure as 3Sum but instead of checking equality, we track the minimum absolute difference. Sorted order still lets us use two-pointer direction logic — too small means move left right, too big means move right left. We update the closest whenever we find a better approximation.
Time: O(n²) · Space: O(1)
</details>

---

<a id="q24"></a>
### Q24 · not-moving-both-pointers-bug — The "Not Moving Both Pointers" Bug 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


The following 3Sum implementation has a subtle bug that causes either an infinite loop or duplicate results. Find both bugs and explain the fix.

```python
def three_sum_buggy(nums):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                # Bug 1: what happens here?
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                # Neither pointer has been advanced past the current match
            elif s < 0:
                left += 1
            else:
                right -= 1
    return result
```

<details>
<summary>Hint</summary>
After the duplicate-skipping while loops, `left` and `right` still point at the elements that formed the match. The next iteration of the outer `while left < right` loop will find the same pair again.
</details>

<details>
<summary>Answer</summary>

```python
# Bug 1: After recording the match and skipping duplicates, neither left nor right
# has been advanced past the current matching elements. The next outer-while iteration
# reprocesses the same pair → infinite loop on arrays with duplicates.

# Bug 2: The duplicate-skipping checks the WRONG side:
#   nums[left] == nums[left + 1]  should be  nums[left] == nums[left - 1]
# (after advancing left, check backward to skip the value we just moved past)

def three_sum_correct(nums):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                left += 1    # Fix 1: MUST advance past current match
                right -= 1   # Fix 1: advance both
                # Now skip duplicates of the values we just used
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
            elif s < 0:
                left += 1
            else:
                right -= 1
    return result

assert sorted(map(tuple, three_sum_correct([-1, 0, 1, 2, -1, -4]))) == \
       sorted([(-1, -1, 2), (-1, 0, 1)])
assert three_sum_correct([0, 0, 0]) == [[0, 0, 0]]
```

**Why:** The golden rule of two-pointer loops: every iteration must advance at least one pointer, otherwise the loop runs forever. After recording a match, always advance before skipping duplicates. The duplicate-skip direction was also reversed — we compare the newly advanced pointer to the value it just moved past (`nums[left - 1]` after `left += 1`).
Time: O(n²) · Space: O(1)
</details>

---

<a id="q25"></a>
### Q25 · nth-node-from-end — Nth Node From End of Linked List 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


Given the head of a linked list and an integer `n`, remove the nth node from the end and return the head.

```
Input:  1 -> 2 -> 3 -> 4 -> 5, n = 2
Output: 1 -> 2 -> 3 -> 5  (removed node 4, which is 2nd from end)

Input:  1, n = 1
Output: [] (empty list)
```

<details>
<summary>Hint</summary>
Advance `fast` n steps ahead of `slow`. Then advance both until fast reaches the end. `slow` lands on the node just before the target — update its `next` pointer to skip the target.
</details>

<details>
<summary>Answer</summary>

```python
def remove_nth_from_end(head: ListNode, n: int) -> ListNode:
    dummy = ListNode(0)
    dummy.next = head
    slow = fast = dummy

    # Advance fast n+1 steps so slow is one before the target
    for _ in range(n + 1):
        fast = fast.next

    # Move both until fast hits None
    while fast:
        slow = slow.next
        fast = fast.next

    # slow is now one node before the target — skip the target
    slow.next = slow.next.next
    return dummy.next
```

**Why:** The gap between fast and slow is maintained at n+1 nodes. When fast is None (past the tail), slow is exactly n+1 nodes from the end — pointing at the predecessor of the node to remove. The dummy node handles the edge case where the first node must be removed (slow would be the dummy, and `dummy.next = dummy.next.next` correctly removes the head).
Time: O(L) · Space: O(1)
</details>

---

## Navigation

**[Back to README](../README.md)**

**Prev:** [Theory](./theory.md) &nbsp;|&nbsp; **Practice:** [practice_local.py](./practice_local.py) &nbsp;|&nbsp; **Next:** [Cheat Sheet](./cheetsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md) · [Visual Explanation](./visual_explanation.md) · [Patterns](./patterns.md) · [Common Mistakes](./common_mistakes.md)
