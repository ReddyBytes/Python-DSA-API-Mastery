# Tries — The Library That Organizes Itself by Sound

---

## The Filing System That Reads Your Mind

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

---

## Scene 1: Building the Library — Words as Paths

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

**This is the compression that makes tries fast.**

---

## Scene 2: Insert — One Letter at a Time

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

**Insert time:** O(L) where L is the length of the word. Nothing depends on how many
words are already in the trie.

---

## Scene 3: Search — Following the Breadcrumbs

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

Result: FOUND ✓
```

**Case 2: Search for "cat" (exists)**

```
'c' → YES. 'a' → YES. 't' → YES.
End of word. Marked as end? YES.

Result: FOUND ✓
```

**Case 3: Search for "cab" (does NOT exist)**

```
'c' → YES. 'a' → YES. 'b' → a-node has children 't' and 'r', but NOT 'b'.

Result: NOT FOUND ✗
```

We knew "cab" wasn't there after just 3 steps. We didn't scan a single other word.

**Case 4: Search for "ca" (prefix exists, but "ca" is not a complete word)**

```
'c' → YES. 'a' → YES.
End of word. Marked as end? NO. (The a-node has children but isn't marked as a word.)

Result: NOT FOUND as a word ✗  (but the prefix "ca" exists!)
```

This distinction is crucial: a node existing != a word ending there.
The `is_end` flag is what separates "ca" (prefix) from "cat" (complete word).

---

## Scene 4: Prefix Search — startsWith in 3 Steps

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
Return True ✓

startsWith("do"):
'd' → found. 'o' → found. Return True ✓

startsWith("dx"):
'd' → found. 'x' → d-node has only 'o', not 'x'. Return False ✗
```

The trie never looked at "cat", "car", "card", "care", or "dog" as words.
It just walked two nodes.

---

## Scene 5: Autocomplete — The Party Trick

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
 │     't' is marked end → collect "ca" + "t" = "cat" ✓
 │
 └── explore 'r' branch:
       'r' is marked end → collect "ca" + "r" = "car" ✓
       ├── explore 'd' branch:
       │     'd' is marked end → collect "ca" + "r" + "d" = "card" ✓
       │
       └── explore 'e' branch:
             'e' is marked end → collect "ca" + "r" + "e" = "care" ✓

Result: ["cat", "car", "card", "care"]
```

The entire "do" subtree was never touched. We went straight to the right section
of the library and collected everything in it.

**Autocomplete time:** O(P + W) where P = prefix length, W = number of results.
You only pay for the work that matters.

---

## Scene 6: Two Ways to Build a Trie Node

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

---

## Quick Reference

```
┌───────────────────────────────────────────────────────────┐
│  TRIE CHEAT SHEET                                         │
├───────────────────────────────────────────────────────────┤
│  Structure:  Tree where each node = one character         │
│  Root:       Empty (represents the empty string)          │
│  End marker: is_end flag on nodes where words finish      │
│                                                           │
│  Operations:                                              │
│    insert(word)          → O(L)   L = word length         │
│    search(word)          → O(L)   exact match             │
│    starts_with(prefix)   → O(P)   P = prefix length       │
│    autocomplete(prefix)  → O(P+W) W = number of results   │
│                                                           │
│  Key insight:                                             │
│    Search time = length of query, NOT size of dictionary  │
│                                                           │
│  Classic use cases:                                       │
│    Autocomplete / search suggestions                      │
│    Spell checker                                          │
│    IP routing (longest prefix match)                      │
│    Word games (Boggle, Wordle solver)                     │
│    Replace HashMap<String, V> when prefix ops matter      │
└───────────────────────────────────────────────────────────┘
```

The key insight: a trie trades space for speed on prefix operations. Where a hash map
asks "does this exact key exist?", a trie asks "does anything *start with* this key?"

When your problem involves prefixes, autocomplete, or shared structure between strings —
reach for the trie. The library that organizes itself by sound.
