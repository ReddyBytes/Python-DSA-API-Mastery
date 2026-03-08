# Hashing — Common Mistakes & Error Prevention

---

## Mistake 1: Mutating a Key — Using a List as a Dict Key (Unhashable Type)

### The Bug

Python's dict (and set) requires keys to be **hashable**. Lists are mutable, so they cannot be hashed. Passing a list as a key raises a `TypeError` immediately.

### WRONG Code

```python
def wrong_list_key():
    d = {}
    d[[1, 2, 3]] = "value"   # TypeError: unhashable type: 'list'
    return d
```

### CORRECT Code

```python
def correct_tuple_key():
    d = {}
    d[tuple([1, 2, 3])] = "value"   # tuple is immutable, therefore hashable
    return d


# Also works with frozenset when order doesn't matter
def correct_frozenset_key():
    d = {}
    d[frozenset([1, 2, 3])] = "value"
    return d
```

### Test Cases That Expose the Bug

```python
import pytest


def test_list_key_raises():
    d = {}
    with pytest.raises(TypeError, match="unhashable type"):
        d[[1, 2, 3]] = "value"


def test_tuple_key_works():
    d = {}
    key = tuple([1, 2, 3])
    d[key] = "value"
    assert d[(1, 2, 3)] == "value"


def test_frozenset_key_works():
    d = {}
    d[frozenset([1, 2, 3])] = "value"
    assert d[frozenset([3, 1, 2])] == "value"   # frozenset ignores order


def test_grouping_anagrams_wrong():
    """Demonstrates a common real-world case where this error surfaces."""
    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    groups = {}
    with pytest.raises(TypeError, match="unhashable type"):
        for word in words:
            key = sorted(word)      # sorted() returns a list — WRONG
            if key not in groups:
                groups[key] = []
            groups[key].append(word)


def test_grouping_anagrams_correct():
    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    groups = {}
    for word in words:
        key = "".join(sorted(word))   # join makes it a string — CORRECT
        if key not in groups:
            groups[key] = []
        groups[key].append(word)

    assert sorted(groups["aet"]) == sorted(["eat", "tea", "ate"])
    assert sorted(groups["ant"]) == sorted(["tan", "nat"])
    assert groups["abt"] == ["bat"]


if __name__ == "__main__":
    # Manual run
    try:
        wrong_list_key()
    except TypeError as e:
        print(f"WRONG (expected error): {e}")

    result = correct_tuple_key()
    print(f"CORRECT tuple key: {result}")

    result = correct_frozenset_key()
    print(f"CORRECT frozenset key: {result}")
```

### Key Takeaway

| Approach | Hashable | Use When |
|---|---|---|
| `tuple(lst)` | Yes | Order matters (e.g., anagram grouping) |
| `frozenset(lst)` | Yes | Order does NOT matter (e.g., set grouping) |
| `"".join(sorted(lst))` | Yes | String-based canonical form |

---

## Mistake 2: Missing Default in dict vs defaultdict — KeyError on First Increment

### The Bug

When you try to increment a value for a key that does not yet exist in a plain `dict`, Python raises `KeyError`. Beginners often write `counts[key] += 1` without initialising the key first.

### WRONG Code

```python
def count_chars_wrong(s: str) -> dict:
    counts = {}
    for ch in s:
        counts[ch] += 1     # KeyError on first occurrence of any character
    return counts
```

### CORRECT Code — Option A: dict.get() with default

```python
def count_chars_get(s: str) -> dict:
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1   # get returns 0 if key absent
    return counts
```

### CORRECT Code — Option B: defaultdict(int)

```python
from collections import defaultdict


def count_chars_defaultdict(s: str) -> dict:
    counts = defaultdict(int)   # missing keys automatically initialised to 0
    for ch in s:
        counts[ch] += 1
    return dict(counts)
```

### CORRECT Code — Option C: Counter (most Pythonic)

```python
from collections import Counter


def count_chars_counter(s: str) -> dict:
    return dict(Counter(s))
```

### Test Cases That Expose the Bug

```python
import pytest
from collections import defaultdict, Counter


def test_plain_dict_raises_key_error():
    counts = {}
    with pytest.raises(KeyError):
        for ch in "hello":
            counts[ch] += 1     # crashes on first 'h'


def test_get_with_default_correct():
    counts = {}
    for ch in "hello":
        counts[ch] = counts.get(ch, 0) + 1
    assert counts == {"h": 1, "e": 1, "l": 2, "o": 1}


def test_defaultdict_correct():
    counts = defaultdict(int)
    for ch in "hello":
        counts[ch] += 1
    assert dict(counts) == {"h": 1, "e": 1, "l": 2, "o": 1}


def test_counter_correct():
    counts = Counter("hello")
    assert counts == {"h": 1, "e": 1, "l": 2, "o": 1}


def test_accessing_missing_key_defaultdict_does_not_raise():
    d = defaultdict(list)
    d["new_key"].append(1)    # no KeyError — automatically creates []
    assert d["new_key"] == [1]


def test_accessing_missing_key_plain_dict_raises():
    d = {}
    with pytest.raises(KeyError):
        _ = d["missing"]


def test_get_returns_none_by_default():
    d = {"a": 1}
    assert d.get("b") is None        # no error, returns None
    assert d.get("b", 0) == 0        # with explicit default


if __name__ == "__main__":
    try:
        counts = {}
        for ch in "hello":
            counts[ch] += 1
    except KeyError as e:
        print(f"WRONG (expected KeyError): {e}")

    counts = {}
    for ch in "hello":
        counts[ch] = counts.get(ch, 0) + 1
    print(f"CORRECT (get): {counts}")
```

### Key Takeaway

| Pattern | Syntax | Best For |
|---|---|---|
| `dict.get(key, default)` | `d.get(k, 0)` | One-off lookups |
| `defaultdict(int)` | `d[k] += 1` | Frequency counting loops |
| `Counter(iterable)` | `Counter(seq)` | Counting entire sequences |

---

## Mistake 3: Two Sum — Using the Same Element Twice

### The Bug

The classic Two Sum problem asks for two *different* indices whose values sum to `target`. A naive lookup in a `set` of all values will re-use the same element when `target == 2 * nums[i]`. For example, with `nums = [3, 5]` and `target = 6`, the number 3 appears once but the wrong implementation reports it as a valid pair.

### WRONG Code

```python
def two_sum_wrong(nums: list[int], target: int) -> list[int]:
    seen = set(nums)            # stores VALUES, not indices
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:  # may find num itself when target == 2*num
            return [i, nums.index(complement)]
    return []
```

**Why this is doubly wrong:**

1. It may pair an element with itself (e.g., `nums = [3]`, `target = 6`).
2. `nums.index(complement)` always returns the *first* occurrence, not necessarily the second one, producing wrong indices.

### CORRECT Code

```python
def two_sum_correct(nums: list[int], target: int) -> list[int]:
    seen = {}                           # maps value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:          # complement was seen at a DIFFERENT index
            return [seen[complement], i]
        seen[num] = i                   # store AFTER checking to avoid self-pairing
    return []
```

**The critical ordering: store the current element AFTER the lookup.** This guarantees we never pair an index with itself, because the current index is not yet in `seen` when we check.

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_uses_same_element_twice():
    """[3] with target=6 should return [] but wrong version finds (3,3)."""
    nums = [3]
    target = 6
    # The wrong version would attempt to use index 0 twice
    result = two_sum_wrong(nums, target)
    # Even if it returns something, verify it's invalid
    if result:
        i, j = result
        assert i != j, "WRONG: same element used twice"


def test_wrong_incorrect_index_on_duplicate():
    """[3, 2, 4] target=6 — complement of 2 is 4 (index 2), not 0."""
    nums = [3, 2, 4]
    target = 6
    result = two_sum_wrong(nums, target)
    # wrong version may return [0, 0] because nums.index(3) = 0 = i
    # The correct answer is [1, 2]
    assert result != [0, 0], "WRONG: self-pairing detected"


def test_correct_basic():
    assert two_sum_correct([2, 7, 11, 15], 9) == [0, 1]


def test_correct_no_self_pairing():
    """Target is exactly double the only element — should return []."""
    assert two_sum_correct([3], 6) == []


def test_correct_duplicate_values():
    """[3, 3] with target=6 — two different indices both holding value 3."""
    result = two_sum_correct([3, 3], 6)
    assert result == [0, 1]


def test_correct_complement_is_later():
    assert two_sum_correct([3, 2, 4], 6) == [1, 2]


def test_correct_negative_numbers():
    assert two_sum_correct([-1, -2, -3, -4, -5], -8) == [2, 4]


def test_correct_zero_target():
    assert two_sum_correct([0, 4, 3, 0], 0) == [0, 3]


if __name__ == "__main__":
    # Demonstrate the self-pairing bug
    print("=== WRONG version ===")
    print(two_sum_wrong([3], 6))          # may incorrectly return [0, 0]
    print(two_sum_wrong([3, 2, 4], 6))    # may return wrong indices

    print("\n=== CORRECT version ===")
    print(two_sum_correct([3], 6))        # []
    print(two_sum_correct([3, 3], 6))     # [0, 1]
    print(two_sum_correct([3, 2, 4], 6))  # [1, 2]
```

### Key Takeaway

- Always store **value → index** (not just presence in a set).
- Store the element **after** the lookup so the current index can never pair with itself.
- `nums.index(x)` always finds the first occurrence — it is the wrong tool for this problem when duplicates exist.

---

## Mistake 4: Anagram Grouping — Using list as Dict Key

### The Bug

`sorted(word)` returns a `list`. Lists are not hashable. Using one as a dict key raises `TypeError: unhashable type: 'list'` immediately.

### WRONG Code

```python
def group_anagrams_wrong(words: list[str]) -> list[list[str]]:
    groups = {}
    for word in words:
        key = sorted(word)          # sorted() returns a LIST — not hashable!
        if key not in groups:       # TypeError raised here
            groups[key] = []
        groups[key].append(word)
    return list(groups.values())
```

### CORRECT Code — Option A: join sorted characters into a string

```python
def group_anagrams_joined(words: list[str]) -> list[list[str]]:
    groups = {}
    for word in words:
        key = "".join(sorted(word))   # string is hashable
        if key not in groups:
            groups[key] = []
        groups[key].append(word)
    return list(groups.values())
```

### CORRECT Code — Option B: tuple of sorted characters

```python
def group_anagrams_tuple(words: list[str]) -> list[list[str]]:
    groups = {}
    for word in words:
        key = tuple(sorted(word))     # tuple is hashable
        if key not in groups:
            groups[key] = []
        groups[key].append(word)
    return list(groups.values())
```

### CORRECT Code — Option C: character frequency tuple (O(1) for fixed alphabet)

```python
from collections import defaultdict


def group_anagrams_freq(words: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    for word in words:
        freq = [0] * 26
        for ch in word:
            freq[ord(ch) - ord('a')] += 1
        key = tuple(freq)             # 26-element tuple is hashable, O(1) compare
        groups[key].append(word)
    return list(groups.values())
```

### Test Cases That Expose the Bug

```python
import pytest
from collections import defaultdict


def test_wrong_list_key_raises():
    words = ["eat", "tea", "tan"]
    with pytest.raises(TypeError, match="unhashable type"):
        group_anagrams_wrong(words)


def test_joined_basic():
    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    result = group_anagrams_joined(words)
    result_sets = [frozenset(g) for g in result]
    assert frozenset(["eat", "tea", "ate"]) in result_sets
    assert frozenset(["tan", "nat"]) in result_sets
    assert frozenset(["bat"]) in result_sets


def test_tuple_basic():
    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    result = group_anagrams_tuple(words)
    result_sets = [frozenset(g) for g in result]
    assert frozenset(["eat", "tea", "ate"]) in result_sets


def test_freq_basic():
    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    result = group_anagrams_freq(words)
    result_sets = [frozenset(g) for g in result]
    assert frozenset(["eat", "tea", "ate"]) in result_sets


def test_empty_string():
    words = ["", ""]
    result = group_anagrams_joined(words)
    assert len(result) == 1 and len(result[0]) == 2


def test_single_char_words():
    words = ["a", "b", "a"]
    result = group_anagrams_joined(words)
    result_sets = [frozenset(g) for g in result]
    assert frozenset(["a", "a"]) in result_sets
    assert frozenset(["b"]) in result_sets


if __name__ == "__main__":
    try:
        group_anagrams_wrong(["eat", "tea"])
    except TypeError as e:
        print(f"WRONG (expected error): {e}")

    print("CORRECT joined:", group_anagrams_joined(["eat", "tea", "tan", "ate"]))
    print("CORRECT tuple: ", group_anagrams_tuple(["eat", "tea", "tan", "ate"]))
    print("CORRECT freq:  ", group_anagrams_freq(["eat", "tea", "tan", "ate"]))
```

### Key Takeaway

| Key Type | Hashable | Notes |
|---|---|---|
| `sorted(word)` returns `list` | No | Always raises TypeError |
| `"".join(sorted(word))` | Yes | Clean, readable |
| `tuple(sorted(word))` | Yes | Slightly faster for very long words |
| `tuple(freq_array)` | Yes | O(k) construction, O(1) lookup for fixed alphabet |

---

## Mistake 5: Counter Subtraction Drops Negative and Zero Counts

### The Bug

`Counter(a) - Counter(b)` silently drops all results that are zero or negative. This is not a crash — it is silent data loss, making it one of the most dangerous Counter mistakes. If you expect to see negative values (e.g., "b has 3 more X than a"), the `-` operator will give you an empty Counter instead.

### WRONG Code

```python
from collections import Counter


def compare_counts_wrong(a: str, b: str) -> Counter:
    ca = Counter(a)
    cb = Counter(b)
    diff = ca - cb          # drops zero and negative values silently
    return diff             # missing information!
```

```python
# Also wrong: assuming subtraction preserves all entries
def check_can_build_wrong(s: str, t: str) -> bool:
    """Check if t can be built from characters of s (each used at most once)."""
    diff = Counter(s) - Counter(t)
    # Wrong: if diff is empty AND Counter(t) had entries, that means s lacked chars
    # But if diff is empty and Counter(t) was also empty, s had exactly enough
    # The logic is ambiguous without checking the original counts
    return len(diff) == 0   # WRONG — empty diff can mean "exact match" OR "s had fewer"
```

### CORRECT Code — Use subtract() for full arithmetic

```python
from collections import Counter


def compare_counts_correct(a: str, b: str) -> Counter:
    ca = Counter(a)
    ca.subtract(Counter(b))   # subtract() PRESERVES zero and negative counts
    return ca                 # now shows full picture including deficits


def check_can_build_correct(s: str, t: str) -> bool:
    """Check if t can be built from characters of s."""
    available = Counter(s)
    needed = Counter(t)
    for char, count in needed.items():
        if available[char] < count:   # explicit comparison, no subtraction needed
            return False
    return True


def missing_chars(s: str, t: str) -> dict:
    """Return characters in t that s does not have enough of."""
    result = Counter(t)
    result.subtract(Counter(s))
    return {k: v for k, v in result.items() if v > 0}   # only deficits
```

### Test Cases That Expose the Bug

```python
import pytest
from collections import Counter


def test_subtraction_drops_negatives():
    ca = Counter("aab")    # {'a': 2, 'b': 1}
    cb = Counter("aaab")   # {'a': 3, 'b': 1}
    diff = ca - cb
    # 'a' would be -1, 'b' would be 0 — BOTH dropped
    assert diff == Counter(), "Counter subtraction drops negatives and zeros"
    assert "a" not in diff
    assert "b" not in diff


def test_subtract_preserves_negatives():
    ca = Counter("aab")
    ca.subtract(Counter("aaab"))
    assert ca["a"] == -1    # negative preserved
    assert ca["b"] == 0     # zero preserved


def test_wrong_build_logic():
    """'ab' cannot build 'aab' but wrong function returns True."""
    wrong_result = (Counter("ab") - Counter("aab")) == Counter()
    # diff is Counter() because all entries are zero or negative
    # so wrong logic says "can build" when it cannot
    assert wrong_result is True, "Demonstrates the wrong function is buggy"


def test_correct_build_logic():
    assert check_can_build_correct("aab", "ab") is True
    assert check_can_build_correct("ab", "aab") is False     # s lacks one 'a'
    assert check_can_build_correct("abc", "abc") is True
    assert check_can_build_correct("aabbcc", "abc") is True
    assert check_can_build_correct("", "a") is False


def test_missing_chars():
    assert missing_chars("ab", "aab") == {"a": 1}
    assert missing_chars("abc", "aabbcc") == {"a": 1, "b": 1, "c": 1}
    assert missing_chars("aab", "aab") == {}


def test_counter_subtraction_positive_entries_kept():
    """Only positive remainders survive Counter subtraction."""
    ca = Counter("aaabbc")   # a:3, b:2, c:1
    cb = Counter("ab")       # a:1, b:1
    diff = ca - cb
    assert diff == Counter({"a": 2, "b": 1, "c": 1})   # positives kept


if __name__ == "__main__":
    print("=== Subtraction operator ===")
    ca = Counter("aab")
    cb = Counter("aaab")
    print(f"Counter('aab') - Counter('aaab') = {ca - cb}")   # Counter() — misleading!

    print("\n=== subtract() method ===")
    ca = Counter("aab")
    ca.subtract(Counter("aaab"))
    print(f"After subtract: {dict(ca)}")   # {'a': -1, 'b': 0} — full picture

    print("\n=== can_build checks ===")
    print(check_can_build_correct("ab", "aab"))   # False
    print(check_can_build_correct("aab", "ab"))   # True
```

### Key Takeaway

| Operation | Keeps zero/negative? | Use For |
|---|---|---|
| `Counter(a) - Counter(b)` | No — silently drops | When you only want positive remainders |
| `a.subtract(b)` | Yes | Full arithmetic, deficit analysis |
| Manual comparison loop | Yes | Most explicit and interview-safe |

**Interview rule:** Never use `Counter(a) - Counter(b)` to check whether one string can be built from another — use an explicit loop over `needed.items()`.

---

## Mistake 6: Modifying a Dict While Iterating Over It — RuntimeError

### The Bug

In Python 3, iterating over a dict and deleting keys during the same loop raises `RuntimeError: dictionary changed size during iteration`. This is a hard error that crashes the program.

### WRONG Code

```python
def remove_negatives_wrong(d: dict) -> dict:
    for k in d:
        if d[k] < 0:
            del d[k]        # RuntimeError: dictionary changed size during iteration
    return d


def evict_expired_wrong(cache: dict, expired_keys: set) -> dict:
    for k in cache:
        if k in expired_keys:
            del cache[k]    # same RuntimeError
    return cache
```

### CORRECT Code — Option A: collect keys first, then delete

```python
def remove_negatives_correct(d: dict) -> dict:
    to_delete = [k for k in d if d[k] < 0]   # snapshot of keys to remove
    for k in to_delete:
        del d[k]
    return d
```

### CORRECT Code — Option B: build a new dict (functional style)

```python
def remove_negatives_new_dict(d: dict) -> dict:
    return {k: v for k, v in d.items() if v >= 0}
```

### CORRECT Code — Option C: iterate over a snapshot using list(d.items())

```python
def remove_negatives_snapshot(d: dict) -> dict:
    for k, v in list(d.items()):    # list() materialises a snapshot
        if v < 0:
            del d[k]
    return d
```

### Test Cases That Expose the Bug

```python
import pytest


def test_modify_during_iteration_raises():
    d = {"a": 1, "b": -1, "c": 3}
    with pytest.raises(RuntimeError, match="dictionary changed size during iteration"):
        for k in d:
            if d[k] < 0:
                del d[k]


def test_collect_then_delete_correct():
    d = {"a": 1, "b": -1, "c": 3, "d": -5}
    result = remove_negatives_correct(d)
    assert result == {"a": 1, "c": 3}
    assert "b" not in result
    assert "d" not in result


def test_new_dict_style_correct():
    d = {"a": 1, "b": -1, "c": 3, "d": -5}
    result = remove_negatives_new_dict(d)
    assert result == {"a": 1, "c": 3}


def test_snapshot_iteration_correct():
    d = {"a": 1, "b": -1, "c": 3, "d": -5}
    result = remove_negatives_snapshot(d)
    assert result == {"a": 1, "c": 3}


def test_all_negatives():
    d = {"a": -1, "b": -2}
    assert remove_negatives_correct(d) == {}
    assert remove_negatives_new_dict({"a": -1, "b": -2}) == {}


def test_no_negatives():
    d = {"a": 1, "b": 2}
    assert remove_negatives_correct(d) == {"a": 1, "b": 2}


def test_empty_dict():
    d = {}
    assert remove_negatives_correct(d) == {}
    assert remove_negatives_new_dict(d) == {}


def test_cache_eviction_wrong():
    """Realistic cache eviction scenario."""
    cache = {"user:1": "Alice", "user:2": "Bob", "user:3": "Carol"}
    expired = {"user:1", "user:3"}
    with pytest.raises(RuntimeError, match="dictionary changed size during iteration"):
        evict_expired_wrong(cache, expired)


def test_cache_eviction_correct():
    cache = {"user:1": "Alice", "user:2": "Bob", "user:3": "Carol"}
    expired = {"user:1", "user:3"}
    for k in list(cache.keys()):
        if k in expired:
            del cache[k]
    assert cache == {"user:2": "Bob"}


if __name__ == "__main__":
    # Demonstrate the RuntimeError
    d = {"a": 1, "b": -1, "c": 3}
    try:
        for k in d:
            if d[k] < 0:
                del d[k]
    except RuntimeError as e:
        print(f"WRONG (expected error): {e}")

    # Correct approaches
    d = {"a": 1, "b": -1, "c": 3}
    print(f"CORRECT (collect first): {remove_negatives_correct(d)}")

    d = {"a": 1, "b": -1, "c": 3}
    print(f"CORRECT (new dict):      {remove_negatives_new_dict(d)}")

    d = {"a": 1, "b": -1, "c": 3}
    print(f"CORRECT (snapshot):      {remove_negatives_snapshot(d)}")
```

### Key Takeaway

| Approach | Mutates original? | Performance | Readability |
|---|---|---|---|
| Collect keys, then delete | Yes | O(n) | Clear intent |
| Dict comprehension | No (new dict) | O(n) | Most Pythonic |
| `list(d.items())` snapshot | Yes | O(n) (snapshot cost) | Concise |

**The rule:** Never add or remove keys from a dict while directly iterating its view. Either iterate over a copy (`list(d.keys())`) or build a new dict.

---

## Summary Table

| # | Mistake | Root Cause | Fix |
|---|---|---|---|
| 1 | List as dict key | Lists are mutable, not hashable | Use `tuple()` or `frozenset()` |
| 2 | `counts[k] += 1` on plain dict | Key not initialised before increment | `defaultdict(int)` or `.get(k, 0)` |
| 3 | Two Sum self-pairing | Set stores values, not indices | Store `value → index`, insert after lookup |
| 4 | `sorted(word)` as key | `sorted()` returns unhashable list | `"".join(sorted(word))` or `tuple(sorted(word))` |
| 5 | `Counter(a) - Counter(b)` drops info | Operator silently removes zero/negative | Use `.subtract()` for full arithmetic |
| 6 | Delete during iteration | Dict view becomes invalid mid-loop | Collect keys first or use `list(d.items())` |
