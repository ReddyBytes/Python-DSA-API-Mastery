# 🎯 Greedy Algorithms — Interview Preparation Guide (Decision Strategy Mastery)

> Greedy problems test whether you can:
> - Identify optimal local choice
> - Justify correctness
> - Avoid unnecessary complexity
> - Recognize when greedy fails
>
> Greedy is about confidence in decisions.

---

# 🔎 How Greedy Questions Appear in Interviews

Rarely asked:
“What is greedy?”

More commonly:

- Activity selection
- Meeting rooms
- Minimum coins
- Jump game
- Gas station problem
- Task scheduler
- Merge intervals
- Huffman coding
- Partition labels
- Minimum number of arrows to burst balloons

If you see:

- Maximize number of activities
- Minimize cost
- Scheduling
- Intervals
- Local best choice
- Sorting helps

Think: **Greedy**

---

# 🧠 How to Respond Before Coding

Instead of:

“I’ll try greedy.”

Say:

> “Since making the locally optimal choice at each step appears to lead to a globally optimal solution, we can use a greedy approach. I’ll sort the data based on the key decision parameter.”

That shows reasoning.

---

# 🔹 Basic Level Questions (0–2 Years)

---

**Q1: What is a Greedy Algorithm?**

<details>
<summary>💡 Show Answer</summary>

Professional answer:

A greedy algorithm makes the locally optimal choice at each step with the hope of achieving a globally optimal solution.

</details>

<br>

**Q2: Does Greedy Always Work?**

<details>
<summary>💡 Show Answer</summary>

No.

Greedy works only when:

- Greedy choice property holds
- Optimal substructure exists

Important to mention.

</details>

<br>

**Q3: Why Sorting Often Used in Greedy?**

<details>
<summary>💡 Show Answer</summary>

Sorting helps us:

- Decide best candidate first
- Make structured decisions
- Avoid revisiting choices

Example:
Activity selection sorted by end time.

</details>


# 🔹 Intermediate Level Questions (2–5 Years)

---

**Q4: Activity Selection**

<details>
<summary>💡 Show Answer</summary>

Problem:
Maximize number of non-overlapping intervals.

Approach:

1. Sort by finish time.
2. Pick earliest finishing.
3. Skip overlapping.

Time:
O(n log n)

Interview tip:
Explain why earliest finish leaves more room.

</details>

<br>

**Q5: Merge Intervals**

<details>
<summary>💡 Show Answer</summary>

Sort by start time.

If overlapping:
Merge.

Else:
Add new interval.

Time:
O(n log n)

Common pattern.

</details>

<br>

**Q6: Jump Game**

<details>
<summary>💡 Show Answer</summary>

Greedy rule:

Track maximum reachable index.

If current index > max reachable → fail.

Time:
O(n)

Shows forward decision tracking.

</details>

<br>

**Q7: Gas Station Problem**

<details>
<summary>💡 Show Answer</summary>

Track total gas and current tank.

If tank becomes negative:
Reset start.

Greedy works because total feasibility ensures solution.

Must explain reasoning clearly.

</details>

<br>

**Q8: Partition Labels**

<details>
<summary>💡 Show Answer</summary>

Track last occurrence of each character.

Extend window until all characters covered.

Greedy segmentation.

Time:
O(n)

</details>


# 🔹 Advanced Level Questions (5–10 Years)

---

**Q9: Huffman Coding**

<details>
<summary>💡 Show Answer</summary>

Greedy:
Always merge two smallest frequencies.

Use min heap.

Time:
O(n log n)

Explain why merging smallest first is optimal.

</details>

<br>

**Q10: Task Scheduler**

<details>
<summary>💡 Show Answer</summary>

Arrange tasks with cooldown.

Use greedy frequency ordering.

Often combined with heap.

</details>

<br>

**Q11: Why Greedy Fails in 0/1 Knapsack**

<details>
<summary>💡 Show Answer</summary>

Because:

Local best value/weight ratio may block better combination later.

Example:
Demonstrate counterexample.

Strong candidates mention this.

</details>

<br>

**Q12: How to Prove Greedy Correctness**

<details>
<summary>💡 Show Answer</summary>

Approaches:

- Exchange argument
- Contradiction
- Optimal substructure reasoning

You don’t need formal proof,
but explain intuition.

</details>


# 🔥 Scenario-Based Questions

---

## Scenario 1:

Greedy solution fails on edge case.

<details>
<summary>💡 Show Answer</summary>

Possible issue:
Greedy property not valid.

Consider DP instead.

</details>
---

## Scenario 2:

Sorting unnecessary increases complexity.

<details>
<summary>💡 Show Answer</summary>

If input already sorted,
avoid extra sort.

</details>
---

## Scenario 3:

Time limit tight.

<details>
<summary>💡 Show Answer</summary>

Greedy preferred over DP.

Explain trade-off.

</details>
---

## Scenario 4:

Need minimal number of intervals removed.

<details>
<summary>💡 Show Answer</summary>

Sort by end time.

Apply activity selection logic.

</details>
---

## Scenario 5:

Need to minimize number of arrows to burst balloons.

<details>
<summary>💡 Show Answer</summary>

Sort intervals by end.

Same pattern.

Recognize interval scheduling pattern.

</details>
---

# 🧠 How to Communicate Like a Strong Candidate

Weak candidate:

“I think greedy works.”

Strong candidate:

> “Since selecting the interval with the earliest finishing time always leaves the maximum space for remaining intervals, this greedy strategy leads to an optimal solution.”

That shows logical justification.

---

# 🎯 Interview Cracking Strategy for Greedy

1. Identify decision parameter.
2. Check if sorting helps.
3. Make local optimal choice.
4. Verify no future conflict.
5. Mention time complexity O(n log n).
6. Consider counterexample.
7. Compare with DP alternative.
8. Explain reasoning clearly.

Greedy requires confidence + reasoning.

---

# ⚠️ Common Weak Candidate Mistakes

- Using greedy without proof
- Ignoring counterexamples
- Not sorting properly
- Choosing wrong sorting key
- Assuming greedy always works
- Not explaining why it works

Greedy requires logical clarity.

---

# 🎯 Rapid-Fire Revision Points

- Greedy = local optimal choice
- Often involves sorting
- Time complexity usually O(n log n)
- Works when greedy choice property holds
- Activity selection classic example
- Fractional knapsack works
- 0/1 knapsack fails
- Prove correctness intuitively
- Compare with DP when unsure

---

# 🏆 Final Interview Mindset

Greedy problems test:

- Decision-making confidence
- Logical justification
- Pattern recognition
- Optimization instinct

If you can:

- Identify greedy pattern quickly
- Justify why it works
- Compare with DP intelligently
- Recognize interval scheduling
- Handle edge cases carefully

You are strong in greedy-based interviews.

Greedy mastery improves:

- Speed in interviews
- Algorithm selection skill
- Real-world optimization thinking

---

# 🔁 Navigation

Previous:  
[19_greedy/theory.md](/dsa-complete-mastery/19_greedy/theory.md)

Next:  
[20_backtracking/theory.md](/dsa-complete-mastery/20_backtracking/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Common Mistakes](./common_mistakes.md) &nbsp;|&nbsp; **Next:** [Backtracking — Theory →](../20_backtracking/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md)
