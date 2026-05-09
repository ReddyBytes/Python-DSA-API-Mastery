<a id="top"></a>
# Greedy Algorithms — The Art of Smart Immediate Decisions

> Greedy means:
>
> "Take the best option right now."
>
> Without worrying too much about the future.

Greedy algorithms are fast.
But they are not always correct.

Understanding when greedy works
is one of the most important interview skills.

## 📖 Table of Contents

1. [The Greedy Choice — Why Local Beats Global](#1-the-greedy-choice)
  - [The Buffet Strategy](#visual-the-buffet-strategy)
2. [When Greedy Fails — The Knapsack Lesson](#2-when-greedy-fails)
  - [Greedy Stays Ahead](#visual-why-greedy-sometimes-works)
3. [What Is a Greedy Algorithm?](#3-what-is-a-greedy-algorithm)
4. [When Does Greedy Work?](#4-when-does-greedy-work)
  - [The Greedy Decision Flowchart](#visual-the-greedy-decision-flowchart)
5. [Classic Greedy Problems](#5-classic-greedy-problems)
  - [Activity Selection](#activity-selection)
  - [Merge Intervals](#merge-intervals)
  - [Minimum Number of Coins](#minimum-number-of-coins)
  - [Huffman Coding](#huffman-coding)
  - [Fractional Knapsack](#fractional-knapsack)
  - [Job Sequencing with Deadlines](#job-sequencing-with-deadlines)
  - [Jump Game](#visual-jump-game)
  - [Minimum Platforms — Sweep Line](#visual-minimum-platforms)
6. [Greedy vs Dynamic Programming](#6-greedy-vs-dynamic-programming)
  - [Sort Order Cheat Sheet](#visual-sort-order-cheat-sheet)
7. [How to Recognize Greedy Problems](#7-how-to-recognize-greedy-problems)
8. [Time Complexity](#8-time-complexity)
9. [Common Mistakes](#9-common-mistakes)
  - [Wrong vs Correct Greedy Choices](#visual-wrong-vs-correct-greedy-choices)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
greedy choice property · optimal substructure · when greedy is provably correct

**Should Learn** — Important for real projects, comes up regularly:
activity selection · coin change · fractional knapsack · interval problems

**Good to Know** — Useful in specific situations, not always tested:
greedy vs DP distinction · Huffman coding

**Reference** — Know it exists, look up syntax when needed:
job sequencing · graph-based greedy (Kruskal's/Prim's overview)

<a id="1-the-greedy-choice"></a>
# 1. The Greedy Choice — Why Local Beats Global

Felix is an event planner running a massive catered gala. At the dessert table, he sees cake pieces: small, medium, and large. Felix grabs the largest piece first without calculating how many guests still need dessert — that is a greedy choice. Sometimes this strategy fills everyone's plate perfectly; sometimes it leaves the last guests with nothing.

You have cake pieces:

Small, medium, large.

If you're hungry,
you might take the largest piece first.

That is greedy choice.

You don't calculate total calories later.
You just pick the biggest now.

Sometimes good.
Sometimes wrong.

<a id="visual-the-buffet-strategy"></a>
## Visual: The Buffet Strategy

You're at an all-you-can-eat buffet. You're hungry. You have a strategy:

**Greedy strategy:** At every moment, eat the most delicious-looking dish right in front of you.
Don't plan ahead. Don't think about what's coming. Just take the best option available *right now*.

Sometimes this works brilliantly. Sometimes it backfires spectacularly.

```
Situation:  [Pizza] [Tiny Salad] [Massive Steak]
Greedy:      Skip pizza, skip salad, grab the steak immediately.

Works great when the steak really IS the best choice.
Fails when the steak is salty and ruins your appetite for the incredible dessert coming next.
```

The key question in any greedy problem: **"Is the locally best choice always safe?"**
If yes: greedy is elegant and fast. If no: you need dynamic programming.

> [↑ Back to Top](#top)

<a id="2-when-greedy-fails"></a>
# 2. When Greedy Fails — The Knapsack Lesson

Felix is packing supplies for an outdoor wedding. His van has limited space, and he wants to maximize the total value of what he delivers. His greedy instinct says: load the single most expensive item first. But what if two medium-priced centerpieces together are worth more than one expensive ice sculpture? Felix learns the hard way — greedy does not always give the global optimum.

You have limited space.

You want maximum value.

Greedy idea:

Pick item with highest value first.

But what if:
Two medium items together give more value than one big item?

Greedy fails.

This shows:

Greedy doesn't always give global optimum.

<a id="visual-why-greedy-sometimes-works"></a>
## Visual: Why Greedy Sometimes Works — "Greedy Stays Ahead"

The formal intuition is called the "greedy stays ahead" argument.

Imagine a race between two runners:
- **Greedy runner**: always sprints ahead as fast as possible right now
- **Optimal runner**: plans the perfect pacing strategy

If you can prove that after every single step, the greedy runner is NEVER behind the optimal runner —
then the greedy runner wins (or ties). That's the proof technique.

For problems where greedy works, the local best choice never "locks you out" of a better global solution.

> [↑ Back to Top](#top)

<a id="3-what-is-a-greedy-algorithm"></a>
# 3. What Is a Greedy Algorithm?

Felix plans events one decision at a time. Once he books a vendor, he never calls them back to renegotiate. He picks the best available option at each step and moves forward — no backtracking, no second-guessing. That is exactly how a greedy algorithm operates.

A greedy algorithm:

- Makes locally optimal choice
- At each step
- Without revisiting previous decisions

It never backtracks.

> [↑ Back to Top](#top)

<a id="4-when-does-greedy-work"></a>
# 4. When Does Greedy Work?

Felix wonders: when can he trust his instinct to just pick the best option now? It works when two conditions hold — the greedy choice property (locally optimal leads to globally optimal) and optimal substructure (solving the remaining subproblem optimally still gives the overall optimum). Not all planning problems have these properties.

Greedy works when:

Problem has:

1. Greedy choice property
2. Optimal substructure

Greedy choice property means:

A local optimal choice leads to global optimal solution.

Not all problems have this.

<a id="visual-the-greedy-decision-flowchart"></a>
## Visual: The Greedy Decision Flowchart

```
Does the problem ask for maximum/minimum of something?
    |
    v
Can you sort the input and make a local decision at each step?
    |
    v
Can you prove that this local choice never "locks you out" of a better solution?
    |
    +-- YES -> Greedy! Clean, O(n log n) or O(n)
    |
    +-- MAYBE -> Test with examples.
        If greedy fails on a simple case -> Dynamic Programming.
```

> [↑ Back to Top](#top)

<a id="5-classic-greedy-problems"></a>
# 5. Classic Greedy Problems

Felix faces the ultimate test: a week of back-to-back events. Each event requires its own greedy strategy — scheduling meetings, budgeting coins, compressing guest lists, packing gift bags, assigning staff, and planning routes. These are the classic problems every event planner (and every interview candidate) must master.

> 📝 [Practice Q3-Q8 — Basic Problems](./practice.md#basic-q1q8) · [Practice Q9-Q20 — Intermediate Problems](./practice.md#intermediate-q9q20)

<a id="activity-selection"></a>
## Activity Selection

> 📝 [Practice Q3 — Max Meetings](./practice.md#q3-activity-selection--maximum-non-overlapping-meetings) · [Practice Q13 — Min Intervals to Remove](./practice.md#q13-minimum-intervals-to-remove-non-overlapping) · [Practice Q21 — Prove Correctness](./practice.md#q21-prove-activity-selection-correctness--exchange-argument)

You have activities with start/end times.

Goal:
Maximize number of non-overlapping activities.

Greedy rule:
Choose activity with earliest finish time.

Why it works?

Finishing early leaves more room for others.

Correct greedy logic.

## Visual: Activity Selection Step-by-Step

You have a meeting room. Several teams want to book it. You want to fit the MAXIMUM number of meetings.

Here are 6 meetings (start time -> end time):

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

**Wrong approach — sort by start time:**

```
Pick A (starts at 1): occupies 1-4
Next earliest start is D (starts at 2): BLOCKED by A
Next is B (starts at 3): BLOCKED by A
Next is F (starts at 4): pick it, occupies 4-6
Next is C (starts at 6): pick it, occupies 6-9
Next is E (starts at 8): BLOCKED by C

Result: A, F, C = 3 meetings
```

**Correct approach — sort by end time:**

```
Sort by end time:
  A: ends 4
  D: ends 5
  F: ends 6
  B: ends 8
  C: ends 9
  E: ends 11

Step 1: Pick A (ends at 4). Room busy until 4.
        A selected. Last end time = 4.

Step 2: D starts at 2. 2 < 4, OVERLAPS with A. Skip D.

Step 3: F starts at 4. 4 >= 4, no overlap. Pick F!
        F selected. Last end time = 6.

Step 4: B starts at 3. 3 < 6, overlaps. Skip B.

Step 5: C starts at 6. 6 >= 6, no overlap. Pick C!
        C selected. Last end time = 9.

Step 6: E starts at 8. 8 < 9, overlaps. Skip E.

Result: A, F, C = 3 meetings
```

```
  Short+early:  |=|            ends at 2    <- greedy picks this
  Long+early:   |==========|   ends at 10
  Short+late:          |=|     ends at 8    <- then this
```

Sorting by start time might grab the long meeting and block two short ones.
Sorting by end time grabs the two short ones. More meetings = better answer.

**Why "earliest end time" works:**
By picking the meeting that ends earliest, we leave the maximum remaining time for future meetings.
No other strategy can do better — any swap would either tie or lose.

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
```

**Common mistake — wrong greedy property for activity selection:** Sorting by shortest duration or earliest start time produces incorrect results silently. The only correct greedy choice is earliest finish time — any other sort key fails on simple counterexamples like `[(0,100),(1,2),(3,4)]` where start-time greedy picks only 1 activity instead of 3.

<a id="merge-intervals"></a>
## Merge Intervals

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

```
Activity Selection:   "Which intervals can I pick so NONE overlap?" -> maximize count
Merge Intervals:      "Combine all overlapping intervals"           -> minimize count

Same problem of overlapping ranges. Completely different algorithms. Different greedy choices.
```

```python
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
```

**Common mistake — wrong sort order for interval problems:** Activity selection needs sort by END time; merge intervals needs sort by START time. Using the wrong key runs without errors but silently gives the wrong answer. Check: `[[1,10],[2,3],[4,5],[6,7]]` — sort-by-start picks 1 interval, sort-by-end correctly picks 3.

<a id="minimum-number-of-coins"></a>
## Minimum Number of Coins (Certain Systems)

> 📝 [Practice Q4 — Coin Change Counterexample](./practice.md#q4-does-greedy-always-work-coin-change-counterexample) · [Practice Q15 — When Greedy Fails, Use DP](./practice.md#q15-coin-change--when-greedy-fails-use-dp) · [Practice Q22 — When Greedy Works](./practice.md#q22-when-does-coin-change-greedy-work-prove-it)

Coins:
1, 5, 10, 25

Greedy:
Take largest possible coin first.

Works in canonical coin systems.

But not always.

Example:
Coins: 1, 3, 4
Amount: 6

Greedy:
4 + 1 + 1 = 3 coins

Optimal:
3 + 3 = 2 coins

Greedy fails.

## Visual: When Greedy Fails — The Coin Change Trap

Greedy is seductive — it always feels right. But it can mislead you.

**Problem:** Make change for amount = 6, using coins [1, 3, 4].

```
Greedy path:     6 -> [take 4] -> 2 -> [take 1] -> 1 -> [take 1] -> 0   (3 coins)
                                                                     NOT optimal
Optimal path:    6 -> [take 3] -> 3 -> [take 3] -> 0                   (2 coins)
                                                                     OPTIMAL
```

**Why did greedy fail?**

```
Greedy choice: "4 is the biggest coin, take it first"

But taking 4 forces you to make up 2 with small coins (1+1).
If you skip 4 and take 3 instead, the remaining 3 is perfectly a single coin.

The "locally best" choice (biggest coin) blocked the "globally best" path.
```

The rule of thumb:
- Greedy works when picking the locally best option never eliminates a better global option
- Greedy fails when a local choice closes off paths that lead to a better answer
- When greedy fails -> consider **Dynamic Programming** (which explores ALL options)

**Common mistake — applying greedy to arbitrary coin denominations:** Greedy (largest coin first) only works when each denomination divides evenly into the next larger one, like `[1, 5, 10, 25]`. For arbitrary denominations like `[1, 3, 4]`, use DP. The fix: `dp[i] = min(dp[i], dp[i - coin] + 1)` for all coins at each amount.

<a id="huffman-coding"></a>
## Huffman Coding

> 📝 [Practice Q14 — Build the Huffman Tree](./practice.md#q14-huffman-encoding--build-the-optimal-prefix-tree) · [Practice Q23 — Min Cost to Connect Ropes](./practice.md#q23-minimum-cost-to-connect-all-ropes)

Build optimal prefix code.

Greedy:
Merge two smallest frequencies first.

Always optimal.

Used in compression.

<a id="fractional-knapsack"></a>
## Fractional Knapsack

> 📝 [Practice Q7 — Fractional Knapsack](./practice.md#q7-fractional-knapsack)

You can take fraction of item.

Greedy rule:
Pick highest value/weight ratio first.

This works.

But 0/1 knapsack?
Greedy fails.

Important difference.

<a id="job-sequencing-with-deadlines"></a>
## Job Sequencing with Deadlines

> 📝 [Practice Q20 — Task Assignment](./practice.md#q20-task-assignment--minimize-maximum-completion-time) · [Practice Q12 — Task Scheduler](./practice.md#q12-task-scheduler-with-cooldown)

Sort jobs by profit.
Schedule greedily.

Works due to problem structure.

<a id="visual-jump-game"></a>
## Visual: Jump Game

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

```
Failing example: [3, 2, 1, 0, 4]

Index 0: val=3, max_reach = max(0, 0+3) = 3
Index 1: val=2, max_reach = max(3, 1+2) = 3
Index 2: val=1, max_reach = max(3, 2+1) = 3
Index 3: val=0, max_reach = max(3, 3+0) = 3
Index 4: current=4 > max_reach=3. STUCK! Cannot reach end.
```

**The trick:** You don't track which specific jumps you made. You just track the frontier:
"what's the farthest position reachable from anywhere we've been so far?"
If you ever reach a tile where your current index > max_reach, you're stuck. Game over.

```python
# Jump Game
def can_jump(nums):
    max_reach = 0
    for i, val in enumerate(nums):
        if i > max_reach:
            return False                 # stuck
        max_reach = max(max_reach, i + val)
    return True
```

**Common mistake — Jump Game off-by-one in the loop guard:** The check `if i > max_reach: return False` must come BEFORE updating max_reach. If you update max_reach for unreachable indices, you get false positives. The critical invariant: only update max_reach when you can actually be at index i.

<a id="visual-minimum-platforms"></a>
## Visual: Minimum Platforms — Sweep Line

The sweep-line approach for "minimum platforms needed" requires TWO separately sorted arrays: arrivals and departures.

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
            platforms += 1
            max_platforms = max(max_platforms, platforms)
            i += 1
        else:
            platforms -= 1
            j += 1

    return max_platforms
```

```
If a train arrives at the same time another departs, the arriving train CAN use
the platform the departing train just vacated. So <= means "arrival is not after
departure" — we count it as the departing train leaving first.
```

**Common mistake — mixing arrivals and departures into one event sort:** When arrival and departure have the same time, alphabetical tuple sort processes 'arrival' before 'departure', making it appear an extra platform is needed even though one just freed up. Fix: use two separate sorted arrays with two pointers.

> [↑ Back to Top](#top)

<a id="6-greedy-vs-dynamic-programming"></a>
# 6. Greedy vs Dynamic Programming

Felix faces a dilemma: should he commit to a vendor instantly (greedy) or compare all quotes before deciding (dynamic programming)? Greedy is fast — one pass, decision made. DP is thorough — it explores every combination. The trade-off is speed versus guaranteed optimality.

> 📝 [Practice Q25 — Full Decision Framework](./practice.md#q25-greedy-vs-dp--full-decision-framework) · [Practice Q4 — Coin Change Counterexample](./practice.md#q4-does-greedy-always-work-coin-change-counterexample)

Greedy:
- Fast
- Simple
- Makes local decision
- No backtracking

DP:
- Explores all possibilities
- Uses memory
- Guarantees optimal

If greedy property not proven,
use DP.

<a id="visual-sort-order-cheat-sheet"></a>
## Visual: Sort Order Cheat Sheet

```
Problem                             Sort by     Why
-----------------------------------------------------------------------
Maximize non-overlapping intervals  END time    Earliest finish = most room left
Merge overlapping intervals         START time  Detect consecutive overlaps
Minimum rooms (meeting rooms)       START time  Process in arrival order
Task scheduling (earliest deadline) DEADLINE    Classic EDF scheduling
```

> [↑ Back to Top](#top)

<a id="7-how-to-recognize-greedy-problems"></a>
# 7. How to Recognize Greedy Problems

Felix has learned to spot greedy-friendly situations by pattern. If the event requirements can be sorted and handled one-at-a-time without revisiting past decisions, greedy will likely work. The moment he catches himself needing to undo a choice, that is the signal to switch strategies.

> 📝 [Practice Q1 — Greedy Choice Property](./practice.md#q1-what-is-the-greedy-choice-property) · [Practice Q2 — Optimal Substructure](./practice.md#q2-optimal-substructure-in-greedy)

Look for:

- Sorting helps
- Interval problems
- Scheduling
- Maximizing count
- Minimizing cost
- Choosing best immediate option
- No revisiting past decisions

Sorting often involved.

> [↑ Back to Top](#top)

<a id="8-time-complexity"></a>
# 8. Time Complexity

Felix notices that his greedy decisions always follow the same two-phase pattern: first he sorts all the vendor bids (O(n log n)), then he walks through them once picking the best at each step (O(n)). That makes greedy algorithms among the fastest optimization strategies available.

> 📝 [Practice Q3 — Activity Selection](./practice.md#q3-activity-selection--maximum-non-overlapping-meetings) · [Practice Q6 — Jump Game O(n)](./practice.md#q6-jump-game-i--can-you-reach-the-end)

Most greedy problems:

Sort -> O(n log n)
Then iterate -> O(n)

Total:
O(n log n)

Efficient.

> [↑ Back to Top](#top)

<a id="9-common-mistakes"></a>
# 9. Common Mistakes

Felix learned every one of these the hard way — each mistake cost him a failed event or a panicked last-minute fix. The pattern is always the same: assuming the obvious local choice is safe without testing a counterexample first.

> 📝 [Practice Q4 — Greedy Fails for Coins](./practice.md#q4-does-greedy-always-work-coin-change-counterexample) · [Practice Q21 — Prove Correctness](./practice.md#q21-prove-activity-selection-correctness--exchange-argument)

- Assuming greedy always works
- Not proving greedy property
- Using greedy where DP needed
- Ignoring counterexamples
- Sorting incorrectly

Greedy requires proof intuition.

<a id="visual-wrong-vs-correct-greedy-choices"></a>
## Visual: Summary of Wrong vs Correct Greedy Choices

```
Problem                       WRONG choice           CORRECT choice
----------------------------------------------------------------------
Max non-overlapping intervals  Shortest duration      Earliest finish time
Max non-overlapping intervals  Earliest start time    Earliest finish time
Minimum coins                  Largest coin           DP (no greedy for arbitrary)
Jump Game                      Skip unreachable check Guard: if i > max_reach: stop
Min platforms                  Mixed event sort       Separate sorted arrivals/deps
```

| Mistake | Root Cause | One-Line Fix |
|---|---|---|
| Greedy for arbitrary coin change | Greedy choice is not locally safe | Use DP for arbitrary denominations |
| Wrong sort order for intervals | Different problems need different keys | Schedule: sort by END; Merge: sort by START |
| Mixed event sort for platforms | Simultaneous events ordered wrong | Use two separate sorted arrays with two pointers |
| Jump Game off-by-one | Updating max_reach for unreachable index | Check `if i > max_reach: return False` FIRST |
| Activity selection by duration | Shortest duration is not greedy-safe | Sort by FINISH TIME, not duration or start time |

**Common mistake — not proving greedy works before trusting it:** Always test on a few examples before committing to a greedy approach. If greedy fails on even one counterexample, switch to DP. The "greedy stays ahead" exchange argument is the standard proof technique — if you can't sketch it, you haven't proven correctness.

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

Greedy is:

- Local decision strategy
- Fast and efficient
- Requires proof of correctness
- Often involves sorting
- Used in scheduling and optimization
- Not always safe

**Mental Model:** Greedy is like climbing a mountain — at every step, move in the steepest upward direction. Usually works, but sometimes leads to a local peak while the global maximum is elsewhere.

**Real-World Applications:**
- Network bandwidth allocation
- Scheduling meetings
- Task prioritization
- Resource allocation
- Data compression (Huffman coding)
- Cache replacement policies

Greedy is used widely in systems wherever speed matters and the greedy choice property holds.

**Felix's Final Lesson:** Mastering greedy improves interview speed, pattern recognition, and optimization thinking. The confidence to trust a local choice — backed by proof — is what separates a correct greedy solution from a lucky guess.

> 📝 [Practice — All 25 Problems](./practice.md)

> [↑ Back to Top](#top)

**[Back to README](../README.md)**

| Prev | Next |
|------|------|
| [Graphs](../18_graphs/theory.md) | [Backtracking](../20_backtracking/theory.md) |

**This folder:** [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)

**Related modules:** [Dynamic Programming](../21_dynamic_programming/theory.md) · [Graphs](../18_graphs/theory.md) · [Backtracking](../20_backtracking/theory.md)

**Jump to:** [Activity Selection](#activity-selection) · [Coin Change](#minimum-number-of-coins) · [Jump Game](#visual-jump-game) · [Greedy vs DP](#6-greedy-vs-dynamic-programming) · [Common Mistakes](#9-common-mistakes)
