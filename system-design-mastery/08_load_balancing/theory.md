# ⚖️ Load Balancing — Theory

> 📝 **Practice:** [Q6 · load-balancer-purpose](../system_design_practice_questions_100.md#q6--normal--load-balancer-purpose)
> Distribute traffic intelligently across servers to maximise availability, throughput, and fault tolerance.

> 📝 **Practice:** [Q7 · load-balancing-algorithms](../system_design_practice_questions_100.md#q7--normal--load-balancing-algorithms)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
L4 vs L7 load balancing · algorithms (round-robin/least-connections/IP hash) · health checks

**Should Learn** — Important for real projects, comes up regularly:
consistent hashing for minimizing reshuffling · sticky sessions anti-pattern · stateless alternatives

**Good to Know** — Useful in specific situations, not always tested:
GSLB (global server load balancing) · weighted routing

**Reference** — Know it exists, look up syntax when needed:
DSR (Direct Server Return) mode · active vs passive health checking · connection draining

---

## 📋 Contents

```
1.  Why load balancing? — single server limits
2.  Algorithms — round-robin, least-connections, IP hash, consistent hashing
3.  L4 vs L7 load balancing — transport vs application layer
4.  Health checks — detecting and removing unhealthy nodes
5.  Sticky sessions — when clients must hit the same server
6.  Global server load balancing (GSLB) — multi-region traffic routing
```

---

## 📖 **Main content**: [traffic_manager.md](./traffic_manager.md)

---

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ⬅️ Previous | [07 — Storage & CDN](../07_storage_cdn/theory.md) |
| ➡️ Next | [09 — Message Queues](../09_message_queues/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Storage Cdn — Interview Q&A](../07_storage_cdn/interview.md) &nbsp;|&nbsp; **Next:** [Traffic Manager →](./traffic_manager.md)

**Related Topics:** [Traffic Manager](./traffic_manager.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
