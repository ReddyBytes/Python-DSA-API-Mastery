# 📘 Trie — The Tree of Words

> If BST organizes numbers,
> Trie organizes letters.
>
> Trie is built for one powerful purpose:
>
> **Fast prefix searching.**

Trie is also called:
Prefix Tree.

It is one of the most important structures
for string-based problems.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
trie node structure · insert · search · prefix search

**Should Learn** — Important for real projects, comes up regularly:
autocomplete pattern · memory optimization with arrays · word search applications

**Good to Know** — Useful in specific situations, not always tested:
trie vs hashmap trade-offs · deletion from trie

**Reference** — Know it exists, look up syntax when needed:
compressed trie · radix tree · patricia tree · DAWG

---

# 📖 1️⃣ Real Life Story — Dictionary in Your Brain

Imagine you have a dictionary.

You open it and search for:

"cat"

You don’t scan every word.

You go to:

C → A → T

Then check if word exists.

Your brain organizes words by prefix.

That structure is Trie.

---

# 🌳 2️⃣ What Is a Trie?

A Trie is a tree where:

- Each node represents one character
- Words are formed from root to leaf
- Path represents prefix

Important:

Nodes store:
- Children (dictionary/map of characters)
- End-of-word marker

---

# 🧩 3️⃣ Visual Example

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

“cat” and “car” share prefix “ca”.

That is key advantage.

---

# 🔠 4️⃣ Why Trie Is Powerful

Searching word in Trie:

Time complexity:
O(L)

Where L = length of word.

Not dependent on number of words.

Very efficient for large dictionaries.

---

# 🛠 5️⃣ How Trie Node Is Defined

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

---

# ➕ 6️⃣ Inserting Word Into Trie

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

---

# 🔍 7️⃣ Searching Word in Trie

To search "cat":

1. Start at root.
2. Move along characters.
3. If any character missing → return False.
4. After last character:
   Check is_end flag.

Prefix path alone not enough.
Must check word end.

---

# 🔎 8️⃣ Searching Prefix

Example:

Does any word start with "ca"?

Just traverse prefix.
No need to check is_end.

If path exists → prefix exists.

Very efficient.

---

# 🧠 9️⃣ Why Not Use Hashmap?

If you use hashmap:

Store all words.

Searching:
O(L) average.

But prefix search?
You must scan all words.

Trie solves prefix problem elegantly.

---

# 📦 1️⃣0️⃣ Memory Usage

Trie uses more memory than hashmap.

Because:
Each node stores children map.

But memory trade-off gives fast prefix queries.

Used when prefix search frequent.

---

# 🔄 1️⃣1️⃣ Common Trie Problems

- Implement Trie
- Word Search
- Word Break
- Replace Words
- Longest Common Prefix
- Autocomplete System
- Count distinct substrings
- Search suggestion system

Very common in interviews.

---

# ⚡ 1️⃣2️⃣ Optimization — Using Array Instead of Dictionary

If only lowercase letters:

Use array of size 26 instead of dictionary.

Reduces overhead.

Faster lookup.

---

# 🌍 1️⃣3️⃣ Real-World Applications

- Search engine autocomplete
- Spell check
- IP routing
- Contact search
- Predictive typing
- DNA sequence matching

Search engines heavily use Trie-like structures.

---

# ⚠️ 1️⃣4️⃣ Common Mistakes

- Forgetting end-of-word marker
- Confusing prefix with full word
- Not handling empty string
- Memory blowup with many nodes
- Not cleaning up on deletion

Trie requires careful memory design.

---

# 🧠 1️⃣5️⃣ Mental Model

Think of Trie as:

A word tree.

Each level = next character.

All words sharing prefix share same path.

Trie is prefix-sharing machine.

---

# 📌 Final Understanding

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

---

# 🔁 Navigation

Previous:  
[16_heaps/interview.md](/dsa-complete-mastery/16_heaps/interview.md)

Next:  
[17_trie/interview.md](/dsa-complete-mastery/17_trie/interview.md)  
[18_graphs/theory.md](/dsa-complete-mastery/18_graphs/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Heaps — Interview Q&A](../16_heaps/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
