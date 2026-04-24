# 💾 Storage & CDN — Theory

> Store, retrieve, and serve files at global scale — from raw bytes to video streams delivered milliseconds from every user.

> 📝 **Practice:** [Q8 · cdn-what-and-why](../system_design_practice_questions_100.md#q8--normal--cdn-what-and-why) · [Q35 · blob-storage-patterns](../system_design_practice_questions_100.md#q35--normal--blob-storage-patterns) · [Q36 · cdn-cache-invalidation](../system_design_practice_questions_100.md#q36--thinking--cdn-cache-invalidation) · [Q37 · push-vs-pull-cdn](../system_design_practice_questions_100.md#q37--normal--push-vs-pull-cdn) · [Q100 · design-global-cdn](../system_design_practice_questions_100.md#q100--design--design-global-cdn)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
block vs file vs object storage selection · CDN architecture and PoPs · cache headers (Cache-Control/ETag)

**Should Learn** — Important for real projects, comes up regularly:
S3 consistency model · media processing pipeline (transcoding/thumbnails) · presigned URLs

**Good to Know** — Useful in specific situations, not always tested:
storage class transitions (hot/warm/cold/archive) · multipart uploads

**Reference** — Know it exists, look up syntax when needed:
cross-region replication · data durability (11 9s) explanation · bandwidth optimization

---

## 📋 Contents

```
1.  Block vs file vs object storage — choosing the right abstraction
2.  Object storage (S3) — architecture, consistency, and use cases
3.  CDN architecture — PoPs, origin pull, and push models
4.  Edge caching — cache control headers, TTL, and invalidation
5.  Media processing pipeline — transcoding, thumbnails, adaptive bitrate
6.  BLOB handling — uploading, chunking, and resumable transfers
```

---

## 📖 **Main content**: [storage_guide.md](./storage_guide.md)

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ⬅️ Previous | [06 — Caching](../06_caching/theory.md) |
| ➡️ Next | [08 — Load Balancing](../08_load_balancing/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Caching — Interview Q&A](../06_caching/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Storage Guide](./storage_guide.md) · [Interview Q&A](./interview.md)
