# 📨 Message Queues — Theory

> 📝 **Practice:** [Q48 · dead-letter-queues](../system_design_practice_questions_100.md#q48--normal--dead-letter-queues)

> 📝 **Practice:** [Q19 · message-queue-purpose](../system_design_practice_questions_100.md#q19--normal--message-queue-purpose)
> Decouple producers from consumers, absorb traffic spikes, and guarantee reliable async communication between services.

> 📝 **Practice:** [Q49 · backpressure-queues](../system_design_practice_questions_100.md#q49--thinking--backpressure-queues)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
why queues (decoupling/buffering) · Kafka vs RabbitMQ selection · pub-sub vs point-to-point · delivery semantics (at-least-once/exactly-once)

**Should Learn** — Important for real projects, comes up regularly:
consumer groups · dead letter queues · consumer lag monitoring · partition strategy

**Good to Know** — Useful in specific situations, not always tested:
topic compaction · message ordering guarantees · backpressure strategies

**Reference** — Know it exists, look up syntax when needed:
offset management · exactly-once complexity · message retention policies

---

## 📋 Contents

```
1.  Why message queues? — decoupling and buffering
2.  Pub-sub vs point-to-point — routing models
3.  Kafka architecture — brokers, topics, partitions, offsets
4.  RabbitMQ — exchanges, queues, bindings
5.  At-least-once vs exactly-once delivery semantics
6.  Dead letter queues — handling poison messages
7.  Ordering guarantees — per-partition vs global
8.  Consumer groups — parallel consumption and load balancing
```

---

## 📖 **Main content**: [why_queues_exist.md](./why_queues_exist.md)

---

---

## 📝 Practice Questions

> 📝 **Practice:** [Q82 · compare-kafka-rabbitmq](../system_design_practice_questions_100.md#q82--interview--compare-kafka-rabbitmq)
> 📝 **Practice:** [Q96 · debug-duplicate-messages](../system_design_practice_questions_100.md#q96--critical--debug-duplicate-messages)

> 📝 **Practice:** [Q20 · sync-vs-async-communication](../system_design_practice_questions_100.md#q20--thinking--sync-vs-async-communication)

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ⬅️ Previous | [08 — Load Balancing](../08_load_balancing/theory.md) |
| ➡️ Next | [10 — Distributed Systems](../10_distributed_systems/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Load Balancing — Interview Q&A](../08_load_balancing/interview.md) &nbsp;|&nbsp; **Next:** [Why Queues Exist →](./why_queues_exist.md)

**Related Topics:** [Why Queues Exist](./why_queues_exist.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
