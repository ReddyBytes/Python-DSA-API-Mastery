# 🧾 Logging & Debugging in Python  
From Print Statements to Production Observability

---

# 🎯 Why Logging Is Critical

Imagine your production system crashes at 2 AM.

Users are angry.
Money is being lost.

You cannot sit near the server and run print().

You need logs.

Logs are:

The memory of your system.

Without logging:

- You cannot debug production issues
- You cannot track user behavior
- You cannot investigate crashes
- You cannot audit actions
- You cannot monitor performance

Logging is not optional.
It is professional engineering practice.

---

# 🧠 1️⃣ Print vs Logging

Beginners use:

```python
print("Value is", x)
```

Why print is bad in production:

- No log levels
- Cannot disable selectively
- No timestamps
- No severity tagging
- Cannot redirect easily
- No structured format
- Hard to manage in large systems

Logging solves all of this.

---

# 🧱 2️⃣ Basic Logging Example

```python
import logging

logging.basicConfig(level=logging.INFO)

logging.info("Application started")
```

Now logs include:

- Level
- Timestamp
- Message

Better than print.

---

# 📌 3️⃣ Logging Levels (Very Important)

Python provides 5 main levels:

---

## 🔹 DEBUG

Detailed information.
Used for development.

Example:
Variable values.

---

## 🔹 INFO

General events.
Normal system operation.

Example:
User logged in.

---

## 🔹 WARNING

Something unexpected.
But system still works.

Example:
Retrying connection.

---

## 🔹 ERROR

Serious issue.
Operation failed.

Example:
Database connection failed.

---

## 🔹 CRITICAL

System failure.
Immediate attention required.

Example:
Service cannot start.

---

# 🧠 4️⃣ Logging Level Strategy

In development:
Use DEBUG.

In production:
Use INFO or WARNING.

Never leave DEBUG in high-traffic production.
It creates massive logs.

---

# 🏗 5️⃣ Logging Architecture — Logger, Handler, Formatter

Logging has three main parts:

---

## 1️⃣ Logger

Creates log message.

---

## 2️⃣ Handler

Decides where log goes:

- Console
- File
- Remote server
- Email
- Syslog

---

## 3️⃣ Formatter

Controls format:

- Timestamp
- Level
- Message
- File name
- Line number

Example:

```python
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)
```

Professional systems use custom formatters.

---

# 🧠 6️⃣ Logging to File

```python
logging.basicConfig(
    filename="app.log",
    level=logging.INFO
)
```

Now logs go to file.

Used in production.

---

# 🔄 7️⃣ Log Rotation

If logs grow forever,
disk fills up.

Solution:

RotatingFileHandler.

```python
from logging.handlers import RotatingFileHandler
```

Allows:

- Max file size
- Backup count

Prevents disk crash.

---

# 🧠 8️⃣ Structured Logging (Advanced & Important)

Instead of plain text logs:

Use structured logs (JSON format).

Example:

```json
{
  "timestamp": "2024-01-01T10:00:00",
  "level": "ERROR",
  "user_id": 123,
  "message": "Payment failed"
}
```

Why structured logs are powerful:

- Easy to search
- Easy to filter
- Used in centralized logging systems
- Works with ELK stack
- Used in cloud environments

Modern production systems use structured logging.

---

# 🌍 9️⃣ Centralized Logging

In distributed systems:

Logs from multiple servers go to:

- Elasticsearch
- Datadog
- Splunk
- CloudWatch

Why?

Single place to monitor system.

---

# 🧠 🔟 What Is Debugging?

Debugging is:

Finding root cause of issue.

Not just fixing symptom.

---

# 🔎 1️⃣1️⃣ Debugging Techniques

---

## 🔹 Read Traceback Carefully

Example:

```
Traceback (most recent call last):
  File "app.py", line 10
```

Start from bottom.
Understand call stack.

---

## 🔹 Add Targeted Logs

Not random prints.

Add logs around failure area.

---

## 🔹 Reproduce Issue Locally

Always try to reproduce.

---

## 🔹 Use Debugger

Use pdb:

```python
import pdb
pdb.set_trace()
```

Allows step-by-step execution.

---

# 🧠 1️⃣2️⃣ Logging + Exception Handling

Best practice:

```python
try:
    ...
except Exception as e:
    logging.exception("Unexpected error")
```

logging.exception automatically logs stack trace.

Important in production.

---

# ⚡ 1️⃣3️⃣ Performance Considerations

Logging is I/O heavy.

Too much logging:

- Slows system
- Consumes disk
- Increases storage cost

Use correct level.
Do not log inside tight loops unnecessarily.

---

# 🔐 1️⃣4️⃣ Sensitive Data Warning

Never log:

- Passwords
- Credit card numbers
- Personal information
- API keys

Logs are often stored externally.
Security risk.

---

# 🏗 1️⃣5️⃣ Logging Best Practices

✔ Use proper log levels  
✔ Avoid print in production  
✔ Use structured logs  
✔ Add meaningful context  
✔ Avoid excessive logs  
✔ Never swallow exceptions silently  
✔ Use centralized logging  
✔ Protect sensitive data  

---

# 🚨 1️⃣6️⃣ Real Production Incident Example

Scenario:

Users report payment failure.

Logs show:

```
ERROR - DB timeout
```

Investigation:

- DB overloaded
- Connection pool exhausted
- Retry logic missing

Logs helped identify root cause.

Without logs:
Guesswork.

---

# 🧠 1️⃣7️⃣ Debugging Mindset

Do not:

- Blame random part
- Add random prints
- Restart blindly

Instead:

- Analyze logs
- Narrow down failure
- Reproduce
- Isolate
- Fix root cause
- Add better logs if needed

Professional debugging is structured.

---

# ⚠️ 1️⃣8️⃣ Common Logging Mistakes

❌ Using print in production  
❌ Logging too much debug data  
❌ Not using levels properly  
❌ Not rotating logs  
❌ Logging sensitive data  
❌ Catching exception without logging  
❌ Writing logs without timestamps  

---

# 🏆 1️⃣9️⃣ Engineering Maturity Levels

Beginner:
Uses print.

Intermediate:
Uses logging.

Advanced:
Uses structured logging + log rotation.

Senior:
Designs centralized logging + observability strategy.

---

# 🧠 Final Mental Model

Logging is:

The black box recorder of your system.

Debugging is:

The investigation process after a crash.

If your logging is poor,
debugging becomes impossible.

If your logging is strong,
production becomes manageable.

Logging & debugging are survival tools for engineers.

---

# 🔁 Navigation

Previous:  
[08_file_handling/interview.md](../08_file_handling/interview.md)

Next:  
[09_logging_debugging/interview.md](./interview.md)

