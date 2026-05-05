# 🔤 Regular Expressions — Interview Questions

---

**Q: What is the difference between `re.match()`, `re.search()`, and `re.fullmatch()`?**

`re.match()` only succeeds if the pattern matches at the **start** of the string — it doesn't scan forward. `re.search()` scans through the entire string and returns the first match anywhere. `re.fullmatch()` requires the pattern to match the **entire** string, not just a part of it. In practice, `re.search()` is what you almost always want; `re.match()` is a common source of bugs because developers forget it anchors to the start. `re.fullmatch()` is useful for input validation — ZIP codes, phone numbers — where you need to confirm the whole string matches a format.

---

**Q: What is a greedy quantifier and when does it cause problems?**

Greedy quantifiers (`*`, `+`, `?`, `{n,m}`) consume **as much as possible** while still allowing the overall pattern to match. This causes problems with patterns like `<(.*)>` on `<a>click</a>`: instead of matching just `a`, the `.*` expands to grab `a>click</a`, giving you `a>click</a` as the group. The fix is the **non-greedy (lazy)** form `.*?`, which matches as little as possible: `<(.*?)>` correctly returns `a` and then `a`. Rule of thumb: use lazy quantifiers when you're matching delimited content where the delimiter can appear multiple times.

---

**Q: What are named groups and why use them over positional groups?**

Named groups `(?P<name>...)` let you reference captures by name instead of number: `m.group("date")` instead of `m.group(1)`. This makes patterns self-documenting and resilient to reordering — if you add a group in the middle of a pattern, all `\1`, `\2` references break but named references don't. Use `m.groupdict()` to get all named groups as a dict, which makes parsing structured text (log lines, CSV variants) much cleaner. Named groups also work in `re.sub()` replacements as `\g<name>`.

---

**Q: What is the difference between a capturing group `(...)` and a non-capturing group `(?:...)`?**

Both group subpatterns for applying quantifiers or alternation. The difference is that `(...)` creates a backreference (`\1`, `\2`) and appears in `m.groups()` and `re.findall()` results, while `(?:...)` does not. Use `(?:...)` when you need to group for structure (like `(?:https?|ftp)://`) but don't want that group polluting your extracted data. With `re.findall()`, if there are any capturing groups in the pattern, it returns only the group contents — not the full match. This often surprises people, so prefer `(?:...)` unless you actually need to extract that piece.

---

**Q: Explain lookahead and lookbehind with an example.**

Lookaheads and lookbehinds are **zero-width assertions** — they check what's around a match without consuming those characters. `(?=...)` is a positive lookahead: `\d+(?=px)` matches digits only when followed by "px", without including "px" in the match. `(?<=...)` is a positive lookbehind: `(?<=\$)\d+` matches digits that follow a dollar sign, without including "$" in the match. The negative forms `(?!...)` and `(?<!...)` assert the opposite. A common use case: extract all prices as numbers but only from dollar amounts, not euro amounts: `(?<=\$)\d+(?:\.\d{2})?` matches `9.99` from `$9.99` but not from `€9.99`.

---

**Q: What is catastrophic backtracking and how do you avoid it?**

Catastrophic backtracking happens when a regex engine has to explore an exponential number of partial match possibilities before determining there's no match. The classic example: `(a+)+b` on the string `"aaaaaaaaaaaaaaac"`. Because `a+` can match varying numbers of `a`s and the outer `+` repeats it, the engine explores O(2^n) combinations trying to find a `b` that never appears. This can hang a server. Fixes: (1) avoid nested quantifiers on the same character class, (2) use atomic groups or possessive quantifiers if your engine supports them, (3) restructure to use a possessive `a++` which never backtracks, (4) test patterns on pathological inputs before deploying, (5) set a timeout on the match operation.

---

**Q: When should you compile a regex with `re.compile()` vs calling `re.search()` directly?**

Both approaches work, but `re.compile()` caches the compiled pattern object and avoids re-parsing the pattern string on every call. Use `re.compile()` when: (1) calling the same pattern in a loop over many strings, (2) combining with multiple methods (`pattern.search()`, `pattern.sub()`, `pattern.findall()`) on the same pattern, or (3) you want to store the pattern as a module-level constant. For one-off calls (validate a single email once at startup), the difference is negligible because Python internally caches recently compiled patterns anyway. The real benefit of `re.compile()` is code organization — named constants for patterns make the code more readable and testable.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Prev Module | [../32_streamlit_flask/theory.md](../32_streamlit_flask/theory.md) |
| ➡️ Next Module | [../99_interview_master/README.md](../99_interview_master/README.md) |

---

**[🏠 Back to README](../README.md)**
