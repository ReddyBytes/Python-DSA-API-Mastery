# 💻 Practice — Virtual Environments

> For hints and answers, expand the dropdowns. Work through each problem in `practice_local.py` first.

---

## Quick Index

| Q# | Topic | Difficulty |
|---|---|---|
| Q1 | Create and activate | 🟢 Beginner |
| Q2 | Requirements freeze | 🟢 Beginner |
| Q3 | Which python | 🟢 Beginner |
| Q4 | requirements.txt | 🟡 Intermediate |
| Q5 | pip install -e | 🟡 Intermediate |
| Q6 | venv structure | 🟡 Intermediate |
| Q7 | .gitignore | 🟡 Intermediate |
| Q8 | pyproject.toml basics | 🟡 Intermediate |
| Q9 | Diagnose ModuleNotFoundError | 🟡 Intermediate |
| Q10 | poetry workflow | 🟠 Advanced |
| Q11 | pyenv | 🟠 Advanced |
| Q12 | Capstone | 🟠 Advanced |

---

## Q1 🟢 · Create and activate — venv creation commands

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

Write the exact commands to create a venv called `env`, activate it on macOS/Linux, and verify it's active.

<details>
<summary>Hint</summary>

`python3 -m venv` creates the directory. Activation modifies your `$PATH`. There's a built-in command that shows you where `python` currently resolves.

</details>

<details>
<summary>Answer</summary>

```bash
# Create the venv
python3 -m venv env

# Activate (macOS/Linux)
source env/bin/activate

# Verify it's active — prompt changes and which python points into the venv
which python        # → /your/project/env/bin/python
python --version    # confirm version

# Also check:
echo $VIRTUAL_ENV   # → /your/project/env
```

Note: convention is `.venv` (hidden) not `env`, but `env` is perfectly valid. The key tell is that `which python` points inside your project directory, not to `/usr/bin/python3` or a Homebrew path.

</details>

---

## Q2 🟢 · Requirements freeze — capturing and reproducing environments

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

What does `pip freeze > requirements.txt` do? When would you run it? Write the command to recreate the env on another machine.

<details>
<summary>Hint</summary>

`pip freeze` lists all installed packages with their exact pinned versions. Think: when is "exact version" important?

</details>

<details>
<summary>Answer</summary>

`pip freeze` outputs every installed package and its exact version in `package==version` format. Redirecting to `requirements.txt` captures that snapshot.

**When to run it:** After you've finished installing all your project's dependencies and they're working correctly — before committing, before sharing, before deploying.

**Recreate on another machine:**

```bash
# On the new machine:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This installs the exact same versions, making the environment reproducible. Without pinned versions, `pip install` fetches the latest — which may have breaking changes.

</details>

---

## Q3 🟢 · Which python — confirming you're in the venv

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

After activating a venv, which command confirms you're using the venv's Python (not the system one)?

<details>
<summary>Hint</summary>

Two approaches: one shell command, one Python one-liner. The Python one-liner is more reliable because it checks what the interpreter itself thinks its path is.

</details>

<details>
<summary>Answer</summary>

```bash
# Shell approach
which python          # should point to .venv/bin/python (or env/bin/python)

# Python approach — more reliable, works even in scripts
python -c "import sys; print(sys.executable)"
```

The Python approach is the gold standard. `which python` can be fooled by shell aliases or PATH ordering. `sys.executable` is the actual binary path the running interpreter knows about itself.

Expected output when venv is active:
```
/Users/yourname/yourproject/.venv/bin/python
```

If you see `/usr/bin/python3` or `/opt/homebrew/bin/python3` — the venv is not active, or the wrong binary is running your script.

</details>

---

## Q4 🟡 · requirements.txt — installing and upgrading selectively

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

You have a `requirements.txt` with `requests==2.28.0` and `flask`. Write the command to install from it, then upgrade only `flask`.

<details>
<summary>Hint</summary>

Installing from a requirements file is one command. Upgrading a single package doesn't touch the file — it's a separate install command with a flag.

</details>

<details>
<summary>Answer</summary>

```bash
# Install everything from requirements.txt
pip install -r requirements.txt

# Upgrade only flask (does not affect requests)
pip install --upgrade flask
# or equivalently:
pip install -U flask

# After upgrading, re-freeze to capture the new version:
pip freeze > requirements.txt
```

Important: `pip install --upgrade flask` upgrades flask and its dependencies, but leaves `requests==2.28.0` untouched because it's not a flask dependency. If you want to see what version was installed: `pip show flask`.

</details>

---

## Q5 🟡 · pip install -e — editable installs

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

What does `pip install -e .` do? When would you use it in your own project?

<details>
<summary>Hint</summary>

The `-e` flag stands for "editable". Think about what happens when you're developing a library and you want your changes to take effect immediately without reinstalling.

</details>

<details>
<summary>Answer</summary>

`pip install -e .` installs the current directory as a package in **editable mode**. Instead of copying your code into `site-packages`, it creates a link (`.pth` file or direct reference) pointing back to your source directory.

**Effect:** Any change you make to your source files is immediately reflected when you `import` the package — no reinstall needed.

**When to use it:**
- You're developing a library or package and want to test it in another project
- You have a `src/` layout and need your package importable from tests
- You're working on a shared internal package and want live edits

```bash
# Your project has a pyproject.toml or setup.py
pip install -e .

# Now you can import your package anywhere in the venv:
python -c "import mypackage"   # picks up live source changes
```

**Contrast with regular install:** `pip install .` copies your code to site-packages at install time. Changes to source require reinstalling.

</details>

---

## Q6 🟡 · venv structure — what's inside and how Python finds packages

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

Describe what's in `venv/lib/python3.11/site-packages/` and how Python finds packages there via `sys.path`.

<details>
<summary>Hint</summary>

`site-packages` is where pip deposits installed packages. `sys.path` is the search list Python walks when resolving an import. How does Python know to look in the venv's site-packages?

</details>

<details>
<summary>Answer</summary>

**`site-packages/` contents:**
Every package installed via `pip` lands here as a directory (or single `.py` file for simple packages). For example, after `pip install requests`:
```
venv/lib/python3.11/site-packages/
├── requests/           ← the package directory
├── requests-2.28.0.dist-info/  ← metadata (version, deps, files list)
├── certifi/            ← requests' dependency
└── ...
```

**How Python finds it:**
When you activate a venv, the `activate` script prepends the venv's `bin/` to `$PATH`. More importantly, the venv's Python binary was compiled with knowledge of its own `lib/pythonX.Y/site-packages/` path. The `site` module (auto-imported at startup) adds this path to `sys.path`.

```python
import sys
print(sys.path)
# [
#   '',                                          ← script's directory
#   '/usr/lib/python311.zip',                    ← frozen stdlib
#   '/usr/lib/python3.11',                       ← stdlib
#   '/your/project/.venv/lib/python3.11/site-packages',  ← YOUR PACKAGES
# ]
```

Python walks `sys.path` left to right and returns the first match. The venv's site-packages entry is added by the `site` module based on which Python binary is running — this is why running the wrong binary means imports fail even if the venv is "active".

</details>

---

## Q7 🟡 · .gitignore — what to exclude and why

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

What should you add to `.gitignore` for a venv? Why should you never commit the venv directory?

<details>
<summary>Hint</summary>

Think about what's inside a venv: compiled binaries, absolute paths, OS-specific files. What happens if another developer on a different OS clones it?

</details>

<details>
<summary>Answer</summary>

**Add to `.gitignore`:**

```gitignore
# Virtual environments — all common names
.venv/
venv/
env/
.env/

# Also common:
ENV/
venv.bak/
```

**Why never commit the venv:**

1. **Size** — a venv with a few packages can be 50–500MB. It bloats the repo and makes clones slow.

2. **Absolute paths** — `pyvenv.cfg` and activation scripts contain hardcoded paths to where the venv was created on your machine (`home = /Users/yourname/...`). These paths are wrong on every other machine.

3. **OS-specific binaries** — compiled `.so`/`.dylib` files for macOS won't run on Linux. Windows paths differ entirely (`.venv/Scripts/` vs `.venv/bin/`).

4. **Version-specific bytecode** — `.pyc` files are tied to a specific Python minor version.

**The right approach:** commit `requirements.txt` (or `pyproject.toml`). Each developer runs `pip install -r requirements.txt` to create their own local venv.

</details>

---

## Q8 🟡 · pyproject.toml basics — minimal project spec

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

Write a minimal `pyproject.toml` for a project named "myapp" with Python ≥3.11 and two dependencies: `requests` and `pydantic`.

<details>
<summary>Hint</summary>

`pyproject.toml` replaced `setup.py` as the modern Python packaging standard (PEP 517/518). The `[project]` table holds metadata. Dependencies are a list of strings in pip-compatible format.

</details>

<details>
<summary>Answer</summary>

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.28",
    "pydantic>=2.0",
]
```

**Key fields explained:**
- `[build-system]` — tells pip how to build the package. `hatchling` is the modern default; `setuptools` is the traditional alternative.
- `requires-python` — pip will refuse to install on older Python versions.
- `dependencies` — equivalent to `install_requires` in old `setup.py`. Version specifiers are optional but recommended.

**Optional additions for dev tools:**

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "black>=23.0",
    "mypy>=1.0",
]
```

Install dev deps with: `pip install -e ".[dev]"`

</details>

---

## Q9 🟡 · Diagnose ModuleNotFoundError — 3 causes and fixes

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

A script raises `ModuleNotFoundError: No module named 'requests'` even though you pip-installed it. List 3 reasons this happens and how to diagnose each.

<details>
<summary>Hint</summary>

The root cause is always: the Python running your script is not the same Python that has `requests` installed. There are multiple ways this mismatch can happen.

</details>

<details>
<summary>Answer</summary>

**Cause 1 — Venv not activated**

The venv with `requests` installed isn't active in this shell session.

```bash
# Diagnose:
python -c "import sys; print(sys.executable)"
# If it shows /usr/bin/python3 or /opt/homebrew/bin/python3 → venv not active

# Fix:
source .venv/bin/activate
```

**Cause 2 — Installed into the wrong Python**

You ran `pip install requests` but `pip` belonged to a different Python than the one running your script.

```bash
# Diagnose:
which pip            # which pip are you using?
which python         # which python are you using?
# If they point to different locations → mismatch

# Fix: always install using the running Python:
python -m pip install requests
```

**Cause 3 — Running the script with an explicit Python path that bypasses the venv**

Your script is invoked with `python3 script.py` or `/usr/bin/python3 script.py` instead of the venv's Python.

```bash
# Diagnose:
python3 -c "import sys; print(sys.executable)"  # system Python
.venv/bin/python -c "import sys; print(sys.executable)"  # venv Python
# Check which one has requests:
python3 -c "import requests"             # fails
.venv/bin/python -c "import requests"   # works

# Fix: use the venv's Python explicitly, or activate the venv first:
source .venv/bin/activate && python script.py
# or use shebang in the script pointing to the venv Python
```

**Quick universal diagnostic:**
```bash
python -c "import sys; print(sys.executable); print('\n'.join(sys.path))"
pip show requests   # compare Location: path to sys.path entries above
```

</details>

---

## Q10 🟠 · poetry workflow — dependency management commands

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

Write the sequence of `poetry` commands to: init a new project, add `fastapi` as a dependency, add `pytest` as a dev dependency, and run tests.

<details>
<summary>Hint</summary>

`poetry` wraps venv creation, dependency resolution, and lock file management into a single tool. It distinguishes between regular deps and dev-only deps via groups.

</details>

<details>
<summary>Answer</summary>

```bash
# 1. Initialize a new project (creates pyproject.toml, src layout, git init)
poetry new myproject
cd myproject

# Or if you're in an existing directory:
poetry init    # interactive wizard

# 2. Add fastapi as a production dependency
poetry add fastapi

# This does three things:
# - Resolves compatible versions
# - Updates pyproject.toml [tool.poetry.dependencies]
# - Updates poetry.lock with exact pinned versions

# 3. Add pytest as a dev-only dependency
poetry add --group dev pytest

# 4. Run tests (poetry uses its managed venv automatically)
poetry run pytest

# Other useful commands:
poetry install          # install all deps from poetry.lock (reproducible)
poetry update           # update deps to latest compatible versions
poetry shell            # activate the managed venv in a subshell
poetry show             # list installed packages
poetry env info         # show venv location and Python version
```

**Key difference from venv+pip:** `poetry.lock` pins the entire dependency tree (including transitive deps) to exact versions. `requirements.txt` only pins top-level packages unless you use `pip freeze`. This makes poetry installs fully reproducible without manual effort.

</details>

---

## Q11 🟠 · pyenv — version management vs isolation

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

Explain what pyenv does vs what venv does. Write the commands to install Python 3.12 via pyenv and set it as the local version for a project.

<details>
<summary>Hint</summary>

They solve different problems and are meant to be used together, not instead of each other.

</details>

<details>
<summary>Answer</summary>

**pyenv** — manages which Python *version* is installed and active on your machine. It does not isolate packages.

**venv** — creates an isolated package environment for a single Python version. It does not manage Python versions.

They're complementary: pyenv gives you the right Python version, venv gives you an isolated package space for that version.

```
pyenv  →  controls which python3 binary is invoked
venv   →  controls which site-packages that binary looks in
```

**Commands:**

```bash
# Install pyenv (macOS)
brew install pyenv

# Add to shell config (~/.zshrc or ~/.bashrc):
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# List available versions (long list — pipe to grep)
pyenv install --list | grep "3.12"

# Install Python 3.12
pyenv install 3.12.0

# Set as global default (affects all new shells)
pyenv global 3.12.0

# Set as LOCAL version for this project only
# (creates a .python-version file in the current directory)
cd my-project
pyenv local 3.12.0

# Verify
python --version    # → Python 3.12.0
which python        # → /Users/yourname/.pyenv/shims/python

# Now create a venv using this version:
python -m venv .venv
source .venv/bin/activate
```

`.python-version` file is worth committing — it tells other devs (and pyenv) which Python version this project needs.

</details>

---

## Q12 🟠 · Capstone — new developer onboarding README

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

You're onboarding a new developer to your project. Write the complete README "Setup" section: clone, create venv, install deps, set env vars, run tests.

<details>
<summary>Hint</summary>

Think about every command a developer who has never seen your project would need to run, in exact order. Include: prerequisites, clone, Python version, venv, deps, env vars (without leaking secrets), and verification.

</details>

<details>
<summary>Answer</summary>

```markdown
## Setup

### Prerequisites

- Python 3.11+ ([pyenv recommended](https://github.com/pyenv/pyenv))
- Git

### 1. Clone the repository

```bash
git clone https://github.com/your-org/myapp.git
cd myapp
```

### 2. Set up Python version (if using pyenv)

```bash
pyenv install 3.11.6   # skip if already installed
# .python-version file in the repo sets this automatically
```

### 3. Create and activate a virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# Windows: .venv\Scripts\activate.bat
```

### 4. Install dependencies

```bash
pip install -r requirements.txt        # production deps
pip install -r requirements-dev.txt    # dev/test tools
```

### 5. Configure environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set the required values (see `.env.example` for descriptions).
Never commit `.env` — it's in `.gitignore`.

### 6. Verify the setup

```bash
# Confirm you're using the venv Python
python -c "import sys; print(sys.executable)"
# Expected: .../myapp/.venv/bin/python

# Run the test suite
pytest

# Start the development server
python -m myapp
```

### Troubleshooting

If you see `ModuleNotFoundError`, ensure the venv is active:
```bash
source .venv/bin/activate
```

If tests fail on import, confirm you installed dev dependencies:
```bash
pip install -r requirements-dev.txt
```
```

**Key elements of a good onboarding section:**
- Explicit Python version requirement
- venv creation + activation (both platforms)
- Separate prod and dev requirements
- Env var setup via `.env.example` (never commit secrets)
- A verification step so the developer knows it worked
- A short troubleshooting section for the most common failure

</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [07_modules_packages/theory.md](../theory.md) |
| 📖 Theory | [theory.md](./theory.md) |
| 🐍 Practice Local | [practice_local.py](./practice_local.py) |
| ⬅️ Prev Subfolder | [03_subprocess ←](../03_subprocess/theory.md) |

---

**Related:** [01_sys_module](../01_sys_module/theory.md) · [02_argparse](../02_argparse/theory.md) · [03_subprocess](../03_subprocess/theory.md)
