# 📘 System Design Patterns — From Algorithms to Real Systems

> Data Structures solve problems.
> System Design scales them.
>
> This is where DSA meets the real world.

In this section, we study:

1. LRU Cache
2. Rate Limiter
3. Caching Strategies

These are extremely common in backend and system design interviews.

---

# 🧠 1️⃣ LRU Cache — Least Recently Used

## 📖 Real Life Example

Imagine your phone has limited memory.

When memory is full,
it deletes apps you haven’t used recently.

That is LRU policy.

---

## 🧩 Problem

Design a cache that:

- Stores key-value pairs
- Has fixed capacity
- Removes least recently used item when full
- Supports get and put in O(1)

---

## 🛠 Data Structures Used

To achieve O(1):

Use:

- Hashmap (for fast lookup)
- Doubly linked list (for order tracking)

Why?

Hashmap:
O(1) access.

Linked list:
O(1) insert/delete.

Together:
Perfect combination.

---

## 🔄 Operations

### get(key)

- If exists:
  Move node to front.
- Else:
  Return -1.

### put(key, value)

- If key exists:
  Update value.
  Move to front.
- If capacity exceeded:
  Remove tail node.

---

## 📏 Time Complexity

get → O(1)  
put → O(1)

---

## 🌍 Real-World Usage

- Browser caching
- Database query caching
- CDN
- Memory management
- OS page replacement

LRU is extremely common.

---

# 🚦 2️⃣ Rate Limiter — Controlling Traffic

## 📖 Real Life Example

A toll gate allows only 10 cars per minute.

If more cars arrive,
some must wait.

That is rate limiting.

---

## 🧩 Problem

Limit number of requests per user per time window.

Example:
100 requests per minute.

---

## 🛠 Common Algorithms

---

### 🔹 Fixed Window Counter

Track:

Count per time window.

Simple but bursty.

---

### 🔹 Sliding Window Log

Store timestamps.

Remove old timestamps.

More accurate.

---

### 🔹 Token Bucket

Bucket fills at steady rate.

Each request consumes token.

If no tokens → reject.

Allows bursts.

---

### 🔹 Leaky Bucket

Processes at constant rate.

Queue-based.

---

## 📏 Time Complexity

Depends on implementation.

Usually O(1) or O(log n).

---

## 🌍 Real-World Usage

- API gateways
- Payment systems
- Login attempts
- Cloud services
- Microservices

Rate limiting protects systems.

---

# 🗄 3️⃣ Caching Strategies

Caching improves performance.

But strategy matters.

---

## 🔹 Cache Aside (Lazy Loading)

Application:

1. Check cache.
2. If miss:
   Fetch from DB.
   Store in cache.

Most common.

---

## 🔹 Write Through

Write to cache and DB simultaneously.

Strong consistency.

---

## 🔹 Write Back (Write Behind)

Write to cache first.
Later update DB.

High performance.
Risky.

---

## 🔹 Refresh Ahead

Update cache before expiration.

Used for hot data.

---

# ⚖️ Trade-Off Discussion

| Strategy | Pros | Cons |
|----------|------|------|
| Cache Aside | Simple | Stale data risk |
| Write Through | Consistent | Slower writes |
| Write Back | Fast | Data loss risk |
| Token Bucket | Smooth bursts | Implementation complexity |

Interviewers expect trade-off reasoning.

---

# 🧠 Connecting DSA to System Design

LRU:
Uses hashmap + linked list.

Rate limiter:
Uses queue, hashmap, timestamps.

Caching:
Uses hashing, TTL logic.

DSA knowledge directly applies.

---

# ⚠️ Common Mistakes

- Not discussing concurrency
- Ignoring race conditions
- Not handling memory limits
- Forgetting eviction logic
- Ignoring distributed system issues

System design is about scale + trade-offs.

---

# 🧠 Mental Model

Think of system design as:

Applying DSA under real-world constraints:

- Memory limit
- Concurrency
- Failures
- Network delay
- Data consistency

System design is applied DSA at scale.

---

# 📌 Final Understanding

System Design Patterns are:

- Real-world extensions of DSA
- Used in backend systems
- Critical for senior interviews
- About trade-offs and scaling

Mastering this prepares you for:

- Backend interviews
- Infrastructure roles
- Senior software engineer roles
- System architecture discussions

This is where coding meets real engineering.

---

# 🔁 Navigation

Previous:  
[25_advanced_graphs/interview.md](/dsa-complete-mastery/25_advanced_graphs/interview.md)

Next:  
[26_system_design_patterns/interview.md](/dsa-complete-mastery/26_system_design_patterns/interview.md)  
[99_interview_master/0_2_years.md](/dsa-complete-mastery/99_interview_master/0_2_years.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
