# Stack — Real-World Usage

A stack is the most "invisible" data structure in computing — it is running constantly
beneath every function call you make, every expression the Python parser evaluates,
every Ctrl+Z you press. Here is where it actually lives in production systems.

---

## 1. The Call Stack — How Python's Execution Stack Works

Every running Python program has a call stack managed by the CPython interpreter.
Each function call pushes a new frame onto the stack; a return pops it. When an
exception is raised, Python walks the call stack to produce the traceback you see.

```python
import traceback
import sys


def compute_discount(price: float, pct: float) -> float:
    return apply_rate(price, pct / 100)


def apply_rate(amount: float, rate: float) -> float:
    return round_currency(amount * (1 - rate))


def round_currency(value: float) -> float:
    # Deliberately show the call stack at this point
    print("=== Call stack at round_currency ===")
    traceback.print_stack()
    return round(value, 2)


compute_discount(99.99, 15)

print(f"\nDefault recursion limit: {sys.getrecursionlimit()}")
```

The `traceback.print_stack()` call reveals the exact stack of frames — identical to
what you see in an unhandled exception. Each frame corresponds to a node on the
interpreter's internal stack of `PyFrameObject` pointers.

**What this means in practice:**
- Stack frames are the reason deep recursion crashes with `RecursionError`.
- Each frame stores local variables, the bytecode instruction pointer, and a reference
  to the enclosing scope — this is why closures work.
- Async frameworks like asyncio avoid deep call stacks by using coroutines (stackless
  continuation objects) instead of real OS stack frames.

```python
# Demonstrate RecursionError from stack exhaustion
def infinite_recurse(n: int = 0) -> int:
    return infinite_recurse(n + 1)


try:
    infinite_recurse()
except RecursionError as e:
    print(f"RecursionError at depth ~{sys.getrecursionlimit()}: {e}")

# Temporarily increase the limit for legitimate deep recursion (e.g., deep JSON trees)
sys.setrecursionlimit(5000)
print(f"New limit: {sys.getrecursionlimit()}")
sys.setrecursionlimit(1000)  # restore
```

---

## 2. Browser Back/Forward — Navigation Stack

While a doubly linked list models the full history (see linked list notes), the simpler
and more common mental model treats the back history as a stack. Each visit pushes to
the back-stack; pressing Back pops from it and pushes to the forward-stack; visiting a
new URL clears the forward-stack.

```python
from typing import Optional


class Browser:
    """
    Stack-based browser navigation.
    Chrome and Firefox use this exact model internally (history stack per tab).
    """

    def __init__(self, homepage: str):
        self._back_stack:    list[str] = []
        self._forward_stack: list[str] = []
        self._current: str = homepage

    def navigate(self, url: str) -> None:
        self._back_stack.append(self._current)
        self._forward_stack.clear()    # forward history invalidated
        self._current = url
        print(f"  Navigate → {url}")

    def back(self) -> Optional[str]:
        if not self._back_stack:
            print("  (nothing to go back to)")
            return self._current
        self._forward_stack.append(self._current)
        self._current = self._back_stack.pop()
        print(f"  Back ← {self._current}")
        return self._current

    def forward(self) -> Optional[str]:
        if not self._forward_stack:
            print("  (nothing to go forward to)")
            return self._current
        self._back_stack.append(self._current)
        self._current = self._forward_stack.pop()
        print(f"  Forward → {self._current}")
        return self._current

    def status(self) -> None:
        print(f"  Current: {self._current}")
        print(f"  Back stack:    {self._back_stack}")
        print(f"  Forward stack: {self._forward_stack}")


browser = Browser("https://google.com")
browser.navigate("https://github.com")
browser.navigate("https://docs.python.org")
browser.back()
browser.back()
browser.forward()
browser.navigate("https://anthropic.com")   # clears forward stack
browser.status()
browser.forward()                            # nothing to go forward to
```

---

## 3. Expression Evaluation — Parsing "3 + 4 * 2" with Operator Precedence

Every programming language compiler and calculator app needs to evaluate arithmetic
expressions that respect operator precedence (BODMAS). The standard algorithm — used
in Python's own parser, JavaScript engines, and every spreadsheet application — is
Dijkstra's Shunting-Yard algorithm, which uses two stacks: one for operands, one for
operators.

```python
def evaluate_expression(expr: str) -> float:
    """
    Evaluate an arithmetic expression string using two stacks.
    Supports +, -, *, / and parentheses.
    Used by: calculators, spreadsheet formula engines, expression evaluators in compilers.
    """
    PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2}

    def apply_op(operands: list, op: str) -> None:
        b, a = operands.pop(), operands.pop()
        if op == '+': operands.append(a + b)
        elif op == '-': operands.append(a - b)
        elif op == '*': operands.append(a * b)
        elif op == '/': operands.append(a / b)

    operands: list[float] = []
    operators: list[str]  = []
    i = 0
    tokens = expr.replace(" ", "")

    while i < len(tokens):
        ch = tokens[i]

        if ch.isdigit() or (ch == '-' and (i == 0 or tokens[i-1] == '(')):
            # Parse full number (handles multi-digit numbers)
            j = i + 1
            while j < len(tokens) and (tokens[j].isdigit() or tokens[j] == '.'):
                j += 1
            operands.append(float(tokens[i:j]))
            i = j
            continue

        elif ch == '(':
            operators.append(ch)

        elif ch == ')':
            while operators and operators[-1] != '(':
                apply_op(operands, operators.pop())
            operators.pop()   # discard '('

        elif ch in PRECEDENCE:
            while (operators and operators[-1] != '(' and
                   operators[-1] in PRECEDENCE and
                   PRECEDENCE[operators[-1]] >= PRECEDENCE[ch]):
                apply_op(operands, operators.pop())
            operators.append(ch)

        i += 1

    while operators:
        apply_op(operands, operators.pop())

    return operands[0]


# Test cases
expressions = [
    ("3 + 4 * 2",          11.0),
    ("(3 + 4) * 2",        14.0),
    ("10 + 2 * 6",         22.0),
    ("100 * 2 + 12",      212.0),
    ("100 * (2 + 12)",   1400.0),
    ("100 * (2 + 12) / 14", 100.0),
]

for expr, expected in expressions:
    result = evaluate_expression(expr)
    status = "OK" if abs(result - expected) < 1e-9 else "FAIL"
    print(f"  [{status}] {expr:30s} = {result}")
```

---

## 4. Function Call Stack in Compilers — Stack Overflow in Practice

Languages that compile to native code (C, C++, Rust, Go) allocate a fixed-size stack
per thread (typically 1-8 MB). Deep or infinite recursion exhausts this stack, causing
a segfault or `stack overflow`. Python raises `RecursionError` before that happens.

Understanding this is critical for production code: any recursive algorithm that
processes unbounded input (deep XML trees, large file system traversals, graphs with
long chains) must be converted to an iterative approach using an explicit stack.

```python
import sys
from typing import Any


# Problem: traverse a deeply nested dictionary (config files, JSON, YAML)
# Recursive version — will crash on deep structures

def traverse_recursive(node: Any, depth: int = 0) -> int:
    """Count total nodes. Crashes with RecursionError on deep nesting."""
    if not isinstance(node, dict):
        return 1
    return 1 + sum(traverse_recursive(v, depth + 1) for v in node.values())


# Iterative version using an explicit stack — safe for any depth
def traverse_iterative(root: Any) -> int:
    """
    Same traversal, but uses an explicit stack on the heap instead of
    the call stack. This is the safe production pattern.
    Used by: JSON parsers, XML parsers, file system walkers (os.walk internals).
    """
    count = 0
    stack = [root]
    while stack:
        node = stack.pop()
        count += 1
        if isinstance(node, dict):
            stack.extend(node.values())
    return count


# Build a deeply nested dict that would crash the recursive version
def build_deep_dict(depth: int) -> dict:
    node: Any = {"value": 42}
    for _ in range(depth):
        node = {"child": node}
    return node


shallow = build_deep_dict(10)
deep    = build_deep_dict(2000)   # deeper than Python's recursion limit

print("Recursive  (shallow):", traverse_recursive(shallow))

try:
    traverse_recursive(deep)
except RecursionError:
    print("Recursive  (deep):    RecursionError — stack overflow!")

print("Iterative  (deep):   ", traverse_iterative(deep), "nodes — no crash")
```

---

## 5. Monotonic Stack — Stock Span Problem

A monotonic stack maintains elements in a strictly increasing or decreasing order.
Whenever a new element violates the order, the stack is popped until order is restored.
This achieves O(n) for problems that would naively be O(n²).

The stock span problem: for each day, find the number of consecutive previous days
where the stock price was less than or equal to today's price. Used in financial
analytics dashboards (Bloomberg Terminal, trading platforms).

```python
class StockSpanner:
    """
    For each new price, returns its "span": how many consecutive days
    (including today) the price was <= today's price.

    Monotonic stack stores (price, span) pairs.
    O(n) amortised — each element is pushed and popped at most once.

    Real use: stock charts that highlight "new N-day highs", RSI calculations,
    candlestick pattern detection in algo-trading systems.
    """

    def __init__(self):
        # Stack of (price, span) — monotonically decreasing by price
        self._stack: list[tuple[int, int]] = []

    def next(self, price: int) -> int:
        span = 1
        # Absorb all previous days that are <= today's price
        while self._stack and self._stack[-1][0] <= price:
            _, prev_span = self._stack.pop()
            span += prev_span
        self._stack.append((price, span))
        return span


# Daily closing prices for a stock (like AAPL, MSFT)
prices  = [100, 80, 60, 70, 60, 75, 85, 100]
spanner = StockSpanner()

print(f"{'Day':<5} {'Price':<8} {'Span':<6} Interpretation")
print("-" * 55)
for day, price in enumerate(prices, start=1):
    span = spanner.next(price)
    interp = f"new {span}-day high" if span > 1 else "no higher run"
    print(f"{day:<5} ${price:<7} {span:<6} {interp}")
```

---

## 6. Undo Mechanism in Text Editors — Ctrl+Z Stack

VS Code, Vim, Sublime Text, and every terminal shell (readline's `Ctrl+_`) implement
undo using a command stack. Each edit operation is pushed as a command object; undo
pops and reverses it. This is the Command design pattern backed by a stack.

```python
from dataclasses import dataclass
from typing import Protocol


class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self)    -> None: ...


@dataclass
class InsertCommand:
    editor: "TextEditor"
    text: str
    position: int

    def execute(self) -> None:
        s = self.editor.content
        self.editor.content = s[:self.position] + self.text + s[self.position:]

    def undo(self) -> None:
        s = self.editor.content
        self.editor.content = s[:self.position] + s[self.position + len(self.text):]


@dataclass
class DeleteCommand:
    editor: "TextEditor"
    position: int
    length: int
    _deleted: str = ""   # store what we deleted so undo can restore it

    def execute(self) -> None:
        s = self.editor.content
        self._deleted = s[self.position:self.position + self.length]
        self.editor.content = s[:self.position] + s[self.position + self.length:]

    def undo(self) -> None:
        s = self.editor.content
        self.editor.content = s[:self.position] + self._deleted + s[self.position:]


class TextEditor:
    """
    Stack-based undo/redo.
    Mirrors VS Code's edit model (TextDocument + EditStack),
    and readline's undo ring (used in Bash, Python REPL).
    """

    def __init__(self, initial: str = ""):
        self.content: str = initial
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []

    def insert(self, position: int, text: str) -> None:
        cmd = InsertCommand(self, text, position)
        cmd.execute()
        self._undo_stack.append(cmd)
        self._redo_stack.clear()
        print(f"  insert({position!r}, {text!r}) → {self.content!r}")

    def delete(self, position: int, length: int) -> None:
        cmd = DeleteCommand(self, position, length)
        cmd.execute()
        self._undo_stack.append(cmd)
        self._redo_stack.clear()
        print(f"  delete({position}, {length})   → {self.content!r}")

    def undo(self) -> None:
        if not self._undo_stack:
            print("  (nothing to undo)")
            return
        cmd = self._undo_stack.pop()
        cmd.undo()
        self._redo_stack.append(cmd)
        print(f"  undo               → {self.content!r}")

    def redo(self) -> None:
        if not self._redo_stack:
            print("  (nothing to redo)")
            return
        cmd = self._redo_stack.pop()
        cmd.execute()
        self._undo_stack.append(cmd)
        print(f"  redo               → {self.content!r}")


# --- Demo: editing a Python function signature ---
ed = TextEditor()
ed.insert(0, "def greet():")
ed.insert(12, "name: str")          # 'def greet(name: str):'  — but off by index
ed.delete(10, 0)                    # no-op delete to show the mechanism
ed.insert(len(ed.content), "\n    return f'Hello, {name}'")
print()
ed.undo()
ed.undo()
print()
ed.redo()
