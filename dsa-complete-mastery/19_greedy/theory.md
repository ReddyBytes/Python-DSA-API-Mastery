# 📘 Greedy Algorithms — The Art of Smart Immediate Decisions

> Greedy means:
>
> “Take the best option right now.”
>
> Without worrying too much about the future.

Greedy algorithms are fast.
But they are not always correct.

Understanding when greedy works
is one of the most important interview skills.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
greedy choice property · optimal substructure · when greedy is provably correct

**Should Learn** — Important for real projects, comes up regularly:
activity selection · coin change · fractional knapsack · interval problems

**Good to Know** — Useful in specific situations, not always tested:
greedy vs DP distinction · Huffman coding

**Reference** — Know it exists, look up syntax when needed:
job sequencing · graph-based greedy (Kruskal's/Prim's overview)

---

# 🍰 1️⃣ Real Life Story — Eating Cake

You have cake pieces:

Small, medium, large.

If you’re hungry,
you might take the largest piece first.

That is greedy choice.

You don’t calculate total calories later.
You just pick the biggest now.

Sometimes good.
Sometimes wrong.

---

# 🎒 2️⃣ Backpack Story — Choosing Items

You have limited space.

You want maximum value.

Greedy idea:

Pick item with highest value first.

But what if:
Two medium items together give more value than one big item?

Greedy fails.

This shows:

Greedy doesn’t always give global optimum.

---

# 🧠 3️⃣ What Is a Greedy Algorithm?

A greedy algorithm:

- Makes locally optimal choice
- At each step
- Without revisiting previous decisions

It never backtracks.

---

# 🔍 4️⃣ When Does Greedy Work?

Greedy works when:

Problem has:

1. Greedy choice property
2. Optimal substructure

Greedy choice property means:

A local optimal choice leads to global optimal solution.

Not all problems have this.

---

# 📏 5️⃣ Classic Greedy Problems

---

## 🔹 Activity Selection

You have activities with start/end times.

Goal:
Maximize number of non-overlapping activities.

Greedy rule:
Choose activity with earliest finish time.

Why it works?

Finishing early leaves more room for others.

Correct greedy logic.

---

## 🔹 Fractional Knapsack

You can take fraction of item.

Greedy rule:
Pick highest value/weight ratio first.

This works.

But 0/1 knapsack?
Greedy fails.

Important difference.

---

## 🔹 Minimum Number of Coins (Certain Systems)

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

---

## 🔹 Huffman Coding

Build optimal prefix code.

Greedy:
Merge two smallest frequencies first.

Always optimal.

Used in compression.

---

## 🔹 Job Sequencing with Deadlines

Sort jobs by profit.
Schedule greedily.

Works due to problem structure.

---

# ⚖️ 6️⃣ Greedy vs Dynamic Programming

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

---

# 🧠 7️⃣ How to Recognize Greedy Problems

Look for:

- Sorting helps
- Interval problems
- Scheduling
- Maximizing count
- Minimizing cost
- Choosing best immediate option
- No revisiting past decisions

Sorting often involved.

---

# 🔢 8️⃣ Time Complexity

Most greedy problems:

Sort → O(n log n)
Then iterate → O(n)

Total:
O(n log n)

Efficient.

---

# 🌍 9️⃣ Real-World Applications

- Network bandwidth allocation
- Scheduling meetings
- Task prioritization
- Resource allocation
- Data compression
- Cache replacement policies

Greedy used widely in systems.

---

# ⚠️ 1️⃣0️⃣ Common Mistakes

- Assuming greedy always works
- Not proving greedy property
- Using greedy where DP needed
- Ignoring counterexamples
- Sorting incorrectly

Greedy requires proof intuition.

---

# 🧠 1️⃣1️⃣ Mental Model

Greedy is like:

Climbing mountain.

At every step:
Move in steepest upward direction.

Usually works.
But sometimes leads to local peak.

Global maximum may be elsewhere.

---

# 📌 1️⃣2️⃣ Final Understanding

Greedy is:

- Local decision strategy
- Fast and efficient
- Requires proof of correctness
- Often involves sorting
- Used in scheduling and optimization
- Not always safe

Mastering greedy improves:

- Interview speed
- Pattern recognition
- Optimization thinking

Greedy is about confidence in local choices.

---

# 🔁 Navigation

Previous:  
[18_graphs/interview.md](/dsa-complete-mastery/18_graphs/interview.md)

Next:  
[19_greedy/interview.md](/dsa-complete-mastery/19_greedy/interview.md)  
[20_backtracking/theory.md](/dsa-complete-mastery/20_backtracking/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Graphs — Interview Q&A](../18_graphs/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
