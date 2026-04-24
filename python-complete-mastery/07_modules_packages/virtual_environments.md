# 🎯 Virtual Environments — Complete Guide to Python Isolation

Imagine you are a chef working at two restaurants simultaneously. Restaurant A wants 2014-era recipes — specific ingredients, old techniques. Restaurant B wants modern cuisine with entirely different tools. If you share one kitchen, the tools clash. A **virtual environment** is a separate kitchen for each project — its own Python interpreter, its own installed packages, completely isolated from every other project on your machine.

---

## 📌 Learning Priority

**Must Learn** — daily use, every Python project:
venv creation · activation · pip install · requirements.txt · deactivation

**Should Learn** — important for real projects:
python -m pip · pyvenv.cfg · site-packages path · version pinning · recreating from requirements.txt

**Good to Know** — useful in specific situations:
pipenv · poetry · conda envs · pyenv · tox

**Reference** — know it exists:
virtualenvwrapper · mkvirtualenv · uv

---

## 🧠 Why Virtual Environments Exist

Python has one global package location per interpreter. Every `pip install` without a venv drops packages there. Three problems follow immediately.

**Version conflicts** — Project A needs `django==3.2`. Project B needs `django==4.2`. You cannot install both in the same location. Installing one version overwrites the other. Your projects break each other silently.

**System Python contamination** — macOS and Linux ship with a system Python used internally by the OS. Installing packages into it can break system tools. On modern macOS, Apple deliberately locks this down — `pip install` into `/usr/bin/python3` fails or is discouraged for this reason.

**Reproducibility** — "It works on my machine" happens when two developers have different global package versions. A `requirements.txt` generated from a venv captures exact versions and makes the environment reproducible on any machine.

---

## 🔍 What a venv Actually Is on Disk

A venv is not magic — it is a directory containing a self-contained Python installation:

```
.venv/
├── bin/                          (Scripts/ on Windows)
│   ├── python                    ← symlink or copy of the interpreter
│   ├── python3                   ← same
│   ├── pip                       ← pip that installs INTO this venv only
│   ├── pip3                      ← same
│   └── activate                  ← shell script that modifies PATH
├── lib/
│   └── python3.11/
│       └── site-packages/        ← all installed packages live here
│           ├── numpy/
│           ├── pandas/
│           └── ...
├── include/                      ← C headers for compiled extensions
└── pyvenv.cfg                    ← records base Python version and path
```

`pyvenv.cfg` is the venv's identity card:

```ini
home = /opt/homebrew/bin          # ← where the base Python came from
version = 3.11.6
include-system-site-packages = false  # ← isolated from global packages
```

---

## ⚡ How Python Finds Packages — The Resolution Chain

When you write `import numpy`, Python searches locations **in this exact order**:

```
1. sys.modules          ← cache of already-imported modules (fastest)
2. Built-in modules     ← compiled into the interpreter (math, os, sys)
3. Frozen modules       ← bytecode frozen into the interpreter
4. sys.path entries:
   a. Script's directory
   b. PYTHONPATH environment variable (if set)
   c. Installation-dependent default (site-packages)
```

`sys.path` is constructed at startup based on **which Python binary launched the process** — not which one is in your PATH, not which venv is "active", but which binary is actually executing your script.

```python
# See exactly where your Python looks:
import sys
print(sys.executable)        # which binary is running
print('\n'.join(sys.path))   # in what order it searches
```

This is the root of most `ModuleNotFoundError` issues — the wrong binary is running, so it looks in the wrong site-packages.

---

## 🛠️ Creating a venv

```bash
# Basic — uses whatever python3 resolves to
python3 -m venv .venv

# Specify exact version (recommended)
python3.11 -m venv .venv

# Full path (most explicit, never ambiguous)
/opt/homebrew/bin/python3.11 -m venv .venv

# Without pip (lighter, if you'll install pip separately)
python3.11 -m venv .venv --without-pip

# Allow access to global site-packages (rarely needed)
python3.11 -m venv .venv --system-site-packages

# Upgrade existing venv to a newer Python (recreates binaries only)
python3.12 -m venv .venv --upgrade
```

Convention: name it `.venv` (hidden, at project root). Git-ignore it — never commit a venv.

```gitignore
# .gitignore
.venv/
venv/
env/
```

---

## ▶️ Activating and Deactivating

Activation prepends `.venv/bin/` to your `$PATH` so `python` and `pip` resolve to the venv versions for the duration of the shell session.

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Fish shell
source .venv/bin/activate.fish
```

After activation, your prompt shows the venv name:

```
(.venv) user@machine project %
```

```bash
# Verify you are using the right Python:
which python          # → /your/project/.venv/bin/python
python --version      # → Python 3.11.x

# Deactivate — restores original PATH
deactivate
```

**Important:** Activation only affects the current shell session. Opening a new terminal tab = no venv active.

---

## 📦 Installing Packages

```bash
# Always use this form — eliminates all ambiguity
python -m pip install numpy

# The above is equivalent to, but safer than:
pip install numpy

# Why safer: `pip` in PATH might not match `python` in PATH
# `python -m pip` always uses the pip of the running python

# Install specific version
pip install "numpy==1.26.0"

# Install version range
pip install "numpy>=1.24,<2.0"

# Install multiple packages
pip install numpy pandas matplotlib seaborn

# Install from requirements file
pip install -r requirements.txt

# Install in editable mode (for local packages you are developing)
pip install -e .

# Upgrade an existing package
pip install --upgrade numpy

# Uninstall
pip uninstall numpy
```

---

## 📋 Managing Dependencies

```bash
# Capture current environment — exact versions of everything installed
pip freeze > requirements.txt

# requirements.txt looks like:
# numpy==1.26.0
# pandas==2.1.4
# matplotlib==3.8.2

# Reproduce environment on another machine:
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Best practice — split requirements:**

```
requirements.txt          ← production dependencies only
requirements-dev.txt      ← dev/test tools (pytest, black, mypy)
```

```bash
# requirements-dev.txt often starts with:
-r requirements.txt       # ← includes production deps
pytest==7.4.0
black==23.12.0
mypy==1.8.0
```

---

## 🗺️ The Python Runtimes on Your Machine

Multiple Python installations can coexist. Each is completely independent:

```
/usr/bin/python3              ← macOS system Python (3.9 on older Macs)
                                 DO NOT install packages here
                                 Apple uses it for system tools

/opt/homebrew/bin/python3     ← Homebrew Python (latest stable)
                                 Safe to use, managed by brew

/opt/homebrew/bin/python3.11  ← specific Homebrew version
/opt/homebrew/bin/python3.12  ← another Homebrew version

~/.pyenv/versions/3.11.6/bin/python  ← pyenv-managed version
                                        pyenv lets you switch default Python

.venv/bin/python              ← your project's isolated Python
                                 (symlink to one of the above)
```

Each has its own `site-packages`. A package installed into one is **invisible** to all others.

```bash
# See all Python installations on your machine:
which -a python3

# See where a specific Python's packages live:
python3.11 -c "import site; print(site.getsitepackages())"
```

---

## 🔁 venv vs Other Tools

| Tool | What it does | When to use |
|---|---|---|
| `venv` | Built-in, creates isolated envs | Default choice for most projects |
| `virtualenv` | Third-party, faster, more features than venv | When you need Python 2 support or extra features |
| `pipenv` | venv + Pipfile + lock file in one tool | Teams who want combined dep management |
| `poetry` | Dep management + packaging + publishing | Library authors, complex dep graphs |
| `conda` | Env manager + package manager (includes non-Python packages) | Data science, packages with C/CUDA deps (numpy, torch) |
| `pyenv` | Manages multiple Python versions on one machine | When you need Python 3.9, 3.11, 3.12 side by side |
| `uv` | Rust-based, extremely fast pip/venv replacement | Speed-critical CI/CD, large projects |

For most Python/ML work: **venv + pip** is sufficient and has zero dependencies.

---

## 🐼 conda — Environment Manager for Data Science

**conda** is a different beast from venv. It is not just a Python virtual environment tool — it is a full **package and environment manager** that handles Python itself, non-Python dependencies (C libraries, CUDA, MKL), and binary packages all in one. It ships as part of **Anaconda** (full distribution, ~3GB) or **Miniconda** (minimal installer, ~400MB — recommended).

The key difference from venv: conda environments are not tied to a project directory. They are named environments stored centrally, and you switch between them by name.

---

### Why conda Exists

Some Python packages — `numpy`, `pytorch`, `tensorflow`, `opencv` — wrap compiled C/C++/CUDA code. `pip` installs Python wheels, but the underlying C libraries (BLAS, LAPACK, CUDA toolkit) must already exist on your system. conda installs those C libraries too, eliminating "it compiled but crashes at runtime" failures.

```
pip install numpy     → installs Python wheel, assumes C libraries exist
conda install numpy   → installs Python wheel + MKL/OpenBLAS C libraries together
```

This is why the ML/data science world standardized on conda for years.

---

### Installing conda (Miniconda — recommended)

```bash
# macOS (Apple Silicon)
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh

# macOS (Intel)
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh

# After install, initialize shell integration:
conda init zsh     # or bash, fish

# Restart terminal, then verify:
conda --version
```

---

### Creating and Managing conda Environments

```bash
# Create a named environment with a specific Python version
conda create -n myproject python=3.11

# Create with packages pre-installed
conda create -n mlenv python=3.11 numpy pandas matplotlib

# Activate
conda activate myproject      # ← works on all platforms (no source needed)

# Deactivate
conda deactivate

# List all environments
conda env list
# or:
conda info --envs

# Remove an environment
conda env remove -n myproject
```

Unlike venv, the env lives at `~/miniconda3/envs/myproject/` — not inside your project folder. This is intentional: the same env can be shared across multiple projects.

---

### Installing Packages in conda

```bash
# Install from conda's default channel
conda install numpy

# Install from conda-forge (community channel, more packages, more up-to-date)
conda install -c conda-forge numpy

# Install a specific version
conda install numpy=1.26.0

# Install multiple packages at once (conda resolves dependencies together)
conda install numpy pandas matplotlib scikit-learn

# Install a package that's only on PyPI (not in conda channels):
pip install some-package     # ← fine to mix, but conda-installed packages first
```

**Best practice when mixing conda and pip:**
1. Install everything you can via conda first
2. Use pip only for packages not available in conda channels
3. Never use `conda install` after `pip install` in the same env — conda may overwrite pip-installed packages

---

### Exporting and Reproducing Environments

```bash
# Export full environment spec (exact versions, all channels)
conda env export > environment.yml

# environment.yml looks like:
# name: myproject
# channels:
#   - conda-forge
#   - defaults
# dependencies:
#   - python=3.11.6
#   - numpy=1.26.0
#   - pandas=2.1.4
#   - pip:
#     - some-pypi-only-package==1.2.3

# Recreate from environment.yml on another machine:
conda env create -f environment.yml

# Update existing env to match environment.yml:
conda env update -f environment.yml --prune   # ← --prune removes packages not in file
```

---

### conda Channels

A **channel** is a repository of conda packages. The main ones:

| Channel | Description |
|---|---|
| `defaults` | Anaconda's official channel. Stable but sometimes behind. |
| `conda-forge` | Community-maintained. More packages, faster updates. Recommended for most use. |
| `pytorch` | Official PyTorch channel — use for GPU-enabled torch installs |
| `nvidia` | NVIDIA CUDA packages |

```bash
# Set conda-forge as default channel (recommended):
conda config --add channels conda-forge
conda config --set channel_priority strict

# Install from a specific channel:
conda install -c pytorch -c nvidia pytorch torchvision pytorch-cuda=12.1
```

---

### conda vs venv — When to Use Which

| Situation | Use |
|---|---|
| Pure Python web project, API, scripts | `venv` — lightweight, no overhead |
| Data science / ML with numpy, torch, cv2 | `conda` — handles C/CUDA deps |
| Need specific CUDA version for GPU training | `conda` — installs cudatoolkit alongside torch |
| CI/CD pipeline | `venv` — faster, no conda overhead |
| Sharing env across multiple projects | `conda` — named envs not tied to a directory |
| Need Python 3.9 and 3.12 side by side | Either (`conda create -n ... python=3.9` or `pyenv`) |
| Deploying to production server | `venv` — lighter, standard, Docker-friendly |

---

### Common conda Issues

**`conda activate` not working in a new terminal:**
```bash
# Run conda init for your shell:
conda init zsh
# Restart terminal
```

**Environment solving takes forever:**
```bash
# Install mamba — a faster drop-in replacement for conda
conda install -n base -c conda-forge mamba
mamba install numpy pandas   # same syntax as conda, much faster
```

**Mixing conda and pip breaks packages:**
```bash
# Check what's installed and from where:
conda list    # shows packages and whether they came from conda or pip
```

**Cannot find a package in conda:**
```bash
# Search conda-forge:
conda search -c conda-forge package-name
# If not there, use pip:
pip install package-name
```

---

## 🐍 pyenv — Managing Multiple Python Versions

`pyenv` solves the problem of needing different Python versions per project:

```bash
# Install pyenv (macOS)
brew install pyenv

# List available Python versions
pyenv install --list

# Install a specific version
pyenv install 3.11.6
pyenv install 3.12.0

# Set global default
pyenv global 3.11.6

# Set version for current directory only (creates .python-version file)
pyenv local 3.11.6

# Check what version is active
pyenv version
python --version
```

Combine with venv: use `pyenv` to install the right Python version, then `python -m venv .venv` to create the project environment.

---

## 🏗️ Project Setup — Complete Workflow

```bash
# 1. Install the Python version you need (once per version, not per project)
pyenv install 3.11.6

# 2. Go to your project
cd my-project

# 3. Create venv with exact Python version
python3.11 -m venv .venv

# 4. Activate
source .venv/bin/activate

# 5. Verify
which python           # → .../my-project/.venv/bin/python
python --version       # → Python 3.11.6

# 6. Install dependencies
pip install numpy pandas matplotlib

# 7. Pin versions
pip freeze > requirements.txt

# 8. Add to .gitignore
echo ".venv/" >> .gitignore

# 9. Work...

# 10. Deactivate when done
deactivate
```

---

## 🚨 Diagnosing `ModuleNotFoundError`

Four commands that identify any venv problem:

```bash
# 1. Which Python binary is actually running?
python -c "import sys; print(sys.executable)"

# 2. Where does it look for packages?
python -c "import sys; print('\n'.join(sys.path))"

# 3. Where is the package installed?
pip show numpy         # shows Location: /path/to/site-packages

# 4. Is the package installed in the Python that's running?
python -c "import numpy; print(numpy.__file__)"
```

If output of command 1 does not match the location in command 3 — wrong Python is running. Fix:

```bash
# Always install using the Python that runs your code:
python -m pip install numpy
# NOT: pip install numpy  (pip might be from a different Python)
```

---

## 🔌 IDE Integration

**VS Code** — select interpreter per workspace:
- `Cmd+Shift+P` → "Python: Select Interpreter"
- Choose `.venv/bin/python` from the list
- VS Code stores this in `.vscode/settings.json`

**PyCharm** — configure project interpreter:
- Settings → Project → Python Interpreter → Add → Existing Environment
- Point to `.venv/bin/python`

**Jupyter** — register venv as a kernel:
```bash
source .venv/bin/activate
pip install ipykernel
python -m ipykernel install --user --name=myproject --display-name "Python (myproject)"
# Now appears in Jupyter's kernel list
```

---

## ⚠️ Common Mistakes

| Mistake | What happens | Fix |
|---|---|---|
| `pip install` without activating venv | Package goes into global Python | Activate first, or use `python -m pip install` |
| Committing `.venv/` to git | Repo becomes huge, paths break on other machines | Add `.venv/` to `.gitignore` |
| `pip freeze` includes dev tools in `requirements.txt` | Production installs pytest, black, etc. | Split into `requirements.txt` and `requirements-dev.txt` |
| Creating venv with wrong Python version | Packages built for wrong ABI | `rm -rf .venv`, recreate with explicit version |
| Using `pip install` vs `python -m pip install` | May install into different Python | Always use `python -m pip install` |
| Not pinning versions in `requirements.txt` | `pip install -r requirements.txt` installs different versions on different machines | Use `pip freeze` to pin |
| Activating venv in one terminal, running code in another | No venv in the other terminal | Activate in each shell separately |

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |

---

**[🏠 Back to README](../README.md)**

**Related Topics:** [Modules and Packages](./theory.md) · [Production Best Practices](../19_production_best_practices/theory.md)
