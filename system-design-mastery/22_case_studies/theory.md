# 22 — Case Studies
> Each case study is a complete system design walkthrough. Read the individual files in order — each one introduces patterns that appear in later ones.

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

## 🔁 Navigation

| | |
|---|---|
| ← Previous | [21 — Real-Time Systems](../21_real_time_systems/real_time_guide.md) |
| ➡️ Next | [23 — Interview Framework](../23_interview_framework/the_45_minute_playbook.md) |
| 🏠 Home | [README.md](../README.md) |
