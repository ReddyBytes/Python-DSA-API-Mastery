# 🎯 Recursion — Interview Preparation Guide

> This file prepares you to handle recursion discussions in technical interviews
> from basic correctness to performance reasoning and system-level trade-offs.
>  
> Recursion questions are rarely about syntax.
> They are about understanding call stack behavior, termination conditions,
> complexity growth, and optimization strategies.

---

# 🔹 Part 1: What Interviewers Actually Evaluate in Recursion

Before jumping into Q&A, understand what is being tested.

Interviewers look for:

- Clear base case definition
- Correct reduction of problem size
- No infinite recursion
- Proper complexity analysis
- Awareness of stack memory
- Ability to optimize exponential recursion
- Conversion to iterative solution when needed

Recursion reveals whether you understand execution flow deeply.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is recursion?**

<details>
<summary>💡 Show Answer</summary>

Recursion is when a function calls itself to solve smaller subproblems until a base condition is met.

Key components:
- Base case
- Recursive case

Without base case → infinite recursion.

</details>

<br>

**Q2: What happens internally when a recursive function is called?**

<details>
<summary>💡 Show Answer</summary>

Each call:

- Creates a new stack frame
- Stores parameters
- Stores local variables
- Stores return address

Execution resumes in reverse order when base case is reached.

This is called the **call stack mechanism**.

</details>

<br>

**Q3: What is the space complexity of recursion?**

<details>
<summary>💡 Show Answer</summary>

Even if no extra data structures are used,
recursion uses stack space.

If recursion depth is n → space complexity O(n).

Many candidates forget stack space.

</details>

<br>

**Q4: What causes stack overflow?**

<details>
<summary>💡 Show Answer</summary>

If recursion depth exceeds Python’s recursion limit (~1000 by default).

Common causes:
- Missing base case
- Large input
- Infinite recursion

Professional awareness:
Recursion depth matters in production systems.

</details>

<br>

**Q5: When is recursion better than iteration?**

<details>
<summary>💡 Show Answer</summary>

Recursion is often cleaner when:

- Problem is hierarchical
- Structure is tree-like
- Backtracking is required
- Divide-and-conquer strategy is used

Clarity sometimes outweighs small performance differences.

</details>


# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: How do you analyze time complexity of recursion?**

<details>
<summary>💡 Show Answer</summary>

Approach:

1. Count number of recursive calls.
2. Multiply by work per call.
3. Form recurrence relation.

Example:

```
T(n) = T(n-1) + O(1)
→ O(n)
```

Binary recursion example:

```
T(n) = 2T(n-1) + O(1)
→ O(2ⁿ)
```

Be comfortable deriving this.

</details>

<br>

**Q7: What is tail recursion?**

<details>
<summary>💡 Show Answer</summary>

Tail recursion means the recursive call is the last operation in the function.

Some languages optimize it.

Python does NOT perform tail call optimization.

So stack still grows.

Important clarification during interviews.

</details>

<br>

**Q8: How do you optimize naive recursive Fibonacci?**

<details>
<summary>💡 Show Answer</summary>

Naive:

```
T(n) = T(n-1) + T(n-2)
→ O(2ⁿ)
```

Optimization:

Use memoization.

```
Time → O(n)
Space → O(n)
```

Interviewers expect you to identify repeated subproblems.

</details>

<br>

**Q9: When would you convert recursion to iteration?**

<details>
<summary>💡 Show Answer</summary>

Situations:

- Very deep recursion
- Stack overflow risk
- Performance-critical systems
- When iterative version is clearer

Example:
DFS recursive → iterative using explicit stack.

This shows flexibility.

</details>

<br>

**Q10: What are common recursion mistakes?**

<details>
<summary>💡 Show Answer</summary>

- Missing base case
- Incorrect base case
- Wrong input reduction
- Infinite recursion
- Forgetting return value propagation
- Ignoring exponential growth

</details>


# 🔹 Advanced Level Questions (5–10 Years)

**Q11: Explain recursion tree analysis.**

<details>
<summary>💡 Show Answer</summary>

Example:

```
T(n) = 2T(n/2) + O(n)
```

At each level:
Total work = O(n)

Number of levels = log n

Total work:
O(n log n)

You should be able to explain visually.

</details>

<br>

**Q12: What is the difference between recursion and divide-and-conquer?**

<details>
<summary>💡 Show Answer</summary>

Recursion:
Function calls itself.

Divide-and-conquer:
Divide problem into smaller parts,
solve recursively,
combine results.

All divide-and-conquer uses recursion,
but not all recursion is divide-and-conquer.

</details>

<br>

**Q13: How do you detect overlapping subproblems?**

<details>
<summary>💡 Show Answer</summary>

If recursive tree shows repeated states,
problem likely requires memoization.

Example:
Fibonacci.

Recognition of overlap separates strong candidates.

</details>

<br>

**Q14: Discuss recursion in memory-constrained systems.**

<details>
<summary>💡 Show Answer</summary>

Concerns:

- Stack overflow
- Increased memory usage
- Harder debugging
- Risk of uncontrolled depth

In production systems,
iteration is often preferred for reliability.

</details>

<br>

**Q15: How does recursion behave in multi-threaded systems?**

<details>
<summary>💡 Show Answer</summary>

Each thread has its own stack.

Deep recursion in multiple threads
can increase memory usage significantly.

Senior engineers consider stack size when designing systems.

</details>


# 🔥 Scenario-Based Questions

---

## Scenario 1:

Your recursive function works for small inputs but crashes for large inputs.

<details>
<summary>💡 Show Answer</summary>

Likely cause:
Stack overflow.

Fix:
- Convert to iterative
- Increase recursion limit (temporary)
- Optimize recursion depth

</details>
---

## Scenario 2:

Your recursive algorithm is extremely slow for n = 40.

<details>
<summary>💡 Show Answer</summary>

Problem:
Exponential time complexity.

Fix:
Introduce memoization or dynamic programming.

</details>
---

## Scenario 3:

You need to traverse a directory structure with millions of nested folders.

<details>
<summary>💡 Show Answer</summary>

Recursive approach may fail.

Better:
Iterative using explicit stack.

Shows production awareness.

</details>
---

## Scenario 4:

Your recursive backtracking solution times out.

<details>
<summary>💡 Show Answer</summary>

Possible improvements:

- Prune search space
- Add memoization
- Sort input to enable pruning
- Convert to DP

Optimization thinking is expected.

</details>
---

## Scenario 5:

You are solving tree traversal.

<details>
<summary>💡 Show Answer</summary>

Interviewer asks:
“Can you do this without recursion?”

You should:
Explain iterative approach using stack.

Demonstrates deeper understanding.

</details>
---

# 🧠 Senior-Level Structured Answer Example

If interviewer asks:

“When would you avoid recursion?”

Professional answer:

I avoid recursion when the depth can grow unbounded or when stack overflow is a risk. In performance-critical systems or memory-constrained environments, I prefer iterative approaches because they provide better control over memory usage. However, for tree-based or divide-and-conquer problems, recursion improves clarity and reduces logical complexity. My choice depends on constraints and expected input size.

This reflects engineering maturity.

---

# 🎯 Rapid-Fire Revision Points

- Recursion requires base case.
- Each call consumes stack memory.
- Time complexity derived via recurrence.
- Exponential recursion must be optimized.
- Python does not optimize tail recursion.
- Memoization reduces repeated computation.
- Iterative conversion is a valuable skill.
- Stack overflow is a real production concern.

If you can clearly explain stack behavior, complexity growth, and optimization strategies,
you are well-prepared for recursion discussions in mid-level and senior interviews.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Common Mistakes](./common_mistakes.md) &nbsp;|&nbsp; **Next:** [Sorting — Theory →](../05_sorting/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md)
