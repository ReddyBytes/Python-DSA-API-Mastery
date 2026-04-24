# 🗄️ Databases — Theory

> 📝 **Practice:** [Q33 · cassandra-data-model](../system_design_practice_questions_100.md#q33--thinking--cassandra-data-model)

> 📝 **Practice:** [Q15 · database-replication](../system_design_practice_questions_100.md#q15--thinking--database-replication)

> 📝 **Practice:** [Q14 · database-sharding](../system_design_practice_questions_100.md#q14--normal--database-sharding)

> 📝 **Practice:** [Q12 · database-index](../system_design_practice_questions_100.md#q12--thinking--database-index)

> 📝 **Practice:** [Q86 · production-db-bottleneck](../system_design_practice_questions_100.md#q86--design--production-db-bottleneck)
> The storage layer of every system: how to choose, configure, and scale databases for correctness and performance.

> 📝 **Practice:** [Q74 · data-replication-lag](../system_design_practice_questions_100.md#q74--thinking--data-replication-lag)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
SQL vs NoSQL selection criteria · ACID properties · index trade-offs · sharding strategies

**Should Learn** — Important for real projects, comes up regularly:
replication modes (async vs sync) · connection pool sizing · query optimization basics

**Good to Know** — Useful in specific situations, not always tested:
transaction isolation levels · B-tree vs LSM-tree trade-offs · read replicas

**Reference** — Know it exists, look up syntax when needed:
write amplification · PITR backup · schema versioning and migrations

---

## 📋 Contents

```
1.  SQL vs NoSQL — choosing the right tool
2.  ACID properties — the foundation of correctness
3.  Indexes — accelerating reads
4.  Sharding — horizontal partitioning for scale
5.  Replication — redundancy and read scaling
6.  Connection pooling — managing DB connections efficiently
7.  Query optimization — making slow queries fast
```

---

## 📖 **Main content**: [the_story_of_data.md](./the_story_of_data.md)

---

---

## 📝 Practice Questions

> 📝 **Practice:** [Q24 · relational-vs-nosql](../system_design_practice_questions_100.md#q24--interview--relational-vs-nosql)
> 📝 **Practice:** [Q25 · sql-vs-nosql-when](../system_design_practice_questions_100.md#q25--design--sql-vs-nosql-when)
> 📝 **Practice:** [Q27 · master-slave-replication](../system_design_practice_questions_100.md#q27--thinking--master-slave-replication)
> 📝 **Practice:** [Q28 · multi-master-conflicts](../system_design_practice_questions_100.md#q28--critical--multi-master-conflicts)
> 📝 **Practice:** [Q29 · db-partitioning-strategies](../system_design_practice_questions_100.md#q29--normal--db-partitioning-strategies)
> 📝 **Practice:** [Q39 · connection-pooling](../system_design_practice_questions_100.md#q39--thinking--connection-pooling)
> 📝 **Practice:** [Q66 · replication-lag](../system_design_practice_questions_100.md#q66--critical--replication-lag)
> 📝 **Practice:** [Q69 · hot-partition](../system_design_practice_questions_100.md#q69--critical--hot-partition)
> 📝 **Practice:** [Q78 · explain-sharding-analogy](../system_design_practice_questions_100.md#q78--interview--explain-sharding-analogy)
> 📝 **Practice:** [Q81 · compare-sql-nosql](../system_design_practice_questions_100.md#q81--interview--compare-sql-nosql)
> 📝 **Practice:** [Q89 · production-hot-partition-cassandra](../system_design_practice_questions_100.md#q89--design--production-hot-partition-cassandra)
> 📝 **Practice:** [Q95 · debug-replica-lag](../system_design_practice_questions_100.md#q95--critical--debug-replica-lag)
> 📝 **Practice:** [Q98 · design-decision-sql-nosql-profiles](../system_design_practice_questions_100.md#q98--design--design-decision-sql-nosql-profiles)

> 📝 **Practice:** [Q13 · btree-vs-hash-index](../system_design_practice_questions_100.md#q13--normal--btree-vs-hash-index)

## 🔁 Navigation

| | |
|---|---|
| 🎯 Interview | [interview.md](./interview.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| ⬅️ Previous | [04 — Backend Architecture](../04_backend_architecture/intro.md) |
| ➡️ Next | [06 — Caching](../06_caching/theory.md) |
| 🏠 Home | [README.md](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Backend Architecture — Introduction](../04_backend_architecture/intro.md) &nbsp;|&nbsp; **Next:** [The Story of Data →](./the_story_of_data.md)

**Related Topics:** [The Story of Data](./the_story_of_data.md) · [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
