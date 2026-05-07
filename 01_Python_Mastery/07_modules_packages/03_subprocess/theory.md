# ⚙️ subprocess — Running External Programs

> `subprocess` lets your Python program run shell commands and other executables — capturing their output, handling errors, and coordinating pipelines — without the shell injection risk of `os.system()`.
> Think of it as the expediter between your Python manager and the shell kitchen: it sends the ticket, waits for the result, and returns it in a structured form you can act on.

---

## 📌 Learning Priority

**Must Learn** — Foundation of external process control:
`subprocess.run()` · `capture_output=True` · `check=True` · `CalledProcessError` · `returncode`

**Should Learn** — Common real-world patterns:
`subprocess.check_output()` · `text=True` · `timeout=` · passing env vars · `cwd=`

**Good to Know** — For long-running / streaming:
`subprocess.Popen` · `communicate()` · `stdout=PIPE` · pipes between processes

**Reference** — Avoid unless you know the risk:
`shell=True` — know what it does and why it's dangerous

---

## What subprocess Replaces and Why

Before `subprocess`, Python had `os.system()` — the equivalent of shouting a command into a room and hoping someone wrote down the answer. You got back a single integer (the exit code) and whatever happened on the terminal happened, with no way to capture or redirect it. `subprocess` replaced that chaos with a structured conversation: you send a message, you get a structured reply, and injection attacks become impossible when you use the list form.

```
os.system("ls -la")            # ← runs it, but output goes straight to terminal
                               # ← returns exit code only (integer)
                               # ← no capture, no error raise, injection risk

subprocess.run(["ls", "-la"],  # ← structured call
    capture_output=True,       # ← captures stdout and stderr
    text=True,                 # ← decode bytes to str
    check=True)                # ← raise on non-zero exit
```

The **list form** `["ls", "-la"]` is the correct way. Each element is one argument — the OS passes them directly to the process without a shell. No injection possible. The string form `"ls -la"` requires `shell=True`, which opens the door to injection when any part of the command comes from user input.

---

## subprocess.run() — The Main Interface

Ordering coffee at a counter is a `subprocess.run()` call: you hand over your order, the barista makes it, and when the cup lands in front of you the interaction is over. You did not watch each step — you just waited, then received a complete result. `subprocess.run()` works the same way: it launches the command, waits for it to finish, and returns a single `CompletedProcess` object with everything you need to act on.

`subprocess.run()` was added in Python 3.5 and is the recommended entry point for the vast majority of cases. It runs the command, waits for it to finish, and returns a `CompletedProcess` object.

```
subprocess.run(args, *, stdin=None, stdout=None, stderr=None,
               capture_output=False, shell=False, cwd=None,
               timeout=None, check=False, env=None, text=False)
```

### The Core Parameters

```python
import subprocess

result = subprocess.run(
    ["git", "status"],          # ← list of command + arguments, no shell
    capture_output=True,        # ← equivalent to stdout=PIPE, stderr=PIPE
    text=True,                  # ← decode output as UTF-8 string (not bytes)
    check=True,                 # ← raise CalledProcessError if exit code != 0
    cwd="/path/to/repo",        # ← set working directory for the subprocess
    timeout=30,                 # ← kill and raise TimeoutExpired after 30s
    env={**os.environ,          # ← environment variables (see section below)
         "GIT_PAGER": "cat"},
)

print(result.returncode)        # ← integer: 0 = success
print(result.stdout)            # ← str (because text=True)
print(result.stderr)            # ← str
```

### The CompletedProcess Object

```
CompletedProcess
├── .args           ← the command that was run (list or str)
├── .returncode     ← exit code (0 = success, non-zero = failure)
├── .stdout         ← captured stdout (str if text=True, bytes otherwise, None if not captured)
└── .stderr         ← captured stderr (same rules as stdout)
```

If you pass `check=True` and the command exits with a non-zero code, `run()` raises immediately — you never see the `CompletedProcess` object. That is usually what you want: fail fast, fail loudly.

---

## Capturing Output — The Patterns

Output capture is like choosing what to record in a meeting: sometimes you want separate notes for the main discussion (stdout) and the side conversations (stderr); sometimes you want everything in one chronological log; sometimes you just need to know it happened and do not care what was said. These three patterns cover every real scenario.

### Pattern 1: Capture both stdout and stderr separately

```python
result = subprocess.run(
    ["git", "log", "--oneline", "-5"],
    capture_output=True,    # ← stdout=PIPE + stderr=PIPE
    text=True,
    check=True,
)
print(result.stdout)        # ← the five commit lines
print(result.stderr)        # ← any git warnings (usually empty)
```

### Pattern 2: Combine stderr into stdout

```python
result = subprocess.run(
    ["make", "build"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,   # ← merge stderr into stdout stream
    text=True,
)
print(result.stdout)            # ← interleaved stdout + stderr in order
```

Use this when you want a single combined log output.

### Pattern 3: Discard output entirely

```python
subprocess.run(
    ["some-noisy-command"],
    stdout=subprocess.DEVNULL,  # ← discard stdout
    stderr=subprocess.DEVNULL,  # ← discard stderr
    check=True,
)
```

Use this for fire-and-forget commands where output is irrelevant.

### What capture_output=True Actually Does

```
capture_output=True
    ↓
stdout=subprocess.PIPE   ← creates an in-memory pipe; output is buffered
stderr=subprocess.PIPE   ← same for stderr

Without PIPE: output goes to the terminal (inherited file descriptors)
With PIPE:    output is held in a buffer until the process exits
```

**Caution:** if the process produces enormous output (gigabytes of logs), `PIPE` buffers it all in memory before you can read it. For large output, use `Popen` with streaming reads instead.

---

## Error Handling

A subprocess that fails silently is like a contractor who does not finish the job but still sends an invoice with a thumbs up. `check=True` is your clause that says "if this failed, tell me immediately with all the details" — and the three exception types cover every failure mode: bad exit code, ran too long, or the tool was not installed at all.

### CalledProcessError — non-zero exit code

```python
import subprocess

try:
    result = subprocess.run(
        ["git", "push", "origin", "main"],
        capture_output=True,
        text=True,
        check=True,             # ← triggers CalledProcessError on failure
    )
except subprocess.CalledProcessError as e:
    print(f"Command failed with exit code {e.returncode}")
    print(f"stdout: {e.stdout}")
    print(f"stderr: {e.stderr}")
    raise
```

`CalledProcessError` carries `.returncode`, `.stdout`, and `.stderr` — everything you need to diagnose the failure.

### TimeoutExpired — process took too long

```python
try:
    subprocess.run(
        ["some-slow-command"],
        timeout=10,             # ← seconds
        check=True,
    )
except subprocess.TimeoutExpired as e:
    print(f"Timed out after {e.timeout}s")
    # process has been killed at this point
```

When timeout fires, `subprocess` sends `SIGKILL` to the process and raises `TimeoutExpired`. Always set a timeout on any command that could hang.

### FileNotFoundError — command not found

```python
try:
    subprocess.run(["nonexistent-tool", "--version"])
except FileNotFoundError:
    print("Tool not installed or not on PATH")
```

This is a Python-level exception raised before any process starts — the OS could not find the executable.

### Full Production Pattern

```python
import subprocess
import logging

def run_command(cmd: list[str], cwd: str = None) -> str:
    """Run a shell command and return stdout. Raises on failure."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
            timeout=60,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error("Command %s failed (exit %d): %s", cmd, e.returncode, e.stderr)
        raise
    except subprocess.TimeoutExpired:
        logging.error("Command %s timed out", cmd)
        raise
    except FileNotFoundError:
        logging.error("Command not found: %s", cmd[0])
        raise
```

---

## subprocess.check_output() — Legacy but Common

Before `subprocess.run()` arrived in Python 3.5, `check_output()` was the standard way to capture output from a command. It still appears constantly in older codebases and Stack Overflow answers, so recognizing it on sight — and knowing its exact equivalent in modern code — saves time when you are reading someone else's scripts.

You will see this in older codebases and Stack Overflow answers:

```python
output = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True)
```

It is equivalent to:

```python
output = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    capture_output=True,
    text=True,
    check=True,
).stdout
```

`check_output()` raises `CalledProcessError` on non-zero exit, captures stdout, and returns it directly. It does not capture stderr by default (stderr goes to the terminal unless you pass `stderr=subprocess.PIPE`).

Prefer `subprocess.run()` in new code — it is more explicit and handles all cases.

---

## shell=True — What It Does and Why to Avoid It

Imagine handing a note to a translator who reads it aloud in a public square, where anyone nearby can add their own words before the message reaches its destination. That is `shell=True`: your command string passes through `/bin/sh`, which interprets special characters — and if any part of that string came from user input, the "anyone nearby" is the attacker. The list form bypasses the shell entirely and delivers each argument directly to the OS, with no interpreter in the middle.

```
subprocess.run("ls -la | grep py", shell=True)
                ↑
                passed as-is to /bin/sh -c "ls -la | grep py"
```

`shell=True` passes your command string to the system shell (`/bin/sh` on Unix). The shell interprets it — so pipes (`|`), redirects (`>`), glob expansion (`*.py`), environment variable substitution (`$HOME`), and chaining (`&&`, `;`) all work.

### The Injection Risk

```python
# User provides this value from a form field:
user_input = "foo; rm -rf /"

# DANGEROUS — attacker injects arbitrary shell commands:
subprocess.run(f"echo {user_input}", shell=True)
# Runs: echo foo; rm -rf /
```

When `shell=False` (the default), this is impossible — each list element is passed verbatim to the OS as a single argument. There is no shell to interpret `;` as a command separator.

### When shell=True Is Actually Needed

```
Scenario                              | Solution
--------------------------------------|------------------------------------------
Pipe between commands (cmd1 | cmd2)  | Use Popen with two processes (see below)
Shell built-ins: cd, source, export  | Usually avoidable; restructure in Python
Glob expansion: *.log                | Use glob.glob() in Python instead
One-off scripts you fully control    | Acceptable if no user input involved
```

### Safe Alternative to shell=True

```python
# Instead of:
subprocess.run("cat /var/log/app.log | grep ERROR | tail -20", shell=True)

# Do this in Python:
import subprocess
cat = subprocess.Popen(["cat", "/var/log/app.log"], stdout=subprocess.PIPE)
grep = subprocess.Popen(["grep", "ERROR"], stdin=cat.stdout, stdout=subprocess.PIPE)
tail = subprocess.Popen(["tail", "-20"], stdin=grep.stdout, stdout=subprocess.PIPE)
cat.stdout.close()
grep.stdout.close()
output, _ = tail.communicate()
print(output.decode())
```

More verbose, but injection-proof and works identically.

---

## Popen — For Long-Running Processes and Real-Time Output

Think of `subprocess.run()` as ordering takeout — you place the order and wait until it is ready before you do anything else. `subprocess.Popen` is like cooking it yourself in a restaurant kitchen — you can check on it, stir it, add ingredients, and taste as it goes.

`Popen` starts the process immediately and returns control to your Python code. You then interact with it as it runs.

```
subprocess.run()    ← wait here until the process finishes, then return
subprocess.Popen()  ← start the process, return immediately, interact as needed
```

### Basic Popen Usage

```python
import subprocess

proc = subprocess.Popen(
    ["python3", "long_script.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

# Option 1: wait and collect all output at once
stdout, stderr = proc.communicate()   # ← blocks until process exits
print(f"Exit code: {proc.returncode}")
```

### Streaming Output Line by Line

The most common reason to reach for `Popen` over `run()`:

```python
proc = subprocess.Popen(
    ["tail", "-f", "/var/log/app.log"],
    stdout=subprocess.PIPE,
    text=True,
)

try:
    for line in proc.stdout:            # ← each iteration yields one line as it arrives
        print(f"[LOG] {line}", end="")  # ← real-time streaming
except KeyboardInterrupt:
    proc.terminate()
```

### Checking if a Process is Still Running

```python
proc = subprocess.Popen(["sleep", "60"])

status = proc.poll()    # ← returns None if still running, returncode if done
if status is None:
    print("Still running")
else:
    print(f"Finished with code {status}")
```

### Stopping a Process

```python
proc = subprocess.Popen(["long-running-tool"])

proc.terminate()    # ← sends SIGTERM (graceful shutdown request)
proc.kill()         # ← sends SIGKILL (immediate kill, cannot be caught)
proc.wait()         # ← wait for it to actually stop before continuing
```

Always call `proc.wait()` or `proc.communicate()` after terminating to avoid zombie processes.

### Context Manager (Recommended)

```python
with subprocess.Popen(
    ["ffmpeg", "-i", "input.mp4", "output.mp4"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
) as proc:
    stdout, stderr = proc.communicate()
# proc is guaranteed cleaned up here
```

---

## Pipes Between Processes

Unix pipelines are one of computing's most elegant ideas: the output of one program becomes the input of the next, and complex transformations assemble from simple, focused tools. `shell=True` lets the shell wire those pipes for you, but it trades safety for convenience. Doing it in Python with `Popen` is more verbose, but it is injection-proof and gives you full control over each process's lifetime.

Reproducing `cmd1 | cmd2` without `shell=True`:

```
ps aux | grep python

  proc1 = Popen(["ps", "aux"],    stdout=PIPE)
                                        ↓
  proc2 = Popen(["grep", "python"], stdin=proc1.stdout, stdout=PIPE)
```

```python
import subprocess

proc1 = subprocess.Popen(["ps", "aux"], stdout=subprocess.PIPE)
proc2 = subprocess.Popen(
    ["grep", "python"],
    stdin=proc1.stdout,          # ← connect proc1's output to proc2's input
    stdout=subprocess.PIPE,
    text=True,
)
proc1.stdout.close()             # ← allow proc1 to receive SIGPIPE if proc2 exits early
output, _ = proc2.communicate()
print(output)
```

**Why close `proc1.stdout` before `proc2.communicate()`?** If `proc2` exits early (e.g., grep finds nothing), `proc1` needs to receive `SIGPIPE` to stop writing. If you hold the file descriptor open in the parent process, `proc1` will never get that signal and will hang.

---

## Passing Environment Variables

A subprocess inherits its parent's environment the same way a new employee inherits the office culture — everything is passed down by default. But when you override `env=`, you are handing the new hire a completely blank rulebook with only the pages you wrote. Forget to include `PATH` and the subprocess cannot find any commands at all. The safe pattern is always: copy the full environment first, then add or override the specific variables you need.

Subprocesses inherit the parent process environment by default (when `env=None`). When you pass `env=...`, you replace the entire environment.

```python
import os
import subprocess

# WRONG — strips ALL system env vars including PATH
# The subprocess cannot find any commands
subprocess.run(["git", "status"], env={"MY_TOKEN": "secret"})

# CORRECT — start from current env, add/override specific vars
custom_env = os.environ.copy()          # ← copy the full current environment
custom_env["MY_TOKEN"] = "secret"       # ← add or override
custom_env["DEBUG"] = "1"

subprocess.run(["my-tool"], env=custom_env)
```

```
os.environ.copy()
    ↓
{"PATH": "/usr/bin:/bin:...",   ← all existing vars preserved
 "HOME": "/Users/you",
 "LANG": "en_US.UTF-8",
 ...
 "MY_TOKEN": "secret",         ← your addition
 "DEBUG": "1"}                 ← your addition
```

---

## Real-World Patterns

The best way to internalize subprocess is to see it doing real work. Each pattern below solves a problem that comes up in production — git automation, AWS CLI calls, health checks, build scripts — using the same core principles: list form, `check=True`, `text=True`, and explicit timeouts.

### Run git commands and parse output

```python
def get_current_branch() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()   # ← strip trailing newline

def get_last_n_commits(n: int) -> list[str]:
    result = subprocess.run(
        ["git", "log", "--oneline", f"-{n}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().splitlines()
```

### Run AWS CLI and parse JSON

```python
import json
import subprocess

def get_secret(secret_name: str) -> dict:
    result = subprocess.run(
        ["aws", "secretsmanager", "get-secret-value",
         "--secret-id", secret_name,
         "--query", "SecretString",
         "--output", "text"],
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    return json.loads(result.stdout)   # ← parse the JSON string output
```

### Health check in CI

```python
def service_is_healthy(url: str) -> bool:
    result = subprocess.run(
        ["curl", "--silent", "--fail", "--max-time", "5", url],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0      # ← no check=True; we handle the result ourselves
```

### Execute a shell script with parameters

```python
subprocess.run(
    ["/usr/local/bin/deploy.sh", "--env", "production", "--version", "1.2.3"],
    check=True,
    cwd="/opt/app",
    env={**os.environ, "DEPLOY_KEY": os.environ["CI_DEPLOY_KEY"]},
    timeout=300,
)
```

### Run a Python script as a subprocess

```python
import sys
import subprocess

result = subprocess.run(
    [sys.executable, "scripts/migrate.py", "--dry-run"],   # ← sys.executable = same Python
    capture_output=True,
    text=True,
    check=True,
)
print(result.stdout)
```

Using `sys.executable` ensures the subprocess uses the same virtual environment Python as the current process.

### Stream build output in real time

```python
def run_build(project_dir: str):
    with subprocess.Popen(
        ["make", "all"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,   # ← merge so we see errors inline
        text=True,
        cwd=project_dir,
    ) as proc:
        for line in proc.stdout:
            print(line, end="", flush=True)   # ← flush each line immediately
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, "make all")
```

---

## Common Mistakes

Most subprocess bugs follow a short list of patterns — the same ones that surface on Stack Overflow over and over. Knowing these in advance means diagnosing a hanging process or a silent failure in seconds rather than minutes of confused debugging.

```
Mistake                             | Effect                          | Fix
------------------------------------|----------------------------------|------------------------------
shell=True with user input          | Command injection vulnerability  | Use list form, shell=False
Forgetting text=True                | stdout/stderr are bytes, not str | Always add text=True
Not using check=True                | Silent failures — wrong exit     | Add check=True or check manually
No timeout set                      | Process hangs forever            | Always set timeout=N
env={"KEY": "val"} alone            | Strips PATH, HOME, all sys vars  | os.environ.copy() then update
Not closing proc1.stdout in pipes   | proc1 hangs waiting for reader   | Call proc1.stdout.close()
Popen without communicate/wait      | Zombie processes, resource leak  | Always call communicate() or wait()
Parsing stderr for success signals  | Fragile, breaks on version bumps | Parse stdout, check returncode
```

---

## Quick Reference: run() vs Popen

Choosing between `run()` and `Popen` is like choosing between a vending machine and a full kitchen. The vending machine (`run()`) is perfect 95% of the time — you press a button, you get your item, done. The kitchen (`Popen`) is there for when you need to watch something cook, start multiple burners simultaneously, or pull it off the heat based on taste. Default to `run()` and reach for `Popen` only when you need the extra control.

```
Use subprocess.run() when:
  - You want to wait for the command to finish before continuing
  - You need all output at once after the process exits
  - The process is short-lived (seconds to minutes)
  - 95% of real-world use cases

Use subprocess.Popen() when:
  - You need to stream output line by line as it arrives
  - You need to send data to stdin interactively
  - You need to run multiple processes in parallel
  - You need to check if a process is still running (poll())
  - You need to kill a process based on a condition
```

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [07_modules_packages/theory.md](../theory.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⬅️ Prev Subfolder | [02_argparse ←](../02_argparse/theory.md) |
| ➡️ Next Subfolder | [04_virtual_environments →](../04_virtual_environments/theory.md) |

---

**Related:** [01_sys_module](../01_sys_module/theory.md) · [02_argparse](../02_argparse/theory.md) · [04_virtual_environments](../04_virtual_environments/theory.md)
