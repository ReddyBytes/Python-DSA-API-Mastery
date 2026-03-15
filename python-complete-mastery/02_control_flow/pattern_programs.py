"""
02_control_flow/pattern_programs.py
=====================================
CONCEPT: Control flow mastery through progressively complex pattern programs.
WHY THIS MATTERS: Nested loops, conditional logic, and loop control (break/
continue/else) are tested in every Python interview. These patterns build the
muscle memory to think in loops.

LEARNING PATH:
  Part 1 (this module): all patterns using only loops and conditionals
  Part 2 (bottom):      revisit AFTER completing Module 04 (Functions)
                        — cleaner versions with def for reusability

Pattern programs also reveal how to decompose a visual problem into math — a
skill that transfers directly to grid traversal and 2D algorithms.
"""

# =============================================================================
# PART 1 — Requires only: Modules 01–02 (variables, loops, conditionals)
# =============================================================================

# =============================================================================
# SECTION 1: Basic nested loop patterns
# =============================================================================

# CONCEPT: Nested loops let the outer loop control rows, inner loop columns.
# The relationship between i (row) and j (column) defines the shape.

print("=== Section 1: Basic Patterns ===")

# --- Square of stars ---
# CONCEPT: both loops run same number of iterations — square shape
print("\nSquare (5x5):")
for i in range(5):
    for j in range(5):
        print("*", end=" ")
    print()   # newline after each row

# --- Right-angle triangle ---
# CONCEPT: inner loop runs `i+1` times — triangular shape
# Each row i prints i+1 stars: row 0 → 1 star, row 1 → 2 stars, etc.
print("\nRight-angle triangle:")
for i in range(5):
    for j in range(i + 1):    # inner loop depends on outer loop variable
        print("*", end=" ")
    print()

# --- Inverted triangle ---
# CONCEPT: inner loop runs `n - i` times — countdown creates inverted shape
print("\nInverted triangle:")
n = 5
for i in range(n):
    for j in range(n - i):    # decreasing inner iterations
        print("*", end=" ")
    print()


# =============================================================================
# SECTION 2: Number patterns
# =============================================================================

# CONCEPT: Replace the '*' with a computed value (i, j, i*j, etc.)
# to create number patterns. Understanding the math behind each pattern
# is more valuable than memorizing the code.

print("\n=== Section 2: Number Patterns ===")

# --- Row number pattern ---
# Each row prints its row number (1-indexed)
print("\nRow number pattern:")
for i in range(1, 6):
    for j in range(i):
        print(i, end=" ")   # print row number, not column number
    print()

# --- Sequence pattern ---
# Print 1 2 3 ... i on each row i
print("\n1-to-i on each row:")
for i in range(1, 6):
    for j in range(1, i + 1):
        print(j, end=" ")
    print()

# --- Multiplication table ---
# CONCEPT: value at (i, j) = i * j — classic 2D math grid
print("\nMultiplication table (5x5):")
for i in range(1, 6):
    for j in range(1, 6):
        print(f"{i*j:3}", end=" ")  # :3 pads to 3 chars for alignment
    print()


# =============================================================================
# SECTION 3: Pyramid and diamond patterns
# =============================================================================

# CONCEPT: Pyramids require leading spaces. The formula for spaces and stars
# per row unlocks all pyramid variants.
# Row i of an n-row pyramid: (n - i - 1) spaces, then (2*i + 1) stars.

print("\n=== Section 3: Pyramid Patterns ===")

# --- Centered pyramid ---
n = 5
print("\nCentered pyramid:")
for i in range(n):
    spaces = n - i - 1         # decreasing spaces from left
    stars  = 2 * i + 1         # increasing odd number of stars
    print(" " * spaces + "* " * stars)

# --- Inverted pyramid ---
print("\nInverted pyramid:")
for i in range(n - 1, -1, -1):   # count down from n-1 to 0
    spaces = n - i - 1
    stars  = 2 * i + 1
    print(" " * spaces + "* " * stars)

# --- Diamond (pyramid + inverted pyramid) ---
print("\nDiamond:")
for i in range(n):
    print(" " * (n - i - 1) + "* " * (2 * i + 1))
for i in range(n - 2, -1, -1):   # start from n-2 to avoid duplicate middle
    print(" " * (n - i - 1) + "* " * (2 * i + 1))


# =============================================================================
# SECTION 4: Hollow patterns
# =============================================================================

# CONCEPT: Hollow patterns print only borders, not interior.
# The condition: print character if on the first/last row OR first/last column.
# Everything else prints a space. This introduces multi-condition logic.

print("\n=== Section 4: Hollow Patterns ===")

# --- Hollow square ---
n = 5
print("\nHollow square:")
for i in range(n):
    for j in range(n):
        # Print star if on any border, space otherwise
        if i == 0 or i == n-1 or j == 0 or j == n-1:
            print("*", end=" ")
        else:
            print(" ", end=" ")   # interior is hollow
    print()

# --- Hollow right-angle triangle ---
print("\nHollow right-angle triangle:")
for i in range(1, n + 1):
    for j in range(1, i + 1):
        # Print star if: first row, last row, or leftmost/rightmost column
        if i == 1 or i == n or j == 1 or j == i:
            print("*", end=" ")
        else:
            print(" ", end=" ")
    print()


# =============================================================================
# SECTION 5: Character patterns
# =============================================================================

# CONCEPT: Same loop structure, but use chr(65 + i) to get A, B, C...
# Shows how loop variables map to different output types.

print("\n=== Section 5: Character Patterns ===")

# --- Alphabet triangle ---
print("\nAlphabet triangle:")
for i in range(5):
    for j in range(i + 1):
        print(chr(65 + j), end=" ")   # chr(65)='A', chr(66)='B', etc.
    print()

# --- Same letter per row ---
print("\nSame letter per row:")
for i in range(5):
    for j in range(i + 1):
        print(chr(65 + i), end=" ")   # chr(65+0)='A', chr(65+1)='B', etc.
    print()

# --- Alphabet in reverse ---
print("\nAlphabet reverse triangle:")
n = 5
for i in range(n):
    for j in range(n - i):
        print(chr(65 + j), end=" ")
    print()


# =============================================================================
# SECTION 6: Classic loop problems — break, continue, else
# =============================================================================

# CONCEPT: These demonstrate real control flow scenarios:
# break — early exit (search found), continue — skip item,
# loop else — "I looked everywhere and didn't find it"

print("\n=== Section 6: break, continue, loop else ===")

# --- loop else — runs ONLY when loop completed WITHOUT hitting `break` ---
# CONCEPT: This is Python-unique. Used for "search and check if found" logic.
print("\nPrime check using loop-else (no def needed):")
for n in [7, 12, 17, 25]:
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            print(f"  {n} is NOT prime (divisible by {i})")
            break          # found a divisor — not prime
    else:
        print(f"  {n} IS prime")   # loop finished without break → prime

# --- FizzBuzz (classic interview loop with conditions) ---
print("\nFizzBuzz (1-20):")
for n in range(1, 21):
    if n % 15 == 0:       # check 15 first (both 3 and 5) — order matters!
        print("FizzBuzz", end=" ")
    elif n % 3 == 0:
        print("Fizz", end=" ")
    elif n % 5 == 0:
        print("Buzz", end=" ")
    else:
        print(n, end=" ")
print()

# --- Collatz sequence (while loop with complex condition) ---
# CONCEPT: while loop where the exit condition changes dynamically
print("\nCollatz sequence starting at 27:")
n = 27
steps = [n]
while n != 1:
    if n % 2 == 0:
        n = n // 2      # even: divide by 2
    else:
        n = 3 * n + 1   # odd: triple plus one
    steps.append(n)

print(f"  {len(steps)} steps, max value = {max(steps)}")
print(f"  First 10: {steps[:10]}...")
print(f"  Last 5:   {steps[-5:]}")

# --- Two-sum using early break ---
# CONCEPT: break as soon as answer found — don't iterate more than needed
nums   = [2, 7, 11, 15]
target = 9
found  = None

for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        if nums[i] + nums[j] == target:
            found = (i, j)
            break          # stop inner loop
    if found:
        break              # stop outer loop too

print(f"\nTwo-sum {nums} → target {target}: indices {found}")


# =============================================================================
# SECTION 7: Pascal's triangle — building each row from the previous
# =============================================================================

# CONCEPT: Each row is built from the previous row using list operations.
# row[j] = prev[j-1] + prev[j] (boundary values = 1).
# No functions needed — just a list that grows one row at a time.

print("\n=== Section 7: Pascal's Triangle (7 rows) ===")

triangle = [[1]]
for i in range(1, 7):
    prev    = triangle[-1]
    # Each interior element is sum of two elements above it
    new_row = [1] + [prev[j-1] + prev[j] for j in range(1, i)] + [1]
    triangle.append(new_row)

for row in triangle:
    print("  " + "  ".join(f"{n:3}" for n in row))


print("\n=== Part 1 complete ===")
print("Key loop insights:")
print("  1. Outer loop = rows, inner loop = columns; their relationship = shape")
print("  2. Pyramid formula: row i → (n-i-1) spaces, (2i+1) stars")
print("  3. Hollow patterns: print border if i/j is 0, n-1, or i==j")
print("  4. `loop else` — runs when loop completed without hitting break")
print("  5. Break as soon as you find what you need")
print()
print(">>> Come back after Module 04 (Functions) for Part 2 below <<<")


# =============================================================================
# PART 2 — Requires: Module 04 (Functions) completed first
# =============================================================================
# Reusable versions of the same patterns wrapped in def for cleaner code.
# =============================================================================

print("\n" + "="*60)
print("PART 2: Requires Module 04 (Functions)")
print("="*60)

# =============================================================================
# SECTION 8: Reusable pattern functions
# =============================================================================

print("\n=== Section 8: Pattern Functions ===")

def is_prime(n):
    """Returns True if n is prime. Uses loop-else idiom."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            break
    else:
        return True
    return False

primes = [n for n in range(2, 50) if is_prime(n)]
print(f"Primes up to 50: {primes}")


def collatz(n):
    """Return the full Collatz sequence starting at n."""
    steps = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps.append(n)
    return steps

seq = collatz(27)
print(f"Collatz(27): {len(seq)} steps, max={max(seq)}")


def two_sum_indices(nums, target):
    """Find two indices that sum to target. Returns (i, j) or None."""
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None

result = two_sum_indices([2, 7, 11, 15], 9)
print(f"Two-sum [2,7,11,15] → target 9: indices {result}")


def spiral_matrix(n):
    """Fill n×n matrix with numbers 1..n² in spiral order."""
    matrix = [[0] * n for _ in range(n)]
    top, bottom, left, right = 0, n-1, 0, n-1
    num = 1

    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            matrix[top][j] = num; num += 1
        top += 1
        for i in range(top, bottom + 1):
            matrix[i][right] = num; num += 1
        right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1):
                matrix[bottom][j] = num; num += 1
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                matrix[i][left] = num; num += 1
            left += 1

    return matrix

print("\nSpiral Matrix (4x4):")
for row in spiral_matrix(4):
    print("  " + "  ".join(f"{n:3}" for n in row))


print("\n=== All sections complete ===")
