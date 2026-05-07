# 💻 Practice — subprocess

> For hints and answers, expand the dropdowns. Work through each problem in `practice_local.py` first.

---

## Quick Index

| Q# | Topic | Difficulty |
|---|---|---|
| Q1 | Basic run — echo and print output | 🟢 Easy |
| Q2 | Check returncode without raising | 🟢 Easy |
| Q3 | capture_output with text=True | 🟢 Easy |
| Q4 | check=True and CalledProcessError | 🟡 Medium |
| Q5 | Working directory with cwd= | 🟡 Medium |
| Q6 | Passing env vars | 🟡 Medium |
| Q7 | timeout and TimeoutExpired | 🟡 Medium |
| Q8 | check_output() with error handling | 🟡 Medium |
| Q9 | shell=True dangers and safe rewrite | 🟡 Medium |
| Q10 | Popen streaming output | 🟠 Hard |
| Q11 | Pipe between two processes | 🟠 Hard |
| Q12 | Capstone — run_command() helper | 🟠 Hard |

---

## Q1 🟢 · Basic run — Run echo and print output

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

Run `echo "hello world"` using `subprocess.run()` and print its captured output.

<details>
<summary>Hint</summary>

Use `capture_output=True` and `text=True` so the output comes back as a string. Access it via `result.stdout`.

</details>

<details>
<summary>Answer</summary>

```python
import subprocess

result = subprocess.run(
    ["echo", "hello world"],
    capture_output=True,
    text=True,
)
print(result.stdout)   # hello world
```

`capture_output=True` is shorthand for `stdout=PIPE, stderr=PIPE`. Without it, output goes straight to the terminal and `result.stdout` is `None`.

</details>

---

## Q2 🟢 · Check returncode — Run a failing command without raising

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

Run `ls /nonexistent` and inspect the `returncode` without letting the program crash.

<details>
<summary>Hint</summary>

Do NOT use `check=True` here. Let the command fail silently, then read `result.returncode` yourself.

</details>

<details>
<summary>Answer</summary>

```python
import subprocess

result = subprocess.run(
    ["ls", "/nonexistent"],
    capture_output=True,
    text=True,
    # no check=True — we handle the result manually
)

print(f"Return code: {result.returncode}")   # non-zero (1 or 2 depending on OS)
print(f"stderr: {result.stderr.strip()}")    # e.g. "ls: /nonexistent: No such file or directory"

if result.returncode != 0:
    print("Command failed — handling gracefully")
```

`returncode == 0` means success. Any non-zero value signals failure. The exact value is command-specific (e.g. `ls` returns `1` or `2` depending on the OS).

</details>

---

## Q3 🟢 · capture_output — Capture git --version as a string

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

Run `git --version` and capture its stdout as a Python string (not bytes).

<details>
<summary>Hint</summary>

`text=True` tells subprocess to decode the bytes output using UTF-8 automatically. Without it, `result.stdout` is `bytes`.

</details>

<details>
<summary>Answer</summary>

```python
import subprocess

result = subprocess.run(
    ["git", "--version"],
    capture_output=True,
    text=True,
    check=True,
)

version = result.stdout.strip()
print(version)              # git version 2.x.x
print(type(version))        # <class 'str'>
```

Without `text=True`, you would get `b'git version 2.x.x\n'` (bytes) and need to call `.decode("utf-8")` manually.

</details>

---

## Q4 🟡 · check=True — Catch CalledProcessError from a failing command

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

Use `check=True` to run a command that will fail. Catch the `CalledProcessError` and print the returncode and stderr.

<details>
<summary>Hint</summary>

`subprocess.CalledProcessError` is raised when `check=True` and the exit code is non-zero. The exception object carries `.returncode`, `.stdout`, and `.stderr`.

</details>

<details>
<summary>Answer</summary>

```python
import subprocess

try:
    subprocess.run(
        ["ls", "/this/path/does/not/exist"],
        capture_output=True,
        text=True,
        check=True,   # ← raises if returncode != 0
    )
except subprocess.CalledProcessError as e:
    print(f"Command failed. Exit code: {e.returncode}")
    print(f"stderr: {e.stderr.strip()}")
```

When `check=True` triggers, you never see the `CompletedProcess` object — the exception carries all the diagnostic info you need.

</details>

---

## Q5 🟡 · Working directory — Run ls in a specific directory using cwd=

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

Run `ls` and have it list the contents of `/tmp` by setting the working directory, not by passing the path as an argument.

<details>
<summary>Hint</summary>

`cwd=` sets the working directory for the subprocess before it starts. The process sees that directory as its current directory.

</details>

<details>
<summary>Answer</summary>

```python
import subprocess

result = subprocess.run(
    ["ls"],
    capture_output=True,
    text=True,
    check=True,
    cwd="/tmp",   # ← subprocess starts in /tmp
)

print(result.stdout)
```

This is equivalent to `cd /tmp && ls` in the shell, but without `shell=True`. Useful for running build tools, git commands, or scripts that expect to be run from a specific directory.

</details>

---

## Q6 🟡 · Passing env vars — Inject a custom environment variable

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

Run a Python one-liner subprocess that reads and prints a custom environment variable you inject via `env=`.

<details>
<summary>Hint</summary>

Always start from `os.environ.copy()` before adding your vars. Passing only `{"MY_VAR": "value"}` strips PATH and every other system variable — the subprocess cannot even find `python3`.

</details>

<details>
<summary>Answer</summary>

```python
import os
import subprocess

custom_env = os.environ.copy()
custom_env["GREETING"] = "hello from parent"

result = subprocess.run(
    ["python3", "-c", "import os; print(os.environ['GREETING'])"],
    capture_output=True,
    text=True,
    check=True,
    env=custom_env,
)

print(result.stdout.strip())   # hello from parent
```

The child process inherits all system env vars plus the one you added. Without `os.environ.copy()`, the child would have no PATH and the `python3` executable would not be found.

</details>

---

## Q7 🟡 · timeout — Run a command with a timeout and catch TimeoutExpired

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

Run a command that sleeps for 30 seconds. Set a 2-second timeout. Catch `TimeoutExpired` and print a message.

<details>
<summary>Hint</summary>

`timeout=` takes seconds (int or float). When it fires, the subprocess is killed and `subprocess.TimeoutExpired` is raised. The process is already dead by the time you handle the exception.

</details>

<details>
<summary>Answer</summary>

```python
import subprocess

try:
    subprocess.run(
        ["sleep", "30"],
        timeout=2,    # ← kill after 2 seconds
        check=True,
    )
except subprocess.TimeoutExpired as e:
    print(f"Command timed out after {e.timeout}s")
    print(f"Command was: {e.cmd}")
```

Always set a timeout on commands that could hang (network calls, long-running builds, external tools). Without it, your program can block indefinitely.

</details>

---

## Q8 🟡 · check_output — Capture the output of date using check_output()

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

Use `subprocess.check_output()` to capture the current date. Handle `CalledProcessError` if it arises.

<details>
<summary>Hint</summary>

`check_output()` returns the stdout directly as its return value (not a `CompletedProcess` object). Pass `text=True` to get a string instead of bytes.

</details>

<details>
<summary>Answer</summary>

```python
import subprocess

try:
    output = subprocess.check_output(["date"], text=True)
    print(output.strip())
except subprocess.CalledProcessError as e:
    print(f"Failed with exit code {e.returncode}")
```

`check_output()` is equivalent to `subprocess.run(..., capture_output=True, text=True, check=True).stdout`. Prefer `subprocess.run()` in new code — it is more explicit and gives you stderr access too.

</details>

---

## Q9 🟡 · shell=True dangers — Explain the risk and rewrite safely

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

Given this code:

```python
user_input = input("Enter filename: ")
subprocess.run(f"ls {user_input}", shell=True)
```

(a) Explain exactly what happens if `user_input = "; rm -rf ~"`.
(b) Rewrite it safely without `shell=True`.

<details>
<summary>Hint</summary>

With `shell=True`, the string is passed to `/bin/sh -c "..."`. The shell interprets `;` as a command separator, so anything after it runs as a separate command with full privileges.

</details>

<details>
<summary>Answer</summary>

**(a) What goes wrong:**

```python
user_input = "; rm -rf ~"
# shell receives: /bin/sh -c "ls ; rm -rf ~"
# runs two commands: ls (harmless), then rm -rf ~ (deletes home dir)
```

The `;` is interpreted by the shell as "run the next command". The attacker controls what runs next.

**(b) Safe rewrite:**

```python
import subprocess

user_input = input("Enter filename: ")

result = subprocess.run(
    ["ls", user_input],   # ← each element is one literal argument, no shell involved
    capture_output=True,
    text=True,
)
print(result.stdout)
```

With `shell=False` (the default), `user_input` is passed as a single literal argument to `ls`. The OS does not interpret `;`, `&&`, `|`, or any other shell metacharacter. Injection is impossible.

</details>

---

## Q10 🟠 · Popen streaming — Stream output line by line as it arrives

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

Use `subprocess.Popen` to run a command that produces output over time and print each line as it arrives, rather than waiting for the full output.

Use `ping -c 5 localhost` (or `python3 -c "import time; [print(i, flush=True) or time.sleep(0.5) for i in range(5)]"`) as your long-running command.

<details>
<summary>Hint</summary>

Iterate directly over `proc.stdout` — each iteration blocks until the next line arrives, giving you real-time streaming. `subprocess.run()` cannot do this; it buffers everything first.

</details>

<details>
<summary>Answer</summary>

```python
import subprocess

proc = subprocess.Popen(
    ["python3", "-c",
     "import time; [print(i, flush=True) or time.sleep(0.5) for i in range(5)]"],
    stdout=subprocess.PIPE,
    text=True,
)

for line in proc.stdout:
    print(f"[stream] {line}", end="")

proc.wait()   # ← reap the process after stdout is exhausted
print(f"\nExit code: {proc.returncode}")
```

Each iteration of `for line in proc.stdout` blocks until the subprocess writes a line and flushes it. You see output as it arrives — not after the process finishes. Always call `proc.wait()` or `proc.communicate()` afterward to clean up.

</details>

---

## Q11 🟠 · Pipe between processes — echo into wc -w without shell=True

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

Reproduce `echo "hello world" | wc -w` using two `Popen` objects and `stdout=PIPE` / `stdin=`.

<details>
<summary>Hint</summary>

Connect `proc1.stdout` to `proc2`'s `stdin=`. After starting both processes, call `proc1.stdout.close()` in the parent — this lets `proc1` receive SIGPIPE if `proc2` exits early.

</details>

<details>
<summary>Answer</summary>

```python
import subprocess

proc1 = subprocess.Popen(
    ["echo", "hello world"],
    stdout=subprocess.PIPE,
)

proc2 = subprocess.Popen(
    ["wc", "-w"],
    stdin=proc1.stdout,       # ← wire proc1's stdout to proc2's stdin
    stdout=subprocess.PIPE,
    text=True,
)

proc1.stdout.close()          # ← allow proc1 to receive SIGPIPE if proc2 exits early
output, _ = proc2.communicate()

print(output.strip())         # 2  (two words: "hello" and "world")
```

Why `proc1.stdout.close()`? The parent process holds an open file descriptor to that pipe. If you don't close it, `proc1` will never get SIGPIPE when `proc2` is done reading — `proc1` will hang waiting for a reader that no longer exists.

</details>

---

## Q12 🟠 · Capstone — Write a run_command() helper that never raises

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

Write a function `run_command(cmd, cwd=None, env=None, timeout=30)` that:
- Runs the command
- Returns a named tuple or tuple of `(returncode, stdout, stderr)`
- Never raises an exception — catches `CalledProcessError`, `TimeoutExpired`, and `FileNotFoundError`
- On timeout, returns `returncode=-1, stdout="", stderr="timed out"`
- On file not found, returns `returncode=-2, stdout="", stderr="command not found: <cmd[0]>"`

<details>
<summary>Hint</summary>

Do NOT use `check=True` — you are handling the result yourself. Catch all three subprocess exceptions explicitly and return a consistent tuple for each case.

</details>

<details>
<summary>Answer</summary>

```python
import subprocess
import os
from typing import NamedTuple

class CommandResult(NamedTuple):
    returncode: int
    stdout: str
    stderr: str

def run_command(
    cmd: list[str],
    cwd: str = None,
    env: dict = None,
    timeout: int = 30,
) -> CommandResult:
    """Run a shell command. Returns (returncode, stdout, stderr). Never raises."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            env=env,
            timeout=timeout,
            # no check=True — we handle returncode ourselves
        )
        return CommandResult(result.returncode, result.stdout, result.stderr)

    except subprocess.TimeoutExpired:
        return CommandResult(-1, "", f"timed out after {timeout}s")

    except FileNotFoundError:
        return CommandResult(-2, "", f"command not found: {cmd[0]}")

    except subprocess.CalledProcessError as e:
        # only reachable if check=True is added later — defensive catch
        return CommandResult(e.returncode, e.stdout or "", e.stderr or "")


# Usage
rc, out, err = run_command(["git", "status"], cwd="/tmp")
print(rc, out, err)

rc, out, err = run_command(["sleep", "60"], timeout=1)
print(rc, err)   # -1, timed out after 1s

rc, out, err = run_command(["notarealthing"])
print(rc, err)   # -2, command not found: notarealthing
```

The sentinel codes (`-1`, `-2`) distinguish "timed out" from "not found" from "ran and failed" (`returncode > 0`). Using a `NamedTuple` makes the return value self-documenting and unpacks cleanly.

</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [07_modules_packages/theory.md](../theory.md) |
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Practice File | [practice_local.py](./practice_local.py) |
| ⬅️ Prev Subfolder | [02_argparse ←](../02_argparse/practice.md) |
| ➡️ Next Subfolder | [04_virtual_environments →](../04_virtual_environments/practice.md) |
