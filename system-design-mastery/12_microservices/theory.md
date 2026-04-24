# 🧩 Microservices — Theory

> 📝 **Practice:** [Q21 · what-is-microservice](../system_design_practice_questions_100.md#q21--normal--what-is-microservice) · [Q22 · monolith-vs-microservice](../system_design_practice_questions_100.md#q22--interview--monolith-vs-microservice) · [Q54 · service-discovery](../system_design_practice_questions_100.md#q54--normal--service-discovery) · [Q59 · service-mesh](../system_design_practice_questions_100.md#q59--thinking--service-mesh) · [Q83 · compare-monolith-microservice](../system_design_practice_questions_100.md#q83--interview--compare-monolith-microservice) · [Q97 · design-decision-monolith-startup](../system_design_practice_questions_100.md#q97--design--design-decision-monolith-startup)
> Break a monolith into independently deployable services — and manage the distributed systems complexity that follows.

> 📝 **Practice:** [Q55 · circuit-breaker-microservices](../system_design_practice_questions_100.md#q55--thinking--circuit-breaker-microservices)

---

## 📋 Contents

```
1.  Monolith vs microservices — when to split and when not to
2.  Synchronous communication — REST and gRPC between services
3.  Asynchronous communication — events and message queues
4.  Service discovery — how services find each other at runtime
5.  API gateway — single entry point, auth, routing, rate limiting
6.  Circuit breaker — preventing cascade failures
7.  Saga pattern — distributed transactions without two-phase commit
8.  Distributed tracing — following a request across service boundaries
```

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
monolith vs microservices trade-offs · Strangler Fig decomposition pattern · synchronous vs asynchronous communication selection

**Should Learn** — Important for real projects, comes up regularly:
circuit breaker pattern · saga pattern · service discovery · distributed tracing need

**Good to Know** — Useful in specific situations, not always tested:
API gateway role · Conway's Law implications

**Reference** — Know it exists, look up syntax when needed:
service mesh (Istio/Linkerd) · mTLS between services · cost per service (operational overhead)

---

## 📖 **Main content**: [monolith_to_micro.md](./monolith_to_micro.md)

---

---

## 📝 Practice Questions

> 📝 **Practice:** [Q57 · sidecar-pattern](../system_design_practice_questions_100.md#q57--normal--sidecar-pattern)
> 📝 **Practice:** [Q58 · bff-pattern](../system_design_practice_questions_100.md#q58--design--bff-pattern)
> 📝 **Practice:** [Q88 · production-cascade-failure](../system_design_practice_questions_100.md#q88--design--production-cascade-failure)

> 📝 **Practice:** [Q56 · bulkhead-pattern](../system_design_practice_questions_100.md#q56--normal--bulkhead-pattern)

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ⬅️ Previous | [11 — Scalability Patterns](../11_scalability_patterns/theory.md) |
| ➡️ Next | [13 — Security](../13_security/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Scalability Patterns — Interview Q&A](../11_scalability_patterns/interview.md) &nbsp;|&nbsp; **Next:** [Monolith to Microservices →](./monolith_to_micro.md)

**Related Topics:** [Monolith to Microservices](./monolith_to_micro.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
