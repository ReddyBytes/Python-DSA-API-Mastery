# Greedy Algorithms — The Impatient Optimizer

---

## The Buffet Strategy

You're at an all-you-can-eat buffet. You're hungry. You have a strategy:

**Greedy strategy:** At every moment, eat the most delicious-looking dish right in front of you.
Don't plan ahead. Don't think about what's coming. Just take the best option available *right now*.

Sometimes this works brilliantly. Sometimes it backfires spectacularly.

That's greedy algorithms in a nutshell.

```
Situation:  [Pizza] [Tiny Salad] [Massive Steak]
Greedy:      Skip pizza, skip salad, grab the steak immediately.

Works great when the steak really IS the best choice.
Fails when the steak is salty and ruins your appetite for the incredible dessert coming next.
```

The key question in any greedy problem: **"Is the locally best choice always safe?"**
If yes: greedy is elegant and fast. If no: you need dynamic programming.

---

## Why Greedy Sometimes Works: "Greedy Stays Ahead"

The formal intuition is called the "greedy stays ahead" argument.

Imagine a race between two runners:
- **Greedy runner**: always sprints ahead as fast as possible right now
- **Optimal runner**: plans the perfect pacing strategy

If you can prove that after every single step, the greedy runner is NEVER behind the optimal runner —
then the greedy runner wins (or ties). That's the proof technique.

For problems where greedy works, the local best choice never "locks you out" of a better global solution.
Let's see this in action.

---

## Problem 1: Activity Selection

You have a meeting room. Several teams want to book it. You want to fit the MAXIMUM number of meetings.

Here are 6 meetings (start time → end time):

```
Meeting A:  |====|                    starts 1, ends 4
Meeting B:       |========|           starts 3, ends 8
Meeting C:              |====|        starts 6, ends 9
Meeting D:   |===|                    starts 2, ends 5
Meeting E:                  |====|    starts 8, ends 11
Meeting F:        |=|                 starts 4, ends 6

Timeline:  1  2  3  4  5  6  7  8  9 10 11
           |--A--|
              |--D--|
                 |------B------|
                    |--F--|
                          |--C--|
                             |---E---|
```

### Wrong Approach: Sort by Start Time

"Pick the meeting that starts earliest!" Sounds logical. But:

```
Pick A (starts at 1): occupies 1-4
Next earliest start is D (starts at 2): BLOCKED by A
Next is B (starts at 3): BLOCKED by A
Next is F (starts at 4): pick it, occupies 4-6
Next is C (starts at 6): pick it, occupies 6-9
Next is E (starts at 8): BLOCKED by C

Result: A, F, C = 3 meetings
```

### Correct Approach: Sort by END Time

"Pick the meeting that ENDS earliest!" This frees up the room as soon as possible.

```
Sort by end time:
  A: ends 4
  D: ends 5
  F: ends 6
  B: ends 8
  C: ends 9
  E: ends 11
```

Now trace through:

```
Step 1: Pick A (ends at 4). Room busy until 4.
        ✓ A selected. Last end time = 4.

Step 2: D starts at 2. 2 < 4, OVERLAPS with A. Skip D.

Step 3: F starts at 4. 4 >= 4, no overlap. Pick F!
        ✓ F selected. Last end time = 6.

Step 4: B starts at 3. 3 < 6, overlaps. Skip B.

Step 5: C starts at 6. 6 >= 6, no overlap. Pick C!
        ✓ C selected. Last end time = 9.

Step 6: E starts at 8. 8 < 9, overlaps. Skip E.

Result: A, F, C = 3 meetings
```

Hmm, same count here. Let's try a case where it makes a real difference:

```
  Short+early:  |=|            ends at 2    ← greedy picks this
  Long+early:   |==========|   ends at 10
  Short+late:          |=|     ends at 8    ← then this
```

Sorting by start time might grab the long meeting and block two short ones.
Sorting by end time grabs the two short ones. More meetings = better answer.

**Why "earliest end time" works:**
By picking the meeting that ends earliest, we leave the maximum remaining time for future meetings.
No other strategy can do better — any swap would either tie or lose.

---

## Problem 2: Merge Intervals

Different goal: you don't want to pick the max meetings. You want to **merge** all overlapping intervals
into the smallest possible set of non-overlapping ranges.

Input intervals: `[1,4], [3,6], [5,8], [10,12], [11,14]`

```
[1,4]:   |====|
[3,6]:      |====|
[5,8]:          |====|
[10,12]:               |====|
[11,14]:                  |=====|

Timeline: 1  2  3  4  5  6  7  8  9 10 11 12 13 14
```

**Strategy: Sort by start time, then greedily merge.**

```
Sort by start: [1,4], [3,6], [5,8], [10,12], [11,14]

Start with [1,4]. Current merged = [1,4].

[3,6]: starts at 3. 3 <= 4 (current end). Overlaps!
       Merge: extend end to max(4,6) = 6. Current = [1,6].

[5,8]: starts at 5. 5 <= 6 (current end). Overlaps!
       Merge: extend end to max(6,8) = 8. Current = [1,8].

[10,12]: starts at 10. 10 > 8. No overlap. Save [1,8], start new: [10,12].

[11,14]: starts at 11. 11 <= 12 (current end). Overlaps!
         Merge: extend end to max(12,14) = 14. Current = [10,14].

Done! Final: save [10,14].
```

**Result: [1,8] and [10,14]**

```
Before merging:                    After merging:
[1,4]:   |====|                    [1,8]:   |========|
[3,6]:      |====|                 [10,14]:              |=======|
[5,8]:          |====|
[10,12]:               |====|
[11,14]:                  |=====|
```

### Activity Selection vs Merge Intervals — Same Data, Different Goals

```
Activity Selection:   "Which intervals can I pick so NONE overlap?" → maximize count
Merge Intervals:      "Combine all overlapping intervals"           → minimize count

Same problem of overlapping ranges. Completely different algorithms. Different greedy choices.
```

---

## Problem 3: Jump Game

You're playing a board game. Each tile tells you the maximum number of steps you can jump forward.

```
Board: [2, 3, 1, 1, 4]
Index:  0  1  2  3  4

At index 0: can jump up to 2 steps (reach index 1 or 2)
At index 1: can jump up to 3 steps (reach index 2, 3, or 4)
At index 2: can jump up to 1 step  (reach index 3)
At index 3: can jump up to 1 step  (reach index 4)
At index 4: you're at the last tile — WIN!
```

**Goal:** Can you reach the last tile?

**Greedy insight:** Track the farthest position you CAN reach at any moment.

```
Start: max_reach = 0 (you're at index 0)

Index 0: value = 2. Can reach index 0+2 = 2.
         max_reach = max(0, 0+2) = 2
         Current index (0) <= max_reach (2). Still alive!

Index 1: value = 3. Can reach index 1+3 = 4.
         max_reach = max(2, 1+3) = 4
         Current index (1) <= max_reach (4). Still alive!

Index 2: value = 1. Can reach index 2+1 = 3.
         max_reach = max(4, 2+1) = 4   (no improvement)
         Current index (2) <= max_reach (4). Still alive!

Index 3: value = 1. Can reach index 3+1 = 4.
         max_reach = max(4, 3+1) = 4   (no improvement)
         Current index (3) <= max_reach (4). Still alive!

Index 4: We reached index 4 = last index. WIN!
```

**The trick:** You don't track which specific jumps you made. You just track the frontier:
"what's the farthest position reachable from anywhere we've been so far?"

If you ever reach a tile where your current index > max_reach, you're stuck. Game over.

```
Failing example: [3, 2, 1, 0, 4]

Index 0: val=3, max_reach = max(0, 0+3) = 3
Index 1: val=2, max_reach = max(3, 1+2) = 3
Index 2: val=1, max_reach = max(3, 2+1) = 3
Index 3: val=0, max_reach = max(3, 3+0) = 3
Index 4: current=4 > max_reach=3. STUCK! Cannot reach end.
```

---

## When Greedy FAILS: The Coin Change Trap

This is important. Greedy is seductive — it always feels right. But it can mislead you.

**Problem:** Make change for amount = 6, using coins [1, 3, 4].

**Greedy approach:** Always pick the largest coin that fits.

```
Amount = 6
Largest coin ≤ 6: pick 4. Remaining: 6 - 4 = 2.
Largest coin ≤ 2: pick 1. Remaining: 2 - 1 = 1.
Largest coin ≤ 1: pick 1. Remaining: 1 - 1 = 0.

Greedy answer: [4, 1, 1] = 3 coins
```

**Optimal answer:** [3, 3] = 2 coins

Greedy used 3 coins. Optimal uses 2 coins. Greedy was WRONG.

**Why did greedy fail?**

```
Greedy choice: "4 is the biggest coin, take it first"

But taking 4 forces you to make up 2 with small coins (1+1).
If you skip 4 and take 3 instead, the remaining 3 is perfectly a single coin.

The "locally best" choice (biggest coin) blocked the "globally best" path.
```

```
Greedy path:     6 → [take 4] → 2 → [take 1] → 1 → [take 1] → 0   (3 coins)
                                                                     ✗ NOT optimal
Optimal path:    6 → [take 3] → 3 → [take 3] → 0                   (2 coins)
                                                                     ✓ OPTIMAL
```

**The rule of thumb:**
- Greedy works when picking the locally best option never eliminates a better global option
- Greedy fails when a local choice closes off paths that lead to a better answer
- When greedy fails → consider **Dynamic Programming** (which explores ALL options)

---

## The Greedy Decision Flowchart

```
Does the problem ask for maximum/minimum of something?
    │
    ▼
Can you sort the input and make a local decision at each step?
    │
    ▼
Can you prove that this local choice never "locks you out" of a better solution?
    │
    ├── YES → Greedy! Clean, O(n log n) or O(n)
    │
    └── MAYBE → Test with examples.
        If greedy fails on a simple case → Dynamic Programming.
```

---

## Quick Code Reference

```python
# Activity Selection
def max_activities(intervals):
    intervals.sort(key=lambda x: x[1])  # sort by end time
    count = 1
    last_end = intervals[0][1]
    for start, end in intervals[1:]:
        if start >= last_end:           # no overlap
            count += 1
            last_end = end
    return count

# Merge Intervals
def merge_intervals(intervals):
    intervals.sort(key=lambda x: x[0])  # sort by start time
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:       # overlaps
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged

# Jump Game
def can_jump(nums):
    max_reach = 0
    for i, val in enumerate(nums):
        if i > max_reach:
            return False                 # stuck
        max_reach = max(max_reach, i + val)
    return True
```

---

## The One-Sentence Summary

Greedy algorithms make the locally best choice at every step — blindingly fast and elegant when
the local optimum leads to a global optimum, but dangerously wrong when it doesn't.
Always test greedy on a few examples before trusting it.
