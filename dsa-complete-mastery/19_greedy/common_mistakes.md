# Greedy — Common Mistakes & Error Prevention

---

## Mistake 1: Applying Greedy to a Non-Greedy Problem

### The Bug
Greedy works only when the "locally optimal choice at each step" provably leads to
a globally optimal solution. For the coin change problem, greedy works on standard
denominations (1, 5, 10, 25) because each coin is a multiple of smaller ones.
It FAILS on arbitrary denominations where coins don't divide evenly into each other.

### Wrong Code
```python
def coin_change_greedy_wrong(coins, amount):
    """Greedy: always pick the largest coin that fits."""
    coins_sorted = sorted(coins, reverse=True)
    count = 0
    for coin in coins_sorted:
        while amount >= coin:
            amount -= coin
            count += 1
    if amount != 0:
        return -1   # cannot make exact change
    return count
```

### Correct Code — Dynamic Programming
```python
def coin_change_dp_correct(coins, amount):
    """DP: find minimum coins for every sub-amount from 0 to amount."""
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] + 1 < dp[i]:
                dp[i] = dp[i - coin] + 1

    return dp[amount] if dp[amount] != float('inf') else -1
```

### Counterexample That Exposes the Bug
```
Coins: [1, 3, 4], Amount: 6

Greedy approach:
  Pick 4 (largest that fits): remaining = 2
  Pick 1: remaining = 1
  Pick 1: remaining = 0
  Total: 3 coins (4 + 1 + 1)

Optimal approach (DP):
  3 + 3 = 6
  Total: 2 coins

Greedy gives 3 coins. Optimal is 2 coins. Greedy is WRONG here.
```

### Test Cases That Expose the Bug
```python
# Counterexample: coins [1, 3, 4], amount 6
coins = [1, 3, 4]
amount = 6

greedy_result = coin_change_greedy_wrong(coins, amount)
dp_result = coin_change_dp_correct(coins, amount)

print(f"Greedy: {greedy_result} coins")   # 3 (wrong)
print(f"DP:     {dp_result} coins")       # 2 (correct)

assert greedy_result != dp_result, "This case should expose the greedy bug"
assert dp_result == 2, f"Optimal is 2 coins (3+3), got {dp_result}"

# Standard US coins: greedy DOES work here
us_coins = [1, 5, 10, 25]
assert coin_change_greedy_wrong(us_coins, 30) == coin_change_dp_correct(us_coins, 30)
assert coin_change_dp_correct(us_coins, 30) == 2   # 25 + 5

# Another failing case: coins [1, 5, 6, 9], amount 11
coins2 = [1, 5, 6, 9]
greedy2 = coin_change_greedy_wrong(coins2, 11)  # 9+1+1 = 3 coins
dp2 = coin_change_dp_correct(coins2, 11)        # 5+6 = 2 coins
print(f"coins=[1,5,6,9], amount=11 -> greedy={greedy2}, dp={dp2}")
assert dp2 < greedy2, "DP should find fewer coins than greedy"
print("Coin change greedy-vs-DP test passed")
```

### When Greedy IS Safe for Coin Change
```
Greedy works when each denomination divides evenly into the next larger one.
Examples where greedy works: [1, 5, 10, 25], [1, 2, 5, 10], [1, 10, 100]
Examples where greedy fails: [1, 3, 4], [1, 5, 6, 9], [2, 5, 10] (can't make 1)

Rule of thumb: if you can't prove the greedy property with an exchange argument,
use DP.
```

---

## Mistake 2: Wrong Sort Order for Interval Problems

### The Bug
Different interval problems require different sort keys. Using the wrong sort order
produces incorrect results silently — the algorithm runs without errors but gives
a wrong answer.

### Problem 1: Interval Scheduling (Maximize Count of Non-Overlapping Intervals)
```
Sort by END TIME (not start time).
Rationale: finishing earliest leaves the most room for future intervals.
```

### Wrong Code for Interval Scheduling
```python
def interval_scheduling_wrong(intervals):
    """Maximize number of non-overlapping intervals."""
    # BUG: sorting by start time, not end time
    intervals.sort(key=lambda x: x[0])

    count = 1
    last_end = intervals[0][1]
    for start, end in intervals[1:]:
        if start >= last_end:
            count += 1
            last_end = end
    return count
```

### Correct Code for Interval Scheduling
```python
def interval_scheduling_correct(intervals):
    """Maximize number of non-overlapping intervals — sort by END time."""
    intervals.sort(key=lambda x: x[1])   # sort by END

    count = 1
    last_end = intervals[0][1]
    for start, end in intervals[1:]:
        if start >= last_end:
            count += 1
            last_end = end
    return count
```

### Problem 2: Interval Merging (Merge All Overlapping Intervals)
```
Sort by START TIME.
Rationale: to detect overlaps, consecutive intervals must be in start-time order.
```

### Correct Code for Interval Merging
```python
def merge_intervals(intervals):
    """Merge overlapping intervals — sort by START time."""
    intervals.sort(key=lambda x: x[0])   # sort by START

    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)   # extend the current interval
        else:
            merged.append([start, end])
    return merged
```

### Problem 3: Meeting Rooms II (Minimum Rooms Needed)
```
Sort by START TIME, use a min-heap for end times.
Rationale: process meetings in the order they start; the heap tracks the earliest
           room that becomes free.
```

### Correct Code for Meeting Rooms II
```python
import heapq

def min_meeting_rooms(intervals):
    """Minimum rooms for all meetings — sort by START time."""
    intervals.sort(key=lambda x: x[0])   # sort by START

    rooms = []   # min-heap of end times
    for start, end in intervals:
        if rooms and rooms[0] <= start:
            heapq.heapreplace(rooms, end)   # reuse the earliest-ending room
        else:
            heapq.heappush(rooms, end)      # need a new room

    return len(rooms)
```

### Test Cases That Expose Wrong Sort for Interval Scheduling
```python
# Interval scheduling: sort-by-start gives wrong answer
intervals = [[1, 10], [2, 3], [4, 5], [6, 7]]
# Sorted by start: [1,10], [2,3], [4,5], [6,7]
# Wrong (sort by start): [1,10] is chosen first, blocks everything -> count = 1
# Correct (sort by end): [2,3], [4,5], [6,7] -> count = 3

wrong_count = interval_scheduling_wrong(intervals)
correct_count = interval_scheduling_correct(intervals)

print(f"Scheduling wrong (sort by start): {wrong_count}")   # 1
print(f"Scheduling correct (sort by end): {correct_count}") # 3
assert wrong_count == 1, "Wrong sort gives only 1 interval (greedy picks [1,10])"
assert correct_count == 3, f"Expected 3, got {correct_count}"

# Merging
intervals2 = [[1, 3], [2, 6], [8, 10], [15, 18]]
merged = merge_intervals([list(i) for i in intervals2])
assert merged == [[1, 6], [8, 10], [15, 18]], f"Got {merged}"

# Meeting rooms
intervals3 = [[0, 30], [5, 10], [15, 20]]
rooms = min_meeting_rooms(intervals3)
assert rooms == 2, f"Expected 2 rooms, got {rooms}"
print("All interval sort-order tests passed")
```

### Sort Order Cheat Sheet
```
Problem                             Sort by     Why
-----------------------------------------------------------------------
Maximize non-overlapping intervals  END time    Earliest finish = most room left
Merge overlapping intervals         START time  Detect consecutive overlaps
Minimum rooms (meeting rooms)       START time  Process in arrival order
Task scheduling (earliest deadline) DEADLINE    Classic EDF scheduling
```

---

## Mistake 3: Minimum Number of Platforms — Mixing Arrivals and Departures

### The Bug
The sweep-line approach for "minimum platforms needed" requires TWO separately
sorted arrays: arrivals and departures. If you sort combined events as tuples,
a departure at time T and an arrival at time T might be processed in the wrong
order, giving an off-by-one result on the platform count.

### Wrong Code
```python
def min_platforms_wrong(arrivals, departures):
    """BUG: treats simultaneous arrival and departure incorrectly."""
    events = []
    for a in arrivals:
        events.append((a, 'arrival'))
    for d in departures:
        events.append((d, 'departure'))

    # BUG: when arrival and departure have the same time, the sort order
    # of 'arrival' vs 'departure' is alphabetical: 'arrival' < 'departure'
    # This means an arrival at time T is processed BEFORE a departure at T,
    # making it appear we need an extra platform even though one just freed up.
    events.sort()

    platforms = 0
    max_platforms = 0
    for _, event_type in events:
        if event_type == 'arrival':
            platforms += 1
            max_platforms = max(max_platforms, platforms)
        else:
            platforms -= 1

    return max_platforms
```

### Correct Code — Separate Sorted Arrays
```python
def min_platforms_correct(arrivals, departures):
    """Sort arrivals and departures separately. Two-pointer sweep."""
    arr = sorted(arrivals)
    dep = sorted(departures)

    platforms = 0
    max_platforms = 0
    i = 0   # pointer into arrivals
    j = 0   # pointer into departures

    while i < len(arr):
        if arr[i] <= dep[j]:
            # A train arrives before the earliest-departing train leaves
            platforms += 1
            max_platforms = max(max_platforms, platforms)
            i += 1
        else:
            # The earliest departure frees a platform before next arrival
            platforms -= 1
            j += 1

    return max_platforms
```

### Why `arr[i] <= dep[j]` Uses <=
```
If a train arrives at the same time another departs, the arriving train CAN use
the platform the departing train just vacated. So <= means "arrival is not after
departure" — we count it as the departing train leaving first, then the arriving
train taking that platform. Using < instead of <= would count simultaneous events
as needing an extra platform.
```

### Test Cases That Expose the Bug
```python
# Case where simultaneous arrival/departure matters
arrivals = [900, 940, 950, 1100, 1500, 1800]
departures = [910, 1200, 1120, 1130, 1900, 2000]

wrong = min_platforms_wrong(arrivals, departures)
correct = min_platforms_correct(arrivals, departures)

print(f"Wrong platform count:   {wrong}")
print(f"Correct platform count: {correct}")
assert correct == 3, f"Expected 3 platforms, got {correct}"

# Simultaneous arrival and departure — should NOT require extra platform
arrivals2 = [800, 900]
departures2 = [900, 1000]   # train at 800 departs at 900, new train arrives at 900
correct2 = min_platforms_correct(arrivals2, departures2)
assert correct2 == 1, f"Should need only 1 platform (departure frees before arrival), got {correct2}"

# All trains at same time — need as many platforms as trains
arrivals3 = [100, 100, 100]
departures3 = [200, 200, 200]
assert min_platforms_correct(arrivals3, departures3) == 3
print("All platform tests passed")
```

---

## Mistake 4: Jump Game — Off-by-One in the Loop Guard

### The Bug
In the Jump Game (can you reach the last index?), the loop must stop when `i`
exceeds `max_reach`. If you check `max_reach` only inside the loop body, not
as the loop's exit condition, you continue processing unreachable indices —
the "stuck" indices that have jump length 0 — and `max_reach` never gets updated
past the stuck zone, but you don't know to stop.

### Wrong Code
```python
def can_jump_wrong(nums):
    max_reach = 0
    n = len(nums)

    for i in range(n):            # BUG: iterates over ALL indices including
        max_reach = max(max_reach, i + nums[i])  # unreachable ones

    return max_reach >= n - 1
    # This actually gives the right answer here by luck, but:
```

### Wrong Code — More Subtle Bug
```python
def can_jump_wrong_v2(nums):
    max_reach = 0
    n = len(nums)

    for i in range(n - 1):        # BUG: processes unreachable indices
        if i > max_reach:
            return False           # correctly catches this...
        max_reach = max(max_reach, i + nums[i])
        # ...but the check is AFTER the update on some iterations
        # depending on structure, this can give wrong "True" for some inputs

    return True                   # BUG: doesn't check if n-1 is reachable
```

### Correct Code
```python
def can_jump_correct(nums):
    max_reach = 0
    n = len(nums)

    for i in range(n):
        if i > max_reach:
            # We cannot even REACH index i -- everything beyond is also unreachable
            return False
        max_reach = max(max_reach, i + nums[i])

    return True   # all indices 0..n-1 were reachable
```

### Correct Code — Jump Game II (Minimum Jumps)
```python
def jump_min_jumps(nums):
    """Minimum number of jumps to reach the last index."""
    n = len(nums)
    jumps = 0
    current_end = 0    # furthest index reachable with `jumps` jumps
    farthest = 0       # furthest index reachable with `jumps+1` jumps

    for i in range(n - 1):    # don't need to jump FROM the last index
        farthest = max(farthest, i + nums[i])
        if i == current_end:
            # We've exhausted all positions reachable in `jumps` jumps
            # Must take one more jump
            jumps += 1
            current_end = farthest
            if current_end >= n - 1:
                break

    return jumps
```

### Test Cases That Expose the Bug
```python
# Standard case
assert can_jump_correct([2, 3, 1, 1, 4]) == True
assert can_jump_correct([3, 2, 1, 0, 4]) == False   # stuck at index 3

# Edge cases
assert can_jump_correct([0]) == True       # single element, already at end
assert can_jump_correct([1, 0]) == True    # jump from 0 to 1 (the end)
assert can_jump_correct([0, 1]) == False   # stuck at 0 immediately

# Subtle case: [2, 0, 0] -- can reach index 2 (jump 2 from index 0)
assert can_jump_correct([2, 0, 0]) == True

# Jump Game II
assert jump_min_jumps([2, 3, 1, 1, 4]) == 2  # 0->1->4
assert jump_min_jumps([2, 3, 0, 1, 4]) == 2  # 0->1->4
assert jump_min_jumps([1, 2, 3]) == 2         # 0->1->2 or 0->1->3

print("All Jump Game tests passed")
```

### The Critical Invariant
```
At every index i, BEFORE updating max_reach, check: can we even be at i?
  if i > max_reach: return False   -- i is unreachable

Only update max_reach if we are at a reachable index.
If you update max_reach for unreachable indices, you get false positives.
```

---

## Mistake 5: Activity Selection — Choosing the Wrong Greedy Property

### The Bug
The activity selection problem asks: "select the maximum number of non-overlapping
activities." The correct greedy choice is to always select the activity with the
EARLIEST FINISH TIME. Selecting the shortest duration or earliest start time is
incorrect and fails on simple counterexamples.

### Wrong Code — Greedy by Shortest Duration
```python
def activity_selection_wrong_duration(activities):
    """BUG: selects shortest-duration activities first."""
    # activities = [(start, end), ...]
    activities.sort(key=lambda x: x[1] - x[0])   # sort by duration

    selected = []
    last_end = float('-inf')
    for start, end in activities:
        if start >= last_end:
            selected.append((start, end))
            last_end = end
    return selected
```

### Wrong Code — Greedy by Earliest Start Time
```python
def activity_selection_wrong_start(activities):
    """BUG: selects earliest-starting activities first."""
    activities.sort(key=lambda x: x[0])   # sort by start

    selected = []
    last_end = float('-inf')
    for start, end in activities:
        if start >= last_end:
            selected.append((start, end))
            last_end = end
    return selected
```

### Correct Code — Greedy by Earliest Finish Time
```python
def activity_selection_correct(activities):
    """Correct: select activity with earliest finish time at each step."""
    activities.sort(key=lambda x: x[1])   # sort by END time

    selected = []
    last_end = float('-inf')
    for start, end in activities:
        if start >= last_end:
            selected.append((start, end))
            last_end = end
    return selected
```

### Why Earliest Finish Time Is Correct
```
Claim: choosing the activity with the earliest finish time is always part of
       some optimal solution.

Proof sketch (exchange argument):
  Suppose the optimal solution does NOT include activity A (earliest finish).
  Let B be the first activity in the optimal solution.
  Since A finishes no later than B, we can replace B with A in the optimal
  solution without causing any conflicts. The solution remains valid and
  has the same number of activities. Contradiction with "optimal doesn't include A."

Therefore, A (earliest finish) is always a safe greedy choice.
```

### Counterexamples That Expose Wrong Greedy Choices
```python
# Counterexample for "shortest duration" greedy:
# Activities: [1,10], [2,3], [9,11]
# Durations:     9      1      2
#
# Shortest-duration greedy:
#   Pick [2,3] (duration 1), last_end = 3
#   [9,11] (duration 2): 9 >= 3, pick it. last_end = 11
#   Count: 2
#
# Earliest-finish greedy:
#   Pick [2,3] (ends at 3), last_end = 3
#   [9,11] (starts at 9 >= 3), pick it. last_end = 11
#   Count: 2
# (Same here, need a stronger counterexample)

# Stronger counterexample for "shortest duration" greedy:
# Activities: [1,5], [4,6], [5,8], [2,3]
# Durations:    4      2      3      1
#
# Sorted by duration: [2,3](d=1), [4,6](d=2), [5,8](d=3), [1,5](d=4)
# Shortest-duration: [2,3], then [4,6] (4>=3), then [5,8] skipped (5<6), then skip
# Count: 2 selected
#
# Sorted by end time: [2,3](e=3), [1,5](e=5), [4,6](e=6), [5,8](e=8)
# Earliest-finish: [2,3], [4,6] (4>=3), [5,8] (5<6? no, 5<6, skip)
# Count: 2 selected
# (Equal here -- need different example)

# Clear counterexample for start-time greedy:
activities_start_test = [(0, 100), (1, 2), (3, 4)]
# Sorted by start: (0,100), (1,2), (3,4)
# Start-greedy: picks (0,100) first, then (1,2) start < 100, skip, (3,4) start < 100, skip
# Count: 1

wrong_start = activity_selection_wrong_start(activities_start_test)
correct = activity_selection_correct(activities_start_test)

print(f"Wrong (sort by start): {wrong_start} -> {len(wrong_start)} activities")
print(f"Correct (sort by end): {correct} -> {len(correct)} activities")

assert len(wrong_start) == 1, f"Start-greedy gets 1"
assert len(correct) == 3, f"Optimal is 3 non-overlapping activities, got {len(correct)}"

# Verify correctness: no two selected activities overlap
def no_overlaps(activities):
    for i in range(len(activities) - 1):
        if activities[i][1] > activities[i+1][0]:
            return False
    return True

assert no_overlaps(correct)
print("Activity selection test passed")
```

### Summary of Greedy Choices
```
Problem                       WRONG choice           CORRECT choice
----------------------------------------------------------------------
Max non-overlapping intervals  Shortest duration      Earliest finish time
Max non-overlapping intervals  Earliest start time    Earliest finish time
Minimum coins                  Largest coin           DP (no greedy for arbitrary)
Jump Game                      Skip unreachable check Guard: if i > max_reach: stop
Min platforms                  Mixed event sort       Separate sorted arrivals/deps
```

---

## Quick Reference Summary

| Mistake | Root Cause | One-Line Fix |
|---|---|---|
| Greedy for arbitrary coin change | Greedy choice is not locally safe | Use DP for arbitrary denominations |
| Wrong sort order for intervals | Different problems need different keys | Schedule: sort by END; Merge: sort by START |
| Mixed event sort for platforms | Simultaneous events ordered wrong | Use two separate sorted arrays with two pointers |
| Jump Game off-by-one | Updating max_reach for unreachable index | Check `if i > max_reach: return False` FIRST |
| Activity selection by duration | Shortest duration is not greedy-safe | Sort by FINISH TIME, not duration or start time |
