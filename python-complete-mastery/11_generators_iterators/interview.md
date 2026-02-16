# 🎯 Generators & Iterators — Interview Preparation Guide  
From Basic Iteration to Memory-Efficient System Design

---

# 🧠 What Interviewers Actually Test

This topic tests:

- Do you understand Python internals?
- Can you explain iteration protocol?
- Do you know how memory works?
- Can you design scalable data pipelines?
- Do you understand lazy evaluation?

This separates:

Script writers  
from  
System engineers.

---

# 🔹 Level 1: 0–2 Years Experience

Basic clarity expected.

---

## 1️⃣ What is an iterator?

Strong answer:

> An iterator is an object that implements the `__iter__()` and `__next__()` methods and returns elements one at a time until `StopIteration` is raised.

If you mention StopIteration,
you stand out.

---

## 2️⃣ What is an iterable?

> An iterable is any object that can return an iterator using the `__iter__()` method.

Examples:

- list
- tuple
- string
- dictionary
- set
- file
- generator

---

## 3️⃣ What is a generator?

Strong answer:

> A generator is a special type of iterator created using the `yield` keyword, which produces values lazily instead of storing them in memory.

Avoid saying:
“Generator is like list.”

It is not.

---

## 4️⃣ Difference between return and yield?

return:
- Ends function completely.

yield:
- Pauses execution.
- Saves state.
- Resumes later.

This is core understanding.

---

## 5️⃣ What happens when generator is exhausted?

When no more values:

StopIteration is raised.

In for loop:
Handled automatically.

---

# 🔹 Level 2: 2–5 Years Experience

Now interviewer expects:

- Memory understanding
- Lazy evaluation clarity
- Generator expression knowledge
- Performance awareness

---

## 6️⃣ Why are generators memory efficient?

Strong answer:

> Generators produce one value at a time and do not store the entire dataset in memory. This makes them suitable for large datasets.

Key concept:
Lazy evaluation.

---

## 7️⃣ Difference between list comprehension and generator expression?

List comprehension:

```python
[x*x for x in range(1000)]
```

Creates full list.

Generator expression:

```python
(x*x for x in range(1000))
```

Creates generator object.

Memory difference:
Significant for large data.

---

## 8️⃣ How does for loop work internally?

Strong answer:

> The for loop internally calls `iter()` on the iterable to obtain an iterator and repeatedly calls `next()` until `StopIteration` is raised.

This shows internal knowledge.

---

## 9️⃣ When should you use generators?

Use when:

- Processing large files
- Streaming data
- Building pipelines
- Handling infinite sequences
- Avoiding memory overload

---

## 🔟 When should you NOT use generators?

Avoid when:

- Need random access
- Need multiple passes over data
- Need length immediately
- Small dataset where list is simpler

Shows balanced thinking.

---

# 🔹 Level 3: 5–10 Years Experience

Now discussion moves to:

- Pipeline design
- Streaming systems
- Debugging lazy behavior
- Generator delegation
- Performance trade-offs

---

## 1️⃣1️⃣ What is lazy evaluation?

Lazy evaluation means:

Values are computed only when needed.

Example:

Generator does not compute next value until requested.

This reduces memory and CPU usage.

---

## 1️⃣2️⃣ How would you design a data processing pipeline using generators?

Strong answer:

> I would chain generator expressions where each stage transforms data incrementally. This allows streaming processing without loading entire dataset into memory.

Example:

```python
lines = (line.strip() for line in file)
filtered = (line for line in lines if line)
processed = (transform(line) for line in filtered)
```

Pipeline architecture.

---

## 1️⃣3️⃣ What is yield from?

Used to delegate iteration to another generator.

Simplifies nested loops.

Shows advanced knowledge.

---

## 1️⃣4️⃣ What are common generator debugging issues?

- Generator exhausted
- Accidentally converting to list
- Unexpected lazy behavior
- Forgetting to iterate
- Side effects not running

Shows real-world awareness.

---

## 1️⃣5️⃣ Can generators improve performance?

Yes, but:

- They reduce memory
- They may slightly increase CPU due to repeated calls

Good trade-off for large datasets.

---

# 🔥 Scenario-Based Questions

---

## Scenario 1:
Application crashes due to memory overload while processing large CSV.

Likely cause:

Using read() or list().

Solution:

Process file line-by-line using generator.

---

## Scenario 2:
You convert generator to list and memory usage spikes.

Why?

Because now entire dataset is loaded.

Lazy evaluation lost.

---

## Scenario 3:
Generator works first time but not second time.

Why?

Generators can be iterated only once.

Need to recreate generator.

---

## Scenario 4:
Need to process infinite stream of events.

Solution:

Use generator with infinite loop.
Process in batches.

---

## Scenario 5:
API must return large dataset gradually.

Solution:

Use streaming response with generator.
Send chunk-by-chunk.

Used in real backend systems.

---

# 🧠 How to Answer Like a Strong Candidate

Weak:

“Generator saves memory.”

Strong:

> “Generators implement lazy evaluation, meaning values are produced only when requested. This significantly reduces memory usage when handling large datasets and enables streaming-style data processing pipelines.”

Clear.
Precise.
Mature.

---

# ⚠️ Common Weak Candidate Mistakes

- Confusing iterable and iterator
- Not knowing StopIteration
- Thinking generator stores values
- Not understanding for loop internals
- Forgetting generator exhaustion
- Not understanding lazy evaluation

---

# 🎯 Rapid-Fire Revision

- Iterable → has __iter__()
- Iterator → has __next__()
- Generator → uses yield
- yield pauses execution
- Generators are lazy
- Save memory
- Cannot reuse exhausted generator
- Use for large datasets
- for loop uses iter() and next()

---

# 🏆 Final Interview Mindset

Generators & iterators test:

- Python internals
- Memory awareness
- Scalable thinking
- Pipeline design
- Lazy evaluation understanding

If you demonstrate:

- Clear iterator protocol knowledge
- Lazy evaluation clarity
- Memory trade-off understanding
- Real-world streaming examples
- Structured debugging approach

You appear as strong Python engineer.

Generators are not just syntax.

They are foundation of scalable data processing.

---

# 🔁 Navigation

Previous:  
[11_generators_iterators/theory.md](./theory.md)

Next:  
[12_context_managers/theory.md](../12_context_managers/theory.md)

