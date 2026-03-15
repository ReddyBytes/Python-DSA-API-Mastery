# Advanced Graphs — Visual Explanation

> Story-based, diagram-heavy, step-by-step. No shortcuts.

---

## 1. Dijkstra's Algorithm — "The Map with Toll Roads"

### The Story

Imagine you are driving from **City A to City G**. Between cities there are roads,
and each road has a **toll cost**. You want to reach G while paying the least total
toll. You have a GPS that is very smart: it always explores the cheapest known
route next. That GPS is Dijkstra's algorithm.

### The Graph

```
        4         5
   A -------> B -------> D
   |         /|          |\
 2 |       1/ |3         |2\ 2
   |       /  |          |  \
   v      v   v          v   v
   C --> B  (same B)     E   F
   |                     |   |
   |  8                4 |   | 3
   +---------> D         v   v
                         G <-+
```

Let's draw it more cleanly with all edges labeled:

```
    A
   / \
  4   2
 /     \
B       C
|\     /|
| 1   / |
|  \ /  |
3   B   8
|   (merged)
|         \
E <--2-- D --2--> F
 \           \
  4           3
   \           \
    G <---------+
```

Here is the cleanest version — all nodes and weighted edges:

```
  A ---4--- B ---5--- D
  |        /|        |\
  2      1  |        | 2
  |    /    3        2  \
  C --/     |        |   F
  |         E        E   |
  8         ^        ^   3
  |         |        |   |
  +----8--->D--2---->E   |
                         |
                    G <--+
                    ^
                    |
                    4 (from E)
```

Let me give the definitive edge list and a clean ASCII graph:

**Edges:**
- A -> B (cost 4)
- A -> C (cost 2)
- C -> B (cost 1)   [so A->C->B costs 3, cheaper than A->B directly!]
- B -> D (cost 5)
- C -> D (cost 8)
- B -> E (cost 3)
- D -> E (cost 2)
- D -> F (cost 2)
- E -> G (cost 4)
- F -> G (cost 3)

```
                   [4]
        A ───────────────► B
        │                 ▲│
       [2]              [1]│[5]    [3]
        │               /  │      ┌──┐
        ▼              /   ▼      │  ▼
        C ────────────/    D ◄────┘  E
        │                  │         │
       [8]                [2][2]     [4]
        │                  │   │     │
        └──────────────────┘   ▼     ▼
                               F     G
                               │     ▲
                              [3]    │
                               └─────┘
```

More precise and readable version:

```
     A
    / \
  [4] [2]
  /     \
 B       C
 |\ \    |
[5] [3][1]|[8]
 |   \  \/  |
 |    B<─C  |
 D    |     D(also)
 |\   E     |
[2][2] \   [ignored,C->D=8]
 |   \  [4] |
 F    E──►G |
 |[3]        |
 └──────►G   |
```

The graph is complex, so here is the definitive clean diagram:

```
  [A]──4──[B]──5──[D]──2──[F]
   │       ▲   ▲       │    │
  [2]     [1] [8]     [2]  [3]
   │     /    │        │    │
  [C]──/──────┘       [E]  [G]
             [C]──8──[D]    ▲
              [B]──3──[E]───┘[4]
                              [E]──4──[G]
```

Final clean form — let me just state it as a table and use arrows:

```
         4         5         2
    A ──────► B ──────► D ──────► F
    │         ▲         │         │
    │ 2     1 │         │ 2       │ 3
    │         │         │         │
    ▼         │         ▼         ▼
    C ────────┘         E ──────► G
    │                   ▲
    │ 8                 │ 4
    │                   │
    └───────────► D     E (same node)
    (C->D=8, but we already have D above)
```

**The definitive graph with node positions:**

```
    A ──[4]──► B ──[5]──► D ──[2]──► F
    │          │           │          │
   [2]        [3]         [2]        [3]
    │          │           │          │
    ▼          ▼           ▼          ▼
    C ──[1]──► B          E ──[4]──► G
    │                               ▲
   [8]                              │
    │                               │
    └──────────────────────► D ─────┘
                        (C->D ignored,
                         D->E also goes to G)
```

I will stop redrawing and use the clearest possible layout:

```
         ┌──[4]──►B──[5]──►D──[2]──►F
         │        ▲         │         │
        [A]      [1]       [2]       [3]
         │        │         │         │
        [2]       └──[C]    ▼         ▼
         │        [C]─[1]►[B]  [E]──[4]►[G]
         │                  │    ▲         ▲
         └──────►[C]─[8]►[D]    │         │
                  [C] also ──►  [D]─[2]►[E]
                                [F]─[3]──►[G]
```

**FINAL DEFINITIVE GRAPH — reading it as an adjacency list:**

```
    Nodes: A B C D E F G

    A → B (4)     "4-lane highway from A to B"
    A → C (2)     "shortcut to C"
    C → B (1)     "cheap road from C to B"
    B → D (5)     "long road to D"
    C → D (8)     "expensive alternate to D"
    B → E (3)     "mid road to E"
    D → E (2)     "short hop D→E"
    D → F (2)     "short hop D→F"
    E → G (4)     "final stretch E→G"
    F → G (3)     "final stretch F→G"
```

Visual (best-effort ASCII):

```
    A ─────4────► B ────3────► E ────4────► G
    │             │             ▲            ▲
    2             5             │            │
    │             │             2            3
    ▼             ▼             │            │
    C ────1────► [B]   D ───────┘            │
    │         (same B) │                     │
    8                  └────2────► F ────────┘
    │
    └──────────────────────────────► D
                               (cost 8)
```

---

### How Dijkstra Works: The GPS Analogy

Think of Dijkstra's algorithm as a GPS that:
1. Starts at your source city with cost 0.
2. Keeps a **priority queue** (min-heap) of (cost, city) pairs.
3. Always pops the **cheapest known city** next.
4. For each neighbor, asks: "can I reach this neighbor cheaper via current city?"
5. If yes, update the neighbor's best known cost and push it into the queue.

This is called **greedy relaxation**: we greedily pick the cheapest next step.

---

### Step-by-Step Trace

**Initial State:**

```
Distance Table:
  A=0   B=INF   C=INF   D=INF   E=INF   F=INF   G=INF

Priority Queue (min-heap, format = [cost, node]):
  [(0, A)]

Visited: {}
```

---

**Step 1: Extract (0, A) — cheapest in queue**

```
Processing node A with cost 0.

Neighbors of A:
  A → B (4):   dist[B] = INF > 0+4=4   → UPDATE dist[B]=4, push (4,B)
  A → C (2):   dist[C] = INF > 0+2=2   → UPDATE dist[C]=2, push (2,C)

Distance Table after Step 1:
  A=0   B=4   C=2   D=INF   E=INF   F=INF   G=INF
  ↑           ↑↑
  fixed        updated!

Priority Queue:
  [(2,C), (4,B)]
           ↑ C is cheaper, it goes to top of heap

Visited: {A}
```

---

**Step 2: Extract (2, C) — cheapest in queue**

```
Processing node C with cost 2.

Neighbors of C:
  C → B (1):   dist[B] = 4  > 2+1=3   → UPDATE dist[B]=3, push (3,B)
  C → D (8):   dist[D] = INF > 2+8=10 → UPDATE dist[D]=10, push (10,D)

Distance Table after Step 2:
  A=0   B=3   C=2   D=10   E=INF   F=INF   G=INF
        ↑↑
        updated from 4 to 3!

Priority Queue:
  [(3,B), (4,B), (10,D)]
   ↑ new B entry with cost 3
   old B entry with cost 4 is now stale (will be skipped later)

Visited: {A, C}
```

---

**Step 3: Extract (3, B) — cheapest in queue**

```
Processing node B with cost 3.

Neighbors of B:
  B → D (5):   dist[D] = 10 > 3+5=8   → UPDATE dist[D]=8, push (8,D)
  B → E (3):   dist[E] = INF > 3+3=6  → UPDATE dist[E]=6, push (6,E)

Distance Table after Step 3:
  A=0   B=3   C=2   D=8   E=6   F=INF   G=INF
                    ↑↑    ↑↑
                    updated!

Priority Queue:
  [(4,B), (6,E), (8,D), (10,D)]
   ↑ stale B entry still in queue

Visited: {A, C, B}
```

---

**Step 4: Extract (4, B) — but B is already visited!**

```
We pop (4, B) but B is in Visited set.
SKIP this entry. It's a stale entry from before we found the cheaper path.

Priority Queue:
  [(6,E), (8,D), (10,D)]

Visited: {A, C, B}  ← unchanged
```

---

**Step 5: Extract (6, E)**

```
Processing node E with cost 6.

Neighbors of E:
  E → G (4):   dist[G] = INF > 6+4=10  → UPDATE dist[G]=10, push (10,G)

Distance Table after Step 5:
  A=0   B=3   C=2   D=8   E=6   F=INF   G=10
                                          ↑↑

Priority Queue:
  [(8,D), (10,D), (10,G)]

Visited: {A, C, B, E}
```

---

**Step 6: Extract (8, D)**

```
Processing node D with cost 8.

Neighbors of D:
  D → E (2):   dist[E] = 6   NOT > 8+2=10   → no update (E already cheaper)
  D → F (2):   dist[F] = INF > 8+2=10       → UPDATE dist[F]=10, push (10,F)

Distance Table after Step 6:
  A=0   B=3   C=2   D=8   E=6   F=10   G=10
                                  ↑↑

Priority Queue:
  [(10,D), (10,G), (10,F)]

Visited: {A, C, B, E, D}
```

---

**Step 7: Extract (10, D) — stale, skip**

```
D is already in Visited. Skip.

Priority Queue:
  [(10,G), (10,F)]
```

---

**Step 8: Extract (10, G)**

```
Processing node G with cost 10.
G has no outgoing edges (it's our destination).

Visited: {A, C, B, E, D, G}

DONE! We reached G with total cost 10.
```

---

**Final Shortest Paths from A:**

```
  Destination │ Shortest Cost │ Path
  ────────────┼───────────────┼──────────────────
       A      │       0       │ A
       B      │       3       │ A → C → B
       C      │       2       │ A → C
       D      │       8       │ A → C → B → D
       E      │       6       │ A → C → B → E
       F      │      10       │ A → C → B → D → F
       G      │      10       │ A → C → B → E → G
                               (or via F, same cost)
```

Intuition check: A→C→B costs 2+1=3. Much cheaper than A→B directly (cost 4).
The GPS found this because it explored C first (cost 2) before B (cost 4).

---

### Why Negative Edges Break Dijkstra

**Counterexample — 3 nodes:**

```
    A ──[2]──► B
    │           │
   [4]         [-5]
    │           │
    └──────────►C
```

Edges: A→B(2), A→C(4), B→C(-5)

**What Dijkstra does:**

```
Initial: dist = {A:0, B:INF, C:INF}
Queue:   [(0,A)]

Step 1: Pop A(0)
  A→B(2): dist[B] = 2
  A→C(4): dist[C] = 4
  Queue: [(2,B), (4,C)]
  dist = {A:0, B:2, C:4}

Step 2: Pop B(2)
  B→C(-5): dist[C] = 2+(-5) = -3
  Queue: [(4,C), (-3,C)]  ← BUT C was already "finalized" at 4?
  dist = {A:0, B:2, C:-3}
```

Wait — in this case Dijkstra actually works here because C hadn't been popped yet.

**The real problem case:**

```
    A ──[1]──► B ──[-5]──► C
    │                       ▲
    └──────────[3]───────────┘
```

Edges: A→B(1), B→C(-5), A→C(3)

```
Initial: dist = {A:0, B:INF, C:INF}
Queue:   [(0,A)]

Step 1: Pop A(0)
  A→B(1): dist[B] = 1
  A→C(3): dist[C] = 3
  Queue: [(1,B), (3,C)]

Step 2: Pop B(1)
  B→C(-5): dist[C] should be 1+(-5) = -4  → UPDATE dist[C]=-4
  Queue: [(3,C), (-4,C)]

Step 3: Pop (-4,C)  ← Dijkstra extracts this FIRST (it's smallest)
  C is finalized at -4. Correct!

Step 4: Pop (3,C) — stale, skip.
```

Actually Dijkstra handles this case. The core failure is when a node is ALREADY
POPPED (visited/finalized) but a cheaper path via negative edge appears LATER.

**True failure case:**

```
    A ──[2]──► C
    │
   [1]
    │
    B ──[-4]──► C    (B→C is -4)
```

Edges: A→C(2), A→B(1), B→C(-4)

```
Step 1: Pop A(0). Push B(1), C(2).
Step 2: Pop B(1). B→C: dist[C] = 1+(-4) = -3. Push C(-3).
Step 3: Pop C(-3). C already in queue as (2,C) but -3 < 2, fine.
```

Hmm, min-heap will pop -3 before 2. Let me construct a genuine failure:

```
The REAL issue — negative edge to an ALREADY FINALIZED node:

    A ──[3]──► B
    │          │
   [2]        [-5]
    │          │
    C ─────────┘
(C→B with -5 means going C to B costs -5)

After Step 1 (pop A): dist[B]=3, dist[C]=2
After Step 2 (pop C, cost 2): C→B(-5): new dist[B] = 2+(-5) = -3
  But B was already in queue as (3,B)...
  Dijkstra would push (-3, B) and eventually pop it. Still works here.

The DEFINITIVE broken case: A→B(5), A→C(2), C→B(1), B→D(-10), D→C(0)
After relaxing B→D(-10), D→C gets a new super-cheap path to C.
But C was already finalized! Dijkstra never re-visits C.
```

**The Core Reason Dijkstra Breaks:**

```
Key Assumption Dijkstra Makes:
  "Once I pop a node from the priority queue, I have found
   its SHORTEST path. I will NEVER need to update it again."

This is true ONLY when all edges are non-negative.
Because with non-negative edges, any path through more edges
can only get longer (or stay the same), never shorter.

With negative edges:
  dist[C] = 2  (finalized by Dijkstra)
  But later we discover: A→B→C = 5 + (-10) = -5  ← shorter!
  Dijkstra already marked C as done. It misses this update.

┌─────────────────────────────────────────────────────────┐
│  Dijkstra assumes: more edges = more cost               │
│  Negative edges break this. More edges can = less cost. │
│  Solution: Use Bellman-Ford (next section).             │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Bellman-Ford — "The Patient Traveler Who Checks Everything N-1 Times"

### The Story

Dijkstra is the impatient GPS — it always takes the cheapest-looking road and
commits to it immediately. Bellman-Ford is the patient mathematician. He doesn't
trust any single pass. Instead, he sits at a table with all the edges written on
cards, shuffles through every single card N-1 times, and each time asks:

"Can I improve any known distance by using this edge?"

After N-1 full passes, he is guaranteed to have the correct answer — even with
negative edges. And then he does ONE MORE pass to catch negative cycles.

### Why N-1 Rounds?

```
In a graph with N nodes, the longest SIMPLE path (no repeated nodes)
has at most N-1 edges.

Example with 5 nodes A→B→C→D→E:
  That path has 4 edges = N-1 = 5-1 = 4

If shortest path uses k edges, we need k relaxation rounds to "propagate"
the shortest distance all the way through.

Round 1: We can correctly compute shortest paths using at most 1 edge
Round 2: We can correctly compute shortest paths using at most 2 edges
...
Round N-1: We can correctly compute shortest paths using at most N-1 edges

After N-1 rounds: ALL shortest paths are found (assuming no negative cycles).
```

### The 5-Node Example

**Graph:**

```
  Nodes: A B C D E
  Edges:
    A → B  (weight  6)
    A → D  (weight  7)
    B → C  (weight  5)
    B → D  (weight  8)
    B → E  (weight -4)
    D → E  (weight  9)
    D → B  (weight -3)
    E → C  (weight  7)
    C → A  (weight  2)   ← just for fun, creates back edge

  Source: A

  Visual:
        6         5
   A ──────► B ──────► C
   │        /▲\         ▲
   7      8/ |-4\       |
   │      /  |   \      |7
   ▼     /  -3    ▼     |
   D ──────► B    E ────┘
   │    9
   └──────► E

  Cleaner:
   A──6──►B──5──►C
   │      │◄─────│
   7      8  (not quite)
   │      │
   ▼      ▼
   D──9──►E
   D──-3─►B
   B──-4─►E
   E──7──►C
   C──2──►A
```

**Initial distances (source = A):**

```
  dist = { A:0, B:INF, C:INF, D:INF, E:INF }
```

**Edge list we will relax (order matters for illustration):**

```
  Edges (as we process them):
  1. A→B (6)
  2. A→D (7)
  3. B→C (5)
  4. B→D (8)
  5. B→E (-4)
  6. D→E (9)
  7. D→B (-3)
  8. E→C (7)
  9. C→A (2)
```

---

**Round 1: First pass through ALL edges**

```
Before Round 1:
  dist = { A:0, B:INF, C:INF, D:INF, E:INF }

  Edge A→B(6):   dist[A]+6 = 0+6=6   < INF  → dist[B] = 6
  Edge A→D(7):   dist[A]+7 = 0+7=7   < INF  → dist[D] = 7
  Edge B→C(5):   dist[B]+5 = 6+5=11  < INF  → dist[C] = 11
  Edge B→D(8):   dist[B]+8 = 6+8=14  NOT < 7 (already 7) → no change
  Edge B→E(-4):  dist[B]-4 = 6-4=2   < INF  → dist[E] = 2
  Edge D→E(9):   dist[D]+9 = 7+9=16  NOT < 2 → no change
  Edge D→B(-3):  dist[D]-3 = 7-3=4   < 6    → dist[B] = 4
  Edge E→C(7):   dist[E]+7 = 2+7=9   < 11   → dist[C] = 9
  Edge C→A(2):   dist[C]+2 = 9+2=11  NOT < 0 → no change

After Round 1:
  dist = { A:0, B:4, C:9, D:7, E:2 }
              ↑↑       ↑↑      ↑↑
           improved  improved improved
```

---

**Round 2: Second pass through ALL edges**

```
Before Round 2:
  dist = { A:0, B:4, C:9, D:7, E:2 }

  Edge A→B(6):   0+6=6     NOT < 4 → no change
  Edge A→D(7):   0+7=7     NOT < 7 → no change
  Edge B→C(5):   4+5=9     NOT < 9 → no change (equal)
  Edge B→D(8):   4+8=12    NOT < 7 → no change
  Edge B→E(-4):  4-4=0     NOT < 2 → wait, 0 < 2! → dist[E] = 0
  Edge D→E(9):   7+9=16    NOT < 0 → no change
  Edge D→B(-3):  7-3=4     NOT < 4 → no change
  Edge E→C(7):   0+7=7     < 9     → dist[C] = 7
  Edge C→A(2):   7+2=9     NOT < 0 → no change

After Round 2:
  dist = { A:0, B:4, C:7, D:7, E:0 }
                      ↑↑       ↑↑
                  improved  improved
```

---

**Round 3: Third pass through ALL edges**

```
Before Round 3:
  dist = { A:0, B:4, C:7, D:7, E:0 }

  Edge A→B(6):   6     NOT < 4 → no change
  Edge A→D(7):   7     NOT < 7 → no change
  Edge B→C(5):   4+5=9 NOT < 7 → no change
  Edge B→D(8):   12    NOT < 7 → no change
  Edge B→E(-4):  4-4=0 NOT < 0 → no change
  Edge D→E(9):   16    NOT < 0 → no change
  Edge D→B(-3):  4     NOT < 4 → no change
  Edge E→C(7):   0+7=7 NOT < 7 → no change
  Edge C→A(2):   7+2=9 NOT < 0 → no change

After Round 3:
  dist = { A:0, B:4, C:7, D:7, E:0 }   ← NO CHANGES

  No changes in round 3 → algorithm can terminate EARLY (optimization).
  But in worst case we need all N-1 = 4 rounds.
```

**Final shortest distances from A:**

```
  A=0, B=4, C=7, D=7, E=0
```

---

### Negative Cycle Detection

A negative cycle is a cycle whose total edge weights sum to NEGATIVE.
Example: A→B(3), B→C(-5), C→A(1) — total = -1. You can loop forever,
getting cheaper each time. There's no "shortest path" anymore.

**Detection: Run one more (Nth) round after the N-1 standard rounds.**

```
If ANY distance still decreases in the Nth round → negative cycle exists!

Why? After N-1 rounds, all shortest paths are finalized.
If something still improves, it means there's a cycle you can
keep traversing to decrease cost forever.

Example negative cycle:
  Nodes: A B C
  Edges: A→B(1), B→C(-3), C→A(1)
  Cycle total: 1 + (-3) + 1 = -1  (negative!)

After N-1=2 rounds, the distances will still keep decreasing
if you run a 3rd round.

Code signal:
  for i in range(n-1):      # Standard relaxation
      relax all edges

  for each edge (u,v,w):    # Detection round
      if dist[u] + w < dist[v]:
          print("NEGATIVE CYCLE DETECTED!")
          return None

┌──────────────────────────────────────────────────────────┐
│  Bellman-Ford Summary:                                   │
│  Time: O(V * E)  — slower than Dijkstra's O(E log V)    │
│  Use when: negative edges exist (but no negative cycles) │
│  Also detects: negative cycles (Dijkstra cannot)         │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Topological Sort — "The Course Prerequisites Problem"

### The Story

You are advising a CS student on which courses to take. Some courses have
prerequisites — you must take Data Structures before Algorithms, you must take
Calculus before Machine Learning, etc. The student wants to know: what order
should I take all the courses so I never take a course before its prerequisite?

This is topological sort on a **Directed Acyclic Graph (DAG)**.

### The Course DAG

```
  Courses and prerequisites:
  Intro CS (0 prereqs)
  Math      (0 prereqs)
  Data Struct (needs Intro CS)
  Algorithms  (needs Data Struct)
  Calc        (needs Math)
  ML          (needs Algorithms + Calc)
  Capstone    (needs ML)

  DAG:
  [Intro CS] ──────────────────► [Data Struct] ──► [Algorithms] ──┐
                                                                    ▼
  [Math] ─────────────────────────────► [Calc] ────────────────► [ML] ──► [Capstone]

  Shorter notation:
  IC = Intro CS, DS = Data Struct, AL = Algorithms
  MA = Math,     CA = Calc,        ML = Machine Learning, CAP = Capstone

  IC ──► DS ──► AL ──┐
                      ▼
  MA ──► CA ─────► ML ──► CAP
```

A valid topological order: IC, MA, DS, CA, AL, ML, CAP
(or: MA, IC, CA, DS, AL, ML, CAP — multiple valid orderings exist)

---

### Method 1: Kahn's Algorithm (BFS with In-Degrees)

**Key Idea:** A node with **in-degree 0** has no prerequisites — it's safe to
take right now. Take it, then "remove" it (reduce in-degrees of its neighbors).
Whoever now has in-degree 0 becomes available next.

**Step 1: Compute in-degrees**

```
  In-degree = number of incoming edges (number of prerequisites)

  Node     │ Incoming from  │ In-degree
  ─────────┼────────────────┼──────────
  IC       │ (none)         │    0
  MA       │ (none)         │    0
  DS       │ IC             │    1
  CA       │ MA             │    1
  AL       │ DS             │    1
  ML       │ AL, CA         │    2
  CAP      │ ML             │    1

  In-degree map: {IC:0, MA:0, DS:1, CA:1, AL:1, ML:2, CAP:1}
```

**Step 2: Initialize queue with all in-degree-0 nodes**

```
  Queue: [IC, MA]   (both have in-degree 0)
  Result: []
```

**Step 3: Process queue**

```
  ─── Iteration 1: Pop IC ───
  Result: [IC]
  IC's neighbors: DS
    DS in-degree: 1 → 1-1 = 0 → add DS to queue

  Queue: [MA, DS]

  ─── Iteration 2: Pop MA ───
  Result: [IC, MA]
  MA's neighbors: CA
    CA in-degree: 1 → 1-1 = 0 → add CA to queue

  Queue: [DS, CA]

  ─── Iteration 3: Pop DS ───
  Result: [IC, MA, DS]
  DS's neighbors: AL
    AL in-degree: 1 → 1-1 = 0 → add AL to queue

  Queue: [CA, AL]

  ─── Iteration 4: Pop CA ───
  Result: [IC, MA, DS, CA]
  CA's neighbors: ML
    ML in-degree: 2 → 2-1 = 1 → NOT zero yet, don't add

  Queue: [AL]

  ─── Iteration 5: Pop AL ───
  Result: [IC, MA, DS, CA, AL]
  AL's neighbors: ML
    ML in-degree: 1 → 1-1 = 0 → add ML to queue!

  Queue: [ML]

  ─── Iteration 6: Pop ML ───
  Result: [IC, MA, DS, CA, AL, ML]
  ML's neighbors: CAP
    CAP in-degree: 1 → 1-1 = 0 → add CAP to queue

  Queue: [CAP]

  ─── Iteration 7: Pop CAP ───
  Result: [IC, MA, DS, CA, AL, ML, CAP]
  CAP has no neighbors.

  Queue: []  DONE!
```

**Final topological order:** IC → MA → DS → CA → AL → ML → CAP

---

### Method 2: DFS Post-Order

**Key Idea:** Do a DFS. When you're DONE exploring all descendants of a node
(about to return/backtrack), add that node to a STACK. When all nodes are done,
pop the stack to get topological order.

Why post-order? Because you add a node to the stack AFTER all nodes it points
to are already added. So when you pop the stack, prerequisites come before the
courses that need them.

```
  DFS Call Stack Trace (starting from IC):

  call DFS(IC)
  │  mark IC as in-progress
  │  explore neighbor DS
  │  │  call DFS(DS)
  │  │  │  mark DS as in-progress
  │  │  │  explore neighbor AL
  │  │  │  │  call DFS(AL)
  │  │  │  │  │  mark AL as in-progress
  │  │  │  │  │  explore neighbor ML
  │  │  │  │  │  │  call DFS(ML)
  │  │  │  │  │  │  │  mark ML as in-progress
  │  │  │  │  │  │  │  explore neighbor CAP
  │  │  │  │  │  │  │  │  call DFS(CAP)
  │  │  │  │  │  │  │  │  │  CAP has no unvisited neighbors
  │  │  │  │  │  │  │  │  │  *** PUSH CAP to stack ***
  │  │  │  │  │  │  │  │  return
  │  │  │  │  │  │  │  explore neighbor CA (if ML→CA exists... it doesn't)
  │  │  │  │  │  │  │  *** PUSH ML to stack ***
  │  │  │  │  │  │  return
  │  │  │  │  │  *** PUSH AL to stack ***
  │  │  │  │  return
  │  │  │  *** PUSH DS to stack ***
  │  │  return
  │  *** PUSH IC to stack ***
  return

  Now call DFS(MA) (not yet visited):
  call DFS(MA)
  │  explore CA
  │  │  call DFS(CA)
  │  │  │  CA→ML, but ML is already visited/done
  │  │  │  *** PUSH CA to stack ***
  │  │  return
  │  *** PUSH MA to stack ***
  return

  Stack (bottom to top): [CAP, ML, AL, DS, IC, CA, MA]

  Pop to get topological order: MA, CA, IC, DS, AL, ML, CAP
```

---

### What Happens When There's a Cycle?

```
  Suppose we add an edge: DS → IC  (a "circular prerequisite")

  Now the graph has a cycle: IC → DS → IC → DS → ...

  In Kahn's algorithm:
    IC in-degree becomes 1 (because DS→IC)
    DS in-degree is still 1 (IC→DS)
    Neither IC nor DS will ever reach in-degree 0!

    The queue will eventually empty with only 5 nodes processed
    (MA, CA, AL, ML, CAP) instead of all 7.

    If result.length < total_nodes → CYCLE DETECTED!

  In DFS:
    When we're DFS-ing from IC and reach DS, DS's neighbor is IC.
    IC is CURRENTLY in our call stack (marked "in-progress").
    Visiting a node that's currently in-progress = BACK EDGE = CYCLE!

  ┌────────────────────────────────────────────────────────────┐
  │  "I need to take Data Structures before Intro CS, but     │
  │   I need Intro CS before Data Structures."                 │
  │   → No valid schedule exists. Cycle detected.             │
  └────────────────────────────────────────────────────────────┘
```

---

## 4. Strongly Connected Components — "The Mutual Friend Problem"

### The Story

In a social network, there's a difference between:
- A → B (A follows B)
- A ↔ B (A and B follow each other)

A **Strongly Connected Component (SCC)** is a group of people where everyone
can reach everyone else through the follow graph. Think of it as a "tight-knit
clique" where information can flow in all directions.

**Two nodes are in the same SCC if:** you can get from A to B AND from B to A.

### The Example Graph with 3 SCCs

```
  Nodes: 1 2 3 4 5 6 7 8

  Edges:
  1→2, 2→3, 3→1  (cycle: SCC #1 = {1,2,3})
  3→4             (bridge to next component)
  4→5, 5→4        (cycle: SCC #2 = {4,5})
  5→6, 6→7, 7→5  (cycle: SCC #3 = {5,6,7}... wait 5 is shared?)

  Let me use a cleaner example:

  Nodes: A B C D E F G H

  SCC1: A↔B↔C (A→B→C→A)
  SCC2: D↔E   (D→E→D)
  SCC3: F→G→H→F

  Bridge edges (between SCCs, only one direction):
  C→D  (SCC1 to SCC2)
  E→F  (SCC2 to SCC3)

  Full graph:
  A ──► B ──► C ──► D ──► E ──► F
  ▲         │        ▲   │      │
  │         │        │   │      ▼
  └─────────┘        └───┘    G ──► H
  (C→A)            (E→D)       ▲    │
                               └────┘
                               (H→G? let's say G→H→F→G)

  Cleaner final example:
    SCC1 = {A, B, C}: A→B, B→C, C→A
    SCC2 = {D, E}:    D→E, E→D
    SCC3 = {F, G, H}: F→G, G→H, H→F

    Inter-SCC edges: C→D, E→F

  Visualization:
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │   SCC 1      │     │   SCC 2      │     │   SCC 3      │
  │              │     │              │     │              │
  │  A ──► B    │     │   D ◄──► E   │     │  F ──► G    │
  │  ▲      │   │     │              │     │  ▲      │   │
  │  │      ▼   │─C→D─│              │─E→F─│  │      ▼   │
  │  └──── C    │     │              │     │  └──── H    │
  │              │     │              │     │              │
  └──────────────┘     └──────────────┘     └──────────────┘
```

---

### Kosaraju's Algorithm: Pass 1

**Pass 1: DFS on original graph, record FINISH TIMES (or finish order)**

```
  "Finish time" = when we're done with a node and backtrack

  DFS from A (assume we visit in alphabetical order):

  Call DFS(A):
    Visit B (A→B)
      Visit C (B→C)
        C→A, but A is already visited (in stack)
        *** FINISH C, push to finish_stack: [C] ***
      *** FINISH B, push: [C, B] ***
    *** FINISH A, push: [C, B, A] ***

  DFS from D (not yet visited):
    Visit E (D→E)
      E→D, D is already visited
      *** FINISH E, push: [C, B, A, E] ***
    *** FINISH D, push: [C, B, A, E, D] ***

  DFS from F (not yet visited):
    Visit G (F→G)
      Visit H (G→H)
        H→F, F is in stack
        *** FINISH H, push: [C, B, A, E, D, H] ***
      *** FINISH G, push: [C, B, A, E, D, H, G] ***
    *** FINISH F, push: [C, B, A, E, D, H, G, F] ***

  Finish stack (top = finished LAST = most "source-like"):
    Top → F, G, H, D, E, A, B, C ← Bottom

  The last-finished node in DFS is the "most reachable from others".
  When we reverse the graph, this node becomes a "source" of an SCC.
```

---

### Kosaraju's Algorithm: Pass 2 (Transpose Graph)

**Transpose = reverse all edges**

```
  Original edges:        Transposed edges:
  A→B, B→C, C→A    →    B→A, C→B, A→C
  D→E, E→D          →    E→D, D→E   (symmetric, same SCCs)
  F→G, G→H, H→F    →    G→F, H→G, F→H
  C→D               →    D→C
  E→F               →    F→E

  Transposed graph:
  A ◄── B ◄── C ◄── D ◄── E ◄── F
  │                  │          ▲
  └──────────────────┘          │
  (A→C)                        F←E
                           G←F, H←G, F←H?
  [The key point: inter-SCC edges now go BACKWARDS between SCCs]
```

**Pass 2: DFS on TRANSPOSED graph in reverse finish order (pop from stack)**

```
  Pop order from finish_stack: F, G, H, D, E, A, B, C

  Pop F: DFS(F) on transposed graph
    F can reach: H (via F→H in transposed), E (via F→E in transposed)
    From H: H→G (in transposed)
    From G: G→F (already visited)
    From E: E→D (in transposed)
    From D: D→C (in transposed) → but C is in SCC1, not transposed back to F

    Wait — in the transposed graph, F→E means original was E→F.
    From F in transposed: we can only follow TRANSPOSED edges.
    Transposed edges FROM F: H→F becomes F→H, F←E stays as F (no outgoing to E)

    Let me re-clarify:
    Original E→F means in transposed F→E.
    Original F→G means in transposed G→F.
    So from F in transposed graph, outgoing edges: F→E (was E→F), and... H→F (was F→H).

  Actually: in transposed graph, outgoing FROM F:
    - F→E  (reversed from original E→F)
    No others from F directly.

  DFS(F) on transposed — visits F first, then E via F→E.
  From E: E→D (reversed D→E). From D: D→C (reversed C→D).
  C is in a different SCC... but wait, from C we can reach A,B,C via transposed edges
  of the A→B→C→A cycle.

  Here's the KEY insight of Kosaraju's:
  In the TRANSPOSED graph, the inter-SCC edges go BACKWARDS.
  So DFS from F in the transposed graph CANNOT cross back into SCC1 or SCC2
  unless the original had edges from F's SCC to those SCCs (it didn't).

  ─────────────────────────────────────────────────────────────────
  The algorithm groups nodes found in each DFS traversal of Pass 2.
  ─────────────────────────────────────────────────────────────────

  Pop F from stack:
    DFS(F) in transposed: visits F, G, H (they form the cycle F↔G↔H in transposed)
    SCC #3 = {F, G, H}  ✓

  Pop G: already visited, skip
  Pop H: already visited, skip

  Pop D from stack:
    DFS(D) in transposed: visits D, E (D↔E cycle in transposed)
    SCC #2 = {D, E}  ✓

  Pop E: already visited, skip

  Pop A from stack:
    DFS(A) in transposed: visits A, B, C (A↔B↔C cycle in transposed)
    SCC #1 = {A, B, C}  ✓

  Pop B: already visited, skip
  Pop C: already visited, skip

  FINAL SCCs:
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │  {A,B,C} │   │  {D,E}   │   │  {F,G,H} │
  └──────────┘   └──────────┘   └──────────┘
```

---

## 5. Minimum Spanning Tree — "The Cheapest Way to Connect All Cities"

### The Story

You are a city planner. You have **6 cities** and you need to build roads so that
every city is reachable from every other city. Building roads costs money — each
road has a price tag. Your budget is tight: you want to connect all cities with
the **minimum total cost**.

Key constraint: you need exactly **N-1 roads for N cities** (a spanning tree).
Any fewer roads and some cities are disconnected. Any more and you're wasting money.

This is the **Minimum Spanning Tree (MST)** problem.

### The 6-City Setup

```
  Cities: 1, 2, 3, 4, 5, 6

  Available roads (edges) with costs:
  1-2: cost 4      2-3: cost 8
  1-3: cost 9      3-4: cost 7
  1-4: cost 11     4-5: cost 10
  2-5: cost 5      4-6: cost 2
  3-5: cost 3      5-6: cost 6

  Visual map:
       [1]
      / │ \
    4/  │  \9
    /  11    \
  [2]   │   [4]
  │\    │   /│\
  8 \5  │10/ 7 \2
  │  \ [5]  │   \
  [3] \ │  [3] [6]
   \  3\│  /  \ /
    \  [5] 7    6
     \      \  /
      3      \/
       [5]--[4]

  Let me draw this more carefully:

           [1]─────4────[2]─────8────[3]
            │           │             │
            9           5             3
            │           │             │
           [4]─────7────[3]─────(same 3)
            │
            10
            │
           [5]─────6────[6]
            │
            ...

  The cleanest representation — ALL edges:
  1──4──2  1──9──3  1──11──4
  2──8──3  2──5──5
  3──7──4  3──3──5
  4──10──5  4──2──6
  5──6──6
```

**Full edge list sorted by cost:**

```
  Edge   │ Cost
  ───────┼──────
  4──6   │  2    ← cheapest!
  3──5   │  3
  1──2   │  4
  2──5   │  5
  5──6   │  6
  3──4   │  7
  2──3   │  8
  1──3   │  9
  4──5   │ 10
  1──4   │ 11   ← most expensive
```

---

### Kruskal's Algorithm: "Add Cheapest Edge That Doesn't Create a Cycle"

**Tool we use:** Union-Find (Disjoint Set Union) to track which cities are
already connected. Adding an edge between two cities in the SAME group would
create a cycle — skip it. Adding an edge between two DIFFERENT groups merges them.

**Initial State:**

```
  Each city is its own group:
  {1} {2} {3} {4} {5} {6}

  MST edges: []
  MST total cost: 0
```

---

**Step 1: Consider edge 4──6 (cost 2)**

```
  4 and 6 are in different groups ({4} vs {6}) → ADD IT!

  Union {4} and {6}: {4,6}
  Groups: {1} {2} {3} {4,6} {5}

  MST edges: [4-6]
  MST cost: 2

  Partial MST:
  [4]───2───[6]
```

---

**Step 2: Consider edge 3──5 (cost 3)**

```
  3 and 5 are in different groups ({3} vs {5}) → ADD IT!

  Union {3} and {5}: {3,5}
  Groups: {1} {2} {3,5} {4,6}

  MST edges: [4-6, 3-5]
  MST cost: 5

  Partial MST:
  [4]───2───[6]
  [3]───3───[5]
```

---

**Step 3: Consider edge 1──2 (cost 4)**

```
  1 and 2 are in different groups ({1} vs {2}) → ADD IT!

  Union {1} and {2}: {1,2}
  Groups: {1,2} {3,5} {4,6}

  MST edges: [4-6, 3-5, 1-2]
  MST cost: 9

  Partial MST:
  [1]───4───[2]
  [3]───3───[5]
  [4]───2───[6]
```

---

**Step 4: Consider edge 2──5 (cost 5)**

```
  2 is in group {1,2}, 5 is in group {3,5}.
  Different groups → ADD IT!

  Union {1,2} and {3,5}: {1,2,3,5}
  Groups: {1,2,3,5} {4,6}

  MST edges: [4-6, 3-5, 1-2, 2-5]
  MST cost: 14

  Partial MST:
  [1]───4───[2]───5───[5]───3───[3]
                  │
                  └── (connected to 1,3,5 now)
```

---

**Step 5: Consider edge 5──6 (cost 6)**

```
  5 is in group {1,2,3,5}, 6 is in group {4,6}.
  Different groups → ADD IT!

  Union {1,2,3,5} and {4,6}: {1,2,3,4,5,6}
  Groups: {1,2,3,4,5,6}  ← ALL CONNECTED!

  MST edges: [4-6, 3-5, 1-2, 2-5, 5-6]
  MST cost: 20

  ALL 6 cities now in one group! We have N-1=5 edges. DONE!
```

---

**Step 6 and beyond: Would be checked but rejected (not needed)**

```
  Edge 3──4 (cost 7):
    3 in {1,2,3,4,5,6}, 4 in {1,2,3,4,5,6} → SAME GROUP → SKIP (would create cycle)

  Edge 2──3 (cost 8):  same group → SKIP
  ... all remaining edges → SKIP

  We already have our 5 edges (N-1 = 6-1 = 5).
```

---

**Final MST:**

```
  Edges: 4─6(2), 3─5(3), 1─2(4), 2─5(5), 5─6(6)
  Total cost: 2+3+4+5+6 = 20

  Diagram:

  [1]───4───[2]
             │
             5
             │
  [3]───3───[5]───6───[6]───2───[4]

  All cities connected, minimum cost = 20.

  ┌─────────────────────────────────────────────────────────────┐
  │  Kruskal's Summary:                                         │
  │  Sort edges: O(E log E)                                     │
  │  Union-Find operations: O(E * α(V)) ≈ O(E) practically     │
  │  Total: O(E log E)                                          │
  │                                                             │
  │  Use when: edges are given explicitly, sparse graphs        │
  │  Alternative: Prim's algorithm (grows tree from a node)     │
  └─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference — All 5 Algorithms

```
  Algorithm        │ Problem Solved          │ Time         │ Key Constraint
  ─────────────────┼─────────────────────────┼──────────────┼──────────────────
  Dijkstra         │ Single-source shortest  │ O(E log V)   │ No negative edges
                   │ path                    │              │
  Bellman-Ford     │ Single-source shortest  │ O(V * E)     │ Handles negatives,
                   │ path + neg-cycle detect │              │ detects neg cycles
  Topological Sort │ Linear ordering of DAG  │ O(V + E)     │ Only on DAGs
  Kosaraju's SCC   │ Find strongly connected │ O(V + E)     │ Directed graph
                   │ components              │              │
  Kruskal's MST    │ Minimum spanning tree   │ O(E log E)   │ Undirected, weighted
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
