# Greedy — Pattern Recognition Guide

> **Core Idea**: Make the locally optimal choice at each step. Greedy works when you can
> prove that the locally best choice is also globally best — either via a "greedy stays
> ahead" argument or an "exchange argument."

---

## 1. Greedy Problem Recognition Checklist

Ask these questions before committing to greedy:

```
1. OPTIMIZATION or DECISION?
   "maximize", "minimize", "maximum count", "minimum operations" → possibly greedy

2. CAN LOCAL BEST = GLOBAL BEST?
   Is there a clear "obviously good" choice at each step?
   → If yes, try greedy. If making a local choice closes off better futures,
     use DP instead.

3. NO UNDO NEEDED?
   Greedy commits — you cannot take back a choice.
   → If you might need to revisit choices, use DP or backtracking.

4. CAN YOU SORT THE INPUT?
   Most greedy problems begin with sorting by some key criterion.
   → Finding what to sort by is often 80% of the problem.
```

---

## 2. Pattern 1 — Interval Scheduling (Maximize Non-Overlapping Events)

### When to Use

- "What is the maximum number of non-overlapping intervals you can attend?"
- "Select the most meetings/events possible"
- "Remove minimum intervals to make the rest non-overlapping"

### Recognition Signals

```
"maximum number of non-overlapping"    → sort by END time
"maximum events you can attend"        → sort by END time
"minimum intervals to remove"          → count overlaps after sorting by END time
"activity selection"                   → sort by END time
```

### Why Sort by END Time (Not Start Time)?

```
Intuition: By always choosing the activity that FINISHES EARLIEST, we leave
the maximum possible "room" for future activities.

Counterexample: Why sorting by START TIME fails:
  Intervals: [(1,10), (2,3), (4,5)]
  Sorted by start: [(1,10), (2,3), (4,5)]
  Greedy picks (1,10) first. Now both (2,3) and (4,5) are blocked.
  Result: 1 interval. WRONG.

  Sorted by END:   [(2,3), (4,5), (1,10)]
  Greedy picks (2,3), then (4,5). (1,10) overlaps, skip.
  Result: 2 intervals. CORRECT.

Exchange argument proof:
  Suppose optimal solution picks interval X instead of greedy's choice G
  where G finishes earlier. Swap X for G — G doesn't block anything X didn't
  block (since G ends earlier). The solution is no worse. Greedy is optimal.
```

### Template — Activity Selection

```python
def max_non_overlapping(intervals):
    """
    Returns maximum count of non-overlapping intervals.
    Sort by END time, greedily pick the one that ends soonest.
    """
    # Sort by end time — KEY insight
    intervals.sort(key=lambda x: x[1])

    count = 0
    last_end = float('-inf')       # end time of last chosen interval

    for start, end in intervals:
        if start >= last_end:      # no overlap with last chosen
            count += 1
            last_end = end         # update the "last chosen" end time

    return count

# Time: O(n log n)  |  Space: O(1)

# Variant: minimum intervals to remove = n - max_non_overlapping
def min_erase_overlap(intervals):
    return len(intervals) - max_non_overlapping(intervals)
```

---

## 3. Pattern 2 — Interval Merging

### When to Use

- "Merge all overlapping intervals into one"
- "Insert an interval and merge if needed"
- "Find all non-overlapping groups"

### Recognition Signals

```
"merge overlapping intervals"        → sort by START time, extend end
"insert interval"                    → insert, then merge
"covered intervals"                  → sort by start, track max end
```

### Why Sort by START Time Here?

```
To merge, you process intervals left to right.
You need to know which interval comes first (lowest start)
so you can decide if the next interval overlaps with the current merged one.

Contrast with scheduling:
  Scheduling: sort by END (to maximize future options)
  Merging:    sort by START (to process left to right and extend)
```

### Template — Merge Intervals

```python
def merge_intervals(intervals):
    """
    Merge all overlapping intervals.
    Sort by start, then greedily extend the current merged interval.
    """
    if not intervals:
        return []

    # Sort by START time
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0][:]]     # start with first interval (make a copy)

    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]

        if start <= last_end:           # overlap: extend current merged interval
            merged[-1][1] = max(last_end, end)
        else:                           # no overlap: start new interval
            merged.append([start, end])

    return merged

# Time: O(n log n)  |  Space: O(n)

# Example:
# Input:  [[1,3],[2,6],[8,10],[15,18]]
# After sort: [[1,3],[2,6],[8,10],[15,18]]
# Process [2,6]: overlaps [1,3] → merge to [1,6]
# Process [8,10]: no overlap → add [8,10]
# Process [15,18]: no overlap → add [15,18]
# Output: [[1,6],[8,10],[15,18]]
```

---

## 4. Pattern 3 — Jump Game

### When to Use

- "Can you reach the last index?"
- "What is the minimum number of jumps to reach the end?"

### Recognition Signals

```
"reach the end"                 → greedy max reach tracking
"minimum jumps"                 → greedy: jump at boundary
"coverage", "maximum reachable" → greedy max reach
```

### Template — Can You Reach the End? (Jump Game I)

```python
def can_jump(nums):
    """
    Each element = maximum jump length from that position.
    Can you reach the last index?

    Greedy: track the furthest reachable position.
    If current index exceeds it, we're stuck.
    """
    max_reach = 0

    for i, jump in enumerate(nums):
        if i > max_reach:
            return False            # can't even reach index i

        max_reach = max(max_reach, i + jump)

        if max_reach >= len(nums) - 1:
            return True             # can already reach the end

    return True

# Time: O(n)  |  Space: O(1)
```

### Template — Minimum Jumps (Jump Game II)

```python
def min_jumps(nums):
    """
    Minimum number of jumps to reach last index.
    Greedy: delay each jump as long as possible, always extend to farthest.

    KEY INSIGHT: Think of "jump windows".
    A window is [last_end+1, current_end].
    Process all positions in the window; find max farthest.
    When you hit current_end, you MUST jump — increment counter.
    """
    jumps = 0
    current_end = 0       # end of the current jump window
    farthest = 0          # farthest position reachable from this window

    # Don't need to process last index (we're trying to reach it, not jump from it)
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])   # extend farthest from position i

        if i == current_end:      # exhausted current window — must jump
            jumps += 1
            current_end = farthest

    return jumps

# Time: O(n)  |  Space: O(1)

# Trace: nums = [2,3,1,1,4]
# i=0: farthest=max(0,2)=2. i==current_end(0) → jump=1, current_end=2
# i=1: farthest=max(2,4)=4.
# i=2: farthest=max(4,3)=4. i==current_end(2) → jump=2, current_end=4
# i=3: farthest=max(4,4)=4.
# return jumps=2
```

---

## 5. Pattern 4 — Huffman / Minimum Cost Combining

### When to Use

- "Combine items with minimum total cost"
- "Each combination costs the sum of the two items"
- "Minimize total rope/stone/file combination cost"

### Recognition Signals

```
"minimum cost to combine/merge all"     → always merge two smallest (min-heap)
"connect ropes with minimum cost"       → min-heap Huffman pattern
"minimum cost to sort/arrange"          → Huffman-style
"merge stones / merge piles"            → greedy or DP depending on constraints
```

### Why Always Combine the Two Smallest?

```
When you merge two items of cost A and B, you pay A + B.
The resulting item (cost A+B) will be used in future merges, adding its cost again.

To minimize total, defer large costs as long as possible.
Combining the two smallest first → smallest items participate in fewer future merges.

Counterexample (combine largest first): ropes = [1, 2, 3]
  Combine 3+2=5: total cost so far = 5. Now ropes = [1, 5]
  Combine 5+1=6: total cost = 5+6 = 11. WRONG.

Correct (combine smallest first):
  Combine 1+2=3: total cost so far = 3. Now ropes = [3, 3]
  Combine 3+3=6: total cost = 3+6 = 9. CORRECT (minimum).
```

### Template — Minimum Cost to Connect Ropes

```python
import heapq

def min_cost_to_connect_ropes(ropes):
    """
    Combine all ropes into one. Cost = sum of lengths of two ropes combined.
    Minimize total cost.
    """
    heapq.heapify(ropes)           # build min-heap in O(n)
    total_cost = 0

    while len(ropes) > 1:
        # Always combine two smallest
        first = heapq.heappop(ropes)
        second = heapq.heappop(ropes)

        cost = first + second
        total_cost += cost

        heapq.heappush(ropes, cost)   # combined rope goes back in heap

    return total_cost

# Time: O(n log n)  |  Space: O(n)
```

---

## 6. Pattern 5 — Meeting Rooms / Minimum Resource Allocation

### When to Use

- "Minimum number of conference rooms / meeting rooms / CPUs needed"
- "Maximum concurrent tasks at any point"

### Recognition Signals

```
"minimum meeting rooms"              → sort by start + min-heap of ends
"minimum CPU/servers needed"         → sort by start + min-heap of ends
"maximum overlapping intervals"      → count with sweep line or heap
```

### Template — Meeting Rooms II (Minimum Rooms)

```python
import heapq

def min_meeting_rooms(intervals):
    """
    Minimum meeting rooms needed = maximum concurrent meetings at any time.

    Greedy: sort by start time.
    Use a min-heap of END times of ongoing meetings.
    If the earliest ending meeting ends before new meeting starts → reuse that room.
    Otherwise → need a new room.
    """
    if not intervals:
        return 0

    # Sort by start time
    intervals.sort(key=lambda x: x[0])
    heap = []                          # min-heap of end times (ongoing meetings)

    for start, end in intervals:
        # If the room that ends soonest is free before this meeting starts:
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)   # reuse that room (replace end time)
        else:
            heapq.heappush(heap, end)      # need a new room

    return len(heap)   # number of rooms = size of heap at end

# Time: O(n log n)  |  Space: O(n)

# WHY HEAP OF END TIMES?
# We always want to know: "is there any room currently free?"
# A room is free if its meeting ended before now.
# The MIN-HEAP gives us the EARLIEST ending meeting in O(log n).
# If even the earliest-ending meeting hasn't ended, all rooms are busy.
```

### Alternative — Sweep Line (More Intuitive)

```python
def min_meeting_rooms_sweep(intervals):
    """
    Sweep line: +1 at start, -1 at end.
    Peak value = maximum concurrent meetings.
    """
    events = []
    for start, end in intervals:
        events.append((start, 1))    # meeting starts: need a room
        events.append((end, -1))     # meeting ends: free a room

    # Sort by time; on tie, process END (-1) before START (+1)
    # This avoids counting [1,2] and [2,3] as overlapping
    events.sort(key=lambda x: (x[0], x[1]))

    rooms = 0
    max_rooms = 0
    for time, delta in events:
        rooms += delta
        max_rooms = max(max_rooms, rooms)

    return max_rooms
```

---

## 7. Pattern 6 — Task Scheduler

### When to Use

- "Minimum time to complete tasks with cooldown between same-type tasks"
- "Schedule tasks to minimize idle time"

### Recognition Signals

```
"cooldown", "cooling interval"          → task scheduler pattern
"same task must wait n slots"           → process highest freq first
"minimum intervals to execute tasks"    → max-heap by frequency
```

### Template — Task Scheduler

```python
from collections import Counter
import heapq
from collections import deque

def least_interval(tasks, n):
    """
    Tasks with same label must have n-slot cooldown between them.
    Minimum total slots (including idle) to complete all tasks.

    Greedy: always run the MOST FREQUENT available task.
    Use a max-heap (negate for Python's min-heap) to track frequencies.
    Use a cooldown queue to know when tasks become available again.
    """
    counts = Counter(tasks)
    max_heap = [-cnt for cnt in counts.values()]   # negate for max-heap behavior
    heapq.heapify(max_heap)

    cooldown_queue = deque()   # (negative_remaining_count, available_at_time)
    time = 0

    while max_heap or cooldown_queue:
        time += 1

        # Re-add tasks whose cooldown has expired
        if cooldown_queue and cooldown_queue[0][1] == time:
            _, _ = cooldown_queue[0]
            heapq.heappush(max_heap, cooldown_queue.popleft()[0])

        if max_heap:
            neg_cnt = heapq.heappop(max_heap)    # run most frequent available task
            if neg_cnt + 1 < 0:                  # still has remaining count
                cooldown_queue.append((neg_cnt + 1, time + n + 1))
        # If max_heap is empty, current slot is idle (time still increments)

    return time

# Time: O(t * n) where t = number of unique tasks  |  Space: O(t)
```

### Mathematical Formula Approach (Interview Trick)

```python
def least_interval_formula(tasks, n):
    """
    Formula-based O(n) solution:
    - Let f = frequency of most frequent task.
    - Let count_max = number of tasks with that maximum frequency.
    - Answer = max(len(tasks), (f-1) * (n+1) + count_max)

    Intuition: arrange most frequent task into blocks of size (n+1).
    (f-1) full blocks + 1 last block with count_max tasks.
    If we have enough other tasks to fill the gaps, no idle needed.
    """
    counts = Counter(tasks)
    f = max(counts.values())
    count_max = sum(1 for v in counts.values() if v == f)

    return max(len(tasks), (f - 1) * (n + 1) + count_max)
```

---

## 8. Greedy vs DP — Decision Guide

### When Greedy Works (Local Optimal = Global Optimal)

```
GREEDY WORKS WHEN:
  1. Greedy choice property: the locally best choice is part of some global optimum.
  2. Optimal substructure: optimal solution built from optimal sub-solutions.

Classic greedy-safe problems:
  - Activity selection (sort by end time)
  - Fractional knapsack (sort by value/weight)
  - Huffman coding (merge smallest)
  - Dijkstra (always process closest unvisited node)
```

### When Greedy Fails — Use DP

```
GREEDY FAILS WHEN:
  Making a locally greedy choice blocks a better global path.

Classic counterexample: COIN CHANGE with non-standard denominations

Coins: [1, 3, 4], target = 6

Greedy (pick largest coin that fits):
  Pick 4 → remaining = 2
  Pick 1 → remaining = 1
  Pick 1 → remaining = 0
  Result: 3 coins [4, 1, 1]

DP (optimal):
  6 = 3 + 3
  Result: 2 coins [3, 3]

WHY GREEDY FAILS: Choosing 4 "seemed right" locally, but blocked the
2-coin solution. The sub-problem after choosing 4 has a worse answer.

RULE: If denominations are arbitrary (not always divisible/structured),
      use DP. Standard denominations (1, 5, 10, 25) are greedy-safe
      due to the "greedy stays ahead" property.
```

### Decision Table

| Problem Type | Greedy? | Reason |
|--------------|---------|--------|
| Activity selection (max non-overlapping) | YES | Exchange argument holds |
| Fractional knapsack | YES | Can always take best ratio |
| 0/1 knapsack | NO | Must consider all subsets |
| Coin change (standard denominations) | YES | Coins divide each other |
| Coin change (arbitrary denominations) | NO | Local choice can block optimal |
| Shortest path (non-negative weights) | YES | Dijkstra |
| Shortest path (negative weights) | NO | Bellman-Ford needed |
| Minimum spanning tree | YES | Greedy choice property proven |
| Longest increasing subsequence | NO | Need all previous states |
| Task scheduler with cooldown | YES | Most frequent first is optimal |

```
QUICK TEST: Try a small counterexample.
  If greedy fails on your small test → use DP.
  If greedy works on several tests → try to sketch an exchange argument.
```

---

## 9. Problem → Pattern Decision Table

| Problem | Sort By | Data Structure | Pattern |
|---------|---------|----------------|---------|
| Max non-overlapping intervals | End time | None | Activity selection |
| Merge overlapping intervals | Start time | None | Extend current |
| Min meeting rooms | Start time | Min-heap of ends | Resource allocation |
| Can reach end of array | N/A | max_reach variable | Jump game I |
| Min jumps to end | N/A | current_end, farthest | Jump game II |
| Connect ropes (min cost) | N/A | Min-heap | Huffman pattern |
| Task scheduler (min time) | N/A | Max-heap + cooldown queue | Task scheduler |
| Minimum platforms needed | Start & end events | N/A | Sweep line |
| Fractional knapsack | Value/weight ratio DESC | N/A | Greedy ratio |

---

## 10. Common Interview Signals → Pattern Mapping

```
INTERVIEW SAYS                                YOU THINK
------------------------------------------------------------------------
"maximum events/activities you can attend"  → activity selection, sort by END
"merge all overlapping intervals"           → merge intervals, sort by START
"minimum rooms/resources needed"            → meeting rooms, min-heap of ends
"can you reach the last position"           → jump game I, max_reach greedy
"minimum jumps to reach end"               → jump game II, jump at boundary
"minimum cost to combine/merge all items"  → Huffman, always merge smallest two
"task cooldown, minimize total time"       → task scheduler, max-heap by freq
"arbitrary coin denominations"             → DP (not greedy)
"standard coin denominations"             → greedy works
"maximize value with weight limit"         → if fractional: greedy; if 0/1: DP
```
