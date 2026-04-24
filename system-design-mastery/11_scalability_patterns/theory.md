# 📈 Scalability Patterns — Theory
> Advanced patterns for systems that must scale to hundreds of millions of users with minimal write and read amplification.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
CQRS (Command Query Responsibility Segregation) trade-offs · event sourcing concepts · fan-out on write vs read

**Should Learn** — Important for real projects, comes up regularly:
data denormalization trade-offs · write amplification costs · database federation

**Good to Know** — Useful in specific situations, not always tested:
event versioning · read model construction · temporal queries

**Reference** — Know it exists, look up syntax when needed:
event store internals · cross-shard transactions · operational debugging of event-sourced systems

---

## 📋 Contents

```
1.  CQRS — separating the read and write models
2.  Event sourcing — storing events as the source of truth
3.  Fan-out — push vs pull models for delivering updates
4.  Write amplification — one write causing many physical writes
5.  Read amplification — one read requiring many physical reads
6.  Database federation — splitting databases by function
7.  Data denormalization — trading storage for query performance
```

---

## 📖 **Main content**: [patterns_playbook.md](./patterns_playbook.md)

---

---

## 📝 Practice Questions

> 📝 **Practice:** [Q30 · consistent-hashing](../system_design_practice_questions_100.md#q30--thinking--consistent-hashing)
> 📝 **Practice:** [Q53 · rate-limiting-at-scale](../system_design_practice_questions_100.md#q53--design--rate-limiting-at-scale)
> 📝 **Practice:** [Q68 · write-heavy-optimisations](../system_design_practice_questions_100.md#q68--thinking--write-heavy-optimisations)
> 📝 **Practice:** [Q70 · thundering-herd](../system_design_practice_questions_100.md#q70--thinking--thundering-herd)
> 📝 **Practice:** [Q71 · tail-latency-p99](../system_design_practice_questions_100.md#q71--interview--tail-latency-p99)
> 📝 **Practice:** [Q79 · explain-consistent-hashing](../system_design_practice_questions_100.md#q79--interview--explain-consistent-hashing)
> 📝 **Practice:** [Q80 · explain-rate-limiting-pm](../system_design_practice_questions_100.md#q80--interview--explain-rate-limiting-pm)
> 📝 **Practice:** [Q92 · design-rate-limiter-service](../system_design_practice_questions_100.md#q92--design--design-rate-limiter-service)

> 📝 **Practice:** [Q26 · read-heavy-write-heavy](../system_design_practice_questions_100.md#q26--design--read-heavy-write-heavy)

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ⬅️ Previous | [10 — Distributed Systems](../10_distributed_systems/theory.md) |
| ➡️ Next | [12 — Microservices](../12_microservices/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Distributed Systems — Interview Q&A](../10_distributed_systems/interview.md) &nbsp;|&nbsp; **Next:** [Patterns Playbook →](./patterns_playbook.md)

**Related Topics:** [Patterns Playbook](./patterns_playbook.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
