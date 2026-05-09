# Greedy Algorithms — Practice Problems

25 problems from fundamentals to advanced. Covers greedy choice property, interval scheduling,
fractional knapsack, Huffman, jump games, gas station, task assignment, meeting rooms, coin change
(greedy vs DP), exchange argument proofs, interval merging, and when greedy is wrong.

---

## Quick Index

| # | Problem | Difficulty | Pattern |
|---|---------|-----------|---------|
| [Q1](#q1) | What Is the Greedy Choice Property? | Basic | Concept |
| [Q2](#q2) | Optimal Substructure in Greedy | Basic | Concept |
| [Q3](#q3) | Activity Selection — Maximum Meetings | Basic | Interval scheduling |
| [Q4](#q4) | Does Greedy Always Work? | Basic | Coin change trap |
| [Q5](#q5) | Merge Overlapping Intervals | Basic | Interval merging |
| [Q6](#q6) | Jump Game I — Can You Reach the End? | Basic | Max reach |
| [Q7](#q7) | Fractional Knapsack | Basic | Ratio greedy |
| [Q8](#q8) | Assign Cookies | Basic | Two-pointer greedy |
| [Q9](#q9) | Jump Game II — Minimum Jumps | Intermediate | Jump window |
| [Q10](#q10) | Gas Station — Complete Circuit | Intermediate | Running sum reset |
| [Q11](#q11) | Meeting Rooms II — Minimum Rooms | Intermediate | Heap + interval |
| [Q12](#q12) | Task Scheduler with Cooldown | Intermediate | Max-heap frequency |
| [Q13](#q13) | Minimum Intervals to Remove | Intermediate | Activity selection variant |
| [Q14](#q14) | Huffman Encoding — Build the Tree | Intermediate | Min-heap merging |
| [Q15](#q15) | Coin Change — When Greedy Fails | Intermediate | Greedy vs DP |
| [Q16](#q16) | Partition Labels | Intermediate | Last-occurrence window |
| [Q17](#q17) | Minimum Number of Arrows | Intermediate | Interval end tracking |
| [Q18](#q18) | Minimum Platforms (Trains) | Intermediate | Sweep line |
| [Q19](#q19) | Largest Number from Array | Intermediate | Custom sort |
| [Q20](#q20) | Task Assignment — Minimize Maximum Time | Intermediate | Two-pointer pairing |
| [Q21](#q21) | Prove Activity Selection Correctness | Advanced | Exchange argument |
| [Q22](#q22) | When Does Coin Change Greedy Work? | Advanced | Greedy safety proof |
| [Q23](#q23) | Minimum Cost to Connect Ropes | Advanced | Huffman cost variant |
| [Q24](#q24) | Candy Distribution | Advanced | Two-pass greedy |
| [Q25](#q25) | Greedy vs DP — Full Decision Framework | Advanced | Decision analysis |

---

## Basic (Q1–Q8)

---

<a id="q1"></a>
### Q1. What Is the Greedy Choice Property?

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Explain the greedy choice property in your own words. Give one example of a problem that has it
and one that does not.

<details>
<summary>Hint</summary>
Think: can a locally optimal decision always be extended to a globally optimal solution?
</details>

<details>
<summary>Answer</summary>

The **greedy choice property** means that at each step, the locally optimal choice is safe —
it can always be part of some globally optimal solution. You never need to undo a greedy choice
to reach the best answer.

**Has greedy choice property:** Activity selection (always pick earliest finish time — provable
by exchange argument that no better solution exists by choosing a different activity first).

**Does NOT have it:** Coin change with arbitrary denominations. Choosing the largest coin first
(locally optimal) can force you into using more coins than necessary overall.

```python
# Activity selection: greedy choice is always safe
def activity_selection(intervals):
    intervals.sort(key=lambda x: x[1])   # sort by end time
    count, last_end = 0, float('-inf')
    for start, end in intervals:
        if start >= last_end:
            count += 1
            last_end = end
    return count

# Coin change counterexample: greedy is NOT safe
# coins=[1,3,4], amount=6 → greedy picks [4,1,1]=3, optimal is [3,3]=2
```

**Why:** `activity_selection` — picking the earliest-ending activity never blocks a better
solution (proven by exchange argument). Coin change — picking 4 blocks the 3+3 path.

**Time:** O(n log n) for activity selection. Space: O(1).

</details>

---

<a id="q2"></a>
### Q2. Optimal Substructure in Greedy

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


What is optimal substructure? Explain how it relates to greedy algorithms, and how it differs
from the DP use of optimal substructure.

<details>
<summary>Hint</summary>
Both greedy and DP require optimal substructure. What's different is whether subproblems overlap
and whether you need to explore all options.
</details>

<details>
<summary>Answer</summary>

**Optimal substructure** means the optimal solution to the full problem contains optimal solutions
to its sub-problems. Removing a greedy choice from an optimal solution leaves an optimal solution
to the remaining sub-problem.

**Greedy vs DP use:**
- Greedy: after making the one locally best choice, solve the single remaining sub-problem.
  No branching, no memoization, no revisiting.
- DP: the same sub-problem appears in many branches of the recursion (overlapping sub-problems).
  DP stores all solutions; greedy commits to one.

```
Activity selection:
  Optimal solution = [earliest-finish activity] + [optimal solution for remaining activities]
  This is optimal substructure. The greedy choice reduces the problem size by 1.

0/1 Knapsack:
  Optimal for capacity W = best of (include item i OR exclude item i)
  Must check both branches → DP, not greedy.
```

**Why greedy needs both properties:** Greedy choice property ensures the local pick is globally
safe. Optimal substructure ensures the reduced sub-problem can also be solved optimally by the
same greedy rule.

**Time:** Conceptual — no code complexity. Space: O(1).

</details>

---

<a id="q3"></a>
### Q3. Activity Selection — Maximum Non-Overlapping Meetings

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Given a list of meetings `(start, end)`, return the maximum number of non-overlapping meetings
you can attend.

```python
# Example:
# meetings = [(1,4), (3,8), (4,6), (6,9), (8,11)]
# Answer: 3  →  (1,4), (4,6), (6,9)  or  (1,4), (4,6), (8,11)
```

<details>
<summary>Hint</summary>
Sort by end time. At each step, pick the meeting that ends earliest without conflicting with the
last chosen meeting.
</details>

<details>
<summary>Answer</summary>

```python
def max_meetings(meetings):
    # Sort by end time — greedy choice: finish earliest, leave most room
    meetings.sort(key=lambda x: x[1])
    count = 0
    last_end = float('-inf')

    for start, end in meetings:
        if start >= last_end:   # no overlap with last chosen
            count += 1
            last_end = end

    return count

# meetings = [(1,4), (3,8), (4,6), (6,9), (8,11)]
print(max_meetings([(1,4), (3,8), (4,6), (6,9), (8,11)]))  # 3
```

**Why:** Sorting by end time means we always free up the schedule as soon as possible.
Any alternative choice that ends later either ties or leaves less room — proven by exchange
argument: if optimal picks a later-ending activity first, swap it for the greedy choice and
the solution remains valid with the same or better count.

**Time:** O(n log n) for sort, O(n) scan. **Space:** O(1).

</details>

---

<a id="q4"></a>
### Q4. Does Greedy Always Work? Coin Change Counterexample

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


You have coins `[1, 3, 4]` and need to make amount `6`. The greedy approach picks the
largest coin each time. Show why it fails and give the correct solution.

<details>
<summary>Hint</summary>
Try greedy: 4 + 1 + 1 = 3 coins. Can you do better? Think 3 + 3.
</details>

<details>
<summary>Answer</summary>

```python
def coin_change_greedy(coins, amount):
    """WRONG for arbitrary coins — shows the failure."""
    coins_sorted = sorted(coins, reverse=True)
    count = 0
    for coin in coins_sorted:
        while amount >= coin:
            amount -= coin
            count += 1
    return count if amount == 0 else -1

def coin_change_dp(coins, amount):
    """Correct: DP explores all possibilities."""
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1

coins = [1, 3, 4]
print(coin_change_greedy(coins, 6))  # 3  (4+1+1) — WRONG
print(coin_change_dp(coins, 6))      # 2  (3+3)   — CORRECT
```

**Why greedy fails:** Choosing 4 (locally best) leaves remainder 2, forcing two 1-coins.
The global optimum requires ignoring the "biggest coin first" instinct — 3+3 is better.
The greedy choice property does NOT hold for arbitrary coin denominations.

**When greedy IS safe for coins:** When each denomination is a multiple of the previous
(e.g., 1, 5, 10, 25). Each coin "covers" all combinations of smaller coins.

**Time (DP):** O(amount × len(coins)). **Space:** O(amount).

</details>

---

<a id="q5"></a>
### Q5. Merge Overlapping Intervals

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Given `intervals = [[1,3],[2,6],[8,10],[15,18]]`, merge all overlapping intervals.

<details>
<summary>Hint</summary>
Sort by start time. For each interval, check if it overlaps with the last merged interval.
If yes, extend the end. If no, start a new merged interval.
</details>

<details>
<summary>Answer</summary>

```python
def merge_intervals(intervals):
    if not intervals:
        return []

    # Sort by start time — need left-to-right order to detect overlaps
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0][:]]   # copy first interval

    for start, end in intervals[1:]:
        if start <= merged[-1][1]:           # overlaps current merged
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    return merged

print(merge_intervals([[1,3],[2,6],[8,10],[15,18]]))
# [[1,6],[8,10],[15,18]]
```

**Why sort by START (not end):** We want to process intervals left-to-right so overlaps are
detected by comparing each interval's start against the current merged interval's end.
Sorting by end would miss cases where a later-starting interval extends an earlier one.

**Why `<=` not `<`:** Touching intervals `[1,2]` and `[2,3]` should merge to `[1,3]`.

**Time:** O(n log n). **Space:** O(n) for result.

</details>

---

<a id="q6"></a>
### Q6. Jump Game I — Can You Reach the End?

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Given `nums = [2,3,1,1,4]`, each element is the max jump from that index.
Can you reach the last index?

<details>
<summary>Hint</summary>
Track the farthest reachable index. If you ever visit an index that exceeds max_reach, you're
stuck. Never enumerate specific jump sequences — just track the frontier.
</details>

<details>
<summary>Answer</summary>

```python
def can_jump(nums):
    max_reach = 0

    for i, jump in enumerate(nums):
        if i > max_reach:
            return False                # index i is unreachable
        max_reach = max(max_reach, i + jump)

    return True

print(can_jump([2,3,1,1,4]))   # True
print(can_jump([3,2,1,0,4]))   # False  (stuck at index 3, which has jump=0)
```

**Why:** The greedy insight is to track the frontier of reachable positions. At each index,
we extend max_reach as far as possible. If we encounter an index we cannot reach (i > max_reach),
no future jump can save us — the gap is impassable.

**Critical invariant:** Check `if i > max_reach` BEFORE updating max_reach. Updating for an
unreachable index would give a false positive.

**Time:** O(n). **Space:** O(1).

</details>

---

<a id="q7"></a>
### Q7. Fractional Knapsack

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Items have `(value, weight)`. Capacity is `W`. You can take fractions of items.
Maximize total value.

```python
# items = [(60,10), (100,20), (120,30)], W = 50
# Answer: 240.0  →  take all of item 0 (60), all of item 1 (100), 2/3 of item 2 (80)
```

<details>
<summary>Hint</summary>
Sort by value/weight ratio descending. Take as much of the best-ratio item as possible, then
move to the next. Unlike 0/1 knapsack, fractions are allowed, so greedy is provably optimal.
</details>

<details>
<summary>Answer</summary>

```python
def fractional_knapsack(items, capacity):
    # Sort by value-per-weight ratio descending
    items_sorted = sorted(items, key=lambda x: x[0] / x[1], reverse=True)

    total_value = 0.0
    for value, weight in items_sorted:
        if capacity <= 0:
            break
        take = min(weight, capacity)
        total_value += take * (value / weight)
        capacity -= take

    return total_value

items = [(60, 10), (100, 20), (120, 30)]
print(fractional_knapsack(items, 50))  # 240.0
```

**Why greedy works here (not for 0/1):** Because we can take fractions, the highest-ratio item
always contributes optimally per unit of capacity. There is no "blocking" — taking part of the
best item never prevents a better combination, since any leftover capacity goes to the next-best.
For 0/1 knapsack (whole items only), this logic breaks — a lower-ratio item might be the right
choice if it fits exactly.

**Time:** O(n log n). **Space:** O(1).

</details>

---

<a id="q8"></a>
### Q8. Assign Cookies — Maximize Content Children

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Each child `i` has greed factor `g[i]`. Each cookie `j` has size `s[j]`. A child is content
if `s[j] >= g[i]`. Maximize number of content children.

```python
# g = [1,2,3], s = [1,1]  → 1
# g = [1,2], s = [1,2,3]  → 2
```

<details>
<summary>Hint</summary>
Sort both arrays. Use a two-pointer approach: match the smallest sufficient cookie to the
least greedy unsatisfied child.
</details>

<details>
<summary>Answer</summary>

```python
def find_content_children(g, s):
    g.sort()
    s.sort()

    child = cookie = 0
    while child < len(g) and cookie < len(s):
        if s[cookie] >= g[child]:   # smallest available cookie satisfies this child
            child += 1
        cookie += 1                 # always move cookie pointer

    return child

print(find_content_children([1,2,3], [1,1]))  # 1
print(find_content_children([1,2], [1,2,3]))  # 2
```

**Why:** Sorted order lets us greedily assign the smallest cookie that satisfies each child.
Giving a large cookie to an easy-to-satisfy child wastes capacity — the exchange argument shows
reassigning the smallest sufficient cookie never makes the solution worse.

**Time:** O(n log n + m log m) for sorting, O(n + m) for the scan. **Space:** O(1).

</details>

---

## Intermediate (Q9–Q20)

---

<a id="q9"></a>
### Q9. Jump Game II — Minimum Number of Jumps

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Given `nums = [2,3,1,1,4]`, return the minimum number of jumps to reach the last index.

<details>
<summary>Hint</summary>
Think in "jump windows." A window spans all positions reachable in exactly k jumps. Scan the
window, track the farthest reachable position, and jump when you exhaust the current window.
</details>

<details>
<summary>Answer</summary>

```python
def min_jumps(nums):
    jumps = 0
    current_end = 0   # farthest index reachable with `jumps` jumps
    farthest = 0      # farthest index reachable with `jumps + 1` jumps

    # No need to process last index — we want to REACH it, not jump from it
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])

        if i == current_end:      # exhausted current window → must jump
            jumps += 1
            current_end = farthest
            if current_end >= len(nums) - 1:
                break

    return jumps

print(min_jumps([2,3,1,1,4]))   # 2  (index 0→1→4)
print(min_jumps([2,3,0,1,4]))   # 2  (index 0→1→4)
```

**Why:** We delay each jump as long as possible (jump at the last moment before we'd be stuck).
Within each jump window, we scan all reachable positions to find the farthest the next jump can
reach. This greedy "jump at boundary" strategy is provably optimal — taking an earlier jump
cannot extend the frontier.

**Time:** O(n). **Space:** O(1).

</details>

---

<a id="q10"></a>
### Q10. Gas Station — Can You Complete the Circuit?

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


There are `n` gas stations on a circular route. `gas[i]` is the fuel available at station `i`.
`cost[i]` is the fuel needed to travel from station `i` to `i+1`. Find the starting station
index to complete the full circuit, or return -1 if impossible.

<details>
<summary>Hint</summary>
If total gas >= total cost, a solution exists. The starting station is the one after the point
where the cumulative tank hits its minimum (or where running sum last went negative).
</details>

<details>
<summary>Answer</summary>

```python
def can_complete_circuit(gas, cost):
    total_tank = 0
    current_tank = 0
    start = 0

    for i in range(len(gas)):
        diff = gas[i] - cost[i]
        total_tank += diff
        current_tank += diff

        if current_tank < 0:
            # Can't start from `start` through `i` — reset
            start = i + 1
            current_tank = 0

    return start if total_tank >= 0 else -1

print(can_complete_circuit([1,2,3,4,5], [3,4,5,1,2]))  # 3
print(can_complete_circuit([2,3,4], [3,4,3]))           # -1
```

**Why:** The greedy key insight: if you fail at station `i` (tank goes negative), no station
between `start` and `i` can be the solution — they all would have failed even sooner. So the
next candidate start is `i+1`. If `total_tank >= 0`, a valid start always exists (the circuit
is feasible globally), and the last reset position is it.

**Time:** O(n). **Space:** O(1).

</details>

---

<a id="q11"></a>
### Q11. Meeting Rooms II — Minimum Rooms Needed

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Given `intervals = [(0,30),(5,10),(15,20)]`, find the minimum number of conference rooms needed
to host all meetings simultaneously.

<details>
<summary>Hint</summary>
Sort by start time. Use a min-heap of end times for rooms currently in use. If the earliest-ending
room finishes before the new meeting starts, reuse it. Otherwise, allocate a new room.
</details>

<details>
<summary>Answer</summary>

```python
import heapq

def min_meeting_rooms(intervals):
    if not intervals:
        return 0

    intervals.sort(key=lambda x: x[0])   # sort by start time
    heap = []                             # min-heap of end times

    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)  # reuse earliest-ending room
        else:
            heapq.heappush(heap, end)     # allocate new room

    return len(heap)

print(min_meeting_rooms([(0,30),(5,10),(15,20)]))  # 2
print(min_meeting_rooms([(7,10),(2,4)]))           # 1
```

**Why heap of end times:** We need to know at any moment whether any room has freed up.
The min-heap gives the earliest-ending ongoing meeting in O(log n). If even that room hasn't
ended, all rooms are busy and we need a new one. The heap size at the end equals the peak
concurrent meeting count = minimum rooms needed.

**Time:** O(n log n). **Space:** O(n).

</details>

---

<a id="q12"></a>
### Q12. Task Scheduler with Cooldown

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Given tasks `["A","A","A","B","B","B"]` and cooldown `n=2`, return the minimum number of
intervals (including idle time) to complete all tasks.

<details>
<summary>Hint</summary>
The most frequent task determines the frame. There are `(max_freq - 1)` frames of size `(n+1)`,
plus the final batch. The answer is `max(len(tasks), (max_freq - 1) * (n + 1) + count_max)`.
</details>

<details>
<summary>Answer</summary>

```python
from collections import Counter

def least_interval(tasks, n):
    counts = Counter(tasks)
    max_freq = max(counts.values())
    count_max = sum(1 for v in counts.values() if v == max_freq)

    # Formula: arrange most-frequent task into blocks
    # (max_freq - 1) full blocks of size (n+1), then a tail of count_max tasks
    # If we have enough tasks to fill all idle slots, no idle needed → len(tasks)
    return max(len(tasks), (max_freq - 1) * (n + 1) + count_max)

print(least_interval(["A","A","A","B","B","B"], 2))  # 8  (ABXABXAB)
print(least_interval(["A","A","A","B","B","B"], 0))  # 6  (no cooldown)
```

**Why greedy works:** The most frequent task creates the bottleneck. Always schedule the
most-frequent available task to minimize idle slots. The formula captures this: idle slots only
appear in the (max_freq - 1) gaps between repetitions of the dominant task. If enough other
tasks exist to fill gaps, no idle is needed and the answer is just len(tasks).

**Time:** O(n) where n = number of tasks. **Space:** O(1) (26 uppercase letters max).

</details>

---

<a id="q13"></a>
### Q13. Minimum Intervals to Remove (Non-Overlapping)

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Given `intervals = [[1,2],[2,3],[3,4],[1,3]]`, remove the minimum number of intervals so
the rest are non-overlapping.

<details>
<summary>Hint</summary>
This is the complement of activity selection. Find the max non-overlapping intervals (activity
selection), then subtract from total. `min_remove = n - max_non_overlapping`.
</details>

<details>
<summary>Answer</summary>

```python
def erase_overlap_intervals(intervals):
    if not intervals:
        return 0

    # Sort by end time — same as activity selection
    intervals.sort(key=lambda x: x[1])
    keep = 1
    last_end = intervals[0][1]

    for start, end in intervals[1:]:
        if start >= last_end:   # no overlap: keep this interval
            keep += 1
            last_end = end
        # else: overlap → remove this interval (don't update last_end)

    return len(intervals) - keep

print(erase_overlap_intervals([[1,2],[2,3],[3,4],[1,3]]))  # 1  (remove [1,3])
print(erase_overlap_intervals([[1,2],[1,2],[1,2]]))        # 2  (keep one [1,2])
```

**Why:** Maximizing what we keep (activity selection by earliest end) minimizes what we remove.
The greedy choice — keep the interval that ends earliest — is the same exchange-argument-proven
choice from activity selection.

**Time:** O(n log n). **Space:** O(1).

</details>

---

<a id="q14"></a>
### Q14. Huffman Encoding — Build the Optimal Prefix Tree

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


Given character frequencies `{'a':5, 'b':9, 'c':12, 'd':13, 'e':16, 'f':45}`,
build the Huffman tree and return the codes.

<details>
<summary>Hint</summary>
Use a min-heap. Repeatedly merge the two nodes with lowest frequency. The merged node's
frequency = sum of the two. Push it back. The last node is the root.
</details>

<details>
<summary>Answer</summary>

```python
import heapq

def build_huffman_codes(freq_map):
    # (frequency, unique_id, char_or_None, left_child, right_child)
    heap = [(f, i, ch, None, None) for i, (ch, f) in enumerate(freq_map.items())]
    heapq.heapify(heap)
    counter = len(heap)

    while len(heap) > 1:
        f1, _, ch1, l1, r1 = heapq.heappop(heap)
        f2, _, ch2, l2, r2 = heapq.heappop(heap)
        merged = (f1 + f2, counter, None, (f1, ch1, l1, r1), (f2, ch2, l2, r2))
        heapq.heappush(heap, merged)
        counter += 1

    def extract_codes(node, prefix, codes):
        freq, _, ch, left, right = node
        if ch is not None:
            codes[ch] = prefix or "0"
            return
        if left:  extract_codes(left,  prefix + "0", codes)
        if right: extract_codes(right, prefix + "1", codes)

    codes = {}
    if heap:
        extract_codes(heap[0], "", codes)
    return codes

freq = {'a':5, 'b':9, 'c':12, 'd':13, 'e':16, 'f':45}
codes = build_huffman_codes(freq)
for ch, code in sorted(codes.items()):
    print(f"  {ch}: {code}")
```

**Why merge smallest two:** Each merge adds the combined frequency to all future merge costs.
Smaller items merged early contribute less to total cost. Larger items deferred = fewer times
their cost is re-counted. This is proven optimal by the exchange argument: swapping any two
nodes in the tree only increases or maintains total cost.

**Time:** O(n log n). **Space:** O(n).

</details>

---

<a id="q15"></a>
### Q15. Coin Change — When Greedy Fails, Use DP

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


For `coins=[1,5,6,9]` and `amount=11`:
1. Show why greedy fails.
2. Write the correct DP solution.
3. State the condition under which greedy is safe for coin change.

<details>
<summary>Hint</summary>
Greedy picks 9, leaving 2 → two 1s → total 3 coins. Optimal is 5+6=2 coins. The greedy choice
property fails because picking the largest coin "commits" you to a suboptimal remainder.
</details>

<details>
<summary>Answer</summary>

```python
def coin_change_greedy_fails(coins, amount):
    """Greedy: always pick largest coin. WRONG for arbitrary coins."""
    coins_desc = sorted(coins, reverse=True)
    count = 0
    remaining = amount
    for coin in coins_desc:
        while remaining >= coin:
            remaining -= coin
            count += 1
    return count if remaining == 0 else -1

def coin_change_dp(coins, amount):
    """DP: correct for all coin systems."""
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] + 1 < dp[i]:
                dp[i] = dp[i - coin] + 1
    return dp[amount] if dp[amount] != float('inf') else -1

coins, amount = [1, 5, 6, 9], 11
print(coin_change_greedy_fails(coins, amount))  # 3  (9+1+1)
print(coin_change_dp(coins, amount))            # 2  (5+6)
```

**Why greedy fails:** Coins [1,5,6,9] are not structured so that each denomination "covers"
all smaller ones. 9 looks biggest, but it creates remainder 2 (needing two 1s). Skipping 9
and using 5+6 is better.

**When greedy IS safe:** When each coin divides evenly into the next (canonical systems like
US coins: 1, 5, 10, 25). The "greedy stays ahead" proof holds: you can always swap any
combination of smaller coins for a larger coin without increasing count.

**Time (DP):** O(amount × len(coins)). **Space:** O(amount).

</details>

---

<a id="q16"></a>
### Q16. Partition Labels

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


Given `s = "ababcbacadefegdehijhklij"`, partition it into as many parts as possible such that
each letter appears in at most one part. Return the size of each partition.

<details>
<summary>Hint</summary>
For each character, find its last occurrence. Scan left to right, extending the current window's
end to `max(window_end, last[s[i]])`. When `i == window_end`, the partition is complete.
</details>

<details>
<summary>Answer</summary>

```python
def partition_labels(s):
    last = {ch: i for i, ch in enumerate(s)}   # last occurrence of each char

    partitions = []
    start = 0
    end = 0

    for i, ch in enumerate(s):
        end = max(end, last[ch])   # extend window to cover last occurrence of ch
        if i == end:               # window is closed — all chars seen for last time
            partitions.append(end - start + 1)
            start = i + 1

    return partitions

print(partition_labels("ababcbacadefegdehijhklij"))  # [9, 7, 8]
```

**Why:** The greedy insight is to track the "closing point" of the current partition — the
farthest last-occurrence of any character seen so far. Once we reach that point, we know no
character in this partition appears later, so we can safely cut here.

**Time:** O(n). **Space:** O(1) — at most 26 characters in `last`.

</details>

---

<a id="q17"></a>
### Q17. Minimum Number of Arrows to Burst Balloons

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


Balloons are represented by intervals `[x_start, x_end]`. An arrow shot at position `x` bursts
all balloons with `x_start <= x <= x_end`. Find the minimum arrows needed.

<details>
<summary>Hint</summary>
Sort by end position. One arrow at the end of the first balloon bursts all overlapping balloons.
When a balloon's start exceeds the current arrow position, shoot a new arrow.
</details>

<details>
<summary>Answer</summary>

```python
def find_min_arrows(points):
    if not points:
        return 0

    # Sort by end position — same pattern as activity selection
    points.sort(key=lambda x: x[1])

    arrows = 1
    arrow_pos = points[0][1]   # shoot at the end of the first balloon

    for start, end in points[1:]:
        if start > arrow_pos:  # balloon starts after current arrow position
            arrows += 1
            arrow_pos = end    # shoot at end of this balloon

    return arrows

print(find_min_arrows([[10,16],[2,8],[1,6],[7,12]]))  # 2
print(find_min_arrows([[1,2],[3,4],[5,6],[7,8]]))     # 4
```

**Why:** Shooting at the earliest end of a group of overlapping balloons maximizes the number
of balloons burst per arrow (greedy stays ahead). Every balloon whose start is within the current
arrow range gets burst. This is the same as activity selection — pick the interval that ends
earliest, shoot there.

**Time:** O(n log n). **Space:** O(1).

</details>

---

<a id="q18"></a>
### Q18. Minimum Platforms for Train Station

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Given arrival times `[900,940,950,1100,1500,1800]` and departure times
`[910,1200,1120,1130,1900,2000]`, find the minimum platforms needed.

<details>
<summary>Hint</summary>
Use two sorted arrays (not combined events). Two-pointer sweep: if arrival <= departure, a
train arrives → need platform. Else, a train departs → free platform.
</details>

<details>
<summary>Answer</summary>

```python
def min_platforms(arrivals, departures):
    arr = sorted(arrivals)
    dep = sorted(departures)

    platforms = 0
    max_platforms = 0
    i = j = 0

    while i < len(arr):
        if arr[i] <= dep[j]:   # train arrives before or when earliest departs
            platforms += 1
            max_platforms = max(max_platforms, platforms)
            i += 1
        else:                  # a train departs, freeing a platform
            platforms -= 1
            j += 1

    return max_platforms

print(min_platforms([900,940,950,1100,1500,1800], [910,1200,1120,1130,1900,2000]))  # 3
```

**Why separate arrays (not combined events):** If an arrival and departure share the same
timestamp, the departing train vacates the platform before the arriving train needs it.
Using `<=` (not `<`) handles this: if `arr[i] <= dep[j]`, the arrival happens at or before the
departure, so we do need a new platform. Separate sorted arrays preserve this semantics cleanly.

**Time:** O(n log n). **Space:** O(1).

</details>

---

<a id="q19"></a>
### Q19. Largest Number from Array

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


Given `nums = [10, 2]`, arrange them to form the largest number: `"210"`.
Given `nums = [3,30,34,5,9]`, answer is `"9534330"`.

<details>
<summary>Hint</summary>
Sort using a custom comparator: for two numbers `a` and `b`, compare `str(a)+str(b)` vs
`str(b)+str(a)`. This greedy comparison handles multi-digit edge cases.
</details>

<details>
<summary>Answer</summary>

```python
from functools import cmp_to_key

def largest_number(nums):
    def compare(a, b):
        # If ab > ba, a should come first
        return 1 if str(a) + str(b) > str(b) + str(a) else -1

    nums_sorted = sorted(nums, key=cmp_to_key(compare), reverse=True)
    result = "".join(map(str, nums_sorted))
    return "0" if result[0] == "0" else result   # edge case: all zeros

print(largest_number([10, 2]))          # "210"
print(largest_number([3,30,34,5,9]))    # "9534330"
print(largest_number([0,0]))            # "0"
```

**Why this comparator:** We can't just sort digits — `3` should come before `30` because
`330 > 303`. The custom comparator directly compares concatenation order. It satisfies
transitivity (can be proven), making it a valid total order for sorting.

**Time:** O(n log n × k) where k = average digits per number. **Space:** O(n).

</details>

---

<a id="q20"></a>
### Q20. Task Assignment — Minimize Maximum Completion Time

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


Given `workers = [3,1]` and `tasks = [0,3,5,3]` with 2 workers each doing 2 tasks,
assign each task to a worker to minimize the maximum total time any worker spends.

<details>
<summary>Hint</summary>
Sort workers and tasks. Pair the fastest worker with the hardest task, second-fastest with
second-hardest (two-pointer from opposite ends). This balances load optimally.
</details>

<details>
<summary>Answer</summary>

```python
def assign_tasks(workers, tasks):
    """
    Each worker gets exactly len(tasks) // len(workers) tasks.
    Greedy: pair smallest worker ability with largest task.
    """
    workers_sorted = sorted(workers)
    tasks_sorted = sorted(tasks)

    assignments = {}
    i, j = 0, len(tasks_sorted) - 1

    while i < len(workers_sorted):
        worker = workers_sorted[i]
        # Worker i gets tasks from the hardest going inward
        assigned = []
        for k in range(len(tasks_sorted) // len(workers_sorted)):
            assigned.append(tasks_sorted[j])
            j -= 1
        assignments[worker] = assigned
        i += 1

    return assignments

# Minimum maximum workload when pairing sorted workers with sorted tasks (opposite ends)
def minimize_max_time(workers, tasks):
    workers_sorted = sorted(workers)
    tasks_sorted = sorted(tasks, reverse=True)
    n = len(tasks) // len(workers)

    max_time = 0
    for i, w in enumerate(workers_sorted):
        batch = tasks_sorted[i * n : (i + 1) * n]
        max_time = max(max_time, sum(batch))
    return max_time

print(minimize_max_time([3, 1], [0, 3, 5, 3]))  # 8  (worker 1 gets [5,3], worker 3 gets [3,0])
```

**Why pair smallest worker with largest tasks:** This balances total work across workers.
If the weakest worker takes the lightest tasks, the strongest worker piles up the heaviest —
creating an imbalanced maximum. The exchange argument shows that swapping two workers'
assignments only makes the maximum larger or equal.

**Time:** O(n log n). **Space:** O(n).

</details>

---

## Advanced (Q21–Q25)

---

<a id="q21"></a>
### Q21. Prove Activity Selection Correctness — Exchange Argument

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


Write out the formal exchange argument proof for why "always pick earliest finish time"
is optimal for activity selection.

<details>
<summary>Hint</summary>
Assume an optimal solution O that does NOT start with the greedy choice G (earliest finish).
Show you can swap O's first activity for G without reducing the count.
</summary>
</details>

<details>
<summary>Answer</summary>

```
Exchange Argument Proof for Activity Selection:

Claim: The activity selection algorithm (always choose the activity with earliest
       finish time) produces an optimal solution (maximum number of non-overlapping activities).

Proof:
  Let G = {g1, g2, ..., gk} be the greedy solution (sorted by finish time).
  Let O = {o1, o2, ..., om} be any optimal solution (sorted by finish time).
  We want to show k >= m (greedy is at least as good).

  Step 1: Show g1.finish <= o1.finish.
    The greedy algorithm picks the activity with the earliest finish time.
    Therefore finish(g1) <= finish(o1) by definition.

  Step 2: Swap o1 for g1 in O.
    Define O' = O - {o1} + {g1} = {g1, o2, o3, ..., om}.
    O' has the same number of activities as O.

  Step 3: Show O' is still valid (no overlaps).
    - g1 and g2: finish(g1) <= finish(o1) <= start(o2) <= start(g2).
      So g1 finishes before o2 (and therefore before g2) starts. No overlap.
    - All other pairs (oi, oj) are unchanged from O, so still non-overlapping.
    Therefore O' is a valid solution with |O'| = |O| = m.

  Step 4: Inductive step.
    Now apply the same argument to O' and G for the second activity g2 vs o2.
    finish(g2) <= finish(o2) (greedy chose g2 as earliest from remaining activities
    after g1). Swap o2 for g2 in O' to get O''. Repeat.

  Conclusion: After k swaps, we have a valid solution of size k that is identical to G.
    Since each swap preserved validity and count, m <= k, so greedy is optimal. □
```

```python
# Demonstrating the invariant:
def activity_selection_with_proof(intervals):
    intervals.sort(key=lambda x: x[1])
    selected = []
    last_end = float('-inf')

    for start, end in intervals:
        if start >= last_end:
            selected.append((start, end))
            # INVARIANT: selected[i].finish <= any_optimal[i].finish
            # Maintained by always choosing the earliest-finishing compatible activity
            last_end = end

    return selected
```

**Key insight:** The exchange argument works because finish times only decrease when we
swap — this means the new solution has more remaining time, which can only help future choices.

**Time:** O(n log n). **Space:** O(1).

</details>

---

<a id="q22"></a>
### Q22. When Does Coin Change Greedy Work? Prove It

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


State and prove the condition under which greedy (always pick the largest coin) is
provably correct for coin change.

<details>
<summary>Hint</summary>
The canonical coin condition: each denomination is a multiple of all smaller ones. Use the
exchange argument to show no better combination exists.
</details>

<details>
<summary>Answer</summary>

```
Condition for Greedy Correctness in Coin Change:

Greedy (always pick largest fitting coin) is correct when the coin system is "canonical."
Informally: each larger denomination covers all combinations of smaller ones.

Formal sufficient condition (canonical system):
  For standard coins {c1 < c2 < ... < ck}, greedy is optimal if for every denomination ci,
  the optimal number of coins to make any amount ≤ ci+1 using coins ≤ ci equals
  the greedy solution. This is a recursive property.

Simpler sufficient condition (often tested):
  Each denomination is a multiple of all smaller ones.
  E.g., {1, 5, 10, 25}: 5=5×1, 10=2×5, 25=5×5. ✓

Proof sketch for {1, 5, 10, 25}:
  Claim: no optimal solution uses more than 4 pennies (otherwise 5 pennies = 1 nickel),
  more than 1 nickel in conjunction with pennies in a way that exceeds 1 dime, etc.

  If optimal solution O differs from greedy G:
    - O uses fewer large coins and more small coins at some point.
    - But any k small coins summing to a large coin c can be replaced by 1 coin c.
    - Replacement reduces count by k-1 ≥ 1.
    - This contradicts O being optimal.
    Therefore G = O in count. Greedy is optimal.

Counterexamples where condition fails:
  [1, 3, 4]: 3 is not 3×1 in a canonical sense — 6 needs 3+3 but greedy picks 4+1+1.
  [2, 5, 10]: can't even make 1 (no denomination of 1).
  [1, 5, 6, 9]: 9 is not a multiple of 6 or 5 — see Q15.
```

```python
def verify_greedy_vs_dp(coins, test_amounts):
    """Test if greedy matches DP for all given amounts."""
    def greedy(amount):
        count = 0
        for coin in sorted(coins, reverse=True):
            count += amount // coin
            amount %= coin
        return count if amount == 0 else -1

    def dp(amount):
        dp_arr = [float('inf')] * (amount + 1)
        dp_arr[0] = 0
        for i in range(1, amount + 1):
            for coin in coins:
                if coin <= i:
                    dp_arr[i] = min(dp_arr[i], dp_arr[i - coin] + 1)
        return dp_arr[amount] if dp_arr[amount] != float('inf') else -1

    for amt in test_amounts:
        g, d = greedy(amt), dp(amt)
        if g != d:
            return False, amt, g, d
    return True, None, None, None

# US coins — greedy is safe
ok, *_ = verify_greedy_vs_dp([1,5,10,25], range(1, 100))
print(f"US coins greedy correct: {ok}")   # True

# Arbitrary coins — greedy fails
ok, fail_amt, g, d = verify_greedy_vs_dp([1,3,4], range(1, 20))
print(f"[1,3,4] greedy correct: {ok}, first fail at amount={fail_amt}: greedy={g} dp={d}")
```

**Time:** O(amount × n) for DP verification. **Space:** O(amount).

</details>

---

<a id="q23"></a>
### Q23. Minimum Cost to Connect All Ropes

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Given ropes of lengths `[4, 3, 2, 6]`, you can combine two ropes at a cost equal to their sum.
Find the minimum total cost to combine all ropes into one.

<details>
<summary>Hint</summary>
This is the Huffman cost problem. Use a min-heap. Always combine the two cheapest ropes.
Each combination's cost gets added to future combinations, so defer large values as long as possible.
</details>

<details>
<summary>Answer</summary>

```python
import heapq

def min_cost_connect_ropes(ropes):
    if len(ropes) <= 1:
        return 0

    heapq.heapify(ropes)   # O(n) build
    total_cost = 0

    while len(ropes) > 1:
        first = heapq.heappop(ropes)
        second = heapq.heappop(ropes)
        cost = first + second
        total_cost += cost
        heapq.heappush(ropes, cost)

    return total_cost

print(min_cost_connect_ropes([4, 3, 2, 6]))   # 29
# Step 1: combine 2+3=5 (cost 5). Ropes: [4,5,6]
# Step 2: combine 4+5=9 (cost 9). Ropes: [6,9]
# Step 3: combine 6+9=15 (cost 15). Total: 5+9+15 = 29
```

**Why greedy (combine smallest two) is optimal:**
When you combine two ropes of lengths a and b, you pay a+b. The combined rope re-enters the
pool. Shorter ropes combined early are added to future combined ropes, contributing less to
the final sum. If you combined a large rope early, its length gets counted in every subsequent
merge. The exchange argument: swapping a small-early combine with a large-early combine only
increases total cost. This is identical to building a Huffman tree.

**Counterexample (combine largest first):** Ropes [1,2,3]: combine 3+2=5 (cost 5), then 5+1=6
(cost 6) → total 11. Greedy: combine 1+2=3 (cost 3), then 3+3=6 (cost 6) → total 9.

**Time:** O(n log n). **Space:** O(n).

</details>

---

<a id="q24"></a>
### Q24. Candy Distribution

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


Children stand in a line with ratings. Each child must get ≥1 candy. Children with a higher
rating than their neighbor must get more candy. Minimize total candies.

```python
# ratings = [1,0,2]  → [2,1,2] → 5 candies
# ratings = [1,2,2]  → [1,2,1] → 4 candies
```

<details>
<summary>Hint</summary>
Two-pass greedy: left-to-right pass ensures right-higher is satisfied. Right-to-left pass
ensures left-higher is satisfied. Final answer is max of both passes at each position.
</details>

<details>
<summary>Answer</summary>

```python
def candy(ratings):
    n = len(ratings)
    candies = [1] * n

    # Left-to-right pass: if right child has higher rating than left, give right +1
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            candies[i] = candies[i - 1] + 1

    # Right-to-left pass: if left child has higher rating than right, ensure left gets enough
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            candies[i] = max(candies[i], candies[i + 1] + 1)

    return sum(candies)

print(candy([1, 0, 2]))   # 5  → [2,1,2]
print(candy([1, 2, 2]))   # 4  → [1,2,1]
print(candy([1,3,2,2,1])) # 7  → [1,3,2,2,1] ← wait: [1,2,1,2,1]=7
```

**Why two passes:** A single left-to-right pass only handles left-neighbor constraints.
A right-to-left pass handles right-neighbor constraints. Taking `max` of both ensures both
constraints are satisfied simultaneously with the minimum number of candies at each position.

**Why greedy (not DP):** Each pass makes locally irrevocable decisions. The two-pass structure
is itself the proof: each pass is optimal for one direction, and taking the maximum preserves
both. No sub-problem overlap requires memoization.

**Time:** O(n). **Space:** O(n).

</details>

---

<a id="q25"></a>
### Q25. Greedy vs DP — Full Decision Framework

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


Given the following problems, classify each as "greedy is correct," "greedy fails — use DP,"
or "greedy fails — use other." Justify each.

1. Activity selection (max non-overlapping intervals)
2. 0/1 Knapsack
3. Fractional Knapsack
4. Coin change with arbitrary denominations
5. Coin change with US standard denominations (1, 5, 10, 25)
6. Shortest path with non-negative weights
7. Shortest path with negative weights
8. Longest increasing subsequence
9. Minimum spanning tree
10. Task scheduler with cooldown

<details>
<summary>Hint</summary>
For each, ask: does a locally optimal choice lock out a globally optimal path? If yes, greedy
fails. If the greedy choice property + optimal substructure hold, greedy is correct.
</details>

<details>
<summary>Answer</summary>

```
1. Activity selection — GREEDY CORRECT
   Exchange argument: earliest-finish activity can always replace any optimal first choice.
   Local best (earliest finish) never blocks future options.

2. 0/1 Knapsack — DP REQUIRED
   Can't take fractions. Best ratio item might not fit; two medium items may beat one high-ratio.
   Greedy fails: counterexample items [(10,5), (6,3), (6,3)], capacity=6 → greedy picks (10,5)
   but optimal is (6,3)+(6,3)=12 value vs 10 value.

3. Fractional Knapsack — GREEDY CORRECT
   Can take fractions → always greedily fill with best ratio. No "locking out."
   Proof: any deviation from highest ratio first reduces value per unit capacity.

4. Coin change (arbitrary) — DP REQUIRED
   Greedy choice property fails: see [1,3,4] amount=6 counterexample in Q15.

5. Coin change (US standard) — GREEDY CORRECT
   Canonical system: each denomination covers all combinations of smaller ones.
   Exchange argument: any optimal solution using small coins can be improved by using
   larger coins (reducing count), so greedy (biggest first) is optimal.

6. Shortest path (non-negative weights) — GREEDY CORRECT (Dijkstra)
   Greedy choice: always expand the closest unvisited node.
   Non-negative weights guarantee: once a node is settled, its distance is final.

7. Shortest path (negative weights) — GREEDY FAILS
   A negative edge discovered later might shorten a "settled" path.
   Use Bellman-Ford (DP-like edge relaxation over V-1 iterations).

8. Longest increasing subsequence — DP REQUIRED
   Greedy (always take the largest next element) fails: missing a small element now
   might allow a longer sequence later. Need dp[i] = LIS ending at i.

9. Minimum spanning tree — GREEDY CORRECT (Kruskal's, Prim's)
   Greedy choice: always add the cheapest edge that doesn't create a cycle (Kruskal) or
   cheapest edge connecting new node to tree (Prim). Cut property proves correctness.

10. Task scheduler with cooldown — GREEDY CORRECT
    Always run the most-frequent available task. Proven by formula: idle slots are minimized
    by maximally spacing the dominant task. Exchange argument: running any other task first
    when the most-frequent is available only pushes idle slots later.
```

```python
# Quick sanity check: greedy vs DP on knapsack
def greedy_01_knapsack_fails():
    """Demonstrate greedy fails for 0/1 knapsack."""
    items = [(10, 5), (6, 3), (6, 3)]   # (value, weight)
    capacity = 6

    # Greedy: sort by ratio, take whole items
    items_by_ratio = sorted(items, key=lambda x: x[0]/x[1], reverse=True)
    greedy_val = 0
    cap = capacity
    for v, w in items_by_ratio:
        if w <= cap:
            greedy_val += v
            cap -= w
    print(f"Greedy 0/1: {greedy_val}")   # 10 (takes (10,5) only)

    # DP: correct
    n = len(items)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        v, w = items[i - 1]
        for c in range(capacity + 1):
            dp[i][c] = dp[i-1][c]
            if w <= c:
                dp[i][c] = max(dp[i][c], dp[i-1][c-w] + v)
    print(f"DP 0/1:     {dp[n][capacity]}")   # 12 (takes both (6,3) items)

greedy_01_knapsack_fails()
```

**Decision rule summary:**
- Greedy: if locally best choice never blocks globally better paths (provable by exchange argument or greedy-stays-ahead).
- DP: if sub-problems overlap and choices affect each other's feasibility.
- Other (Bellman-Ford, backtracking): if greedy fails AND DP doesn't fit the structure.

</details>

---

**[Back to README](../README.md)**

**Prev:** [Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Backtracking — Theory](../20_backtracking/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
