# 📂 File Handling in Python  
From Basic File Reading to Production-Grade Data Processing

---

# 🎯 Why File Handling Is Important

Almost every real system interacts with files:

- Reading configuration files
- Writing logs
- Processing CSV datasets
- Uploading user files
- Saving reports
- Processing large datasets
- Reading JSON API responses
- Writing audit records

If you do not understand file handling deeply:

- You will leak file handles
- You will corrupt data
- You will crash under large files
- You will face encoding issues
- You will create security vulnerabilities

File handling is not beginner-only topic.
It is real-world engineering skill.

---

# 🧠 1️⃣ What Is a File in Simple Terms?

A file is:

A sequence of bytes stored on disk.

When we open a file in Python:

We create a connection between:

Your program (memory)
and
The file (disk).

Think of it like opening a tap to a water tank.
You must close it after use.

---

# 🧱 2️⃣ Opening a File

Basic syntax:

```python
file = open("data.txt", "r")
```

Parameters:

- First argument → file path
- Second argument → mode

---

# 📌 3️⃣ File Modes Explained Clearly

---

## 🔹 "r" → Read Mode

Used to read file.
File must exist.

---

## 🔹 "w" → Write Mode

Creates file if not exists.
Overwrites file if exists.

Danger:
Existing content is erased.

---

## 🔹 "a" → Append Mode

Adds content at end.
Does NOT erase file.

---

## 🔹 "x" → Exclusive Create

Creates file.
If file exists → error.

---

## 🔹 "b" → Binary Mode

Used for:

- Images
- PDFs
- Audio
- Video

Example:

```python
open("image.jpg", "rb")
```

---

## 🔹 "t" → Text Mode (Default)

Used for:

- .txt
- .csv
- .json

---

# 🧠 4️⃣ Reading Files

---

## 🔹 Read Entire File

```python
data = file.read()
```

Problem:
If file is very large,
memory can crash.

---

## 🔹 Read Line By Line

```python
for line in file:
    print(line)
```

This is memory-efficient.

Recommended for large files.

---

## 🔹 readlines()

```python
lines = file.readlines()
```

Loads all lines into list.

Not recommended for huge files.

---

# 🔄 5️⃣ Writing to Files

```python
file.write("Hello\n")
```

Important:

Write does not automatically add newline.

You must add "\n".

---

# 🔚 6️⃣ Closing Files

Always close:

```python
file.close()
```

If you don’t:

- Memory leak
- Too many open files error
- Data may not flush to disk

---

# 🧠 7️⃣ The Right Way — Context Manager

Best practice:

```python
with open("data.txt", "r") as file:
    data = file.read()
```

Why better?

- Automatically closes file
- Cleaner
- Safer
- Prevents leaks

Always prefer with.

---

# 📦 8️⃣ Understanding Buffering (Important Concept)

When writing to file:

Python does NOT immediately write to disk.

It writes to buffer in memory.

Then later flushes to disk.

Why?

Disk is slow.
Memory is fast.

You can force flush:

```python
file.flush()
```

Or:

```python
file.close()
```

---

# 🧠 9️⃣ File Pointer (Cursor Position)

File has pointer.

You can move it:

```python
file.seek(0)
```

To check position:

```python
file.tell()
```

Useful for:

- Resuming file reads
- Partial file processing

---

# 🌍 1️⃣0️⃣ Text vs Binary Files

Text mode:

- Converts line endings
- Decodes bytes to strings

Binary mode:

- Raw bytes
- No decoding

Important difference.

---

# 🔤 1️⃣1️⃣ Encoding Explained Clearly

Computers store bytes.
Humans read characters.

Encoding maps characters to bytes.

Common encodings:

- UTF-8 (default)
- ASCII
- UTF-16

Example:

```python
open("file.txt", "r", encoding="utf-8")
```

If encoding wrong:

UnicodeDecodeError happens.

Common production issue.

---

# 🧠 1️⃣2️⃣ Handling Large Files Efficiently

Never do:

```python
data = file.read()
```

For large files.

Instead:

Process line by line.

Or:

Chunk reading:

```python
while chunk := file.read(1024):
    process(chunk)
```

Used in:

- Log processing
- Streaming systems
- ETL pipelines

---

# 📊 1️⃣3️⃣ Working with CSV Files

Use csv module:

```python
import csv

with open("data.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```

Avoid manual splitting.
CSV can contain commas inside quotes.

---

# 📦 1️⃣4️⃣ Working with JSON Files

```python
import json

with open("data.json") as f:
    data = json.load(f)
```

To write:

```python
json.dump(data, file)
```

Always use built-in modules.

---

# 📂 1️⃣5️⃣ Working with File Paths (OS Module)

Never hardcode paths.

Use:

```python
import os

os.path.join("folder", "file.txt")
```

Better for cross-platform compatibility.

---

# 🔒 1️⃣6️⃣ Security Considerations

Never trust user file paths.

Example vulnerability:

Path traversal attack:

```
../../etc/passwd
```

Always sanitize paths.

Use safe directories.

---

# ⚡ 1️⃣7️⃣ Performance Considerations

- Avoid frequent open/close
- Use buffering
- Use chunk reading
- Avoid loading huge files
- Use memory-efficient generators

In data engineering,
file handling performance matters a lot.

---

# 🏗 1️⃣8️⃣ Real Production Patterns

---

## 🔹 Log Writing

Append mode.

```python
open("app.log", "a")
```

---

## 🔹 Temporary Files

Use tempfile module.

---

## 🔹 Atomic Writes

Write to temp file,
then rename.

Prevents partial corruption.

---

## 🔹 Streaming File Upload

Process chunk by chunk.
Do not load entire file.

---

# 🧠 1️⃣9️⃣ Common Mistakes

❌ Forgetting to close file  
❌ Using read() on huge file  
❌ Ignoring encoding  
❌ Overwriting file accidentally  
❌ Hardcoding file paths  
❌ Ignoring security risks  

---

# 🏆 2️⃣0️⃣ Engineering Maturity Levels

Beginner:
Reads and writes files.

Intermediate:
Handles encoding and large files.

Advanced:
Optimizes memory and performance.

Senior:
Designs streaming systems, ensures atomicity, handles security.

---

# 🧠 Final Mental Model

File handling =

Managing connection between:

Memory ↔ Disk

Key concerns:

- Safety
- Performance
- Encoding
- Cleanup
- Security
- Scalability

File handling is simple at surface,
but critical in production.

---

# 🔁 Navigation

Previous:  
[07_modules_packages/interview.md](../07_modules_packages/interview.md)

Next:  
[08_file_handling/interview.md](./interview.md)

