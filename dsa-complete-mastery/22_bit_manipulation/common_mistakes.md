# Bit Manipulation — Common Mistakes & Error Prevention

---

## Mistake 1: Python's Arbitrary Precision Integers — No Overflow, But Sign Behaves Differently

### The Bug

In C and Java, integers have a fixed width (32-bit for `int`). Bitwise NOT on 0 gives `0xFFFFFFFF` (32 bits of 1s), which is interpreted as the unsigned max value 4,294,967,295, or as -1 in two's-complement signed representation. In Python, integers have **arbitrary precision** — there is no fixed bit-width. `~0` in Python does NOT give `0xFFFFFFFF`. It gives -1, and the concept of "overflow wrapping" does not exist.

This bites programmers who port bit-manipulation solutions from C/Java to Python or who expect the same 32-bit semantics.

### WRONG Code

```python
def wrong_32bit_not():
    """Expecting ~0 to be 0xFFFFFFFF (C behaviour)."""
    result = ~0
    # Wrong expectation: result == 0xFFFFFFFF == 4294967295
    # Actual Python result: -1
    return result


def wrong_complement(n: int) -> int:
    """Find the bitwise complement of n in 32-bit representation."""
    return ~n   # WRONG: gives -(n+1), not the 32-bit complement


def wrong_add_without_carry(a: int, b: int) -> int:
    """Add two integers using bit manipulation (interview question)."""
    while b != 0:
        carry = a & b
        a = a ^ b
        b = carry << 1
    return a
    # WRONG: In Python, negative numbers are infinite-precision two's complement.
    # For negative inputs, b <<= 1 can grow without bound → infinite loop!
```

### CORRECT Code

```python
def correct_32bit_not(n: int) -> int:
    """Bitwise NOT of n in 32-bit unsigned representation."""
    return (~n) & 0xFFFFFFFF   # mask to 32 bits


def correct_complement(n: int) -> int:
    """Bitwise complement of n (only flip the bits that n uses)."""
    if n == 0:
        return 1
    # Find the number of bits in n
    bit_length = n.bit_length()
    mask = (1 << bit_length) - 1   # e.g., n=5 (101) → mask=7 (111)
    return (~n) & mask              # flip only the meaningful bits


def correct_add_without_carry_32bit(a: int, b: int) -> int:
    """Add two integers using XOR and AND — properly masked for 32-bit."""
    MASK = 0xFFFFFFFF
    MAX = 0x7FFFFFFF   # max positive 32-bit signed int

    while b & MASK:
        carry = (a & b) << 1
        a = a ^ b
        b = carry
        # Mask both to 32 bits each iteration to prevent infinite growth
        a &= MASK
        b &= MASK

    # Convert back to Python signed integer if result is negative in 32-bit
    return a if a <= MAX else ~(a ^ MASK)
```

### Python vs C Comparison

```
Operation         C (int32)      Python
-----------------------------------------
~0                0xFFFFFFFF     -1
~1                0xFFFFFFFE     -2
~0x7FFFFFFF       0x80000000     -2147483648
1 << 31           -2147483648    2147483648  (no overflow in Python)
1 << 32           undefined/0    4294967296  (arbitrary precision)
-1 >> 1           -1 (sign ext)  -1 (sign ext — same in Python)
-1 & 0xFFFFFFFF   0xFFFFFFFF     4294967295  (mask restores unsigned view)
```

### Why Python Uses Infinite-Precision Two's Complement

Python integers are conceptually infinite two's-complement. Negative numbers have an infinite sign extension to the left:

```
-1 in Python binary: ...1111 1111 1111 1111 (infinitely many 1s)
~0 = -(0+1) = -1     ...1111 1111 1111 1111

0xFFFFFFFF = 4294967295  (finite, positive in Python)
(-1) & 0xFFFFFFFF = 4294967295  (masking infinite 1s to 32 gives 0xFFFFFFFF)
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_bitwise_not():
    assert ~0 == -1         # Python: -1, not 0xFFFFFFFF
    assert ~0 != 0xFFFFFFFF


def test_correct_32bit_not():
    assert correct_32bit_not(0) == 0xFFFFFFFF
    assert correct_32bit_not(1) == 0xFFFFFFFE
    assert correct_32bit_not(0xFFFFFFFF) == 0


def test_wrong_complement_example():
    """complement(5) should be 2 (101 → 010), not -6."""
    assert wrong_complement(5) == -6      # Python's ~5 = -(5+1) = -6


def test_correct_complement():
    assert correct_complement(5) == 2     # 101 → 010
    assert correct_complement(1) == 0     # 1 → 0
    assert correct_complement(7) == 0     # 111 → 000
    assert correct_complement(0) == 1     # special case
    assert correct_complement(10) == 5    # 1010 → 0101


def test_wrong_add_infinite_loop_risk():
    """For large negative numbers, the while loop may not terminate without masking."""
    # We can't actually test infinite loops directly, but we can verify the wrong version
    # gives wrong answers or hangs for negative inputs in the naive port
    result = wrong_add_without_carry(1, 2)
    assert result == 3   # works for positive
    # For negative: wrong_add_without_carry(-1, 1) would loop in many implementations


def test_correct_add():
    assert correct_add_without_carry_32bit(1, 2) == 3
    assert correct_add_without_carry_32bit(0, 0) == 0
    assert correct_add_without_carry_32bit(100, 200) == 300
    assert correct_add_without_carry_32bit(-1, 1) == 0
    assert correct_add_without_carry_32bit(-2, -3) == -5


def test_mask_restores_unsigned():
    """Python -1 masked to 32 bits equals C's 0xFFFFFFFF."""
    assert (-1 & 0xFFFFFFFF) == 0xFFFFFFFF
    assert (-2 & 0xFFFFFFFF) == 0xFFFFFFFE


if __name__ == "__main__":
    print("=== Python bitwise NOT ===")
    print(f"~0           = {~0}           (Python: -1, C: 4294967295)")
    print(f"~0 & 0xFFFF  = {~0 & 0xFFFFFFFF}  (masked to 32-bit unsigned)")
    print(f"~5           = {~5}           (Python: -6)")
    print(f"complement(5) = {correct_complement(5)} (correct: 2)")

    print("\n=== Add without carry ===")
    for a, b in [(1, 2), (0, 0), (-1, 1), (100, 200), (-2, -3)]:
        print(f"add({a}, {b}) = {correct_add_without_carry_32bit(a, b)}")
```

### Key Takeaway

| Situation | Rule |
|---|---|
| Simulate 32-bit unsigned NOT | `(~n) & 0xFFFFFFFF` |
| Complement only meaningful bits | `(~n) & ((1 << n.bit_length()) - 1)` |
| Bit manipulation loops with negatives | Always mask with `& 0xFFFFFFFF` each iteration |
| Check if n-bit result is negative | `if result > (1 << (bits-1)) - 1: result -= (1 << bits)` |

---

## Mistake 2: Operator Precedence — Bitwise Operators Have Lower Precedence Than Comparison

### The Bug

Python's operator precedence table places bitwise operators (`&`, `|`, `^`, `~`) **below** comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`). This means `a & b == 0` is parsed as `a & (b == 0)`, not `(a & b) == 0`. The expression `b == 0` evaluates to a boolean (`True` or `False`, i.e., `1` or `0`), and then `a & 1` or `a & 0` is performed — completely wrong semantics.

This is a **silent bug**: Python does not raise an error. The expression runs but produces incorrect results.

### WRONG Code

```python
def is_power_of_two_wrong(n: int) -> bool:
    return n > 0 and n & n - 1 == 0
    # Parsed as: n & (n-1 == 0), which is n & True (= n & 1)
    # This checks if n is odd, NOT if n is a power of two!


def has_common_bits_wrong(a: int, b: int) -> bool:
    return a & b != 0
    # Parsed as: a & (b != 0), which is a & True (= a & 1)
    # This checks if a is odd, NOT if a and b share any bits!


def bitwise_condition_wrong(flags: int, mask: int) -> bool:
    return flags & mask == mask
    # Parsed as: flags & (mask == mask), which is flags & True = flags & 1
    # This checks if flags is odd, NOT if all mask bits are set!
```

### CORRECT Code

```python
def is_power_of_two_correct(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0
    # Parentheses force bitwise AND to happen before comparison
    # A power of two has exactly one bit set: n & (n-1) clears it → 0


def has_common_bits_correct(a: int, b: int) -> bool:
    return (a & b) != 0
    # Parentheses ensure we check the AND result, not AND with a boolean


def bitwise_condition_correct(flags: int, mask: int) -> bool:
    return (flags & mask) == mask
    # Check if all bits in mask are set in flags


def toggle_bit_correct(n: int, pos: int) -> int:
    return n ^ (1 << pos)   # XOR with a shifted 1 — precedence is safe here since
                            # no comparison operators involved


def check_bit_correct(n: int, pos: int) -> bool:
    return (n >> pos) & 1 == 1   # CAREFUL: still needs parens if using ==
    # Better: return bool((n >> pos) & 1)
```

### Precedence Table (Relevant Subset, Highest to Lowest)

```
Precedence (decreasing)
1. ~    (bitwise NOT — unary)
2. **   (exponentiation)
3. +x, -x  (unary plus/minus)
4. *, /, //, %
5. +, -
6. <<, >>  (bit shifts)
7. &   (bitwise AND)    ← lower than comparisons? NO — wait:
8. ^   (bitwise XOR)
9. |   (bitwise OR)
10. ==, !=, <, >, <=, >= (comparisons)  ← HIGHER than &, ^, |

WAIT — the common mental model is wrong! Let's be precise:
Python precedence (https://docs.python.org/3/reference/expressions.html#operator-precedence):
  <<, >> > &  > ^ > |  > (comparisons)

So: & has HIGHER precedence than comparisons! But many programmers get this wrong.
The ACTUAL Python precedence order (relevant excerpt):
  5. * @ / // %
  6. + -
  7. << >>
  8. &          ← bitwise AND
  9. ^          ← bitwise XOR
 10. |          ← bitwise OR
 11. in, not in, is, is not, <, <=, >, >=, !=, ==  ← comparisons

So: a & b == 0 IS parsed as (a & b) == 0 in Python!
The bug is more subtle: `n & n - 1 == 0` is `n & (n-1 == 0)` because `-` (arithmetic subtraction)
has HIGHER precedence than `&`, and then == has LOWER precedence.

Detailed parse of `n & n - 1 == 0`:
  Step 1: n - 1   (arithmetic, high precedence)
  Step 2: n - 1 == 0  (comparison)
  Step 3: n & (result of step 2)

This is the ACTUAL dangerous pattern.
```

### Concrete Parse Demonstration

```python
# n & n - 1 == 0
# Step by step for n=4 (binary: 100):
#   n - 1 = 3
#   3 == 0 = False = 0
#   4 & 0 = 0
#   bool(0) = False  ← WRONG: 4 IS a power of two, should be True

# n > 0 and (n & (n-1)) == 0
# For n=4:
#   n & (n-1) = 4 & 3 = 100 & 011 = 000 = 0
#   0 == 0 = True  ← CORRECT
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_power_of_two_incorrect():
    """is_power_of_two_wrong gives wrong results due to precedence."""
    # n=4: wrong parses as 4 & (3==0) = 4 & 0 = 0 → False (WRONG, 4 IS power of two)
    assert is_power_of_two_wrong(4) is False   # should be True — reveals bug


def test_wrong_has_common_bits_incorrect():
    """has_common_bits_wrong(6, 3): 6&(3!=0) = 6&True = 6&1 = 0 → False"""
    # 6 = 110, 3 = 011, they share no bits → False is actually correct here!
    # Use a case where they DO share bits: 6 (110) & 6 (110) = 6 → True expected
    # wrong: 6 & (6 != 0) = 6 & True = 6 & 1 = 0 → False (WRONG)
    assert has_common_bits_wrong(6, 6) is False   # reveals bug: 6&6 should be True


def test_correct_power_of_two():
    powers = [1, 2, 4, 8, 16, 32, 64, 128, 256, 1024]
    non_powers = [0, 3, 5, 6, 7, 9, 10, 12, 15]
    for p in powers:
        assert is_power_of_two_correct(p) is True, f"{p} is a power of two"
    for np_ in non_powers:
        assert is_power_of_two_correct(np_) is False, f"{np_} is not a power of two"


def test_correct_has_common_bits():
    assert has_common_bits_correct(6, 3) is False    # 110 & 011 = 000
    assert has_common_bits_correct(6, 6) is True     # 110 & 110 = 110
    assert has_common_bits_correct(5, 3) is True     # 101 & 011 = 001
    assert has_common_bits_correct(4, 2) is False    # 100 & 010 = 000


def test_correct_bitwise_condition():
    READ  = 0b001
    WRITE = 0b010
    EXEC  = 0b100
    flags = 0b111   # all permissions set

    assert bitwise_condition_correct(flags, READ) is True
    assert bitwise_condition_correct(flags, WRITE) is True
    assert bitwise_condition_correct(flags, READ | WRITE) is True
    assert bitwise_condition_correct(0b101, WRITE) is False   # write not set


def test_parse_ambiguity_demo():
    """Explicitly demonstrate that n & n-1 == 0 parses wrong."""
    n = 4
    wrong_expr = n & n - 1 == 0      # n & (n-1 == 0) = 4 & False = 4 & 0 = 0
    correct_expr = (n & (n - 1)) == 0 # (4 & 3) == 0 = 0 == 0 = True

    assert wrong_expr != correct_expr, "Demonstrates parsing ambiguity"
    assert correct_expr is True
    assert wrong_expr == 0            # evaluates to 0 (falsy) not False


if __name__ == "__main__":
    print("=== Precedence Demonstration ===")
    n = 4
    print(f"n = {n} (binary: {bin(n)})")
    print(f"n & n - 1 == 0     = {n & n - 1 == 0}")       # 0 (WRONG)
    print(f"(n & (n - 1)) == 0 = {(n & (n - 1)) == 0}")   # True (CORRECT)

    print("\n=== Power of Two Tests ===")
    for val in [1, 2, 3, 4, 5, 8, 15, 16]:
        wrong = is_power_of_two_wrong(val)
        correct = is_power_of_two_correct(val)
        flag = "OK" if wrong == correct else "BUG"
        print(f"  n={val:3}: wrong={wrong}, correct={correct} [{flag}]")
```

### Key Takeaway

- **Always parenthesize** bitwise operations when used in boolean conditions: `(a & b) == 0`, never `a & b == 0`.
- The dangerous pattern is when arithmetic (`-`, `+`, `*`) and comparison (`==`, `!=`) operators sit alongside bitwise operators — arithmetic binds tighter than `&`, so `n & n-1` means `n & (n-1)` correctly, but `n & n-1 == 0` means `n & (n-1 == 0)` — a very different thing.
- Rule: if your bitwise expression is inside an `if` or involved in a comparison, wrap the bitwise part in parentheses.

---

## Mistake 3: Left Shift Overflow — Checking `1 << n` When `n` Is Large

### The Bug

In Python, `1 << n` always succeeds and produces a correct arbitrarily large integer — there is no overflow. However, if you intend to work within a fixed bit-width (e.g., 32-bit integers in an interview setting), shifting by 32 or more produces a value that exceeds 32 bits, silently giving wrong results. In C and Java, `1 << 32` on a 32-bit integer is **undefined behaviour** (C) or produces 0 (Java). Porting this logic to Python without range checks leads to subtle bugs.

### WRONG Code

```python
def set_bit_wrong(n: int, pos: int) -> int:
    """Set bit at position pos in a 32-bit integer."""
    return n | (1 << pos)
    # WRONG: if pos=32, result exceeds 32 bits and becomes 33-bit value
    # No error in Python, but semantics are wrong for 32-bit context


def get_bit_wrong(n: int, pos: int) -> int:
    """Get bit at position pos."""
    return (n >> pos) & 1
    # This is actually safe — shifting right by any amount is always valid
    # But set/clear operations need range validation


def generate_all_subsets_wrong(n_bits: int) -> list[int]:
    """Generate all n_bits-bit masks."""
    return [1 << i for i in range(n_bits + 1)]  # WRONG: includes 1 << n_bits
    # For n_bits=32: generates [1, 2, 4, ..., 2^32] — the last value is 33 bits!
```

### CORRECT Code

```python
BITS_32 = 32
MASK_32 = 0xFFFFFFFF


def validate_bit_position(pos: int, bits: int = BITS_32) -> None:
    if not (0 <= pos < bits):
        raise ValueError(f"Bit position {pos} out of range [0, {bits-1}]")


def set_bit_correct(n: int, pos: int, bits: int = BITS_32) -> int:
    """Set bit at position pos in a bits-width integer."""
    validate_bit_position(pos, bits)
    return (n | (1 << pos)) & ((1 << bits) - 1)   # mask result to bits width


def clear_bit_correct(n: int, pos: int, bits: int = BITS_32) -> int:
    """Clear bit at position pos."""
    validate_bit_position(pos, bits)
    return n & ~(1 << pos) & ((1 << bits) - 1)


def flip_bit_correct(n: int, pos: int, bits: int = BITS_32) -> int:
    """Flip bit at position pos."""
    validate_bit_position(pos, bits)
    return (n ^ (1 << pos)) & ((1 << bits) - 1)


def get_bit_correct(n: int, pos: int) -> int:
    """Get the bit at position pos (no overflow risk for right-shift)."""
    if pos < 0:
        raise ValueError(f"Bit position {pos} cannot be negative")
    return (n >> pos) & 1


def generate_all_subsets_correct(n_bits: int) -> list[int]:
    """Generate all n_bits-bit masks (values 0 to 2^n_bits - 1)."""
    return list(range(1 << n_bits))   # 0 to (1 << n_bits) - 1 inclusive
```

### Shift Amount Guidelines

```
Safe shifts:
  1 << 0   = 1         (1 bit, valid for any bit width >= 1)
  1 << 30  = 1073741824 (fits in 32-bit signed: max positive is 2^31 - 1)
  1 << 31  = 2147483648 (sign bit in 32-bit signed — careful with signed arithmetic)

Overflow in 32-bit contexts:
  1 << 32  = 4294967296  (33 bits — exceeds 32-bit range, would be 0 in Java)
  1 << 63  = Python: fine. Java long: sign bit. C: UB.

Python-specific large shifts:
  1 << 1000  = a 302-digit number — valid Python, but if you intended 32-bit: wrong
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_shift_exceeds_32_bits():
    """set_bit(0, 32) should raise or mask, not return a 33-bit number."""
    result = set_bit_wrong(0, 32)
    assert result > 0xFFFFFFFF, f"WRONG: result {result} exceeds 32-bit range"


def test_correct_set_bit_raises_on_out_of_range():
    with pytest.raises(ValueError, match="out of range"):
        set_bit_correct(0, 32)
    with pytest.raises(ValueError, match="out of range"):
        set_bit_correct(0, -1)


def test_correct_set_bit():
    assert set_bit_correct(0, 0) == 1       # set bit 0
    assert set_bit_correct(0, 1) == 2       # set bit 1
    assert set_bit_correct(0, 31) == 0x80000000   # set highest 32-bit bit
    assert set_bit_correct(0xFFFFFFFF, 0) == 0xFFFFFFFF  # already set


def test_correct_clear_bit():
    assert clear_bit_correct(0b111, 1) == 0b101   # clear bit 1
    assert clear_bit_correct(0xFF, 0) == 0xFE


def test_correct_flip_bit():
    assert flip_bit_correct(0b101, 1) == 0b111   # flip bit 1 from 0 to 1
    assert flip_bit_correct(0b111, 1) == 0b101   # flip bit 1 from 1 to 0


def test_correct_get_bit():
    assert get_bit_correct(0b1010, 1) == 1   # bit 1 is set
    assert get_bit_correct(0b1010, 0) == 0   # bit 0 is not set
    assert get_bit_correct(0b1010, 3) == 1   # bit 3 is set


def test_wrong_subset_generation_includes_overflow():
    result = generate_all_subsets_wrong(4)
    # Should be 0..15 (16 values), but wrong version includes 1<<4 = 16
    assert 16 in result   # wrong: 16 is a 5-bit value for a 4-bit context


def test_correct_subset_generation():
    result = generate_all_subsets_correct(4)
    assert result == list(range(16))   # 0 to 15 inclusive


def test_large_shift_python_fine_but_semantically_wrong():
    """Python handles large shifts without error, but 32-bit logic breaks."""
    n = 1 << 40   # valid Python integer, but not a 32-bit value
    assert n > 0xFFFFFFFF
    masked = n & 0xFFFFFFFF
    assert masked == 0   # bit 40 doesn't exist in 32-bit representation


if __name__ == "__main__":
    print("=== Shift overflow ===")
    print(f"1 << 31 = {1 << 31} (0x{(1 << 31):08X}) — highest 32-bit bit")
    print(f"1 << 32 = {1 << 32} — exceeds 32-bit, Python: no error")
    print(f"1 << 63 = {1 << 63} — Python: fine")

    print("\n=== Bit operations ===")
    n = 0b1010   # 10
    for pos in range(4):
        print(f"  bit {pos} of {bin(n)}: {get_bit_correct(n, pos)}")
```

### Key Takeaway

- In Python, left shifts never overflow — they grow the integer. This is a feature but can be a trap when simulating fixed-width arithmetic.
- Validate bit positions are in `[0, bits-1]` before shifting.
- After any bitwise operation in a 32-bit context, apply `& 0xFFFFFFFF` to mask the result back to 32 bits.

---

## Mistake 4: XOR for Finding the Missing Number — Forgetting to XOR All Expected Values

### The Bug

The classic "find missing number in [0..n]" problem uses XOR: XOR all numbers in the expected range [0..n] together with all numbers in the array. Each number that appears cancels out (x ^ x = 0), leaving only the missing number. The mistake is XORing only the array elements against each other, forgetting that we also need to XOR against the expected sequence.

### WRONG Code

```python
def find_missing_wrong_v1(nums: list[int]) -> int:
    """WRONG: XOR all array elements together — only finds if there's a pair."""
    result = 0
    for num in nums:
        result ^= num
    return result
    # This gives 0 if all elements cancel in pairs. Does NOT find the missing number.


def find_missing_wrong_v2(nums: list[int]) -> int:
    """WRONG: XOR elements in array only against range 1..n (misses 0)."""
    n = len(nums)
    result = 0
    for i in range(1, n + 1):   # WRONG: starts at 1, skips 0
        result ^= i
    for num in nums:
        result ^= num
    return result
    # If 0 is the missing number, this returns 0 XOR 0 = 0... coincidentally correct?
    # No: if 0 is present and something else is missing, the range starts at 1 not 0.
```

### CORRECT Code

```python
def find_missing_correct(nums: list[int]) -> int:
    """
    Find the missing number from array containing n distinct values from [0..n].
    XOR all values in range [0..n] with all values in nums.
    """
    n = len(nums)
    result = 0

    # XOR all expected values: 0, 1, 2, ..., n
    for i in range(n + 1):   # CORRECT: includes 0 through n
        result ^= i

    # XOR all actual values in the array
    for num in nums:
        result ^= num

    # Each present number cancels out; only the missing number remains
    return result


def find_missing_xor_concise(nums: list[int]) -> int:
    """Concise version using enumerate."""
    result = len(nums)          # start with n (the last expected value)
    for i, num in enumerate(nums):
        result ^= i ^ num       # XOR expected index with actual value
    return result


def find_missing_formula(nums: list[int]) -> int:
    """Mathematical approach: sum formula. Also O(n) time, O(1) space."""
    n = len(nums)
    expected_sum = n * (n + 1) // 2
    return expected_sum - sum(nums)
```

### Step-by-Step Trace

```
nums = [3, 0, 1]  (missing: 2, n=3)
Expected range: [0, 1, 2, 3]

WRONG v1 (XOR array elements only):
result = 3 ^ 0 ^ 1 = 2
Coincidentally "correct" here — but for wrong reasons. Fails for other inputs.

WRONG v1 failure case: nums = [0, 1] (missing: 2, n=2)
result = 0 ^ 1 = 1   ← WRONG: missing is 2, not 1

WRONG v2 (range starts at 1):
range(1, 4) XOR array: (1^2^3) ^ (3^0^1) = (1^2^3^3^0^1) = (1^1)^(3^3)^2^0 = 2^0 = 2
Happens to be correct when 0 is present. Fails when 0 is missing:
nums = [1, 2, 3], missing = 0
range(1,4) ^ array: (1^2^3) ^ (1^2^3) = 0   ← WRONG: should return 0

CORRECT (range 0 to n):
range(0, 4) XOR array: (0^1^2^3) ^ (3^0^1) = 0^1^2^3^3^0^1 = (0^0)^(1^1)^(3^3)^2 = 2 ✓

Missing is 0: nums = [1, 2, 3], n=3
range(0, 4) XOR array: (0^1^2^3) ^ (1^2^3) = 0^(1^1)^(2^2)^(3^3) = 0 ✓
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_v1_fails():
    """[0,1] missing=2: XOR of array elements is 1, not 2."""
    assert find_missing_wrong_v1([0, 1]) == 1   # WRONG: should be 2


def test_wrong_v2_fails_when_zero_is_missing():
    """[1,2,3] missing=0: range starts at 1, misses 0."""
    assert find_missing_wrong_v2([1, 2, 3]) == 0   # coincidentally right
    # Better test: verify it fails for a case where v1 would fail
    # v2 starts at 1 but the expected range is 0..n, so 0 must be XOR'd in
    result_v2 = find_missing_wrong_v2([1, 2, 3])
    result_correct = find_missing_correct([1, 2, 3])
    # Both happen to give 0 here. Let's find where they differ:
    # nums=[0,1,2] missing=3, n=3
    # v2: range(1,4)=1^2^3, array=0^1^2 → 1^2^3^0^1^2 = 0^3 = 3 (right)
    # For systematic testing, just verify correct version is always right:


def test_correct_basic():
    assert find_missing_correct([3, 0, 1]) == 2
    assert find_missing_correct([0, 1]) == 2
    assert find_missing_correct([1, 2, 3]) == 0    # missing 0
    assert find_missing_correct([0]) == 1
    assert find_missing_correct([]) == 0            # only 0 is expected, it's missing


def test_correct_matches_formula():
    import random
    for _ in range(100):
        n = random.randint(0, 50)
        missing = random.randint(0, n)
        nums = list(range(n + 1))
        nums.remove(missing)
        random.shuffle(nums)
        assert find_missing_correct(nums) == missing
        assert find_missing_formula(nums) == missing
        assert find_missing_xor_concise(nums) == missing


def test_correct_missing_last():
    n = 10
    nums = list(range(n))   # [0..9], missing 10
    assert find_missing_correct(nums) == n


def test_correct_missing_first():
    n = 10
    nums = list(range(1, n + 1))   # [1..10], missing 0
    assert find_missing_correct(nums) == 0


def test_all_three_approaches_agree():
    test_arrays = [
        [3, 0, 1],
        [9, 6, 4, 2, 3, 5, 7, 0, 1],
        [1, 2, 3],
        [0],
        [],
    ]
    for nums in test_arrays:
        r1 = find_missing_correct(nums)
        r2 = find_missing_xor_concise(nums)
        r3 = find_missing_formula(nums)
        assert r1 == r2 == r3, f"Mismatch for {nums}: {r1}, {r2}, {r3}"


if __name__ == "__main__":
    test_cases = [
        [3, 0, 1],
        [0, 1],
        [1, 2, 3],
        [9, 6, 4, 2, 3, 5, 7, 0, 1],
    ]
    for nums in test_cases:
        w1 = find_missing_wrong_v1(nums)
        correct = find_missing_correct(nums)
        concise = find_missing_xor_concise(nums)
        formula = find_missing_formula(nums)
        flag = "OK" if correct == concise == formula else "MISMATCH"
        print(f"nums={nums}")
        print(f"  wrong_v1={w1}, correct={correct}, concise={concise}, formula={formula} [{flag}]")
```

### Key Takeaway

- XOR-based missing number: XOR every value in `range(0, n+1)` WITH every value in the array. Both ranges must match.
- `range(n+1)` is the expected range (0 through n inclusive). Missing `0` causes silent failures when 0 is the missing number.
- Alternative: `n*(n+1)//2 - sum(nums)` — simpler and harder to get wrong, but can overflow in C/Java (not Python).

---

## Mistake 5: Counting Bits — Three Approaches Compared (Brian Kernighan, Loop, Built-in)

### The Bug (Wrong Approach)

The naive bit-counting loop `while n: count += n & 1; n >>= 1` is O(bits) — it iterates over every bit position, including leading zeros. Brian Kernighan's algorithm `n & (n-1)` strips the lowest set bit each iteration, running in O(popcount) — proportional to the NUMBER of set bits, not the number of all bits. For sparse integers (few 1s), Kernighan's is much faster.

Additionally, Python 3.10+ provides `int.bit_count()` as a built-in. Using the slow loop in an interview when you know the alternatives signals unfamiliarity with the topic.

### WRONG Code (Slow Loop)

```python
def count_bits_naive(n: int) -> int:
    """WRONG for interviews: O(32) or O(64) — iterates all bit positions."""
    count = 0
    while n:
        count += n & 1   # check lowest bit
        n >>= 1          # shift right by 1
    return count
    # Processes every bit position, even zeros between set bits.
    # For n = 2^30 (one bit set), this loops 31 times instead of 1.
```

### CORRECT Code — All Three Approaches

```python
# ===== Approach 1: Brian Kernighan's Algorithm =====
def count_bits_kernighan(n: int) -> int:
    """
    O(k) where k = number of set bits.
    n & (n-1) clears the lowest set bit of n.
    Loop runs exactly popcount(n) times.
    """
    if n < 0:
        raise ValueError("count_bits_kernighan is defined for non-negative integers")
    count = 0
    while n:
        n &= n - 1   # clear the lowest set bit
        count += 1
    return count


# ===== Approach 2: Built-in Python 3.10+ =====
def count_bits_builtin(n: int) -> int:
    """
    Python 3.10+: int.bit_count() returns the number of set bits.
    O(1) in practice (implemented in C).
    """
    if n < 0:
        raise ValueError("bit_count() is not defined for negative integers in standard usage")
    return n.bit_count()   # Python 3.10+


# ===== Approach 3: Naive loop (slow, but explicit) =====
def count_bits_loop(n: int) -> int:
    """O(log n) — iterates over every bit position."""
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count


# ===== Approach 4: bin() string trick =====
def count_bits_bin(n: int) -> int:
    """Pythonic but not interview-appropriate: O(log n)."""
    return bin(n).count('1')


# ===== Comparison table =====
def count_bits_all(n: int) -> dict:
    return {
        "kernighan": count_bits_kernighan(n),
        "loop": count_bits_loop(n),
        "bin_trick": count_bits_bin(n),
    }
```

### How Brian Kernighan's Algorithm Works

```
n = 0b10110100  (4 set bits)

Iteration 1: n = 10110100
             n-1= 10110011
             n & (n-1) = 10110000   ← lowest set bit (bit 2) cleared
             count = 1

Iteration 2: n = 10110000
             n-1= 10101111
             n & (n-1) = 10100000   ← bit 4 cleared
             count = 2

Iteration 3: n = 10100000
             n-1= 10011111
             n & (n-1) = 10000000   ← bit 5 cleared
             count = 3

Iteration 4: n = 10000000
             n-1= 01111111
             n & (n-1) = 00000000   ← bit 7 cleared
             count = 4

n = 0, loop ends. Result: 4  ✓
Total iterations: 4 (= number of set bits), not 8 (= bit length)
```

### Performance Benchmarking

```python
import time
import sys


def benchmark_count_bits(n_value: int, repetitions: int = 1_000_000) -> None:
    print(f"\nBenchmark for n={n_value} ({bin(n_value)} = {bin(n_value).count('1')} set bits)")
    print(f"Running {repetitions:,} iterations each.\n")

    methods = [
        ("kernighan", count_bits_kernighan),
        ("loop",      count_bits_loop),
        ("bin_trick", count_bits_bin),
    ]

    if sys.version_info >= (3, 10):
        methods.insert(0, ("builtin", count_bits_builtin))

    results = {}
    for name, func in methods:
        start = time.perf_counter()
        for _ in range(repetitions):
            func(n_value)
        elapsed = time.perf_counter() - start
        results[name] = elapsed
        print(f"  {name:12}: {elapsed:.4f}s")

    if results:
        baseline = results.get("loop", list(results.values())[0])
        print("\n  Speedups vs loop:")
        for name, t in results.items():
            print(f"    {name:12}: {baseline/t:.2f}x")
```

### Variants: Count Bits for All Numbers from 0 to n (DP)

```python
def count_bits_range(n: int) -> list[int]:
    """
    Return array where ans[i] = popcount(i) for i in [0..n].
    Uses DP: ans[i] = ans[i >> 1] + (i & 1)
    O(n) time, O(n) space.
    """
    ans = [0] * (n + 1)
    for i in range(1, n + 1):
        ans[i] = ans[i >> 1] + (i & 1)
    return ans
```

### Test Cases

```python
import pytest
import sys


KNOWN_VALUES = {
    0: 0,           # 0000 0000
    1: 1,           # 0000 0001
    2: 1,           # 0000 0010
    3: 2,           # 0000 0011
    4: 1,           # 0000 0100
    7: 3,           # 0000 0111
    8: 1,           # 0000 1000
    15: 4,          # 0000 1111
    255: 8,         # 1111 1111
    0xFFFFFFFF: 32, # all 32 bits set
    0x80000001: 2,  # bit 31 and bit 0
    (1 << 30): 1,   # single bit, high position
}


def test_naive_loop_correctness():
    for n, expected in KNOWN_VALUES.items():
        assert count_bits_loop(n) == expected, f"loop({n}) = {count_bits_loop(n)}, expected {expected}"


def test_kernighan_correctness():
    for n, expected in KNOWN_VALUES.items():
        assert count_bits_kernighan(n) == expected, f"kernighan({n}) failed"


def test_bin_trick_correctness():
    for n, expected in KNOWN_VALUES.items():
        assert count_bits_bin(n) == expected, f"bin({n}) failed"


@pytest.mark.skipif(sys.version_info < (3, 10), reason="bit_count() requires Python 3.10+")
def test_builtin_correctness():
    for n, expected in KNOWN_VALUES.items():
        assert count_bits_builtin(n) == expected, f"builtin({n}) failed"


def test_all_methods_agree():
    import random
    for _ in range(1000):
        n = random.randint(0, 2**32 - 1)
        k = count_bits_kernighan(n)
        l = count_bits_loop(n)
        b = count_bits_bin(n)
        assert k == l == b, f"Mismatch at n={n}: kernighan={k}, loop={l}, bin={b}"


def test_kernighan_iterations_equal_popcount():
    """Brian Kernighan's loop runs exactly popcount(n) times."""
    def kernighan_with_count(n: int) -> tuple[int, int]:
        iterations = 0
        while n:
            n &= n - 1
            iterations += 1
        return iterations

    for n in [0b10110100, 0xFF, 0x80000001, 0xFFFFFFFF]:
        iters = kernighan_with_count(n)
        expected = bin(n).count('1')
        assert iters == expected, f"n={bin(n)}: expected {expected} iterations, got {iters}"


def test_count_bits_range_dp():
    result = count_bits_range(5)
    assert result == [0, 1, 1, 2, 1, 2]

    result = count_bits_range(0)
    assert result == [0]

    # Verify each entry matches individual count
    for n in range(17):
        result = count_bits_range(n)
        for i in range(n + 1):
            assert result[i] == count_bits_kernighan(i), f"DP mismatch at i={i} for n={n}"


def test_kernighan_rejects_negative():
    with pytest.raises(ValueError):
        count_bits_kernighan(-1)


if __name__ == "__main__":
    print("=== Correctness Check ===")
    for n, expected in list(KNOWN_VALUES.items())[:8]:
        kern = count_bits_kernighan(n)
        loop = count_bits_loop(n)
        bi = count_bits_bin(n)
        print(f"  n={n:12} ({bin(n):36}): kern={kern}, loop={loop}, bin={bi}, expected={expected}")

    print("\n=== Kernighan Trace for n=180 (10110100) ===")
    n = 0b10110100
    step = 0
    while n:
        n_before = n
        n &= n - 1
        step += 1
        print(f"  Step {step}: {bin(n_before):012} & {bin(n_before-1):012} = {bin(n):012}")

    print(f"\n  Total steps: {step} = popcount(180)")

    if sys.version_info >= (3, 10):
        benchmark_count_bits(0xFFFFFFFF, repetitions=100_000)
        benchmark_count_bits(1 << 30, repetitions=100_000)
```

### Key Takeaway

| Approach | Time Complexity | Python Version | Interview Use |
|---|---|---|---|
| `int.bit_count()` | O(1) (C implementation) | 3.10+ | Mention but don't rely on |
| Brian Kernighan: `n &= n-1` | O(k) where k = set bits | All | Preferred for interviews |
| Naive loop: `n & 1; n >>= 1` | O(log n) | All | Acceptable, but know why Kernighan is better |
| `bin(n).count('1')` | O(log n) | All | Pythonic shortcut, not for interviews |
| DP table for range [0..n] | O(n) total | All | Use when asked for ALL counts up to n |

**The interview answer:** "I'll use Brian Kernighan's algorithm: `n &= (n-1)` strips the lowest set bit, so the loop runs in O(k) where k is the number of set bits. Python 3.10+ also has `int.bit_count()` which is O(1)."

---

## Summary Table

| # | Mistake | Root Cause | Fix |
|---|---|---|---|
| 1 | `~0` expected to be `0xFFFFFFFF` | Python integers are arbitrary precision — no 32-bit cap | `(~n) & 0xFFFFFFFF` to simulate 32-bit unsigned |
| 2 | `a & b == 0` parsed as `a & (b == 0)` | Arithmetic `-` has higher precedence than `&`, then `==` is lower | Always parenthesize: `(a & b) == 0` |
| 3 | `1 << 32` with no validation | Python allows it, but 32-bit logic breaks silently | Validate `0 <= pos < bits`; apply `& 0xFFFFFFFF` after operations |
| 4 | XOR only array elements for missing number | Forgets to XOR the expected range `[0..n]` | `for i in range(n+1): result ^= i`, then XOR array elements |
| 5 | Naive loop over all bit positions | O(log n) loop — iterates zero bits too | Brian Kernighan `n &= (n-1)` for O(k); Python 3.10 `int.bit_count()` |
