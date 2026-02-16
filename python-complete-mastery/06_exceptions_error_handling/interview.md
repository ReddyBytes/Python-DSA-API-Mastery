# 🎯 Exceptions & Error Handling — Interview Preparation Guide  
From Junior Developer to Production Engineer

---

# 🧠 What Interviewers Actually Test

Exception questions are not about:

- Syntax of try/except

They test:

- Do you understand system reliability?
- Can you prevent crashes?
- Do you think about failure modes?
- Can you debug production issues?
- Do you understand recoverable vs non-recoverable errors?

Error handling reflects engineering maturity.

---

# 🔹 Level 1: 0–2 Years Experience

At this stage, interviewers test:

- Basic syntax
- Understanding of exception flow
- Common built-in exceptions

---

## 1️⃣ What is an exception?

Professional answer:

> An exception is an object that represents an error occurring during program execution. When an exception is raised, normal execution stops and Python searches for a handler in the call stack.

Avoid saying:
“Exception is error.”

Be precise.

---

## 2️⃣ Difference between SyntaxError and Exception?

SyntaxError:
Detected before execution.

Exception:
Occurs during runtime.

SyntaxError cannot be caught using try/except.

---

## 3️⃣ What is the purpose of try-except?

To handle runtime errors gracefully and prevent program termination.

Also mention:

It improves robustness and user experience.

---

## 4️⃣ Difference between except and finally?

except:
Runs when exception occurs.

finally:
Always runs.

Used for cleanup like closing files or DB connections.

---

## 5️⃣ Why should we avoid bare except?

Example:

```python
except:
    pass
```

Why bad?

- Hides real issues
- Makes debugging difficult
- Can swallow critical exceptions like KeyboardInterrupt

Correct practice:
Catch specific exceptions.

---

# 🔹 Level 2: 2–5 Years Experience

Now interviewer expects:

- Specificity
- Production thinking
- Design awareness

---

## 6️⃣ What is exception propagation?

When an exception is not handled in the current function,
it moves up the call stack until a handler is found.

If none found:
Program crashes.

Important in layered architectures.

---

## 7️⃣ What is exception chaining?

```python
raise NewError() from original_error
```

Preserves root cause.

Critical for debugging production issues.

Without chaining:
Original traceback lost.

---

## 8️⃣ Why are exceptions expensive?

Raising exceptions:

- Creates object
- Builds traceback
- Traverses stack

Not suitable for normal flow control.

Example:

Bad:

```python
try:
    value = d[key]
except KeyError:
    ...
```

Better:

```python
if key in d:
```

Shows performance awareness.

---

## 9️⃣ When should you re-raise an exception?

When:

- You log it
- Add context
- Convert to domain-specific error
- Cannot recover locally

Example:

```python
except DatabaseError as e:
    logger.error("DB failure")
    raise
```

Never swallow errors silently.

---

# 🔹 Level 3: 5–10 Years Experience

Now interview shifts to:

- Architecture
- API design
- Distributed systems
- Resilience patterns

---

## 🔟 How do you design exception handling in large systems?

Strong answer:

> I define domain-specific exception classes, categorize them as recoverable or fatal, log all unexpected failures with context, convert internal exceptions to appropriate API responses, and ensure resources are always released using context managers or finally blocks.

This shows system thinking.

---

## 1️⃣1️⃣ How would you map exceptions to HTTP responses?

Example mapping:

- ValueError → 400 Bad Request
- PermissionError → 403 Forbidden
- NotFoundError → 404
- DatabaseError → 503 Service Unavailable
- Unexpected Exception → 500 Internal Server Error

Important:
Never expose internal stack trace to clients.

---

## 1️⃣2️⃣ What is graceful degradation?

If non-critical component fails:

- Log error
- Continue core service

Example:

Analytics service fails.
Payment still works.

---

## 1️⃣3️⃣ What is fail-fast principle?

In critical systems:

If core invariant breaks:
Crash early.

Do not continue in corrupted state.

Example:
Financial ledger inconsistency.

---

## 1️⃣4️⃣ How would you implement retry logic?

For transient failures:

- Network timeouts
- Temporary DB outage

Pattern:

- Retry limited times
- Exponential backoff
- Circuit breaker if repeated failures

Mention backoff.
Shows maturity.

---

## 1️⃣5️⃣ How do exceptions work in multithreading?

In threads:

- Exception in thread does not stop main thread automatically.
- Must capture and handle inside thread.

In multiprocessing:
Exceptions must be serialized.

Shows deeper Python knowledge.

---

# 🔥 Scenario-Based Questions

---

## Scenario 1:
Production API randomly crashes.

What would you check?

Strong answer:

- Logs with stack trace
- Recent deployments
- Input validation issues
- Unhandled exceptions
- Resource leaks
- Thread safety issues

Do not just say:
“I’ll debug.”

Explain systematic approach.

---

## Scenario 2:
File handling code sometimes leaves file open.

Solution:

Use context manager:

```python
with open("file.txt") as f:
    ...
```

Instead of relying only on finally.

---

## Scenario 3:
External API frequently times out.

What do you do?

- Retry with exponential backoff
- Timeout configuration
- Circuit breaker
- Fallback mechanism

---

## Scenario 4:
You see many `except Exception:` blocks in codebase.

What’s wrong?

- Overly broad
- Hard to debug
- Hides specific failures
- Makes system unpredictable

Refactor to specific exception types.

---

## Scenario 5:
System must never lose financial transaction data.

What approach?

- Fail fast on inconsistency
- Log everything
- Use transactional boundaries
- Avoid silent error swallowing
- Possibly halt service if corruption detected

Shows senior reliability thinking.

---

# 🧠 How to Answer Like a Strong Candidate

Weak:

“I’ll catch exception.”

Strong:

> “I would catch only recoverable exceptions at appropriate layer, log them with sufficient context, convert them into domain-specific errors if needed, and allow fatal errors to propagate so they can be handled centrally.”

Precision matters.

---

# ⚠️ Common Weak Candidate Mistakes

- Catching everything
- Using pass
- Not logging
- Not preserving original exception
- Ignoring cleanup
- Using exceptions for control flow
- Not understanding propagation

---

# 🎯 Rapid-Fire Revision

- Exceptions are objects
- SyntaxError ≠ Runtime Exception
- Use specific except blocks
- Use finally for cleanup
- Use custom exceptions for clarity
- Do not swallow exceptions
- Use exception chaining
- Exceptions are expensive
- Handle recoverable vs fatal differently
- Log properly in production

---

# 🏆 Final Interview Mindset

Exception handling questions are maturity tests.

If you demonstrate:

- Precision
- Logging awareness
- Resource cleanup discipline
- API mapping understanding
- Retry/backoff awareness
- Fail-fast reasoning
- Distributed system awareness

You stand out as a strong engineer.

Exception handling is not syntax.

It is reliability engineering.

---

# 🔁 Navigation

Previous:  
[06_exceptions_error_handling/theory.md](./theory.md)

Next:  
[07_modules_packages/theory.md](../07_modules_packages/theory.md)

