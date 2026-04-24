# 22 — Case Studies
> Each case study is a complete system design walkthrough. Read the individual files in order — each one introduces patterns that appear in later ones.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
case study methodology (requirements→estimation→architecture→bottlenecks→trade-offs) · capacity estimation process

**Should Learn** — Important for real projects, comes up regularly:
pattern recognition across system types · URL shortener · Twitter feed design

**Good to Know** — Useful in specific situations, not always tested:
Netflix CDN pattern · Uber geo-indexing · WhatsApp message ordering

**Reference** — Know it exists, look up syntax when needed:
pattern map across case studies · cost estimation per design

---

## 📂 Available Case Studies

| System | Core Patterns | File |
|--------|--------------|------|
| URL Shortener | Hashing, redirects, analytics, read-heavy caching | [url_shortener.md](./url_shortener.md) |
| Twitter Feed | Fan-out on write vs read, Redis sorted sets, celebrity problem | [twitter.md](./twitter.md) |
| Netflix | CDN, adaptive bitrate streaming, recommendation pipeline | [netflix.md](./netflix.md) |
| Uber | Geo-indexing with Redis, real-time WebSockets, surge pricing | [uber.md](./uber.md) |
| WhatsApp | End-to-end encryption, message ordering, offline queues | [whatsapp.md](./whatsapp.md) |

---

## 🧠 How to Use These Case Studies

Each case study follows the same structure used in real interviews:

1. **Clarify requirements** — scope the problem before designing
2. **Estimate scale** — derive the key numbers (storage, throughput, bandwidth)
3. **Design the core flow** — the simplest thing that could work
4. **Identify bottlenecks** — what breaks first as scale increases
5. **Apply targeted solutions** — caching, sharding, async processing, CDN
6. **Discuss trade-offs** — every decision has a cost

---

## 🔁 Pattern Map

The same patterns appear across different systems. Recognizing them is the key to designing new systems quickly.

```
Pattern                    Appears In
─────────────────────────────────────────────────────────
Read-heavy caching         URL Shortener, Twitter, Netflix homepage
Fan-out write              Twitter (pre-compute timelines)
Fan-out read               Twitter (for celebrities), WhatsApp groups
CDN / edge delivery        URL Shortener (redirects), Netflix (video chunks)
Redis GEO                  Uber (driver proximity)
WebSocket push             Uber (live tracking), WhatsApp (message delivery)
Kafka event streaming      Uber (location updates), Netflix (view events)
Cassandra (write-heavy)    WhatsApp (message queue), Uber (trip events)
State machine              Uber (trip lifecycle), Payment systems
Idempotency keys           URL creation, payments, any POST that shouldn't double-fire
Cursor pagination          Twitter feed, WhatsApp message history
Background workers         Netflix (transcoding), URL analytics aggregation
```

---

---

## 📝 Practice Questions

> 📝 **Practice:** [Q90 · production-url-shortener](../system_design_practice_questions_100.md#q90--design--production-url-shortener)

## 🔁 Navigation

| | |
|---|---|
| ← Previous | [21 — Real-Time Systems](../21_real_time_systems/real_time_guide.md) |
| ➡️ Next | [23 — Interview Framework](../23_interview_framework/the_45_minute_playbook.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Real Time Systems — Interview Q&A](../21_real_time_systems/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Netflix Case Study](./netflix.md) · [Twitter Case Study](./twitter.md) · [Uber Case Study](./uber.md) · [URL Shortener Case Study](./url_shortener.md) · [WhatsApp Case Study](./whatsapp.md) · [Interview Q&A](./interview.md)
