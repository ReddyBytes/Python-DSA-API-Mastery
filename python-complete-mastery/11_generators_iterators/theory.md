# 🔄 Generators & Iterators in Python  
From Simple Loops to Memory-Efficient Streaming Systems

---

# 🎯 Why This Topic Matters

Imagine:

You need to process 10 million records.

If you load everything into memory at once:

- Memory crashes
- System slows down
- Server becomes unstable

Generators allow you to:

Process data one item at a time.

This is called:

Lazy evaluation.

This concept is used in:

- Large file processing
- Data pipelines
- APIs
- Streaming systems
- Backend services
- Machine learning pipelines

Understanding generators makes you a better Python engineer.

---

# 🧠 1️⃣ What Is Iteration?

When you write:

```python
for x in [1, 2, 3]:
    print(x)
```

You are iterating.

But what is happening internally?

Python is:

- Taking each element
- One by one
- Until sequence ends

But how?

This leads us to:

Iterator protocol.

---

# 🧱 2️⃣ What Is an Iterable?

An iterable is:

An object that can return its elements one at a time.

Examples:

- List
- Tuple
- String
- Dictionary
- Set
- File object
- Generator

Internally:

An iterable has:

`__iter__()` method

---

# 🧠 3️⃣ What Is an Iterator?

An iterator is:

An object that:

- Implements `__iter__()`
- Implements `__next__()`

It remembers its current position.

Example:

```python
numbers = [1, 2, 3]
iterator = iter(numbers)

print(next(iterator))
print(next(iterator))
print(next(iterator))
```

When elements finish:

`StopIteration` is raised.

That’s how Python knows loop is over.

---

# 🔍 4️⃣ How for Loop Works Internally

This:

```python
for item in iterable:
    print(item)
```

Is roughly equivalent to:

```python
iterator = iter(iterable)

while True:
    try:
        item = next(iterator)
        print(item)
    except StopIteration:
        break
```

Understanding this shows deep knowledge.

---

# 🧠 5️⃣ What Is a Generator?

A generator is:

A special type of iterator.

Instead of returning all values at once,
it yields one value at a time.

Generators use:

`yield` keyword.

---

# 🧱 6️⃣ Simple Generator Example

```python
def count_up_to(n):
    for i in range(n):
        yield i
```

Call it:

```python
gen = count_up_to(5)
```

Important:

The function does NOT run immediately.

It returns a generator object.

Execution starts only when:

`next()` is called.

---

# 🔄 7️⃣ What Does yield Actually Do?

`yield`:

- Pauses function execution
- Saves local variables
- Returns value
- Resumes from same point later

This is powerful.

Unlike return,
which ends function.

---

# 🧠 8️⃣ Generator vs List (Memory Difference)

Example:

```python
numbers = [x for x in range(1_000_000)]
```

This creates entire list in memory.

Now:

```python
numbers = (x for x in range(1_000_000))
```

This creates generator.

Memory difference:

Huge.

Generators store only current state.
Lists store everything.

---

# 📊 9️⃣ Generator Expression vs List Comprehension

List comprehension:

```python
[x*x for x in range(10)]
```

Generator expression:

```python
(x*x for x in range(10))
```

Difference:

Square brackets → list  
Round brackets → generator  

Generators are lazy.

---

# 🧠 🔟 Why Generators Save Memory

Because they:

Do NOT store entire sequence.

They compute value only when needed.

Used in:

- Reading large files
- Database row processing
- Streaming APIs
- Infinite sequences

---

# ♾ 1️⃣1️⃣ Infinite Generators

Example:

```python
def infinite_counter():
    i = 0
    while True:
        yield i
        i += 1
```

This can run forever.

Impossible with list.

Used in:

- Event streaming
- Data simulation

---

# 🧠 1️⃣2️⃣ Generator State & Resumption

Each time you call next():

Generator resumes exactly where it left off.

Local variables preserved.

This is called:

Suspended execution state.

---

# 🔍 1️⃣3️⃣ When StopIteration Happens

When generator finishes:

Python automatically raises StopIteration.

In normal for loop,
you never see it.

But manually calling next():

You may see:

```python
StopIteration
```

---

# 🧠 1️⃣4️⃣ yield vs return

`return`:
Ends function completely.

`yield`:
Pauses and resumes.

Important difference.

---

# 🧱 1️⃣5️⃣ Creating Custom Iterator Class

Example:

```python
class Count:
    def __init__(self, n):
        self.n = n
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < self.n:
            value = self.current
            self.current += 1
            return value
        else:
            raise StopIteration
```

Shows iterator protocol manually.

Generators are simpler way to create iterators.

---

# 🧠 1️⃣6️⃣ yield from (Advanced)

Instead of:

```python
for item in other_generator:
    yield item
```

You can write:

```python
yield from other_generator
```

Cleaner delegation.

---

# ⚡ 1️⃣7️⃣ Performance Considerations

Generators:

✔ Lower memory  
✔ Better for large datasets  
✔ Stream data  
✔ Suitable for pipelines  

But:

- Slight overhead per next() call
- Not suitable if you need random access
- Cannot easily reuse after exhaustion

---

# 🏗 1️⃣8️⃣ Real Production Use Cases

---

## 🔹 Large File Processing

```python
with open("big.log") as f:
    for line in f:
        process(line)
```

File object itself is iterator.

---

## 🔹 Data Pipelines

Chain generators:

```python
filtered = (x for x in data if x > 10)
squared = (x*x for x in filtered)
```

Pipeline style.

---

## 🔹 API Streaming

Yield response chunk by chunk.

Used in:

FastAPI streaming responses.

---

# ⚠️ 1️⃣9️⃣ Common Mistakes

❌ Trying to reuse exhausted generator  
❌ Expecting generator to store values  
❌ Confusing list with generator  
❌ Forgetting StopIteration  
❌ Using generator where list required  

---

# 🏆 2️⃣0️⃣ Engineering Maturity Levels

Beginner:
Uses for loops.

Intermediate:
Uses generator expressions.

Advanced:
Designs streaming pipelines.

Senior:
Builds memory-efficient data systems.

---

# 🧠 Final Mental Model

Iterable:
Something you can loop over.

Iterator:
Object that gives next element.

Generator:
Special iterator created using yield.

Generators are memory-efficient,
lazy,
powerful,
and critical for scalable systems.

---

# 🔁 Navigation

Previous:  
[10_decorators/interview.md](../10_decorators/interview.md)

Next:  
[11_generators_iterators/interview.md](./interview.md)

