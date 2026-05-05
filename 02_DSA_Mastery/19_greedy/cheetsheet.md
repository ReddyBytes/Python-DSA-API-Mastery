# Greedy Algorithms — Quick Reference Cheatsheet

## Core Definition

```
GREEDY: At each step, choose the locally optimal option.
        Hope/prove that local optima → global optimum.

Two proof techniques:
  1. Greedy Stays Ahead: Greedy solution never falls behind optimal at any step.
  2. Exchange Argument:  Any deviation from greedy can be swapped back to greedy
                         without worsening the solution.
```

---

## Greedy vs Dynamic Programming

| Property                      | Greedy              | Dynamic Programming         |
|-------------------------------|---------------------|-----------------------------|
| Subproblem dependence         | Independent         | Overlapping subproblems      |
| Choices                       | Irrevocable         | Explore all options          |
| Optimality guarantee          | If greedy property holds | Always (if DP applicable)|
| Time complexity               | Usually O(n log n)  | Usually O(n^2) or O(n*k)    |
| Space complexity              | O(1) or O(n)        | O(n) or O(n^2) table        |
| When it works                 | Greedy choice property + optimal substructure | Optimal substructure + overlapping subproblems |

### Decision Rule:

```
Does a LOCAL best choice always lead to GLOBAL best?
  YES → Try Greedy  (prove with exchange argument)
  NO  → Use DP      (need to consider all options)

Clue: If problem has "maximize/minimize" AND choices are independent → try greedy first.
```

---

## Greedy Recognition Signals

```
- "Minimum number of ..."        → greedy with sorting
- "Maximum number of ..."        → greedy activity selection
- "Interval scheduling"          → sort by end time
- "Merge intervals"              → sort by start time
- "Jump / reach / coverage"      → greedy max reach
- "Assign tasks / meetings"      → greedy with heap or sorting
- "Can we always make change?"   → check denominations (not always greedy!)
- "Huffman / encoding"           → greedy by frequency
```

---

## Classic Pattern 1: Activity Selection (Interval Scheduling)

```
Goal: Select maximum number of non-overlapping activities.
Key insight: Always pick activity that finishes EARLIEST.

Why? Finishing early leaves maximum room for future activities.
```

```python
def activity_selection(intervals):
    # Sort by END time
    intervals.sort(key=lambda x: x[1])
    count = 0
    last_end = float('-inf')

    for start, end in intervals:
        if start >= last_end:           # no overlap
            count += 1
            last_end = end
    return count
# Time: O(n log n)  |  Proof: exchange argument
```

---

## Classic Pattern 2: Merge Intervals

```python
def merge_intervals(intervals):
    # Sort by START time
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]

    for start, end in intervals[1:]:
        if start <= merged[-1][1]:      # overlapping
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
# Time: O(n log n)
```

---

## Interval Problems: Sort by Which End?

```
Sort by START when:
  - Merging overlapping intervals
  - Checking if intervals overlap (sweep line)
  - Minimum platforms / meeting rooms needed

Sort by END when:
  - Maximizing count of non-overlapping intervals
  - Activity selection
  - Earliest deadline first scheduling

Sort by BOTH (start then end):
  - Insert interval into sorted list
  - Removing covered intervals
```

---

## Classic Pattern 3: Jump Game

```python
# Can you reach the last index?
def can_jump(nums):
    max_reach = 0
    for i, jump in enumerate(nums):
        if i > max_reach:
            return False            # stuck — can't reach i
        max_reach = max(max_reach, i + jump)
    return True
# Greedy: always extend max reach as far as possible

# Minimum jumps to reach end
def min_jumps(nums):
    jumps = 0
    current_end = 0
    farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:        # must make a jump
            jumps += 1
            current_end = farthest
    return jumps
# Time: O(n)  |  Greedy: jump at last possible moment
```

---

## Classic Pattern 4: Meeting Rooms

```python
# Minimum meeting rooms needed (= max overlapping meetings at any time)
import heapq

def min_meeting_rooms(intervals):
    intervals.sort(key=lambda x: x[0])     # sort by start
    heap = []                               # end times of ongoing meetings

    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)    # reuse freed room
        else:
            heapq.heappush(heap, end)       # need new room
    return len(heap)
# Time: O(n log n)

# Alternative O(n log n): sweep line with events
def min_meeting_rooms_v2(intervals):
    events = []
    for s, e in intervals:
        events.append((s, 1))
        events.append((e, -1))
    events.sort()
    rooms = cur = 0
    for _, delta in events:
        cur += delta
        rooms = max(rooms, cur)
    return rooms
```

---

## Classic Pattern 5: Fractional Knapsack

```python
def fractional_knapsack(capacity, items):
    # items = [(value, weight), ...]
    # Sort by value/weight ratio descending
    items.sort(key=lambda x: x[0]/x[1], reverse=True)

    total_value = 0.0
    for value, weight in items:
        if capacity <= 0:
            break
        take = min(weight, capacity)
        total_value += take * (value / weight)
        capacity -= take
    return total_value
# Time: O(n log n)
# NOTE: 0/1 knapsack (whole items only) is NOT greedy → requires DP
```

---

## Huffman Coding (Concept)

```
Goal: Assign shorter codes to more frequent characters.
Greedy: Always merge the two lowest-frequency nodes.

Build min-heap of (frequency, node).
While heap has > 1 element:
  1. Pop two smallest: (f1, n1), (f2, n2)
  2. Create parent node with freq = f1 + f2
  3. Push parent back to heap
Result: optimal prefix-free binary encoding.
Time: O(n log n)
```

```python
import heapq

def huffman(freq_map):
    heap = [(f, i, ch) for i, (ch, f) in enumerate(freq_map.items())]
    heapq.heapify(heap)
    counter = len(heap)

    while len(heap) > 1:
        f1, _, left = heapq.heappop(heap)
        f2, _, right = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, counter, (left, right)))
        counter += 1
    return heap[0][2]   # root of Huffman tree
```

---

## Greedy Proof Techniques

```
1. GREEDY STAYS AHEAD:
   Show at each step i, greedy solution >= optimal solution in progress.
   Example: Activity selection — greedy always has >= activities chosen up to step i.

2. EXCHANGE ARGUMENT:
   Assume optimal solution O differs from greedy G.
   Find first difference — swap O's choice for G's choice.
   Show: resulting solution is no worse than O.
   Conclude: G must be optimal (or equal).

When to use which:
   Greedy stays ahead → when you can compare solutions step-by-step
   Exchange argument  → when you need to argue about the final solution structure
```

---

## Python Sorting with key=

```python
# Single key
intervals.sort(key=lambda x: x[0])             # sort by first element
intervals.sort(key=lambda x: x[1])             # sort by second element

# Multiple keys (primary, secondary)
intervals.sort(key=lambda x: (x[0], x[1]))     # primary: start, secondary: end
intervals.sort(key=lambda x: (x[1], -x[0]))    # primary: end ASC, secondary: start DESC

# Reverse sort
items.sort(key=lambda x: x[0]/x[1], reverse=True)

# Sort objects by attribute
tasks.sort(key=lambda t: t.deadline)

# Sort strings by length then lexicographically
words.sort(key=lambda w: (len(w), w))
```

---

## Common Greedy Pitfalls

```
PITFALL 1: Coin change with arbitrary denominations
  [1, 3, 4], target=6 → greedy gives [4,1,1]=3 coins, optimal is [3,3]=2 coins
  Arbitrary denominations → DP required

PITFALL 2: 0/1 Knapsack (must take whole items)
  Fractional knapsack → greedy (take best ratio)
  0/1 knapsack → DP (can't take fractions)

PITFALL 3: Shortest path with negative weights
  Dijkstra is greedy — fails with negative edges
  Need Bellman-Ford (DP-like relaxation)

PITFALL 4: Assuming "sort and scan" is always greedy
  Must PROVE the greedy choice property holds
  Counterexample testing: try small cases before assuming greedy works

PITFALL 5: Off-by-one in interval overlap checks
  [1,2] and [2,3]: overlap? Depends on open/closed intervals.
  start < end (open) vs start <= end (closed) — match problem statement
```

---

## Quick Reference: Problem → Strategy

```
Merge intervals             → Sort by start, extend end greedily
Max non-overlapping         → Sort by end, pick earliest finishing
Min platforms/rooms         → Sort by start + min-heap of end times
Jump game                   → Track max_reach greedily
Jump game II (min jumps)    → Jump at boundary, extend farthest
Task scheduler              → Max-heap by frequency, cooldown tracking
Gas station                 → Track running sum, reset on negative
Candy distribution          → Two-pass greedy (left-to-right, right-to-left)
Assign cookies              → Sort both, match greedily
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Visual Explanation](./visual_explanation.md) &nbsp;|&nbsp; **Next:** [Patterns →](./patterns.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
