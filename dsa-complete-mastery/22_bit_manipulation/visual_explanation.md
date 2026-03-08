# Bit Manipulation — The Language of Switches

---

## Everything Is a Light Switch

Your computer doesn't understand numbers the way you do. It only understands one thing:
**is the electricity flowing, or not?**

On = 1. Off = 0.

A single bit is a light switch. Eight bits is a row of eight switches. That row of switches
is how your computer stores every number, every character, every pixel on your screen.

Let's take the number **13** and represent it as switches:

```
Binary:    1    1    0    1
           │    │    │    │
Switch:   [ON] [ON] [OFF][ON]
           │    │    │    │
Place:     8    4    2    1
```

Add the "ON" places: 8 + 4 + 0 + 1 = **13**

That's it. That's binary. Each position is worth twice the previous:
```
Position:  7    6    5    4    3    2    1    0
Value:    128   64   32   16    8    4    2    1
```

Let's check a few numbers:
```
13 = 8+4+1   = 1101₂   (4 bits)
10 = 8+2     = 1010₂   (4 bits)
 7 = 4+2+1   = 0111₂   (4 bits)
 8 = 8       = 1000₂   (4 bits, only one switch on)
```

---

## The Six Bit Operations

Let's work with our two numbers throughout:
```
13 = 1101₂
10 = 1010₂
```

### AND (&) — Both switches must be ON

Rule: output is 1 only if BOTH bits are 1. Like a series circuit — both switches must be on.

```
  13 = 1 1 0 1
  10 = 1 0 1 0
       -------
AND  = 1 0 0 0  =  8
```

Position by position:
```
Bit 3:  1 AND 1 = 1   (both on)
Bit 2:  1 AND 0 = 0   (one off)
Bit 1:  0 AND 1 = 0   (one off)
Bit 0:  1 AND 0 = 0   (one off)
```

### OR (|) — Either switch is ON

Rule: output is 1 if EITHER bit is 1. Like a parallel circuit — either switch works.

```
  13 = 1 1 0 1
  10 = 1 0 1 0
       -------
OR   = 1 1 1 1  =  15
```

```
Bit 3:  1 OR 1 = 1   (either on)
Bit 2:  1 OR 0 = 1   (one on)
Bit 1:  0 OR 1 = 1   (one on)
Bit 0:  1 OR 0 = 1   (one on)
```

### XOR (^) — Exactly ONE switch is ON

Rule: output is 1 if bits are DIFFERENT. The "odd one out" operation.

```
  13 = 1 1 0 1
  10 = 1 0 1 0
       -------
XOR  = 0 1 1 1  =  7
```

```
Bit 3:  1 XOR 1 = 0   (same — cancel out)
Bit 2:  1 XOR 0 = 1   (different — keep)
Bit 1:  0 XOR 1 = 1   (different — keep)
Bit 0:  1 XOR 0 = 1   (different — keep)
```

### NOT (~) — Flip Every Switch

Rule: 0 becomes 1, 1 becomes 0.

```
  13 = 0000 ... 0000 1101    (in 32/64-bit representation)
 ~13 = 1111 ... 1111 0010    (all bits flipped)
```

In Python: `~13 = -14`. Why -14 and not 2?

Because Python uses **two's complement** for negative numbers:
- Flipping all bits and interpreting the result as signed gives -(n+1)
- ~13 = -(13+1) = -14
- This is intentional — it makes arithmetic circuits simpler

Just remember: `~n = -(n+1)` in Python.

### Left Shift (<<) — Multiply by 2

Rule: slide all bits to the left, fill the right with zeros.

```
  13 = 1101
  13 << 1:
  Before: 0 0 0 0 1 1 0 1
  After:  0 0 0 1 1 0 1 0  =  26  (13 × 2)

  13 << 2:
  Before: 0 0 0 0 1 1 0 1
  After:  0 0 1 1 0 1 0 0  =  52  (13 × 4)
```

Each left shift multiplies by 2. This is FAST — the CPU does it in a single clock cycle.

### Right Shift (>>) — Divide by 2 (integer)

Rule: slide all bits to the right, drop the rightmost bit.

```
  13 = 1101
  13 >> 1:
  Before: 0 0 0 0 1 1 0 1
  After:  0 0 0 0 0 1 1 0  =  6  (13 ÷ 2, rounded down)

  13 >> 2:
  Before: 0 0 0 0 1 1 0 1
  After:  0 0 0 0 0 0 1 1  =  3  (13 ÷ 4, rounded down)
```

Each right shift divides by 2 (integer division). The dropped bits are just gone.

---

## Power of 2 Check: The Beautiful Trick

Here's one of the most elegant bit tricks. Check if a number is a power of 2:

```python
def is_power_of_2(n):
    return n > 0 and (n & (n - 1)) == 0
```

**Why does this work?** Powers of 2 have exactly ONE bit set:

```
1  = 0001
2  = 0010
4  = 0100
8  = 1000
16 = 10000
```

When you subtract 1 from a power of 2, all the lower bits flip ON and the single 1 turns OFF:

```
8     = 1 0 0 0
8 - 1 = 0 1 1 1
─────────────────
AND   = 0 0 0 0  ← Always zero for powers of 2!
```

Now check a NON-power of 2, like 6:

```
6     = 0 1 1 0
6 - 1 = 0 1 0 1
─────────────────
AND   = 0 1 0 0  ← Not zero! So 6 is NOT a power of 2.
```

The logic: for powers of 2, subtracting 1 flips exactly the bits we want to cancel out.
For anything else, there are "leftover" bits that don't cancel.

---

## Counting Set Bits (Brian Kernighan's Algorithm)

How many 1-bits does 13 have? You could check each bit one by one (8 checks for 8-bit numbers).
Or you could use the Brian Kernighan trick:

**Key insight:** `n & (n-1)` removes exactly the lowest set bit.

```
n = 13 = 1 1 0 1

Step 1: n = 13 = 1101
        n-1 = 12 = 1100
        13 & 12 = 1100 = 12
        (removed the lowest 1 bit, which was at position 0)
        count = 1

Step 2: n = 12 = 1100
        n-1 = 11 = 1011
        12 & 11 = 1000 = 8
        (removed the lowest 1 bit, which was at position 2)
        count = 2

Step 3: n = 8 = 1000
        n-1 = 7 = 0111
        8 & 7 = 0000 = 0
        (removed the lowest 1 bit, which was at position 3)
        count = 3

Step 4: n = 0. Stop.
```

**Result: 3 set bits** (13 = 1101, which has three 1s). Correct!

The algorithm runs in O(number of set bits), not O(total bits).
For a number with few set bits, this is much faster.

```python
def count_set_bits(n):
    count = 0
    while n:
        n &= (n - 1)   # remove lowest set bit
        count += 1
    return count
```

---

## XOR: The Disappearing Trick

XOR has three magical properties:

```
Property 1:  a XOR 0 = a     (XOR with zero changes nothing)
Property 2:  a XOR a = 0     (XOR with yourself = zero — you cancel out)
Property 3:  a XOR b XOR a = b   (apply twice = disappear)
```

Property 3 is wild. Let's verify:

```
a = 5  = 101
b = 9  = 1001

a XOR b:   101 XOR 1001 = 1100 = 12
(12) XOR a: 1100 XOR 0101 = 1001 = 9 = b   ✓
```

The two `a`s cancelled each other out, leaving only `b`.

**Classic problem: Find the single number**

Given an array where every number appears exactly TWICE except one. Find the lone number.

```
Array: [4, 1, 2, 1, 2]
```

Brute force: count frequencies. O(n) space.

XOR trick: XOR everything together.

```
4 XOR 1 XOR 2 XOR 1 XOR 2

= 4 XOR (1 XOR 1) XOR (2 XOR 2)   (rearranging — XOR is associative and commutative)

= 4 XOR 0 XOR 0

= 4
```

Every number that appears twice XORs to 0. The lone number XORs with 0 and stays itself.
O(n) time, O(1) space. Beautiful.

```python
def find_single(nums):
    result = 0
    for num in nums:
        result ^= num       # XOR everything together
    return result           # pairs cancel, only singleton remains
```

---

## Bitmask for Subsets: A Tiny Map

Imagine you have a set of 3 items: **[A, B, C]**.

Each subset can be represented as a 3-bit number:
- Bit 0 (value 1) = is A included?
- Bit 1 (value 2) = is B included?
- Bit 2 (value 4) = is C included?

```
Mask  Binary  Subset        Meaning
───────────────────────────────────────
  0   0 0 0   {}            Nothing selected
  1   0 0 1   {A}           Only A
  2   0 1 0   {B}           Only B
  3   0 1 1   {A, B}        A and B
  4   1 0 0   {C}           Only C
  5   1 0 1   {A, C}        A and C
  6   1 1 0   {B, C}        B and C
  7   1 1 1   {A, B, C}     Everything
```

For n items, there are 2ⁿ subsets. Each subset maps to a unique integer from 0 to 2ⁿ-1.

**Check if element i is in subset `mask`:**
```python
if mask & (1 << i):    # shift 1 to position i, then AND
    # element i is included
```

**Add element i to subset `mask`:**
```python
mask = mask | (1 << i)   # set bit i
```

**Remove element i from subset `mask`:**
```python
mask = mask & ~(1 << i)  # clear bit i
```

**Iterate over all subsets of n elements:**
```python
for mask in range(1 << n):      # 0 to 2^n - 1
    for i in range(n):
        if mask & (1 << i):
            # element i is in this subset
```

This is the foundation of **bitmask dynamic programming** — storing state as a bitmask to represent
which items have been "used" or "visited."

---

## Cheat Sheet: Common Bit Tricks

```
Operation                    Code              Example (n=13=1101)
──────────────────────────────────────────────────────────────────
Check if power of 2          n & (n-1) == 0    12 & 11 = 8 ≠ 0  → Not power of 2
Remove lowest set bit        n & (n-1)         1101 & 1100 = 1100
Get lowest set bit           n & (-n)          1101 & 0011 = 0001
Set bit i                    n | (1 << i)      set bit 1: 1101 | 0010 = 1111
Clear bit i                  n & ~(1 << i)     clear bit 2: 1101 & 1011 = 1001
Toggle bit i                 n ^ (1 << i)      toggle bit 1: 1101 ^ 0010 = 1111
Check bit i                  (n >> i) & 1      check bit 2: (1101 >> 2) & 1 = 1
Multiply by 2^k              n << k            13 << 2 = 52
Divide by 2^k                n >> k            13 >> 2 = 3
```

---

## The One-Sentence Summary

Bit manipulation treats numbers as rows of switches: AND requires both on, OR needs one on,
XOR detects differences, and shifts multiply or divide by powers of 2 — giving you
direct hardware-speed control over data at the binary level.
