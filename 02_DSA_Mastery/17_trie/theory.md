<a id="top"></a>
# Trie — The Tree of Words

> If BST organizes numbers,
> Trie organizes letters.
>
> Trie is built for one powerful purpose:
>
> **Fast prefix searching.**

Trie is also called: Prefix Tree.

It is one of the most important structures for string-based problems.

## 📖 Table of Contents

1. [Real Life Story — Dictionary in Your Brain](#1-real-life-story)
2. [What Is a Trie?](#2-what-is-a-trie)
3. [Visual Example](#3-visual-example)
4. [Why Trie Is Powerful](#4-why-trie-is-powerful)
5. [How Trie Node Is Defined](#5-how-trie-node-is-defined)
6. [Inserting Word Into Trie](#6-inserting-word-into-trie)
7. [Searching Word in Trie](#7-searching-word-in-trie)
8. [Searching Prefix](#8-searching-prefix)
9. [Why Not Use Hashmap?](#9-why-not-use-hashmap)
10. [Memory Usage](#10-memory-usage)
11. [Common Trie Problems](#11-common-trie-problems)
12. [Optimization — Using Array Instead of Dictionary](#12-optimization-array)
13. [Real-World Applications](#13-real-world-applications)
14. [Common Mistakes](#14-common-mistakes)
15. [Mental Model](#15-mental-model)
16. [Final Understanding](#16-final-understanding)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
trie node structure · insert · search · prefix search

**Should Learn** — Important for real projects, comes up regularly:
autocomplete pattern · memory optimization with arrays · word search applications

**Good to Know** — Useful in specific situations, not always tested:
trie vs hashmap trade-offs · deletion from trie

**Reference** — Know it exists, look up syntax when needed:
compressed trie · radix tree · patricia tree · DAWG

<a id="1-real-life-story"></a>
# 1. Real Life Story — Dictionary in Your Brain

Imagine you have a dictionary.

You open it and search for:

"cat"

You don't scan every word.

You go to:

C → A → T

Then check if word exists.

Your brain organizes words by prefix.

That structure is Trie.

## Visual: The Filing System That Reads Your Mind

Imagine the world's most organized library.

You walk up to the librarian and say "I'm looking for books about PRO—"

Before you even finish the word, the librarian is already walking toward shelf P.
By the time you say "PRO", they're at shelf P → R → O. They hand you a list of every
book in that section: *Programming*, *Probability*, *Prototypes*, *Protocols*.

They didn't search through every book in the library. They followed the letters.

That's a trie (pronounced "try", from re**trie**val).

A trie organizes words by their letters, level by level. Every node is one character.
Every path from root to a marked node spells out a complete word.

The payoff: search time depends on the length of your query, not the size of your
dictionary. Looking up "cat" in a trie of 1 million words? Exactly 3 steps. Always.

📝 **Practice:** [Q1 · trie-node-structure-dict](./practice.md#q1--trie-node-structure--dict-approach) · [Q2 · trie-node-structure-array](./practice.md#q2--trie-node-structure--array-approach)

> [↑ Back to Top](#top)

<a id="2-what-is-a-trie"></a>
# 2. What Is a Trie?

A Trie is a tree where:

- Each node represents one character
- Words are formed from root to leaf
- Path represents prefix

Important:

Nodes store:
- Children (dictionary/map of characters)
- End-of-word marker

> [↑ Back to Top](#top)

<a id="3-visual-example"></a>
# 3. Visual Example

Insert words:

```
cat
car
dog
```

Trie looks like:

```
          (root)
         /      \
        c        d
       /          \
      a            o
     / \            \
    t   r            g
```

Notice:

"cat" and "car" share prefix "ca".

That is key advantage.

## Visual: Building the Library — Words as Paths

Let's build a trie for these 5 words: `["cat", "car", "card", "care", "dog"]`

```
root
├── c
│   └── a
│       ├── t*          ("cat" ends here)
│       └── r*          ("car" ends here)
│           ├── d*      ("card" ends here)
│           └── e*      ("care" ends here)
└── d
    └── o
        └── g*          ("dog" ends here)
```

The asterisk (*) marks where a complete word ends.

**Count the nodes:** root + c + a + t + r + d + e + d + o + g = 10 nodes.

If we stored each word as a raw string: "cat"(3) + "car"(3) + "card"(4) + "care"(4) +
"dog"(3) = 17 characters.

The trie uses 10 nodes to represent 17 characters worth of words, because
`c`, `a`, and `r` are **shared** between multiple words. The longer the common prefix,
the more you save.

In a real autocomplete system with hundreds of thousands of English words, the root
node's 26 children cover the first letter of every word in the dictionary. All words
starting with 'c' share that one node. All words starting with "ca" share two nodes.

This is the compression that makes tries fast.

> [↑ Back to Top](#top)

<a id="4-why-trie-is-powerful"></a>
# 4. Why Trie Is Powerful

Searching word in Trie:

Time complexity:
O(L)

Where L = length of word.

Not dependent on number of words.

Very efficient for large dictionaries.

> [↑ Back to Top](#top)

<a id="5-how-trie-node-is-defined"></a>
# 5. How Trie Node Is Defined

In Python:

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
```

Each node stores:

- children (map)
- is_end flag

Simple structure.
Very powerful.

> [↑ Back to Top](#top)

<a id="6-inserting-word-into-trie"></a>
# 6. Inserting Word Into Trie

Example:
Insert "cat"

Steps:

1. Start at root.
2. Check if 'c' exists.
3. If not, create.
4. Move to 'c'.
5. Repeat for 'a'.
6. Repeat for 't'.
7. Mark end-of-word = True.

This builds prefix path.

Time:
O(L)

📝 **Practice:** [Q43 · trie-insert-search](../dsa_practice_questions_100.md#q43--normal--trie-insert-search)

## Visual: Insert — One Letter at a Time

The trie starts empty. Let's insert the word `"care"` letter by letter.

```
State 0: just the root.

  root

Insert 'c':
Does root have a child 'c'? No → create it.

  root
  └── c

Insert 'a':
Does 'c' have a child 'a'? No → create it.

  root
  └── c
      └── a

Insert 'r':
Does 'a' have a child 'r'? No → create it.

  root
  └── c
      └── a
          └── r

Insert 'e':
Does 'r' have a child 'e'? No → create it.
Mark 'e' as end of word.

  root
  └── c
      └── a
          └── r
              └── e*    ← "care" is now stored
```

Now let's insert `"card"`. We're inserting into an existing trie:

```
Insert 'c': Does root have 'c'? YES → follow it. (don't create)
Insert 'a': Does 'c' have 'a'? YES → follow it. (don't create)
Insert 'r': Does 'a' have 'r'? YES → follow it. (don't create)
Insert 'd': Does 'r' have 'd'? No → create it. Mark as end.

  root
  └── c
      └── a
          └── r
              ├── e*    ("care")
              └── d*    ("card")  ← branched here
```

"card" and "care" share the path `c → a → r`. They only diverge at the 4th character.
That shared path was traversed, not duplicated. Three nodes doing the work of six.

Insert time: O(L) where L is the length of the word. Nothing depends on how many
words are already in the trie.

📝 **Practice:** [Q3 · insert-a-word](./practice.md#q3--insert-a-word) · [Q16 · full-trie-class](./practice.md#q16--implement-full-trie-class-from-scratch)

> [↑ Back to Top](#top)

<a id="7-searching-word-in-trie"></a>
# 7. Searching Word in Trie

To search "cat":

1. Start at root.
2. Move along characters.
3. If any character missing → return False.
4. After last character:
   Check is_end flag.

Prefix path alone not enough.
Must check word end.

## Visual: Search — Following the Breadcrumbs

The full trie for our 5 words:

```
root
├── c
│   └── a
│       ├── t*
│       └── r*
│           ├── d*
│           └── e*
└── d
    └── o
        └── g*
```

**Case 1: Search for "card" (exists)**

```
Start at root.
'c' → root has 'c'? YES. Move to c-node.
'a' → c has 'a'?   YES. Move to a-node.
'r' → a has 'r'?   YES. Move to r-node.
'd' → r has 'd'?   YES. Move to d-node.
End of word. Is this node marked as end? YES.

Result: FOUND
```

**Case 2: Search for "cat" (exists)**

```
'c' → YES. 'a' → YES. 't' → YES.
End of word. Marked as end? YES.

Result: FOUND
```

**Case 3: Search for "cab" (does NOT exist)**

```
'c' → YES. 'a' → YES. 'b' → a-node has children 't' and 'r', but NOT 'b'.

Result: NOT FOUND
```

We knew "cab" wasn't there after just 3 steps. We didn't scan a single other word.

**Case 4: Search for "ca" (prefix exists, but "ca" is not a complete word)**

```
'c' → YES. 'a' → YES.
End of word. Marked as end? NO. (The a-node has children but isn't marked as a word.)

Result: NOT FOUND as a word  (but the prefix "ca" exists!)
```

This distinction is crucial: a node existing != a word ending there.
The `is_end` flag is what separates "ca" (prefix) from "cat" (complete word).

**Common mistake — node existence vs word existence:** Returning `node is not None` from `search()` checks whether a path exists, not whether a word was inserted. Always return `node.is_end` from `search()` — a node existing only means some word passes through that path, not that a complete word ends there.

📝 **Practice:** [Q4 · search-exact-word](./practice.md#q4--search-for-an-exact-word) · [Q6 · search-vs-startswith](./practice.md#q6--search-vs-startswith--the-is_end-distinction)

> [↑ Back to Top](#top)

<a id="8-searching-prefix"></a>
# 8. Searching Prefix

Example:

Does any word start with "ca"?

Just traverse prefix.
No need to check is_end.

If path exists → prefix exists.

Very efficient.

📝 **Practice:** [Q44 · trie-prefix-matching](../dsa_practice_questions_100.md#q44--thinking--trie-prefix-matching)

## Visual: Prefix Search — startsWith in 3 Steps

Your phone's search bar doesn't just check full words. It checks prefixes.
When you type "ca", it doesn't need to know if "ca" is a word — it needs to know
if any word *starts with* "ca".

```python
def starts_with(root, prefix):
    node = root
    for char in prefix:
        if char not in node.children:
            return False   # prefix doesn't exist at all
        node = node.children[char]
    return True            # we reached the end of the prefix — it exists!
```

```
startsWith("ca"):
'c' → found. 'a' → found. Ran out of prefix chars.
Return True

startsWith("do"):
'd' → found. 'o' → found. Return True

startsWith("dx"):
'd' → found. 'x' → d-node has only 'o', not 'x'. Return False
```

The trie never looked at "cat", "car", "card", "care", or "dog" as words.
It just walked two nodes.

**Common mistake — search vs startsWith return condition:** Writing `return True` at the end of `search()` makes it behave identically to `starts_with()`. The two methods have different return conditions: `search` must return `node.is_end` (strict — word must end here), `starts_with` returns `True` for any existing path (permissive).

📝 **Practice:** [Q5 · startswith-prefix-check](./practice.md#q5--startswith--prefix-check) · [Q8 · trie-vs-hashmap-prefix](./practice.md#q8--why-trie-wins-over-hashmap-on-prefix-queries)

> [↑ Back to Top](#top)

<a id="9-why-not-use-hashmap"></a>
# 9. Why Not Use Hashmap?

If you use hashmap:

Store all words.

Searching:
O(L) average.

But prefix search?
You must scan all words.

Trie solves prefix problem elegantly.

> [↑ Back to Top](#top)

<a id="10-memory-usage"></a>
# 10. Memory Usage

Trie uses more memory than hashmap.

Because:
Each node stores children map.

But memory trade-off gives fast prefix queries.

Used when prefix search frequent.

📝 **Practice:** [Q14 · memory-dict-vs-array](./practice.md#q14--memory-usage--dict-vs-array-node) · [Q23 · trie-memory-analysis](./practice.md#q23--trie-memory-analysis--when-trie-uses-more-than-hashmap)

> [↑ Back to Top](#top)

<a id="11-common-trie-problems"></a>
# 11. Common Trie Problems

- Implement Trie
- Word Search
- Word Break
- Replace Words
- Longest Common Prefix
- Autocomplete System
- Count distinct substrings
- Search suggestion system

Very common in interviews.

## Visual: Autocomplete — The Party Trick

This is where tries earn their keep. You've typed "ca". The system needs to return
every word that starts with "ca".

**Phase 1: Navigate to the "ca" node.**

```
root → c → a

We're now standing at the 'a' node. Everything in this subtree starts with "ca".
```

**Phase 2: Collect every word in this subtree (DFS).**

```
Starting at 'a' node, we explore every path to an end-marker:

'a' node
 ├── explore 't' branch:
 │     't' is marked end → collect "ca" + "t" = "cat"
 │
 └── explore 'r' branch:
       'r' is marked end → collect "ca" + "r" = "car"
       ├── explore 'd' branch:
       │     'd' is marked end → collect "ca" + "r" + "d" = "card"
       │
       └── explore 'e' branch:
             'e' is marked end → collect "ca" + "r" + "e" = "care"

Result: ["cat", "car", "card", "care"]
```

The entire "do" subtree was never touched. We went straight to the right section
of the library and collected everything in it.

Autocomplete time: O(P + W) where P = prefix length, W = number of results.
You only pay for the work that matters.

**Common mistake — autocomplete forgetting is_end at the starting node:** When collecting all words with a given prefix, the DFS starts at the prefix's last node. If the prefix itself is a complete word, it must be included in the results. Always check `node.is_end` at every visited node — including the starting node — before recursing into children.

📝 **Practice:** [Q9 · count-words-with-prefix](./practice.md#q9--count-words-with-a-given-prefix) · [Q11 · autocomplete-system](./practice.md#q11--autocomplete-system) · [Q12 · longest-common-prefix](./practice.md#q12--longest-common-prefix) · [Q13 · replace-words-with-root](./practice.md#q13--replace-words-with-root) · [Q10 · delete-word](./practice.md#q10--delete-a-word-with-branch-pruning) · [Q21 · word-search-grid](./practice.md#q21--word-search-in-grid-trie--dfs)

> [↑ Back to Top](#top)

<a id="12-optimization-array"></a>
# 12. Optimization — Using Array Instead of Dictionary

If only lowercase letters:

Use array of size 26 instead of dictionary.

Reduces overhead.

Faster lookup.

## Visual: Two Ways to Build a Trie Node

Every trie node needs to store its children. Two common approaches:

**Approach 1: Dictionary (HashMap) — flexible, memory-efficient for sparse alphabets**

```python
class TrieNode:
    def __init__(self):
        self.children = {}          # only stores letters that actually exist
        self.is_end = False

# Node for 'a' in our trie (has children 't' and 'r'):
# children = {'t': <TrieNode>, 'r': <TrieNode>}
# is_end = False
```

Memory usage: O(actual children). Great for large alphabets (Unicode, URLs, etc.)
Lookup: O(1) average (hash map).

**Approach 2: Fixed Array — fast, predictable, great for lowercase English**

```python
class TrieNode:
    def __init__(self):
        self.children = [None] * 26  # always 26 slots, a=0, b=1, ..., z=25
        self.is_end = False

# To find child 'r': children[ord('r') - ord('a')] = children[17]
# To find child 't': children[ord('t') - ord('a')] = children[19]
```

Memory usage: O(26) per node regardless of how many children it has.
Lookup: O(1) guaranteed (direct array indexing, cache-friendly).

**Side-by-side for the 'a' node in our trie:**

```
Dictionary approach:             Array approach:
┌─────────────────────┐         ┌───────────────────────────────┐
│ children: {         │         │ children: [                   │
│   't': <node>,      │         │   None, None, None, None,     │
│   'r': <node>       │         │   None, None, None, None,     │
│ }                   │         │   None, None, None, None,     │
│ is_end: False       │         │   None, None, None, None,     │
└─────────────────────┘         │   None, <r-node>, <t-node>... │
                                │ ]  ↑ index 17       ↑ index 19│
                                │ is_end: False                  │
Uses 2 slots.                   └───────────────────────────────┘
                                Uses 26 slots, 24 are None.
```

For standard LeetCode problems with lowercase English: use the array.
For real-world applications with large or variable alphabets: use the dictionary.

**Common mistake — array trie index calculation error:** Using `idx = ord(ch)` gives indices 97–122, which are out of bounds for a size-26 array. Always subtract the base character: `idx = ord(ch) - ord('a')` maps 'a'→0, 'b'→1, ..., 'z'→25. Add an assertion `0 <= idx < 26` during development to catch this early.

📝 **Practice:** [Q2 · array-node-structure](./practice.md#q2--trie-node-structure--array-approach)

> [↑ Back to Top](#top)

<a id="13-real-world-applications"></a>
# 13. Real-World Applications

- Search engine autocomplete
- Spell check
- IP routing
- Contact search
- Predictive typing
- DNA sequence matching

Search engines heavily use Trie-like structures.

📝 **Practice:** [Q45 · trie-vs-hashmap](../dsa_practice_questions_100.md#q45--interview--trie-vs-hashmap) · [Q90 · design-autocomplete](../dsa_practice_questions_100.md#q90--design--design-autocomplete)

> [↑ Back to Top](#top)

<a id="14-common-mistakes"></a>
# 14. Common Mistakes

- Forgetting end-of-word marker
- Confusing prefix with full word
- Not handling empty string
- Memory blowup with many nodes
- Not cleaning up on deletion

Trie requires careful memory design.

**Common mistake — delete not pruning empty branches:** A naive delete that only clears `is_end` is logically correct but leaves dead nodes permanently allocated. A proper recursive delete must propagate `should_delete` upward: a node is safe to remove when `not node.is_end and len(node.children) == 0`. This is especially critical in production tries with frequent inserts and deletes, such as autocomplete systems that rotate vocabulary.

**Common mistake — not handling empty string:** The empty string `""` is a valid input. After inserting `""`, `search("")` should return `True` because `root.is_end` will be `True`. Always verify your insert/search loops handle zero-length words without special-casing.

📝 **Practice:** [Q25 · common-mistake-gauntlet](./practice.md#q25--common-mistake-gauntlet) · [Q7 · handling-empty-string](./practice.md#q7--handling-the-empty-string)

> [↑ Back to Top](#top)

<a id="15-mental-model"></a>
# 15. Mental Model

Think of Trie as:

A word tree.

Each level = next character.

All words sharing prefix share same path.

Trie is prefix-sharing machine.

> [↑ Back to Top](#top)

<a id="16-final-understanding"></a>
# 16. Final Understanding

Trie is:

- Tree for characters
- Efficient for prefix search
- O(L) search time
- Memory-heavy
- Powerful for dictionary-like problems

Mastering Trie prepares you for:

- Advanced string algorithms
- Autocomplete systems
- Search engine internals
- Pattern matching

Trie is less common than arrays,
but very powerful in string-heavy problems.

> [↑ Back to Top](#top)

**[🏠 Back to README](../README.md)**

**Prev:** [← Heaps — Interview Q&A](../16_heaps/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
