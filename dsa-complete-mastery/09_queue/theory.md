# 📘 Queue — Order, Fairness, and Flow Control

> If Stack is about reversal,
> Queue is about fairness.
>
> Queue follows:
>
> **First In, First Out (FIFO)**

Queues control flow in real systems.
They are not just academic structures.
They model waiting systems.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
FIFO principle · deque (double-ended queue) · BFS usage

**Should Learn** — Important for real projects, comes up regularly:
circular queue · priority queue introduction · Python collections.deque

**Good to Know** — Useful in specific situations, not always tested:
queue in real systems · monotonic deque

**Reference** — Know it exists, look up syntax when needed:
blocking queue · bounded queue · double-ended priority queue

---

# 1️⃣ Daily Life: Where You Already Use Queue

### 🛒 Supermarket Line

You enter the line first.
You leave first.

If someone behind you leaves before you,
system becomes unfair.

Queue guarantees fairness.

---

### 🚦 Traffic Signal

Cars line up.

First car at signal moves first.

Traffic control is a queue system.

---

### 🖨 Printer Jobs

If you send print request first,
it prints before later requests.

That is queue behavior.

---

# 2️⃣ What Is a Queue?

A queue is a linear data structure that follows:

**FIFO — First In, First Out**

Operations:

- Enqueue → Add element at rear
- Dequeue → Remove element from front
- Peek → View front element
- isEmpty → Check empty

Unlike stack:
Insertion and removal happen at opposite ends.

---

# 3️⃣ Visual Representation

```
Front → [10] [20] [30] ← Rear
```

- Enqueue happens at rear
- Dequeue happens at front

Flow direction matters.

---

# 4️⃣ Core Operations Explained Deeply

Let n = number of elements.

| Operation | What Happens | Time |
|------------|--------------|------|
| Enqueue | Insert at rear | O(1) |
| Dequeue | Remove from front | O(1) |
| Peek | Return front | O(1) |

But careful:

In Python list:
pop(0) is O(n).

Because shifting occurs.

So Python’s list is not ideal queue implementation.

---

# 5️⃣ Proper Queue Implementation in Python

Use collections.deque:

```python
from collections import deque

queue = deque()
queue.append(10)       # enqueue
queue.popleft()        # dequeue
```

Deque is optimized for:

- O(1) insertion at both ends
- O(1) removal at both ends

This is production-level knowledge.

---

# 6️⃣ Queue vs Stack (Deep Comparison)

| Feature | Stack | Queue |
|----------|--------|--------|
| Order | LIFO | FIFO |
| Insert | Top | Rear |
| Remove | Top | Front |
| Used in | DFS | BFS |

Stack reverses order.
Queue preserves order.

Choosing wrong one breaks logic.

---

# 7️⃣ Real Systems That Depend on Queue

---

## 🔹 Operating Systems

Process scheduling.

Processes wait in ready queue.
CPU picks from front.

---

## 🔹 Web Servers

Incoming HTTP requests queued before processing.

Prevents overload.

---

## 🔹 Rate Limiting

Requests placed in queue.
Processed gradually.

---

## 🔹 Message Brokers

Kafka, RabbitMQ — internally use queue structures.

---

# 8️⃣ Circular Queue — Efficient Space Usage

Problem:

If we use simple array-based queue,
front shifts cause wasted space.

Circular queue solves this by wrapping around.

Imagine array of size 5:

```
Index: 0 1 2 3 4
```

When rear reaches end,
it wraps to beginning if space available.

Used in embedded systems.

---

# 9️⃣ Double-Ended Queue (Deque)

Deque allows:

- Insert at front
- Insert at rear
- Remove from front
- Remove from rear

More flexible than simple queue.

Used in:

- Sliding window problems
- Monotonic queue
- Cache algorithms

> 📝 **Practice:** [Q34 · queue-deque-ops](../dsa_practice_questions_100.md#q34--normal--queue-deque-ops)

---

# 🔟 Priority Queue (Concept Introduction)

Unlike normal queue:

Order is not based on arrival.
It is based on priority.

Example:

Emergency room patients.

Higher severity treated first.

In programming:
Implemented using heap.

Time complexity:
Insert → O(log n)
Remove → O(log n)

Priority queue is not FIFO.

---

# 1️⃣1️⃣ Queue in Graph Algorithms

Breadth-First Search (BFS) uses queue.

Why?

Because BFS explores level by level.

Nodes discovered first are processed first.

Queue ensures level-order traversal.

---

# 1️⃣2️⃣ Common Queue Patterns

Most interview problems involve:

- BFS
- Sliding window maximum
- Task scheduling
- Rate limiting
- Level order traversal in tree
- Implement stack using queue
- Implement queue using stack

Pattern recognition is important.

---

# 1️⃣3️⃣ When NOT to Use Queue

Avoid queue when:

- You need LIFO behavior
- You need priority-based removal
- You need random access

Queue is specialized for ordered processing.

---

# 1️⃣4️⃣ Memory & Performance Considerations

Queues grow with:

- Incoming tasks
- Pending operations

Unbounded queues can cause memory exhaustion.

In production:
Always consider capacity limits.

---

# 📌 Final Understanding

Queue represents:

- Order
- Fairness
- Controlled flow

It models real-world waiting systems.

Stack controls execution.
Queue controls flow.

Understanding both deeply prepares you for:

- Graph algorithms
- System design
- Concurrency problems
- Scheduling systems

---

# 🔁 Navigation

Previous:  
[08_stack/theory.md]

Next:  
[09_queue/interview.md]  
[10_hashing/theory.md]

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Stack — Interview Q&A](../08_stack/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
