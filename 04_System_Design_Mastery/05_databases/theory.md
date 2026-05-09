<a id="top"></a>

# Databases — Theory

> Bhanu is a Telugu database architect who has built data layers for fintech startups and
> scaled systems serving 200 million users. He thinks of databases the way a city planner
> thinks of water infrastructure: invisible when it works, catastrophic when it fails.
> "Every system design conversation," Bhanu says, "starts and ends with the database."

> **Practice:** [Q33 - cassandra-data-model](../system_design_practice_questions_100.md#q33--thinking--cassandra-data-model)
> **Practice:** [Q15 - database-replication](../system_design_practice_questions_100.md#q15--thinking--database-replication)
> **Practice:** [Q14 - database-sharding](../system_design_practice_questions_100.md#q14--normal--database-sharding)
> **Practice:** [Q12 - database-index](../system_design_practice_questions_100.md#q12--thinking--database-index)
> **Practice:** [Q86 - production-db-bottleneck](../system_design_practice_questions_100.md#q86--design--production-db-bottleneck)
> **Practice:** [Q74 - data-replication-lag](../system_design_practice_questions_100.md#q74--thinking--data-replication-lag)
> **Practice:** [Q24 - relational-vs-nosql](../system_design_practice_questions_100.md#q24--interview--relational-vs-nosql)
> **Practice:** [Q25 - sql-vs-nosql-when](../system_design_practice_questions_100.md#q25--design--sql-vs-nosql-when)
> **Practice:** [Q27 - master-slave-replication](../system_design_practice_questions_100.md#q27--thinking--master-slave-replication)
> **Practice:** [Q28 - multi-master-conflicts](../system_design_practice_questions_100.md#q28--critical--multi-master-conflicts)
> **Practice:** [Q29 - db-partitioning-strategies](../system_design_practice_questions_100.md#q29--normal--db-partitioning-strategies)
> **Practice:** [Q39 - connection-pooling](../system_design_practice_questions_100.md#q39--thinking--connection-pooling)
> **Practice:** [Q66 - replication-lag](../system_design_practice_questions_100.md#q66--critical--replication-lag)
> **Practice:** [Q69 - hot-partition](../system_design_practice_questions_100.md#q69--critical--hot-partition)
> **Practice:** [Q78 - explain-sharding-analogy](../system_design_practice_questions_100.md#q78--interview--explain-sharding-analogy)
> **Practice:** [Q81 - compare-sql-nosql](../system_design_practice_questions_100.md#q81--interview--compare-sql-nosql)
> **Practice:** [Q89 - production-hot-partition-cassandra](../system_design_practice_questions_100.md#q89--design--production-hot-partition-cassandra)
> **Practice:** [Q95 - debug-replica-lag](../system_design_practice_questions_100.md#q95--critical--debug-replica-lag)
> **Practice:** [Q98 - design-decision-sql-nosql-profiles](../system_design_practice_questions_100.md#q98--design--design-decision-sql-nosql-profiles)
> **Practice:** [Q13 - btree-vs-hash-index](../system_design_practice_questions_100.md#q13--normal--btree-vs-hash-index)

## Table of Contents

- [1. Before Databases There Were Files](#1-before-databases-there-were-files)
- [2. SQL The Organized Library](#2-sql-the-organized-library)
  - [Tables Rows Columns](#tables-rows-columns)
  - [ACID The Banks Four Promises](#acid-the-banks-four-promises)
  - [Indexes The Library Card Catalog](#indexes-the-library-card-catalog)
  - [When SQL Is the Right Choice](#when-sql-is-the-right-choice)
- [3. NoSQL Different Tools for Different Jobs](#3-nosql-different-tools-for-different-jobs)
  - [Document Stores](#document-stores)
  - [Key-Value Stores](#key-value-stores)
  - [Column-Family Stores](#column-family-stores)
  - [Graph Databases](#graph-databases)
  - [When NoSQL Wins Over SQL](#when-nosql-wins-over-sql)
- [4. The N+1 Problem](#4-the-n1-problem)
- [5. Replication](#5-replication)
  - [Primary-Replica Replication](#primary-replica-replication)
  - [The Replication Lag Problem](#the-replication-lag-problem)
  - [Read Replicas for Scaling Reads](#read-replicas-for-scaling-reads)
- [6. Sharding](#6-sharding)
  - [The Phone Book Analogy](#the-phone-book-analogy)
  - [Hash Sharding vs Range Sharding](#hash-sharding-vs-range-sharding)
  - [The Cross-Shard Query Problem](#the-cross-shard-query-problem)
  - [When Is Sharding Actually Needed](#when-is-sharding-actually-needed)
- [7. SQL vs NoSQL Quick Reference](#7-sql-vs-nosql-quick-reference)
- [8. Mental Models to Carry Forward](#8-mental-models-to-carry-forward)
- [9. Learning Priority](#9-learning-priority)
- [Summary](#summary)

<a id="1-before-databases-there-were-files"></a>

# 1. Before Databases There Were Files

"Let me tell you how I explain databases to every junior engineer on my team," Bhanu says,
pulling up a whiteboard. "I start with the world before databases existed. Because once
you feel the pain of files, you never question why databases were invented."

Picture a small online bookstore in 1995. The developer is a resourceful person.
"I'll just store my data in files," they say. And so they do.

```
/data/users.txt
  alice,alice@email.com,New York
  bob,bob@email.com,London
  carol,carol@email.com,Tokyo

/data/orders.txt
  order_001,alice,The Great Gatsby,12.99,2024-01-15
  order_002,bob,Dune,14.99,2024-01-16
  order_003,alice,1984,10.99,2024-01-17
```

This works. For about a week.

Then the problems arrive, one by one.

**Problem 1: Two servers, two different files.**
The company gets popular and spins up a second server. Both servers have their
own copy of `users.txt`. Alice updates her email on Server 1. Server 2 still
has the old address. Which one is correct? Nobody knows.

**Problem 2: Two requests at the same time.**
Alice and Bob both place orders at the same millisecond. Both processes open
`orders.txt`, both read "last order was order_003", both write "order_004"...
and one of them overwrites the other. An order disappears. Money is lost.

**Problem 3: The crashed write.**
The server is halfway through writing Alice's order when the power goes out.
The file now contains half a record. Corrupted. Unusable.

**Problem 4: "Show me all orders over $20."**
The developer writes a script to scan every line of `orders.txt`.
At 1,000 orders it's fine. At 1,000,000 orders it takes 3 minutes.

These four problems — **concurrency, consistency, durability, and query
performance** — are exactly what databases were invented to solve.

A database is a file system that grew up.

[Back to Top](#top)

<a id="2-sql-the-organized-library"></a>

# 2. SQL The Organized Library

"SQL databases," Bhanu explains, "are like a perfectly organized library. Every piece
of data has a home, every relationship is explicit, and there are strict rules about
what goes where. This rigidity is their greatest strength."

<a id="tables-rows-columns"></a>

## Tables Rows Columns

Imagine you're designing a library. You decide that every book gets
exactly one card in the card catalog. Every card has the same fields:
Title, Author, ISBN, Year, Shelf Number. No card has extra fields.
No field can be missing. Everything is uniform.

That's a relational database table.

```
Table: books
+---------+--------------------+------------------+--------+------+
|   id    |       title        |      author      |  isbn  | year |
+---------+--------------------+------------------+--------+------+
|    1    |  The Great Gatsby  |  F. Scott Fitz.  | 978... | 1925 |
|    2    |  Dune              |  Frank Herbert   | 978... | 1965 |
|    3    |  1984              |  George Orwell   | 978... | 1949 |
+---------+--------------------+------------------+--------+------+
  ^            ^                      ^               ^       ^
  row          column                 column          column  column
```

The entire library is organized into shelves (tables), each shelf holds
cards (rows), each card has the same slots (columns).

Want to connect books to their orders? You link tables with foreign keys.
No duplication. One source of truth.

```
Table: orders                         Table: users
+---------+---------+------+-------+  +---------+-------+------------------+
|   id    | user_id | book | price |  |   id    | name  | email            |
+---------+---------+------+-------+  +---------+-------+------------------+
|    1    |    1    |  1   | 12.99 |  |    1    | Alice | alice@email.com  |
|    2    |    2    |  2   | 14.99 |  |    2    |  Bob  | bob@email.com    |
|    3    |    1    |  3   | 10.99 |  +---------+-------+------------------+
+---------+---------+------+-------+
         |                                |
         +--------------------------------+
                  foreign key link

```

This is the "relational" in relational database.

[Back to Top](#top)

<a id="acid-the-banks-four-promises"></a>

## ACID The Banks Four Promises

The moment real money is involved, files aren't enough. You need guarantees.

Imagine this scenario: Alice transfers $500 to Bob.

```
Step 1: Subtract $500 from Alice's account
Step 2: Add $500 to Bob's account
```

What happens if the server crashes between Step 1 and Step 2?
Alice's $500 is gone. Bob never got it. Money vanished.

Databases solve this with **ACID** — four properties that together make
operations safe.

**Atomicity — "All or Nothing"**

```
Transaction: Transfer $500
+------------------------------------------------------+
|                                                      |
|   BEGIN TRANSACTION                                  |
|     UPDATE accounts SET balance = balance - 500      |
|       WHERE user = 'Alice'                           |
|     UPDATE accounts SET balance = balance + 500      |
|       WHERE user = 'Bob'                             |
|   COMMIT  <- only if BOTH succeed                    |
|                                                      |
|   If anything fails: ROLLBACK (undo everything)      |
|                                                      |
+------------------------------------------------------+

Crash after step 1?   -> Rollback. Alice keeps her $500.
Both succeed?         -> Commit. Transfer complete.
Partial completion?   -> Impossible. Atomicity forbids it.
```

The transaction is like a light switch — it's either fully ON or fully OFF.
There is no "half on."

**Consistency — "Rules Are Always Enforced"**

The database has rules: "account balance cannot be negative."

Even if a buggy application tries to overdraw Alice's account to -$1,000,
the database will reject the transaction. The rules survive all requests.

**Isolation — "Transactions Don't See Each Other's Mess"**

Two transactions running at the same moment must not corrupt each other.

```
Without isolation:

  Transaction A: reads Alice's balance -> sees $1,000
  Transaction B: reads Alice's balance -> sees $1,000
  Transaction A: subtracts $600 -> writes $400
  Transaction B: subtracts $600 -> writes $400  <- Alice now has $400
                                                   but $1,200 was removed!

With isolation:

  Transaction A: reads $1,000, subtracts $600, commits -> $400
  Transaction B: waits for A to finish, reads $400,
                 tries to subtract $600... rejected (insufficient funds)
```

**Durability — "Once Committed, Always Committed"**

Once the database says "COMMIT: success," that data is safe on disk.
A crash one second later? The data survives. It's written to a
write-ahead log before the commit returns.

[Back to Top](#top)

<a id="indexes-the-library-card-catalog"></a>

## Indexes The Library Card Catalog

Back to the library. You want all books published before 1950.

**Without an index:**
```
Full table scan -- check every single row:

  [row 1: year=1925] <- check  (yes, include)
  [row 2: year=1965] <- check  (no, skip)
  [row 3: year=1949] <- check  (yes, include)
  [row 4: year=2001] <- check  (no, skip)
  ... x 1,000,000 rows

  Time: O(n) -- scans everything, every time
```

**With an index on the `year` column:**
```
B-Tree index structure (simplified):

                     [1960]
                    /      \
               [1940]      [1980]
              /      \    /      \
           [1925]  [1949][1965]  [2001]

Query: year < 1950
  -> Navigate tree: go left from 1960
  -> Found 1925, 1940, 1949
  -> Jump directly to those rows

  Time: O(log n) -- no scan needed
```

The index is the card catalog. Instead of walking every shelf,
you look up the card first, get the exact shelf location, and go
directly there. For a table with 10 million rows, this can be
the difference between 10 seconds and 1 millisecond.

**The tradeoff:** Indexes speed up reads but slow down writes.
Every INSERT or UPDATE must also update the index structure.
Add indexes to columns you query frequently. Don't index everything.

[Back to Top](#top)

<a id="when-sql-is-the-right-choice"></a>

## When SQL Is the Right Choice

```
Use SQL when:

  [x]  Your data has clear relationships (users -> orders -> products)
  [x]  You need ACID guarantees (payments, bookings, anything financial)
  [x]  Your schema is stable (fields don't change shape every week)
  [x]  You need ad-hoc queries ("show me all orders from London last month")
  [x]  Your data fits on one machine (or a few with replication)

Examples: PostgreSQL, MySQL, SQLite
```

[Back to Top](#top)

<a id="3-nosql-different-tools-for-different-jobs"></a>

# 3. NoSQL Different Tools for Different Jobs

"When I was at a social media startup," Bhanu recalls, "we had 50 million user
profiles, each with a different shape. Some had 3 fields, some had 80. We tried
forcing them into SQL tables and ended up with 200 nullable columns. That's when
I understood why NoSQL exists."

SQL is powerful, but it's not the right tool for everything.
In the late 2000s, companies like Google, Amazon, and Facebook were
storing data at a scale that relational databases struggled with.
They needed different shapes of storage. NoSQL was born.

"NoSQL" doesn't mean "no SQL ever." It means "not only SQL."
These are databases designed for specific access patterns.

<a id="document-stores"></a>

## Document Stores

Imagine instead of a strict card catalog, each "book" in your library
is a folder. Each folder can hold any documents, in any shape.
One folder has 3 pages. The next has 50. Each looks completely different.

```
MongoDB document -- each record is a JSON-like object:

{
  "_id": "user_001",
  "name": "Alice",
  "email": "alice@email.com",
  "address": {
    "city": "New York",
    "zip": "10001"
  },
  "orders": [
    { "item": "Dune", "price": 14.99, "date": "2024-01-16" },
    { "item": "1984", "price": 10.99, "date": "2024-01-17" }
  ],
  "preferences": {
    "genres": ["sci-fi", "dystopia"],
    "newsletter": true
  }
}
```

Notice: Alice's orders are embedded inside her document. No JOIN needed.
You retrieve Alice, you get everything about Alice in one read.

This is fast for "give me everything about this one user." It's less
good for "give me all users who ordered Dune last month" — that query
crosses documents and requires scanning.

**Use document stores when:** your data naturally clusters around one
entity, your schema varies across records, and you read by entity ID.

[Back to Top](#top)

<a id="key-value-stores"></a>

## Key-Value Stores

This is the simplest possible data store. You have a key. You want a value.

```
Redis / DynamoDB mental model:

  SET  user:session:abc123  ->  { "user_id": 1, "role": "admin" }
  GET  user:session:abc123  ->  { "user_id": 1, "role": "admin" }

  SET  product:1234:price   ->  "29.99"
  GET  product:1234:price   ->  "29.99"

  SET  rate_limit:ip:1.2.3.4  ->  "47"  (with expiry: 60 seconds)
  GET  rate_limit:ip:1.2.3.4  ->  "47"
```

It's a hashmap. The world's biggest, fastest hashmap.
Lookups are O(1) by key. There is no "give me all keys that start with X"
without scanning. The access pattern is: you know the key, you get the value.

**Use key-value stores when:** you're doing session storage, caching,
counters, rate limiting, feature flags, or any "look up by ID" pattern.

[Back to Top](#top)

<a id="column-family-stores"></a>

## Column-Family Stores

Cassandra is designed around one question: "how do you write 1 million
events per second and still read them back fast?"

The key insight: data is sorted by time on disk, stored in columns grouped
by query pattern. It's optimized for "give me all events for user X
between time A and time B" — the exact shape of time-series data.

```
Cassandra table for IoT sensor readings:

  Partition key: sensor_id  (decides which node holds this data)
  Clustering key: timestamp (orders rows within a partition)

  sensor_001  |  2024-01-01 00:00:01  |  temp=22.5  humidity=45
  sensor_001  |  2024-01-01 00:00:02  |  temp=22.6  humidity=45
  sensor_001  |  2024-01-01 00:00:03  |  temp=22.4  humidity=46
  ...
  sensor_002  |  2024-01-01 00:00:01  |  temp=19.1  humidity=60
```

Writes are sequential appends (very fast). Reads for a given sensor
in a time range scan a contiguous block on disk (also fast).

**Use column-family stores when:** you have massive write volumes,
time-series data, or logs. IoT, metrics, event streams.

[Back to Top](#top)

<a id="graph-databases"></a>

## Graph Databases

In a social network, "Alice follows Bob" is not just data about Alice
or data about Bob. The relationship itself carries meaning.

In SQL, storing 500 million friend connections means a JOIN table
with 500 million rows. Querying "friends of friends of Alice"
requires recursive JOINs that get expensive very fast.

Graph databases store relationships as first-class citizens.

```
Neo4j graph model:

  (Alice) --[FOLLOWS]--> (Bob)
     |                    |
  [FOLLOWS]            [FOLLOWS]
     |                    |
     v                    v
  (Carol)              (Dave)

  Query: "Who are Alice's friends-of-friends?"
  -> Start at Alice
  -> Follow FOLLOWS edges: find Bob, Carol
  -> Follow their FOLLOWS edges: find Dave, Eve, Frank
  -> Return results

  This is a graph traversal, not a join -- O(edges traversed),
  not O(table size). At 1 million hops it stays fast.
```

**Use graph databases when:** the relationships between data points
are as important as the data itself. Social networks, recommendation
engines, fraud detection ("this card shares an address with 3 flagged cards").

[Back to Top](#top)

<a id="when-nosql-wins-over-sql"></a>

## When NoSQL Wins Over SQL

```
NoSQL wins when:

  [x]  Schema varies record to record (user profiles with 50 optional fields)
  [x]  Write volume exceeds what a single SQL primary can handle
  [x]  You need horizontal sharding built-in from day one
  [x]  Access patterns are simple and predictable (always look up by ID)
  [x]  You're storing time-series, events, or logs
  [x]  Relationships between data ARE the data (graph)
  [x]  You need sub-millisecond reads and can tolerate eventual consistency

SQL still wins for:
  [x]  Anything involving money or legal records
  [x]  Complex multi-table queries you can't predict in advance
  [x]  Strong consistency requirements
  [x]  Teams that already know SQL well (don't underestimate this)
```

The honest truth: most startups should start with PostgreSQL.
Switch to NoSQL when you have a concrete problem it solves.

[Back to Top](#top)

<a id="4-the-n1-problem"></a>

# 4. The N+1 Problem

"This one," Bhanu says, shaking his head, "I have seen bring down production
systems at three different companies. The code looks clean. It passes code review.
And then it fires a thousand queries where one would do."

This is a story about a developer who wrote innocent-looking code
and accidentally made 101 database queries where 1 would have done.

The application shows a page with 100 users and their most recent order.

```python
# The developer writes this:

users = db.query("SELECT * FROM users LIMIT 100")     # Query 1

for user in users:
    order = db.query(
        "SELECT * FROM orders WHERE user_id = ? "
        "ORDER BY created_at DESC LIMIT 1",
        user.id
    )                                                  # Query 2, 3, 4, ... 101
    user.latest_order = order
```

This looks clean. It runs. It works. In development, with 10 rows, it's fast.

In production, with 100 users, it fires **101 queries**:
- 1 to load the users
- 100 more, one per user, to load each order

```
Query count explosion:

  Page size    Queries fired    Time (at 1ms/query)
  ----------   -------------    ------------------
     10              11              11ms
    100             101             101ms
    500             501             501ms
  1,000           1,001              ~1 second
```

The fix is a JOIN — fetch everything in one trip:

```sql
-- One query, all the data:
SELECT users.*, orders.id as order_id, orders.total, orders.created_at
FROM users
LEFT JOIN orders ON orders.user_id = users.id
  AND orders.created_at = (
    SELECT MAX(created_at) FROM orders o2
    WHERE o2.user_id = users.id
  )
LIMIT 100;
```

Or in ORM terms, **eager loading** — tell the ORM to load related
records in bulk upfront rather than one by one:

```python
# SQLAlchemy (Python) -- loads all orders in ONE extra query, not 100:
users = db.query(User).options(
    joinedload(User.latest_order)
).limit(100).all()

# Now: 2 queries total. Always 2, regardless of how many users.
```

```
With eager loading:

  Queries: 1 (users) + 1 (all their orders, batched) = 2
  Always 2, no matter the page size.

  vs N+1:
  Queries: 1 + page_size (grows with data)
```

N+1 is one of the most common performance bugs in web applications.
The symptom: page load times that scale linearly with result count.
The fix: always check query counts in your ORM's debug logs.

[Back to Top](#top)

<a id="5-replication"></a>

# 5. Replication

"Replication is insurance," Bhanu explains. "You pay a small premium — some
network bandwidth, a little lag — and in return, your database can survive
hardware failure and serve ten times the read traffic."

Your database has a problem: it's a single machine.
If it dies, your entire application goes down with it.
And as traffic grows, one machine can only serve so many reads.

**Replication** means running multiple copies of your database.

<a id="primary-replica-replication"></a>

## Primary-Replica Replication

```
                    +-------------------+
    All writes  --> |    Primary DB     |
                    |  (source of       |
                    |    truth)         |
                    +--------+----------+
                             |  replication stream
                    +--------+------------------------+
                    |         |                       |
             +------v------+ +------v------+ +-------v-----+
             |  Replica 1  | |  Replica 2  | |  Replica 3  |
             |  (read-only)| |  (read-only)| |  (read-only)|
             +-------------+ +-------------+ +-------------+
                    ^                ^                ^
              reads served     reads served      reads served
```

**Writes** go to the Primary only. The Primary writes the change
to its own storage and simultaneously streams that change to replicas.

**Reads** can be served from any replica — spreading the load
across multiple machines.

**Failover:** if the Primary dies, one replica is promoted to Primary.
Downtime measured in seconds to minutes, not hours.

[Back to Top](#top)

<a id="the-replication-lag-problem"></a>

## The Replication Lag Problem

Replication is not instant. There is always a small delay between
the Primary committing a write and the replicas applying it.

```
Timeline:

  t=0:    User updates their profile picture
  t=0:    Primary writes the change
  t=0.1s: Primary acknowledges success to the user
  t=0.2s: Replica A applies the change
  t=0.3s: Replica B applies the change
                                         <- 0-300ms window
  During this window:
    User refreshes the page
    Load balancer routes them to Replica A (not yet updated)
    They see their OLD profile picture
    "Did my save fail??"
```

This is **replication lag** causing a **stale read**.

Common solutions:
- **Read-your-own-writes consistency:** after a write, route reads for
  that user to the Primary for a short window
- **Sticky sessions:** always route a user to the same replica
- **Sync replication:** wait for replicas to confirm before acknowledging
  the write (much slower, but no lag)

Most applications tolerate a few hundred milliseconds of lag.
Financial systems do not.

[Back to Top](#top)

<a id="read-replicas-for-scaling-reads"></a>

## Read Replicas for Scaling Reads

Most web applications are read-heavy. A typical ratio:
90% reads, 10% writes.

```
Before replicas:
  1 database server -> handles all 10,000 req/sec
  Becomes CPU/memory bottleneck around 5,000-10,000 req/sec

With 3 read replicas:
  1 primary  -> handles all writes (1,000 write req/sec)
  3 replicas -> share 9,000 read req/sec (3,000 each)

  Read capacity: 3x increase with no schema changes
```

This is the cheapest form of database scaling.
Before you consider anything more complex (sharding, new technology),
add read replicas.

[Back to Top](#top)

<a id="6-sharding"></a>

# 6. Sharding

"Sharding," Bhanu says, leaning forward, "is the last resort that everyone
wants to reach for first. I always tell my team: if you're thinking about
sharding before you've tried read replicas, better indexes, and caching,
you're solving the wrong problem."

You've added replicas. You have 10 replicas. Your write volume keeps
growing and only the Primary handles writes. The Primary is now
the bottleneck.

You need to split your data across multiple machines so that
each machine handles a fraction of the total write load.

This is **sharding** (also called horizontal partitioning).

<a id="the-phone-book-analogy"></a>

## The Phone Book Analogy

Imagine a city phone book so large it can't fit in one volume.
The publisher splits it: A-F in Volume 1, G-M in Volume 2, N-Z in Volume 3.

Each volume is a shard. You know which volume to open based on last name.

```
Sharded users table (range sharding by user_id):

  Shard 1           Shard 2           Shard 3
  +-------------+   +-------------+   +-------------+
  | user_id     |   | user_id     |   | user_id     |
  | 1 - 999,999 |   | 1M - 1.99M  |   | 2M - 2.99M  |
  |             |   |             |   |             |
  | Writes: 33% |   | Writes: 33% |   | Writes: 33% |
  +-------------+   +-------------+   +-------------+
```

[Back to Top](#top)

<a id="hash-sharding-vs-range-sharding"></a>

## Hash Sharding vs Range Sharding

```
RANGE SHARDING (split by value range):

  Users 1-1M     -> Shard 1
  Users 1M-2M    -> Shard 2
  Users 2M-3M    -> Shard 3

  Pros:
    + Range queries are efficient ("get users 1000 to 2000")
    + Easy to reason about which shard holds what

  Cons:
    - "Hot shards": if all new signups are in Shard 3, it's overloaded
    - Uneven data distribution over time

HASH SHARDING (split by hash of key):

  shard = hash(user_id) % number_of_shards

  user_id=1:    hash(1)  % 3 = shard 0
  user_id=2:    hash(2)  % 3 = shard 1
  user_id=3:    hash(3)  % 3 = shard 2
  user_id=4:    hash(4)  % 3 = shard 0
  ...

  Pros:
    + Even distribution -- no hot shards
    + Works well when keys are random (UUIDs, user IDs)

  Cons:
    - Range queries are useless (all shards must be checked)
    - Resharding is painful: adding a new shard changes
      hash(key) % n for almost all keys
```

[Back to Top](#top)

<a id="the-cross-shard-query-problem"></a>

## The Cross-Shard Query Problem

Sharding's biggest pain arrives when a query spans multiple shards.

```
Single-shard query (easy):
  "Get user 1,234,567"
  -> Compute shard: hash(1234567) % 3 = shard 2
  -> Query shard 2 only
  -> Fast

Cross-shard query (painful):
  "Get all users who signed up in January"
  -> January users are spread across ALL shards
  -> Must query ALL 3 shards in parallel
  -> Merge results in application code
  -> Slower, more complex

Cross-shard JOIN (very painful):
  "Get all orders where user.country = 'France'"
  -> users and orders may be on different shards
  -> Join cannot happen at the database level
  -> Must fetch users from user shards
  -> Fetch orders from order shards
  -> Join in application memory
  -> Hope everything fits in RAM
```

Sharding turns many simple SQL queries into application-level complexity.
This is why it's a last resort.

[Back to Top](#top)

<a id="when-is-sharding-actually-needed"></a>

## When Is Sharding Actually Needed

The honest answer: later than you think.

```
Most applications never need sharding:

  PostgreSQL handles:
    -> 10,000+ write transactions/second on good hardware
    -> Tables with hundreds of millions of rows (with indexes)
    -> Read replicas handle 10x that read volume

  Sharding becomes necessary around:
    -> >100,000 writes/second sustained
    -> Tables in the tens of billions of rows
    -> Companies like Twitter, Uber, Airbnb scale

  Before sharding, try:
    1. Read replicas (for read-heavy workloads)
    2. Better indexes (for slow queries)
    3. Upgrading hardware (CPUs, RAM, faster SSDs)
    4. Caching (for repeat reads)
    5. Archiving old data (smaller tables = faster queries)
    6. Then: consider sharding
```

The cost of sharding — in operational complexity, lost JOIN support,
resharding pain — is real. Only pay that cost when you must.

[Back to Top](#top)

<a id="7-sql-vs-nosql-quick-reference"></a>

# 7. SQL vs NoSQL Quick Reference

"In interviews," Bhanu advises, "they'll ask you to choose between SQL and NoSQL
for a given system. Don't guess. Use this decision matrix."

```
+----------------------------------+------------+--------------------------+
|  Question                        | Points to  |  Why                     |
+----------------------------------+------------+--------------------------+
| Need ACID transactions?          |    SQL     | NoSQL rarely guarantees  |
|                                  |            | cross-record ACID        |
+----------------------------------+------------+--------------------------+
| Data is financial / legal?       |    SQL     | No eventual consistency  |
|                                  |            | in banking               |
+----------------------------------+------------+--------------------------+
| Complex, ad-hoc queries?         |    SQL     | SQL is expressive;       |
|                                  |            | NoSQL is narrow          |
+----------------------------------+------------+--------------------------+
| Schema changes constantly?       |  NoSQL     | Document stores handle   |
|                                  |  (doc)     | flexible schemas well    |
+----------------------------------+------------+--------------------------+
| Writing millions of events/sec?  |  NoSQL     | Cassandra, DynamoDB are  |
|                                  |            | built for this           |
+----------------------------------+------------+--------------------------+
| Primary access: look up by ID?   |  NoSQL     | Key-value is O(1),       |
|                                  |  (K-V)     | scales infinitely        |
+----------------------------------+------------+--------------------------+
| Data IS the relationships?       |  NoSQL     | Graph DBs navigate       |
|                                  |  (graph)   | relationships natively   |
+----------------------------------+------------+--------------------------+
| Small-to-medium scale?           |    SQL     | PostgreSQL handles more  |
|                                  |            | than most teams need     |
+----------------------------------+------------+--------------------------+
| Team knows SQL well?             |    SQL     | Operational expertise    |
|                                  |            | is a real advantage      |
+----------------------------------+------------+--------------------------+

Default recommendation: Start with PostgreSQL.
Migrate to NoSQL when you have a specific, proven problem it solves.
```

[Back to Top](#top)

<a id="8-mental-models-to-carry-forward"></a>

# 8. Mental Models to Carry Forward

"These are the six truths I carry into every architecture review," Bhanu says.
"Memorize them. They'll save you from bad decisions."

```
1. Databases exist because files can't handle concurrent access,
   crashes mid-write, or large-scale queries.

2. SQL's ACID guarantees are not free -- they require coordination.
   That coordination is why SQL doesn't scale writes infinitely.

3. Indexes trade write speed for read speed.
   Add them where reads are frequent; don't add them everywhere.

4. The N+1 problem is a code issue, not a database issue.
   Always check how many queries your ORM is generating.

5. Replication scales reads. Sharding scales writes.
   Try replication first; sharding is expensive to operate.

6. NoSQL trades the flexibility of SQL for performance
   and scale in specific access patterns. It's a trade, not an upgrade.
```

[Back to Top](#top)

<a id="9-learning-priority"></a>

# 9. Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
SQL vs NoSQL selection criteria, ACID properties, index trade-offs, sharding strategies

**Should Learn** — Important for real projects, comes up regularly:
replication modes (async vs sync), connection pool sizing, query optimization basics

**Good to Know** — Useful in specific situations, not always tested:
transaction isolation levels, B-tree vs LSM-tree trade-offs, read replicas

**Reference** — Know it exists, look up syntax when needed:
write amplification, PITR backup, schema versioning and migrations

[Back to Top](#top)

<a id="summary"></a>

# Summary

| Concept | One-Liner |
|---------|-----------|
| File-based storage | Breaks under concurrency, crashes, and scale — databases solve this |
| SQL / Relational | Structured, ACID-compliant, JOIN-capable — default for most apps |
| ACID | Atomicity + Consistency + Isolation + Durability = safe transactions |
| Indexes | B-tree lookup turns O(n) scans into O(log n) — trade write speed for read speed |
| NoSQL (Document) | Flexible schema, entity-centric reads — MongoDB |
| NoSQL (Key-Value) | O(1) lookup by key — Redis, DynamoDB |
| NoSQL (Column-Family) | Write-optimized time-series — Cassandra |
| NoSQL (Graph) | Relationship traversal as first-class operation — Neo4j |
| N+1 Problem | Loop queries that should be JOINs — fix with eager loading |
| Replication | Multiple copies scale reads and provide failover |
| Replication Lag | Stale reads during the sync window — solve with read-your-own-writes |
| Sharding | Split data across machines to scale writes — last resort |
| Hash vs Range Shard | Even distribution vs range query support — pick based on access pattern |
| Cross-shard queries | JOINs become application-level logic — the cost of sharding |
| Default choice | Start with PostgreSQL until a specific problem demands otherwise |

[Back to Top](#top)

**[Back to README](../README.md)**

**Prev:** [Backend Architecture - theory.md](../04_backend_architecture/theory.md) | **Next:** [Caching - theory.md](../06_caching/theory.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) | [Interview Q&A](./interview.md)
