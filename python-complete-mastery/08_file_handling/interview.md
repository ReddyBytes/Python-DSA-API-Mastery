# 🎯 File Handling — Interview Preparation Guide  
From Basic File Operations to Production-Scale Data Processing

---

# 🧠 What Interviewers Actually Test

File handling questions test:

- Resource management
- Memory awareness
- Encoding knowledge
- Security awareness
- Performance thinking
- Real-world data processing experience

At senior levels, it becomes:

- How do you process 10GB files?
- How do you avoid memory crashes?
- How do you ensure safe writes?
- How do you prevent file corruption?

File handling is real engineering.

---

# 🔹 Level 1: 0–2 Years Experience

Basic understanding expected.

---

## 1️⃣ How do you open and read a file?

```python
with open("file.txt", "r") as f:
    data = f.read()
```

Strong answer includes:

Use `with` to ensure automatic closing.

---

## 2️⃣ Why is `with open()` preferred over manual close?

Because:

- Automatically closes file
- Prevents resource leaks
- Cleaner and safer

Interviewers want resource awareness.

---

## 3️⃣ What are different file modes?

- r → read
- w → write (overwrites)
- a → append
- b → binary
- x → exclusive create

Mention overwrite behavior in "w".

---

## 4️⃣ What is the difference between text mode and binary mode?

Text mode:
Returns string.
Handles encoding.

Binary mode:
Returns bytes.
No encoding applied.

---

## 5️⃣ What happens if you forget to close a file?

Possible issues:

- Resource leak
- "Too many open files" error
- Data not flushed to disk

Shows system-level awareness.

---

# 🔹 Level 2: 2–5 Years Experience

Now interviewer expects:

- Performance awareness
- Large file handling
- Encoding understanding
- Safe writing techniques

---

## 6️⃣ How would you handle a very large file (10GB)?

Strong answer:

- Do not use read()
- Process line by line
- Use chunk-based reading
- Use generators

Example:

```python
with open("big.log") as f:
    for line in f:
        process(line)
```

Memory-efficient answer.

---

## 7️⃣ What is buffering and why is it important?

Buffering stores data in memory before writing to disk.

Why?

Disk I/O is slow.
Memory is fast.

Shows performance understanding.

---

## 8️⃣ What is encoding? What happens if encoding is wrong?

Encoding converts bytes ↔ characters.

If wrong encoding used:

UnicodeDecodeError occurs.

Strong candidate mentions UTF-8 default.

---

## 9️⃣ What is the difference between read(), readline(), readlines()?

read() → entire file  
readline() → one line  
readlines() → list of all lines  

Best practice:
Avoid read() for large files.

---

## 🔟 How do you safely write to a file in production?

Strong answer:

- Write to temporary file
- Flush data
- Rename atomically

Prevents partial corruption.

Shows production awareness.

---

# 🔹 Level 3: 5–10 Years Experience

Now questions become architecture-focused.

---

## 1️⃣1️⃣ How would you design a log processing system?

Strong answer:

- Stream logs
- Process chunk by chunk
- Use buffering
- Avoid loading full file
- Possibly use multiprocessing
- Handle file rotation

Shows real-world thinking.

---

## 1️⃣2️⃣ How do you handle concurrent writes to the same file?

Options:

- File locking
- Use centralized logging system
- Append-only logs
- Avoid race conditions

Senior-level thinking.

---

## 1️⃣3️⃣ What are atomic file operations?

Atomic write ensures:

File is either fully written or not written.

Used in:

- Config updates
- Critical state files

Pattern:

Write to temp → rename.

---

## 1️⃣4️⃣ How would you prevent path traversal attacks?

Example attack:

```
../../etc/passwd
```

Solution:

- Validate paths
- Restrict base directory
- Use os.path.abspath
- Avoid direct user path usage

Security awareness is critical.

---

## 1️⃣5️⃣ How do you process millions of JSON records efficiently?

Strong answer:

- Stream JSON if possible
- Avoid loading entire JSON array
- Use incremental parsing
- Use memory profiling
- Possibly use generators

Shows data engineering awareness.

---

# 🔥 Scenario-Based Questions

---

## Scenario 1:
Your program crashes when reading large CSV file.

Likely cause:

- Using read()
- Memory overflow

Solution:

Process row by row using csv.reader.

---

## Scenario 2:
You see UnicodeDecodeError in production.

What do you check?

- File encoding
- Default encoding
- Byte order mark (BOM)
- Corrupted file

Structured debugging answer wins.

---

## Scenario 3:
Users upload files to server.

What security checks do you apply?

- Validate file type
- Restrict file size
- Sanitize filename
- Avoid overwriting existing files
- Store outside public directory

Security maturity matters.

---

## Scenario 4:
System logs sometimes get corrupted.

Possible causes:

- Concurrent writes
- Crash during write
- No flushing
- Not using atomic operations

Investigate systematically.

---

## Scenario 5:
You need to process file in real-time as it grows.

Solution:

- Use tail-like logic
- Monitor file pointer
- Use file.seek()
- Possibly use OS-level file watcher

Shows deeper knowledge.

---

# 🧠 How to Answer Like a Strong Candidate

Weak:

“I will read file.”

Strong:

> “For small files, I would use read(), but for large datasets I would process the file line-by-line or in chunks to avoid loading everything into memory. I would also ensure proper encoding handling and safe resource cleanup using context managers.”

Clear. Structured. Mature.

---

# ⚠️ Common Weak Candidate Mistakes

- Ignoring large file memory issues
- Not understanding encoding
- Forgetting context manager
- Ignoring concurrency issues
- Not discussing atomic writes
- Not considering security

---

# 🎯 Rapid-Fire Revision

- Always use with
- Avoid read() for huge files
- Understand encoding
- Use chunk processing
- Know file modes
- Understand buffering
- Secure file paths
- Handle concurrency
- Use atomic writes

---

# 🏆 Final Interview Mindset

File handling questions test:

- Resource management
- Performance thinking
- Memory awareness
- Security awareness
- Real-world production maturity

If you show:

- Memory optimization
- Safe writing
- Encoding clarity
- Concurrency awareness
- Security best practices

You stand out.

File handling is simple for scripts,
but critical for production systems.

---

# 🔁 Navigation

Previous:  
[08_file_handling/theory.md](./theory.md)

Next:  
[09_logging_debugging/theory.md](../09_logging_debugging/theory.md)

