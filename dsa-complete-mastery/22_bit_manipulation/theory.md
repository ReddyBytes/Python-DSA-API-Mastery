# 📘 Bit Manipulation — Controlling the Machine at Binary Level

> Computers don’t understand numbers like we do.
> They understand only 0 and 1.
>
> Bit manipulation means:
> Talking directly in computer’s language.

Bit manipulation is:

- Fast
- Efficient
- Often used in optimization
- Frequently tested in interviews

Once you understand binary,
this becomes fun.

---

# 🧠 1️⃣ Real Life Story — Light Switch Board

Imagine a switch board with 8 switches.

Each switch can be:

ON (1)
OFF (0)

Example:

```
Switches: 1 0 1 1 0 0 1 0
```

That’s a binary number.

Each switch represents a bit.

Bit manipulation means:
Turning switches ON or OFF intelligently.

---

# 🔢 2️⃣ Understanding Binary Numbers

Example:

Decimal 5 in binary:

```
5 = 101
```

Position values:

```
(1 × 2²) + (0 × 2¹) + (1 × 2⁰)
```

Binary is base 2.

Each bit represents power of 2.

---

# ⚙️ 3️⃣ Bitwise Operators

---

## 🔹 AND (&)

1 & 1 = 1  
Else = 0

Example:

```
5 = 101
3 = 011
------------
    001 = 1
```

Used for masking.

---

## 🔹 OR (|)

1 | 0 = 1  
0 | 0 = 0

Example:

```
101
011
---
111 = 7
```

Used to set bits.

---

## 🔹 XOR (^)

Same bits → 0  
Different bits → 1

Example:

```
101
011
---
110 = 6
```

Very powerful operator.

---

## 🔹 NOT (~)

Flips bits.

~101 → 010 (in limited bit view)

---

## 🔹 Left Shift (<<)

Shift bits left.

5 << 1:

101 → 1010 = 10

Multiply by 2.

---

## 🔹 Right Shift (>>)

Shift bits right.

8 >> 1:

1000 → 0100 = 4

Divide by 2.

---

# 💡 4️⃣ Important Bit Tricks

---

## 🔹 Check If Number Is Even

Last bit 0 → even

```
if n & 1 == 0:
```

---

## 🔹 Check If Power of Two

Power of two has only one 1 bit.

Example:
8 = 1000

Trick:

```
n & (n - 1) == 0
```

Works because:

1000
0111
----
0000

---

## 🔹 Count Set Bits

Use:

Brian Kernighan’s Algorithm:

```
while n:
    n = n & (n - 1)
    count += 1
```

Removes lowest set bit each time.

Time:
O(number of set bits)

---

## 🔹 Swap Without Temp Variable

```
a = a ^ b
b = a ^ b
a = a ^ b
```

XOR trick.

---

# 🔄 5️⃣ XOR Special Properties

1. a ^ a = 0
2. a ^ 0 = a
3. XOR is commutative

Used in:

Finding single number in array.

Example:

[2, 3, 2, 4, 4]

XOR all:
Result = 3

Because duplicates cancel.

---

# 🎯 6️⃣ Subset Generation Using Bits

For n elements:

Total subsets = 2^n

Represent each subset as binary number.

Example:

Elements: [A, B, C]

Binary:
000 → []
001 → [C]
010 → [B]
011 → [B, C]
100 → [A]
...

Very clean method.

---

# 🧠 7️⃣ Bitmasking

Bitmask represents state.

Example:

For 4 items:

mask = 1010

Means:
Item 1 and Item 3 selected.

Used in:

- Traveling Salesman
- DP on subsets
- Game states

Advanced usage.

---

# ⚡ 8️⃣ Why Bit Manipulation Is Fast

Bit operations happen at hardware level.

Very low overhead.

Constant time operations.

Often faster than arithmetic.

---

# 🌍 9️⃣ Real-World Applications

- Encryption
- Compression
- Network protocols
- Operating systems
- Memory management
- Permission systems (UNIX file permissions)
- Flags in databases

Bit manipulation used heavily in systems.

---

# ⚠️ 1️⃣0️⃣ Common Mistakes

- Operator precedence confusion
- Not using parentheses
- Forgetting negative number behavior
- Confusing XOR with OR
- Overflow misunderstanding

Bit logic must be precise.

---

# 🧠 1️⃣1️⃣ Mental Model

Think of bit manipulation as:

Controlling switches directly.

Instead of thinking in decimal,
think in ON/OFF states.

Every number is just pattern of switches.

---

# 📌 1️⃣2️⃣ Final Understanding

Bit manipulation is:

- Working at binary level
- Extremely fast
- Powerful for optimization
- Used in subset problems
- Used in system-level programming
- Common in interviews

Mastering bits prepares you for:

- Advanced DP with bitmask
- System programming
- Competitive coding tricks
- Performance optimization

Bit manipulation is small but mighty.

---

# 🔁 Navigation

Previous:  
[21_dynamic_programming/interview.md](/dsa-complete-mastery/21_dynamic_programming/interview.md)

Next:  
[22_bit_manipulation/interview.md](/dsa-complete-mastery/22_bit_manipulation/interview.md)  
[23_segment_tree/theory.md](/dsa-complete-mastery/23_segment_tree/theory.md)

