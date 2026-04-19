# 🗃️ Caching — Theory
> Speed up reads and reduce database load by storing frequently accessed data closer to the application.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
cache-aside (lazy loading) · write-through · write-behind · TTL and expiry · eviction policies (LRU/LFU)

**Should Learn** — Important for real projects, comes up regularly:
Redis data structures · cache stampede and thundering herd prevention · CDN caching

**Good to Know** — Useful in specific situations, not always tested:
multi-tier caching (L1 app / L2 Redis / L3 CDN) · cache key design patterns

**Reference** — Know it exists, look up syntax when needed:
bloom filters for negative caching · cache warm-up strategies · cache coherency

---

## 📋 Contents

```
1.  Why caching? — the read amplification problem
2.  Cache-aside — lazy loading pattern
3.  Write-through — synchronous cache population
4.  Write-behind — asynchronous write buffering
5.  Redis data structures — strings, hashes, sorted sets, lists, sets
6.  TTL and expiry — keeping caches fresh
7.  Eviction policies — LRU, LFU, and choosing wisely
8.  CDN caching — pushing content to the edge
9.  Cache stampede — thundering herd at the cache layer
```

---

## 📖 **Main content**: [the_art_of_caching.md](./the_art_of_caching.md)

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ⬅️ Previous | [05 — Databases](../05_databases/theory.md) |
| ➡️ Next | [07 — Storage & CDN](../07_storage_cdn/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Databases — Interview Q&A](../05_databases/interview.md) &nbsp;|&nbsp; **Next:** [The Art of Caching →](./the_art_of_caching.md)

**Related Topics:** [The Art of Caching](./the_art_of_caching.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
