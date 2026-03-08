# Uber — Full System Design Walkthrough

> It is 11:43 PM on a Friday in downtown San Francisco. A rider unlocks her phone and taps "Request UberX."
> In the next two seconds, a server somewhere has found the closest available driver, computed the route,
> calculated surge pricing, sent a push notification, and opened a live WebSocket so she can watch
> that driver icon move toward her in real time.
> That is not one system. It is a dozen systems working in concert under a two-second deadline.

This walkthrough builds Uber's architecture from the ground up — starting with the hardest problem
(matching 15 million trips per day in real time) and adding every layer that makes it work at scale.

---

## 1. The Problem — A Real-Time Marketplace

Uber is fundamentally a two-sided marketplace with hard latency requirements.

On one side: riders who want a car within minutes, not hours. On the other: drivers who need
nearby ride requests delivered to them as soon as those requests exist. Both sides are moving.
Both sides are location-dependent. And the window in which a match has value is measured in seconds,
not minutes.

```
Scale (peak):
  15 million trips per day
  15M / 86,400 sec ≈ 175 trips/second average
  Peak (Friday/Saturday evening): ~600 trips/second

  Active drivers during peak:  ~1,000,000
  Active riders during peak:   ~3,000,000 (browsing + waiting)

  GPS updates per second:      250,000   (see section 2)
  Match latency target:        < 2 seconds from tap to driver offer
  ETA accuracy target:         ± 1 minute, 80% of the time
```

Every design decision in this system traces back to one constraint: the match must happen
fast or riders churn. A rider who waits more than 5 seconds for a "driver found" confirmation
starts doubting the app. A rider who sees a spinner for 10 seconds opens Lyft.

---

## 2. Location Updates at Scale

Before you can match a rider to a driver, you need to know where every driver is — right now,
not two minutes ago. Uber solves this by having every active driver app emit a GPS update every
four seconds.

The math is uncomfortable:

```
1,000,000 active drivers
× 1 update every 4 seconds
= 250,000 location writes per second
```

A standard PostgreSQL instance handles roughly 5,000–10,000 writes per second under good conditions.
250,000 writes per second to a relational database would require a cluster of 25–50 Postgres nodes,
all of which need to agree on the current location of every driver. Worse, the schema you would need —
a `driver_locations` table with rows being constantly updated — creates massive write contention on
hot rows. Every driver's row is being updated once every four seconds.

The deeper problem is that location data is not relational data. You never ask "give me all drivers
sorted by name." You ask "give me all drivers within 5 km of this point, sorted by distance." That
is a geospatial query, and relational databases are not optimized for it without significant extensions
and careful indexing.

### Redis GEO Index — The Right Tool

Redis solves both problems with a single data structure: `GEORADIUS` / `GEOADD`, backed by a sorted
set with geohash-encoded scores. Each driver's latitude and longitude are encoded into a 52-bit integer
(a geohash), stored as the score in a sorted set. Proximity queries become a range scan on that sorted
set — O(log N) reads, not full scans.

```
Driver app sends GPS update every 4 seconds:
  GEOADD drivers:live  -122.4194  37.7749  "driver_8821"
  GEOADD drivers:live  -118.2437  34.0522  "driver_4450"
  GEOADD drivers:live  -87.6298   41.8781  "driver_1903"

  Key:   "drivers:live"
  Field: driver_id (string)
  Score: geohash-encoded (lng, lat) — Redis handles the encoding

When a rider requests a trip at (-122.4174, 37.7751):
  GEORADIUS drivers:live  -122.4174  37.7751  5  km  ASC  COUNT 10
  → Returns: ["driver_8821", "driver_4450", ...]   sorted nearest first
```

Redis handles 250,000 `GEOADD` commands per second easily — each is a single sorted set write.
A well-provisioned Redis cluster (10 shards, r6g.2xlarge each) handles this with headroom.

### The TTL Trick — Driver Expiry

A driver who turns off the app, loses signal, or runs out of battery stops sending GPS updates.
Uber cannot keep showing that driver as "online" indefinitely. The clean solution is a separate
expiry key per driver with a rolling TTL:

```
On each GPS update from driver_8821:
  GEOADD drivers:live  -122.4194  37.7749  "driver_8821"
  SET    driver:active:8821  "1"  EX 30      ← expires in 30 seconds

When checking if a driver is available:
  EXISTS driver:active:8821   → 1 = online, 0 = offline (update expired)
```

If no update arrives within 30 seconds, the key expires and the driver is treated as offline.
No cron job. No batch cleanup. Redis TTL handles it automatically.

### Location Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       DRIVER APP                            │
│   GPS sensor → 4-second timer → POST /location             │
│   { driver_id, lat, lng, heading, speed, status }          │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS POST (250K/sec total)
                             ▼
                  ┌──────────────────────┐
                  │    Location Service  │  Stateless, horizontally
                  │    (50 app servers)  │  scaled behind load balancer
                  └──────────┬───────────┘
                             │
              ┌──────────────┼──────────────────┐
              │              │                  │
              ▼              ▼                  ▼
   ┌──────────────────┐  ┌────────┐   ┌─────────────────────┐
   │  Redis Cluster   │  │ Kafka  │   │  Driver Status DB   │
   │  GEOADD live pos │  │ topic: │   │  (Postgres)         │
   │  SET active TTL  │  │ driver │   │  is_on_trip, type,  │
   └──────────────────┘  │ -locs  │   │  vehicle_class      │
                         └────────┘   └─────────────────────┘
```

The Kafka topic `driver-locations` is not for matching (that happens off Redis). It is for
downstream consumers: the trip tracking service, the ETA calculation service, and the ML pipeline
that builds real-time traffic models. More on each of those later.

---

## 3. Matching — Finding the Nearest Driver

The match is the core value proposition of Uber. When a rider taps "Request," the system has
roughly two seconds to find an appropriate driver and present an offer. Here is what happens
in those two seconds.

### Step 1 — Query Redis for Candidates

```
Rider requests UberX at (-122.4174, 37.7751):

1. GEORADIUS drivers:live -122.4174 37.7751  5 km  ASC  COUNT 20
   → Returns: [driver_8821, driver_0033, driver_5512, ...]   (up to 20 nearest)

2. For each driver_id:
   a. EXISTS driver:active:{id}              ← is the driver still online?
   b. GET    driver:status:{id}              ← "available" or "on_trip"?
   c. GET    driver:vehicle_class:{id}       ← "uberx", "uberblack", "xl"?

3. Filter:
   → Remove offline drivers
   → Remove drivers already on a trip
   → Remove drivers with wrong vehicle class
   → Result: ranked candidate list, nearest first
```

### Step 2 — Offer With Timeout

Uber does not send the ride to one driver and wait indefinitely. The driver has 15 seconds to
accept. If they decline or the window expires, the match service moves to the next candidate.

More importantly, Uber sends offers to a small batch of drivers simultaneously — typically 2–3
within the first round — rather than waiting for each individual decision. This dramatically
reduces the time a rider spends waiting when the first driver declines.

```python
def match_rider(rider_request):
    candidates = query_redis_nearby(
        lat=rider_request.lat,
        lng=rider_request.lng,
        radius_km=5,
        vehicle_class=rider_request.vehicle_class,
        limit=20
    )

    if not candidates:
        # Widen search radius and retry
        candidates = query_redis_nearby(..., radius_km=10, limit=20)

    if not candidates:
        return NoDriversAvailable()

    # Send offers in batches of 3, with 15-second timeout per batch
    batch_size = 3
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i : i + batch_size]

        # Send push notification offer to each driver in batch
        for driver_id in batch:
            send_offer(driver_id, rider_request, timeout_sec=15)

        # Wait for first acceptance in this batch
        accepted = wait_for_acceptance(batch, timeout_sec=15)

        if accepted:
            return DriverMatch(driver_id=accepted, trip_id=rider_request.trip_id)

    return NoDriversAvailable()
```

### Why Not Match Centrally in SQL?

A naive design might query a `drivers` table in PostgreSQL:

```sql
-- DO NOT DO THIS at 600 trips/second
SELECT driver_id, ST_Distance(location, rider_point) AS dist
FROM   drivers
WHERE  status = 'available'
  AND  vehicle_class = 'uberx'
  AND  ST_DWithin(location, rider_point, 5000)   -- 5km in meters
ORDER  BY dist
LIMIT  10;
```

This query requires a geospatial index scan across potentially 1 million rows, runs on every
incoming trip request, and competes with constant location update writes. At 600 trips/second,
you are running 600 such queries simultaneously. The PostGIS index would buckle.

Redis GEORADIUS, by contrast, completes in under 1 millisecond against a sorted set of 1 million
entries. It is the right tool precisely because it is doing one thing: answering "who is nearby?"

---

## 4. Real-Time Trip Tracking (WebSockets)

Once the match is made, a new problem begins: the rider wants to watch the driver's icon move
across the map in real time. This is not a request-response interaction. It is a continuous
stream of state that must flow from the driver's phone to the rider's screen with minimal lag.

HTTP polling ("check for new location every 2 seconds") works but wastes bandwidth and adds
latency. Server-Sent Events work but are one-directional. WebSockets are the right answer:
a persistent, full-duplex connection that stays open for the entire trip duration.

A typical Uber trip lasts 5–45 minutes. During that time:
- The driver sends a GPS update every 4 seconds over HTTP
- The rider's WebSocket connection receives a location push ~every 4 seconds
- The rider sees the driver icon move smoothly on the map

### The Full Data Flow

```
┌──────────────┐     HTTP POST /location      ┌────────────────────┐
│  Driver App  │ ─────────────────────────── ▶│  Location Service  │
└──────────────┘   (every 4 seconds)          └────────┬───────────┘
                                                       │  Publish
                                                       ▼
                                              ┌─────────────────────┐
                                              │  Kafka              │
                                              │  topic:             │
                                              │  driver-locations   │
                                              └────────┬────────────┘
                                                       │  Consume
                                                       ▼
                                              ┌─────────────────────┐
                                              │  Trip Consumer      │
                                              │  (stateless worker) │
                                              │                     │
                                              │  Looks up: which    │
                                              │  rider is on a trip │
                                              │  with this driver?  │
                                              └────────┬────────────┘
                                                       │  Publish
                                                       ▼
                                              ┌─────────────────────┐
                                              │  Redis Pub/Sub      │
                                              │  channel:           │
                                              │  trip:{trip_id}     │
                                              └────────┬────────────┘
                                                       │  Subscribe
                                                       ▼
                                              ┌─────────────────────┐
                                              │  WebSocket Server   │
                                              │  (holds open conn   │
                                              │  to Rider App)      │
                                              └────────┬────────────┘
                                                       │  WebSocket push
                                                       ▼
                                              ┌─────────────────────┐
                                              │  Rider App          │
                                              │  (map updates live) │
                                              └─────────────────────┘
```

### Scaling WebSocket Connections

A single WebSocket server process can hold roughly 50,000–100,000 open connections before
memory and file descriptor limits become binding. At peak, Uber has ~600 active trips per second
× average 15-minute duration ≈ 540,000 concurrent active trips. That requires at least 6–10
WebSocket server processes.

The challenge: a rider's WebSocket connection lives on a specific server process. When a
driver location update arrives (via Kafka → Trip Consumer → Redis Pub/Sub), it must reach
the right server. Redis Pub/Sub makes this clean:

```
Each WebSocket server subscribes to Redis channels for the trips it is hosting:
  SUBSCRIBE trip:abc123  trip:def456  trip:ghi789  ...

When a trip consumer publishes a location update:
  PUBLISH trip:abc123  {"lat": 37.7749, "lng": -122.4194, "heading": 270}

Redis delivers the message to whichever WebSocket server subscribed to that channel.
That server pushes the update over the open WebSocket to the rider.

No sticky sessions required. No coordination between WebSocket servers.
Redis handles the fan-out.
```

---

## 5. Surge Pricing

Surge pricing is how Uber balances supply and demand in real time. When more riders want
cars than there are available drivers, prices rise — which incentivises more drivers to come
online and some riders to wait. It is straightforward economics, but the engineering to make
it work at city scale is not.

### H3 Hex Grids

Uber's open-source H3 library divides the Earth's surface into hexagonal cells at multiple
resolutions. Resolution 8 cells are approximately 0.73 km² each — roughly 1 km across.
Every city is covered by a grid of these cells, and each cell independently tracks its own
supply/demand balance.

Why hexagons instead of squares? Hexagons have uniform distance from center to any edge.
In a square grid, the corner-to-center distance is 41% longer than the edge-to-center distance,
which creates distortions in proximity calculations. Hexagons eliminate this.

```
City divided into H3 resolution-8 cells:

     ___       ___       ___
    /   \     /   \     /   \
   / A1  \___/ B2  \___/ C3  \
   \     /   \     /   \     /
    \___/ A2  \___/ B3  \___/
    /   \     /   \     /   \
   / A3  \___/ B4  \___/ C5  \
   \     /   \     /   \     /
    \___/     \___/     \___/

Each cell tracks (every 5 minutes):
  supply  = count of available drivers inside the cell
  demand  = count of open ride requests inside the cell
  ratio   = demand / supply
  surge   = surge_multiplier(ratio)
```

### Surge Multiplier Calculation

```
surge_multiplier(ratio):
  ratio < 0.5:    1.0x   (oversupply — cheap)
  ratio 0.5–1.0:  1.0x   (balanced)
  ratio 1.0–1.5:  1.2x
  ratio 1.5–2.0:  1.5x
  ratio 2.0–2.5:  1.8x
  ratio 2.5–3.0:  2.1x
  ratio > 3.0:    2.5x   (capped — Uber caps multipliers in most markets)

  Smoothed to avoid jarring jumps:
    new_multiplier = 0.7 * old_multiplier + 0.3 * computed_multiplier
    (exponential moving average — avoids flicker)
```

### Caching Surge Per Cell

Surge is recomputed every 5 minutes, per cell. The result is cached in Redis:

```
After computing surge for all cells in San Francisco:
  SET surge:cell:8828308281fffff  "1.8"  EX 300    ← expires in 5 minutes
  SET surge:cell:882830828dfffff  "1.0"  EX 300
  ...

When a rider requests a trip from cell 8828308281fffff:
  GET surge:cell:8828308281fffff  → "1.8"
  Display "1.8x surge — prices are higher due to demand"
```

The surge computation job is a Spark or Flink batch that reads the last 5 minutes of
driver GPS traces and ride requests from Kafka, counts supply and demand per cell using
H3's indexing functions, and writes results to Redis. It runs on a 5-minute cron.

---

## 6. Trip State Machine

Every trip is a state machine. The state transitions are not just a UX concern — they are
a correctness constraint. A trip that jumps from "requested" directly to "completed" is a
billing error. A trip that goes from "in_progress" back to "driver_assigned" is a data
integrity failure.

```
                   ┌───────────────────────────────────────────────────┐
                   │                  TRIP STATES                       │
                   │                                                    │
                   │  requested ──▶ driver_assigned ──▶ driver_arrived │
                   │                                           │        │
                   │                                           ▼        │
                   │                                      in_progress   │
                   │                                           │        │
                   │                                           ▼        │
                   │                                       completed    │
                   │                                           │        │
                   │                                           ▼        │
                   │                                  payment_processing│
                   │                                           │        │
                   │                                           ▼        │
                   │                                         paid       │
                   │                                                    │
                   │  Any state ──▶ cancelled  (before driver_arrived) │
                   └───────────────────────────────────────────────────┘
```

### Enforcing Valid Transitions

The state machine is enforced in the Trip Service before any database write:

```python
VALID_TRANSITIONS = {
    "requested":          {"driver_assigned", "cancelled"},
    "driver_assigned":    {"driver_arrived",  "cancelled"},
    "driver_arrived":     {"in_progress",     "cancelled"},
    "in_progress":        {"completed"},
    "completed":          {"payment_processing"},
    "payment_processing": {"paid", "payment_failed"},
    "payment_failed":     {"payment_processing"},   # retry allowed
    "paid":               set(),                    # terminal
    "cancelled":          set(),                    # terminal
}

def transition(trip_id: str, new_state: str) -> None:
    trip = db.get_trip(trip_id)  # SELECT ... FOR UPDATE (pessimistic lock)
    current = trip.state

    if new_state not in VALID_TRANSITIONS[current]:
        raise InvalidTransitionError(
            f"Cannot transition from {current} to {new_state}"
        )

    trip.state = new_state
    trip.updated_at = now()
    db.save(trip)

    # Emit state change event to Kafka
    kafka.publish("trip-events", {
        "trip_id": trip_id,
        "from_state": current,
        "to_state": new_state,
        "timestamp": now()
    })
```

The `SELECT ... FOR UPDATE` pessimistic lock is intentional. State transitions must be
serialized — two concurrent requests to transition the same trip cannot both succeed.
This is one of the few places in Uber's system where consistency is more important than
throughput, and ACID PostgreSQL guarantees are the right tool.

### State Transition Triggers

```
requested          → driver_assigned    When matching service finds and confirms a driver
driver_assigned    → driver_arrived     When driver taps "Arrived" in driver app
driver_arrived     → in_progress        When driver taps "Start Trip" after rider gets in
in_progress        → completed          When driver taps "End Trip"
completed          → payment_processing Triggered automatically by trip service
payment_processing → paid               When payment processor (Stripe/Braintree) confirms
payment_processing → payment_failed     On card decline or processor timeout
Any                → cancelled          Rider or driver cancels before trip starts
```

---

## 7. ETA Calculation

The ETA shown to a rider is not the straight-line distance divided by some average speed.
That would be meaningless in a city. A driver 1.2 km away in a straight line might be
4 minutes away (through traffic on a direct route) or 12 minutes away (blocked by a river
with only one bridge nearby). Uber needs actual road network routing with real-time traffic.

### The Road Graph

A city's road network is modeled as a directed weighted graph:

```
Nodes:    road intersections
Edges:    road segments connecting intersections
Weights:  expected travel time for each segment (seconds)

        A ──5s──▶ B ──8s──▶ C
        │                   │
        3s                 12s
        │                   │
        ▼                   ▼
        D ──────────────▶  E

ETA from A to E:
  Path A→B→C→E:  5 + 8 + 12 = 25 seconds
  Path A→D→E:    3 + (direct, but longer road) = depends on edge weight
```

Uber uses a variant of Dijkstra's algorithm with precomputed contraction hierarchies
(a technique from academic routing research) to answer shortest-path queries in milliseconds
even on city-scale graphs with millions of nodes.

### Real-Time Traffic Weights from GPS Probes

Here is the part that makes Uber's ETA uniquely good: every active driver is a moving sensor.
Their GPS traces reveal actual travel speeds on every road segment in real time.

```
Data pipeline:
  1. All drivers emit GPS location every 4 seconds → Kafka topic "driver-locations"
  2. Traffic Model Service consumes this stream
  3. For each driver: map GPS coordinates to the nearest road segment (map matching)
  4. Compute speed on that segment from consecutive GPS points:
       speed = distance(point_t, point_t+4) / 4 seconds
  5. Update the edge weight for that segment in the road graph:
       new_weight = 0.8 * old_weight + 0.2 * observed_travel_time
       (exponential moving average — dampens noise, tracks trends)

Result:
  Road graph weights reflect actual current traffic.
  A highway that is normally 60 seconds to traverse but has an accident
  starts showing 180-second weights within minutes as driver speeds drop.
```

### Historical + ML for Predictions

Real-time data gives you current conditions. But ETA also benefits from historical patterns
(rush hour on Monday morning is predictably bad on I-280 southbound):

```
ML model inputs:
  - Current edge weights (real-time traffic)
  - Time of day
  - Day of week
  - Historical travel times for this segment at this time
  - Weather conditions (rain slows traffic 15–20%)
  - Local events (Giants game ends → downtown grid locks)

Output:
  Predicted travel time per edge for the next 15 minutes.

Result:
  ETA that accounts for where traffic is going, not just where it is.
  Accuracy: ± 1 minute for 80% of trips.
```

---

## 8. The Database Architecture

Different data has different requirements. Uber uses a polyglot persistence strategy — each
storage system is chosen for what it does best.

### PostgreSQL — The Source of Truth

Trip records, user profiles, and payment data all live in PostgreSQL. These require ACID
guarantees: a trip record that is written must be written atomically, a payment that is
processed must not be double-counted, a user's account must be consistent.

```sql
-- Trip table (PostgreSQL)
CREATE TABLE trips (
    trip_id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    rider_id         BIGINT      NOT NULL REFERENCES users(user_id),
    driver_id        BIGINT      NOT NULL REFERENCES drivers(driver_id),
    state            VARCHAR(30) NOT NULL DEFAULT 'requested',
    vehicle_class    VARCHAR(20) NOT NULL,
    origin_lat       DECIMAL(10,7),
    origin_lng       DECIMAL(10,7),
    dest_lat         DECIMAL(10,7),
    dest_lng         DECIMAL(10,7),
    surge_multiplier DECIMAL(4,2) NOT NULL DEFAULT 1.0,
    estimated_fare   DECIMAL(10,2),
    actual_fare      DECIMAL(10,2),
    requested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at       TIMESTAMPTZ,
    completed_at     TIMESTAMPTZ,
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for driver's trip history
CREATE INDEX idx_trips_driver_id ON trips(driver_id, requested_at DESC);
-- Index for rider's trip history
CREATE INDEX idx_trips_rider_id  ON trips(rider_id,  requested_at DESC);
```

### Redis — The Operational Cache

Redis handles everything that must be fast and does not need permanent storage:

```
Key pattern                   Value                    TTL      Purpose
─────────────────────────────────────────────────────────────────────────────
drivers:live                  GEO sorted set           none     All live driver positions
driver:active:{driver_id}     "1"                      30s      Online heartbeat
driver:status:{driver_id}     "available"/"on_trip"    30s      Availability
driver:vehicle:{driver_id}    "uberx"/"xl"/"black"     1h       Vehicle class
surge:cell:{h3_index}         "1.8"                    5min     Surge per cell
trip:state:{trip_id}          "in_progress"            24h      Fast state reads
session:{token}               user_id                  24h      Auth sessions
```

### Kafka — The Event Backbone

Kafka decouples the high-volume write streams from the services that consume them.
Nothing blocks on a Kafka write — it is fire-and-forget from the producer's perspective,
with guaranteed at-least-once delivery to consumers.

```
Topic                  Producers              Consumers
─────────────────────────────────────────────────────────────────────────────────
driver-locations       Location Service       Trip Tracking, Traffic Model,
                                              ETA Service, Surge Computer

trip-events            Trip Service           Payment Service, Notification Service,
                                              Analytics, Driver Rating

payment-events         Payment Service        Trip Service (update state),
                                              Finance reporting

rider-requests         API Gateway            Matching Service
```

### S3 / Data Warehouse — The Long-Term Store

Raw GPS traces, trip logs, and pricing events are written to S3 indefinitely.
This data feeds:
- ML model training (ETA prediction, surge forecasting, fraud detection)
- Business analytics (Hive/Spark queries on historical trip data)
- Regulatory compliance (keep records of trips for minimum 7 years in many jurisdictions)

```
S3 layout:
  s3://uber-data/gps-traces/year=2025/month=03/day=08/hour=22/
  s3://uber-data/trips/year=2025/month=03/day=08/
  s3://uber-data/payments/year=2025/month=03/

Partitioned by time for efficient range queries.
Parquet format for columnar compression (typically 10:1 reduction vs raw JSON).
```

### Full Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           INBOUND TRAFFIC                                   │
│      Driver App (GPS)         Rider App (requests, trip events)            │
└───────────┬────────────────────────────────┬───────────────────────────────┘
            │                                │
            ▼                                ▼
  ┌─────────────────┐               ┌─────────────────┐
  │ Location Service│               │   Trip Service  │
  │ (stateless)     │               │   (stateless)   │
  └────────┬────────┘               └────────┬────────┘
           │                                 │
     ┌─────┼────────────────┐         ┌──────┴──────┐
     │     │                │         │             │
     ▼     ▼                ▼         ▼             ▼
  Redis   Kafka           Redis    Postgres       Kafka
  GEO   "driver-          active   (trips,      "trip-
  index  locations"       TTL      users,        events"
                                   payments)
                                                  │
         ┌────────────────────────────────────────┤
         │                          │             │
         ▼                          ▼             ▼
  ┌─────────────┐          ┌──────────────┐  ┌──────────────┐
  │ Trip Tracker│          │  Matching    │  │  Notification│
  │ (WebSocket) │          │  Service     │  │  Service     │
  └──────┬──────┘          └──────┬───────┘  └──────────────┘
         │                        │
         ▼                        ▼
  Redis Pub/Sub            Driver Push (APNs/FCM)
  → Rider App              "New ride request nearby"
```

---

## 9. Key Numbers

These numbers ground the design and signal engineering maturity in an interview.

```
Throughput:
  Trips per day:              15,000,000
  Average trips per second:   15M / 86,400 ≈ 175
  Peak trips per second:      ~600  (Friday/Saturday evening)
  Active drivers (peak):      1,000,000
  GPS writes per second:      250,000  (1M drivers × 1 update/4s)
  WebSocket connections (peak): ~540,000  (600 trips/sec × 15 min avg)

Latency targets:
  Rider tap → driver offer:   < 2 seconds
  GPS update → Redis write:   < 10 ms
  GEORADIUS query (1M points): < 1 ms
  ETA calculation:            < 200 ms
  Trip state transition:      < 100 ms (Postgres write + Kafka publish)

Storage:
  Trip records (PostgreSQL):
    175 trips/sec × 86,400 sec × 1 KB/trip = ~15 GB/day
    Retain indefinitely (regulatory) → ~5 TB/year
  GPS traces (S3, Parquet):
    1M drivers × 15 updates/min × 60 min × 24h × ~50 bytes ≈ 650 GB/day
    After Parquet compression (~10:1): ~65 GB/day → ~23 TB/year
  Redis driver locations:
    1M drivers × ~100 bytes geohash entry = ~100 MB  (trivial)

ETA accuracy:
  Target: ± 1 minute for 80% of trips
  Achieved via: real-time traffic weights + ML historical model
  Degrades to ±3 min during severe weather or major incidents

Surge computation:
  San Francisco: ~2,000 H3 cells at resolution 8
  Computation time: < 10 seconds per 5-minute window (Spark job)
  Cache TTL: 5 minutes (aligned with computation window)
```

---

## 10. Interview Summary

When a system design interview asks "Design Uber," the depth of your answer is proportional
to how quickly you can identify and articulate the non-obvious decisions.

Here is each key decision and the one-sentence reason it exists:

```
Decision                              Rationale
────────────────────────────────────  ──────────────────────────────────────────────────────
Redis GEOADD for driver locations     Geospatial sorted set handles 250K writes/sec and
                                      returns proximity-sorted results in < 1 ms.

TTL expiry for driver heartbeat       Rolling 30-second TTL auto-removes offline drivers
                                      without batch cleanup jobs.

Parallel driver offers (batch of 3)   Sending to 3 drivers simultaneously reduces rider
                                      wait time when first driver declines.

WebSocket + Redis Pub/Sub             Persistent connection for smooth map updates; Pub/Sub
                                      routes location events to the correct WS server.

H3 hex grid for surge pricing         Uniform-proximity hexagons eliminate square-grid
                                      distance distortion for per-cell supply/demand.

PostgreSQL for trip state machine     ACID transactions with pessimistic locking prevent
                                      concurrent invalid state transitions.

Kafka between location updates        Decouples 250K writes/sec from downstream consumers;
and downstream consumers              consumers process at their own rate without backpressure.

GPS traces as traffic probes          1M moving drivers provide denser real-time traffic
                                      data than any commercial traffic feed.

Contraction hierarchies for routing   Precomputed road graph shortcuts reduce ETA query
                                      time from seconds to milliseconds.

Polyglot persistence                  Redis (speed), Postgres (consistency), Kafka (scale),
                                      S3 (durability) — each used where it is the best fit.
```

### The Three Things Interviewers Actually Want to See

**First:** That you understand why location data cannot go into a standard SQL database.
The write volume (250K/sec) and query type (geospatial radius) make Redis the only
sensible answer at this scale. If you reach for Postgres with PostGIS immediately, you
will be asked to scale it — and the answer becomes Redis anyway.

**Second:** That you know how to build a real-time event pipeline without creating a
synchronous dependency chain. The path from driver GPS update to rider's map should touch
HTTP → Kafka → consumer → Redis Pub/Sub → WebSocket. Any synchronous call in that chain
becomes a latency bottleneck and a failure mode.

**Third:** That you treat state as a first-class concern. The trip state machine with
enforced transitions is what separates a prototype from a production billing system.
Mention the pessimistic lock on state transitions and explain why optimistic locking
would be wrong here (retry on conflict during "start trip" is not acceptable UX).

---

## 🔁 Navigation

| | |
|---|---|
| ← Previous | [Netflix Streaming](./netflix.md) |
| ➡️ Next | [WhatsApp Messaging](./whatsapp.md) |
| 🏠 Home | [README.md](../README.md) |
