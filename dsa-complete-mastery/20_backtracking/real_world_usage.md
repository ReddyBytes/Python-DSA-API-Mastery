# Backtracking — Real World Usage

Backtracking is systematic trial and error: build a solution incrementally, abandon (backtrack)
as soon as you detect a dead end, and try the next option. It powers constraint solvers, game
engines, compiler lexers, and robotics path planners.

---

## 1. Sudoku Solver — Constraint Satisfaction

Sudoku apps on iOS and Android, puzzle generators for newspapers, and logic puzzle engines all
use backtracking. The same pattern underlies SAT solvers (used in chip design verification at
Intel and AMD) and CSP solvers in AI planning systems. The key: prune early by checking row,
column, and box constraints before placing each digit.

```python
def solve_sudoku(board: list[list[int]]) -> bool:
    """
    Solve a 9x9 Sudoku in-place using backtracking.
    0 represents an empty cell.

    Used by: NYT Sudoku app, puzzle generator libraries,
             AI constraint satisfaction research
    """
    def is_valid(row, col, num):
        # Check row
        if num in board[row]:
            return False
        # Check column
        if num in [board[r][col] for r in range(9)]:
            return False
        # Check 3x3 box
        box_r, box_c = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if board[r][c] == num:
                    return False
        return True

    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(row, col, num):
                        board[row][col] = num        # tentative choice
                        if solve_sudoku(board):      # recurse
                            return True
                        board[row][col] = 0          # backtrack
                return False  # no valid number — backtrack further
    return True  # all cells filled


puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

solve_sudoku(puzzle)
print("Solved:")
for row in puzzle:
    print(" ".join(map(str, row)))
```

---

## 2. N-Queens — Robotics and Combinatorial Planning

The N-Queens problem is a canonical benchmark for constraint solvers. In robotics, placing
sensor arrays on a grid without line-of-sight conflicts uses the same logic. Chess engines
use queen-coverage reasoning for positional evaluation. VLSI chip designers use similar
non-attacking placement constraints when routing signal traces.

```python
def n_queens_count(n: int) -> int:
    """
    Count all valid N-Queens solutions for an n x n board.
    Used as a benchmark for: SAT solvers, backtracking optimizers,
    robotics sensor placement, VLSI routing
    """
    count = 0
    cols = set()
    diag1 = set()   # row - col (constant on / diagonal)
    diag2 = set()   # row + col (constant on \ diagonal)

    def backtrack(row):
        nonlocal count
        if row == n:
            count += 1
            return
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            backtrack(row + 1)            # recurse to next row
            cols.remove(col)              # backtrack
            diag1.remove(row - col)
            diag2.remove(row + col)

    backtrack(0)
    return count


def n_queens_one_solution(n: int) -> list[int]:
    """Returns column positions for queens row by row."""
    solution = []
    cols, diag1, diag2 = set(), set(), set()

    def backtrack(row):
        if row == n:
            return True
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue
            cols.add(col); diag1.add(row - col); diag2.add(row + col)
            solution.append(col)
            if backtrack(row + 1):
                return True
            solution.pop()
            cols.remove(col); diag1.remove(row - col); diag2.remove(row + col)
        return False

    backtrack(0)
    return solution


for n in range(1, 10):
    print(f"N={n}: {n_queens_count(n)} solutions")
# N=1: 1, N=4: 2, N=8: 92
```

---

## 3. Regular Expression Matching — NFA Backtracking

Python's `re` module and most regex engines use a backtracking NFA internally for patterns with
`*`, `+`, `?`, and `|`. Understanding this explains catastrophic backtracking (ReDoS attacks),
which have taken down Cloudflare, Stack Overflow, and multiple Node.js servers. Here we build
a minimal matcher for `.` (any char) and `*` (zero or more preceding).

```python
def regex_match(text: str, pattern: str) -> bool:
    """
    Match text against pattern with '.' (any char) and '*' (zero or more).
    This is the exact algorithm in: CPython re module (before the new PEG),
    grep, sed, Java Pattern — and explains ReDoS vulnerabilities.

    LeetCode #10 — Hard. Used in every shell script, log parser, and IDE.
    """
    if not pattern:
        return not text

    first_match = bool(text) and pattern[0] in (text[0], ".")

    if len(pattern) >= 2 and pattern[1] == "*":
        # Two choices: skip "x*" entirely (0 occurrences),
        # OR consume one char and stay at same pattern position
        return (
            regex_match(text, pattern[2:])           # 0 occurrences — backtrack option
            or (first_match and regex_match(text[1:], pattern))  # consume 1 char
        )
    else:
        return first_match and regex_match(text[1:], pattern[1:])


# Real log parsing examples
test_cases = [
    ("2024-01-15", "2...-..-.."),          # date format check
    ("ERROR: disk full", "ERROR.*"),        # log level filter
    ("aab", "c*a*b"),                       # zero c's, two a's, one b
    ("mississippi", "mis*is*p*."),          # complex wildcard
    ("abc", "a.c"),                         # dot wildcard
]

for text, pattern in test_cases:
    print(f"match({text!r}, {pattern!r}) = {regex_match(text, pattern)}")
```

---

## 4. Game AI — Minimax for Tic-Tac-Toe

Game tree search with minimax powers chess engines (Stockfish), checkers solvers (Chinook, the
first program to solve a game), and Go programs before AlphaGo. Every turn-based game AI in
production — from online Scrabble bots to competitive poker AIs — builds on this foundation.
Alpha-beta pruning (an optimized backtracking variant) makes it practical for deep game trees.

```python
def minimax_tictactoe():
    """
    Unbeatable Tic-Tac-Toe AI using minimax backtracking.
    Used in: game engines, AI programming courses,
             foundations of chess/checkers/Go engines
    """
    def winner(board):
        lines = [
            [0,1,2],[3,4,5],[6,7,8],  # rows
            [0,3,6],[1,4,7],[2,5,8],  # cols
            [0,4,8],[2,4,6],           # diagonals
        ]
        for line in lines:
            vals = [board[i] for i in line]
            if vals == ["X","X","X"]: return 1
            if vals == ["O","O","O"]: return -1
        return 0

    def minimax(board, is_maximizing):
        score = winner(board)
        if score != 0:
            return score
        if "." not in board:
            return 0  # draw

        if is_maximizing:
            best = -float("inf")
            for i in range(9):
                if board[i] == ".":
                    board[i] = "X"
                    best = max(best, minimax(board, False))
                    board[i] = "."          # backtrack
            return best
        else:
            best = float("inf")
            for i in range(9):
                if board[i] == ".":
                    board[i] = "O"
                    best = min(best, minimax(board, True))
                    board[i] = "."          # backtrack
            return best

    def best_move(board):
        best_score, move = -float("inf"), -1
        for i in range(9):
            if board[i] == ".":
                board[i] = "X"
                score = minimax(board, False)
                board[i] = "."
                if score > best_score:
                    best_score, move = score, i
        return move

    # Demonstrate: X to move, what is the winning play?
    board = ["X","O","X",
             "O","X",".",
             ".",".","."]
    move = best_move(board)
    print(f"Board: {board[:3]} | {board[3:6]} | {board[6:]}")
    print(f"AI plays position {move} -> X wins!")
    board[move] = "X"
    result = winner(board)
    print(f"Winner: {'X' if result==1 else 'O' if result==-1 else 'Draw'}")

minimax_tictactoe()
```

---

## 5. Maze Solving — Robotics and Pathfinding

Maze-solving with backtracking is used in robotics firmware (Roomba's early navigation before
SLAM), micromouse competition robots, game level generation in Unity/Unreal, and dungeon
exploration in games like Minecraft. It also forms the basis of DFS-based maze generation
algorithms used in procedural content generation.

```python
def solve_maze(
    grid: list[list[int]],
    start: tuple[int, int],
    end: tuple[int, int]
) -> list[tuple[int, int]] | None:
    """
    Find a path through a maze using backtracking DFS.
    grid: 0 = open, 1 = wall
    Returns list of (row, col) positions or None if no path.

    Used in: Roomba navigation firmware (early versions), Unity NavMesh fallback,
             Micromouse robot competitions, game dungeon pathfinding
    """
    rows, cols = len(grid), len(grid[0])
    visited = set()
    path = []

    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols):
            return False
        if (r, c) in visited or grid[r][c] == 1:
            return False

        visited.add((r, c))
        path.append((r, c))

        if (r, c) == end:
            return True

        for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:  # R, D, L, U
            if dfs(r + dr, c + dc):
                return True

        path.pop()   # backtrack: dead end, remove this cell from path
        return False

    if dfs(*start):
        return path
    return None


maze = [
    [0, 1, 0, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0],
    [1, 1, 0, 0, 0],
    [0, 0, 0, 1, 0],
]

path = solve_maze(maze, (0, 0), (4, 4))
if path:
    print(f"Path found ({len(path)} steps):")
    grid_vis = [row[:] for row in maze]
    for r, c in path:
        grid_vis[r][c] = "*"
    for row in grid_vis:
        print(" ".join(str(x) for x in row))
```

---

## 6. Word Search — Boggle and Wordle Engines

Word search on a 2D grid powers Boggle game engines, the NYT Spelling Bee validator, and
content moderation systems that detect prohibited words in user-submitted images (OCR + word
search). The backtracking ensures each cell is used at most once per word path, which is the
key constraint.

```python
def word_search(board: list[list[str]], word: str) -> bool:
    """
    Find if a word exists in a 2D letter grid (8-directional, no cell reuse).
    Used by: Hasbro Boggle engine, NYT Spelling Bee, word game validators,
             OCR post-processing for offensive content detection
    """
    rows, cols = len(board), len(board[0])

    def dfs(r, c, idx, visited):
        if idx == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols):
            return False
        if (r, c) in visited or board[r][c] != word[idx]:
            return False

        visited.add((r, c))

        directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        for dr, dc in directions:
            if dfs(r + dr, c + dc, idx + 1, visited):
                visited.remove((r, c))
                return True

        visited.remove((r, c))   # backtrack
        return False

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0, set()):
                return True
    return False


def find_all_words(board: list[list[str]], dictionary: set[str]) -> list[str]:
    """Find all dictionary words present on the board — Boggle engine."""
    rows, cols = len(board), len(board[0])
    found = set()

    def dfs(r, c, path, visited):
        word = "".join(path)
        # Pruning: if no dictionary word starts with current path, stop
        if not any(w.startswith(word) for w in dictionary):
            return
        if word in dictionary and len(word) > 2:
            found.add(word)
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols
                        and (nr, nc) not in visited):
                    visited.add((nr, nc))
                    dfs(nr, nc, path + [board[nr][nc]], visited)
                    visited.remove((nr, nc))    # backtrack

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, [board[r][c]], {(r, c)})

    return sorted(found)


boggle_board = [
    ["E", "A", "T"],
    ["R", "A", "T"],
    ["E", "S", "E"],
]
vocab = {"eat", "ate", "tea", "rat", "tar", "rate", "tear", "rare", "ear", "era", "are", "sea"}

print("Board:")
for row in boggle_board:
    print(" ".join(row))
print(f"\nWords found: {find_all_words(boggle_board, vocab)}")
```

---

## Key Takeaways

| Problem | Backtracking Pattern | Used In |
|---|---|---|
| Sudoku | Fill cell, check constraints, undo | Puzzle apps, SAT solvers |
| N-Queens | Place queen per row, prune conflicts | Robotics, VLSI design |
| Regex matching | Match or skip with `*`, undo on fail | `re` module, grep, sed |
| Game AI | Minimax: maximize/minimize recursively | Chess engines, board games |
| Maze solving | DFS explore, pop path on dead end | Roomba, game pathfinding |
| Word search | Explore 8 directions, unmark on fail | Boggle, content moderation |

The universal backtracking template is: **choose -> explore -> unchoose**. The power lies in
pruning: the sooner you detect a dead end, the fewer branches you explore. In production, this
is often paired with constraint propagation (Sudoku arc consistency) or memoization to avoid
re-exploring equivalent states.
