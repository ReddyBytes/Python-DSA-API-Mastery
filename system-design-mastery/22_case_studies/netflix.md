# Netflix — Full System Design Walkthrough

> It is 8:47 PM on a Friday. A family settles onto the couch.
> Someone picks up the remote, opens Netflix, and presses play on a 4K movie.
> The first frame appears in under half a second.
> They have no idea that this simple act touched servers on three continents,
> a custom CDN built into their ISP's datacenter, and a recommendation model
> trained on 250 million viewing histories.
> They just wanted to watch a movie.

This walkthrough builds Netflix from scratch — storage, streaming, personalization,
and the infrastructure that makes it feel instant anywhere on Earth.

---

## 1. The Scale Problem

Netflix has roughly 250 million paying subscribers in 190 countries.
At peak on a Friday evening, Netflix accounts for approximately 15% of all global
downstream internet traffic. No other application on Earth moves as many bytes.

The engineering challenge is not just "store videos and play them."
It is doing that simultaneously for 100 million+ concurrent streams,
with content in 20+ languages, on devices ranging from a 4K OLED television
to a 2015 Android phone on a 3G network in rural India.

```
Scale profile:
  Subscribers:        250 million
  Concurrent streams: 100 million+ at peak
  Content library:    ~15,000 titles
  Languages:          20+ for subtitles and audio tracks
  Global traffic:     ~15% of all internet downstream at peak

  Storage reality:
    One original 4K source file:        50 GB – 100 GB
    One title after transcoding (all variants): ~1 petabyte
    Full library storage estimate:      tens of exabytes

  Startup latency goal: < 500 ms (first frame visible)
  Availability target:  99.99% (52 minutes downtime per year maximum)
  CDN hit rate:         > 95% (most users never reach Netflix's origin)
```

The two fundamentally different problems here are worth separating:

1. **Video delivery** — bytes moving from servers to screens. Solved by CDN strategy and adaptive bitrate streaming. Latency-sensitive and bandwidth-intensive.
2. **Personalization** — deciding *which* 40 thumbnails appear on your homepage out of 15,000 titles. Solved by recommendation models and smart caching. Compute-intensive and data-intensive.

These systems share almost no infrastructure but must work together seamlessly.

---

## 2. The Upload Pipeline — Ingesting a New Title

Before any subscriber can watch a new show, Netflix must prepare it.
A studio delivers a finished film as a raw 4K file. That original might be a 100 GB
ProRes or ARRIRAW master. Netflix cannot serve this directly. A 100 GB file
over a 25 Mbps home connection takes 9 hours to download. Even a 4K stream
should consume no more than 25 Mbps. And a user on mobile should get 360p
at 0.3 Mbps, not fail entirely.

The answer is the transcoding pipeline.

### What Transcoding Produces

For every title, Netflix encodes roughly 120+ variants:

```
Resolutions:  240p, 360p, 480p, 720p, 1080p, 1440p, 2160p (4K)
Codecs:       H.264 (widest device support)
              H.265 / HEVC (50% bandwidth saving over H.264)
              AV1 (20-30% better than H.265, open-source, newer devices)
Bitrates:     Multiple per resolution (e.g., 720p at 1 Mbps and at 2.5 Mbps)
Audio:        5.1 surround, stereo, mono; multiple languages per title
Subtitles:    Stored as separate .vtt files per language

Total variants per title: ~120 video + dozens of audio/subtitle tracks
```

Each variant is a series of short video segments — typically 2 to 4 seconds long.
These segments are the atoms of adaptive streaming.

### The Pipeline Architecture

```
STUDIO
  │
  │  Upload 100 GB source file (ProRes, ARRIRAW, etc.)
  │  via Netflix's secure ingest endpoint
  ▼
┌─────────────────────────────────────────────────────┐
│  INGEST SERVICE                                      │
│  - Validate file integrity (checksum)                │
│  - Extract metadata (frame rate, resolution, codec)  │
│  - Store original in S3-equivalent object storage    │
│  - Publish "new title available" event to queue      │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  WORK QUEUE (e.g., SQS / Kafka)                      │
│  One message per encoding job:                       │
│    { title_id, source_path, target_codec,            │
│      target_resolution, target_bitrate,              │
│      segment_duration_secs: 4 }                      │
└─────────────────────┬───────────────────────────────┘
                      │  (120+ messages per title)
                      ▼
┌─────────────────────────────────────────────────────┐
│  TRANSCODER WORKER FLEET  (auto-scaled EC2/spot)     │
│                                                      │
│  Worker 1: encode 4K AV1 2160p @ 15 Mbps            │
│  Worker 2: encode 1080p H.265 @ 4 Mbps              │
│  Worker 3: encode 720p H.264 @ 2.5 Mbps             │
│  Worker N: encode 240p H.264 @ 0.3 Mbps             │
│  ... (all jobs run in parallel on separate machines) │
│                                                      │
│  Each worker:                                        │
│    1. Pull source from object storage                │
│    2. Run FFmpeg with target parameters              │
│    3. Split output into 4-second segments            │
│    4. Generate segment manifest entries              │
│    5. Upload segments to object storage              │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  OBJECT STORAGE  (S3-equivalent)                     │
│                                                      │
│  /titles/tt12345678/                                 │
│    original/source.mov                               │
│    h264/1080p_4mbps/seg_0001.ts                      │
│    h264/1080p_4mbps/seg_0002.ts                      │
│    h264/720p_2500kbps/seg_0001.ts                    │
│    av1/2160p_15mbps/seg_0001.ts                      │
│    manifest.m3u8      ← master manifest              │
│    subtitles/en.vtt                                  │
│    subtitles/es.vtt                                  │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  CDN PROPAGATION                                     │
│  - Manifest files pushed to all CDN nodes            │
│  - Popular title segments pre-positioned to edge     │
│  - Less-popular segments served on-demand (lazy)     │
└─────────────────────────────────────────────────────┘
```

A new blockbuster title might take 6-12 hours of cloud compute time to fully transcode
all 120+ variants, but because the jobs run in parallel across hundreds of spot
instances, wall-clock time is usually under 2 hours.

**Why use spot/preemptible instances for transcoding?**
Transcoding is embarrassingly parallel and fault-tolerant. If a spot instance is
reclaimed mid-job, the worker simply re-queues its segment. The cost savings
(60-90% cheaper than on-demand) make this a clear win for an operation Netflix
runs thousands of times per day.

---

## 3. Adaptive Bitrate Streaming (ABR)

This is the mechanism that makes Netflix work equally well on a 4K television
and a phone on a patchy WiFi connection. Understanding it deeply separates
a surface-level answer from a senior-level one.

### The Core Idea

The client (TV app, browser, mobile app) does not download a video file.
It downloads a *manifest* — a text file describing available quality levels
and where to find each 4-second segment. The client then requests segments
one at a time, choosing quality based on its current download speed measurement.

If your network drops from 20 Mbps to 2 Mbps, the next segment request
fetches a lower-quality version. The transition is seamless. No buffering spinner.
No error message. The picture just quietly becomes slightly less sharp for a few
seconds while your network recovers.

### The Manifest File (HLS format, simplified)

```
#EXTM3U
#EXT-X-VERSION:6

# Master manifest — lists all available quality levels
# Served from: https://open.cdn.netflix.com/tt12345678/manifest.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=400000,RESOLUTION=426x240,CODECS="avc1.42c00c"
240p_400kbps/playlist.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360,CODECS="avc1.42c01e"
360p_800kbps/playlist.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720,CODECS="avc1.4d401f"
720p_2500kbps/playlist.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=8000000,RESOLUTION=1920x1080,CODECS="hvc1.1.6.L120"
1080p_8000kbps_h265/playlist.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=16000000,RESOLUTION=3840x2160,CODECS="av01.0.13M.08"
2160p_16000kbps_av1/playlist.m3u8

#EXT-X-MEDIA:TYPE=SUBTITLES,URI="subtitles/en.m3u8",LANGUAGE="en",NAME="English"
#EXT-X-MEDIA:TYPE=SUBTITLES,URI="subtitles/es.m3u8",LANGUAGE="es",NAME="Español"
```

When the client selects a quality level (e.g., 1080p H.265), it fetches the
quality-specific playlist:

```
# 1080p_8000kbps_h265/playlist.m3u8
#EXTM3U
#EXT-X-VERSION:6
#EXT-X-TARGETDURATION:4

#EXTINF:4.000,
seg_0001.ts
#EXTINF:4.000,
seg_0002.ts
#EXTINF:4.000,
seg_0003.ts
...
#EXTINF:3.820,
seg_1847.ts   ← end of 2-hour film
#EXT-X-ENDLIST
```

The client downloads segments in sequence, building a 30-second buffer ahead
of playback. The ABR algorithm watches download speed for each segment:

```python
# Simplified ABR algorithm (runs in the client player)

def select_next_segment_quality(bandwidth_samples, buffer_level_secs):
    estimated_bandwidth = moving_average(bandwidth_samples, window=5)

    # Safety margin: only use 80% of estimated bandwidth
    # to avoid rebuffering if network fluctuates
    safe_bandwidth = estimated_bandwidth * 0.8

    # Pick the highest quality that fits within safe bandwidth
    best_quality = quality_levels[0]  # start at lowest
    for quality in quality_levels:
        if quality.bandwidth <= safe_bandwidth:
            best_quality = quality

    # Emergency downgrade: if buffer is draining, drop quality fast
    if buffer_level_secs < 10:
        best_quality = quality_levels[0]  # drop to minimum immediately

    return best_quality
```

### Why 4-Second Segments?

The segment duration is a deliberate trade-off.

Shorter segments (1-2 seconds) allow faster quality adaptation — the player can
switch quality levels more often. But shorter segments mean more HTTP requests,
more overhead, and worse compression (video codecs compress better over longer
sequences).

Longer segments (8-10 seconds) compress better and reduce request overhead.
But when your network drops, you are 10 seconds into a high-quality segment
you cannot finish downloading — buffering occurs.

4 seconds is Netflix's empirically chosen sweet spot. It allows quality adaptation
within about 8-12 seconds of a network change while keeping compression efficiency high.

---

## 4. CDN Strategy — Open Connect

This is what separates Netflix's infrastructure from everyone else's.

### The Problem with a Standard CDN

A typical CDN like CloudFront or Akamai consists of edge servers at major internet
exchange points. A user in Kansas City might hit a CDN node in Dallas — better than
hitting an origin in Virginia, but still involving backbone ISP hops.

At Netflix's scale — 100 million concurrent streams each consuming 4+ Mbps —
this still generates enormous amounts of inter-ISP traffic. ISPs pay for this
bandwidth. At peak, Netflix would be responsible for billions of dollars of
ISP transit costs globally. And transit is exactly where congestion happens.

### The Open Connect Solution

Netflix created its own CDN: **Open Connect**. Instead of placing servers at
internet exchange points, Netflix places servers *inside* ISPs — in the same
physical datacenter where the ISP's routers live.

The deal is mutually beneficial:
- ISPs receive the hardware free of charge. Netflix installs and supports it.
- ISPs eliminate enormous amounts of transit cost. Netflix video for their subscribers
  never leaves their network.
- Netflix gets edge nodes as close to users as possible — often just a few router hops away.
- Latency drops from ~30ms to ~2-5ms for video segment requests.

```
WITHOUT OPEN CONNECT:
  User (Kansas City) ─── ISP network ─── ISP's upstream transit ─── CDN node (Dallas)
                     [ISP pays for this bandwidth]
                     [adds 20-30ms latency]

WITH OPEN CONNECT:
  User (Kansas City) ─── ISP network ─── OCA server IN the ISP's datacenter
                     [no transit cost for ISP]
                     [2-5ms latency — same building]
```

An Open Connect Appliance (OCA) is a high-density server with:
- Hundreds of terabytes of flash/SSD storage
- 40-100 Gbps network interfaces
- Standard Linux with Netflix's own caching software

Netflix has thousands of OCAs deployed inside hundreds of ISPs worldwide.
A single large ISP datacenter might host multiple OCAs to handle local peak demand.

### Pre-Positioning — Pushing Content Before It Is Requested

The most sophisticated aspect of Open Connect is **pre-positioning**.

Netflix does not wait for users to request a video before populating the OCAs.
Every night, during off-peak hours (2 AM - 8 AM local time), Netflix runs a
fill process that predicts what content will be popular in the next 24 hours
and pushes it to the relevant OCAs proactively.

```
Nightly fill algorithm (conceptual):

for each_oca in all_ocas:
    region = oca.geographic_region          # e.g., "US-Southwest"
    available_capacity = oca.free_storage

    # Rank titles by predicted popularity in this region
    # Signals: current trending, historical for day-of-week,
    #          recent release schedule, regional preferences
    ranked_titles = predict_regional_popularity(
        region=region,
        date=tomorrow,
        model="gradient_boost_popularity"
    )

    # Fill available capacity with top-ranked content
    # Prioritize: new releases, trending titles, popular evergreen
    bytes_filled = 0
    for title in ranked_titles:
        if bytes_filled + title.size_bytes > available_capacity:
            break
        push_to_oca(oca, title.all_variants)
        bytes_filled += title.size_bytes
```

The result: when a subscriber presses play on a Friday evening, there is a
>95% chance the content is already sitting on an OCA inside their ISP.
Netflix's own origin servers in AWS are almost never involved in playback.

### Full CDN Request Flow

```
                ┌─────────────────────────────────────┐
                │            USER DEVICE               │
                │  Netflix app selects quality,        │
                │  requests segment URL                │
                └───────────────┬─────────────────────┘
                                │ DNS lookup: open.cdn.netflix.com
                                │ Netflix's Anycast DNS returns
                                │ the IP of the nearest OCA
                                ▼
              ┌─────────────────────────────────────────┐
              │     OPEN CONNECT APPLIANCE               │
              │     (inside user's ISP datacenter)       │
              │                                          │
              │  Is the requested segment cached here?   │
              │                                          │
              │  CACHE HIT (>95% of requests):           │
              │    → Return segment bytes directly       │
              │    → 2-5ms latency                       │
              │    → ISP's own bandwidth, no transit     │
              │                                          │
              │  CACHE MISS (<5% of requests):           │
              │    → Fetch from Netflix Origin (AWS)     │
              │    → Cache segment locally               │
              │    → Return to user                      │
              └─────────────────┬───────────────────────┘
                                │ (cache miss path only)
                                ▼
              ┌─────────────────────────────────────────┐
              │     NETFLIX ORIGIN  (AWS S3 + servers)   │
              │     Virginia / Oregon / Dublin           │
              │                                          │
              │  Object storage with all video segments  │
              │  Rarely touched during normal playback   │
              └─────────────────────────────────────────┘
```

The CDN hit rate target is above 95%. In practice, for popular new releases,
hit rates exceed 99.9% because pre-positioning is highly accurate.
For obscure back-catalog titles in small markets, a cache miss is acceptable
because the traffic volume is low.

---

## 5. The Recommendation System

Here is a statistic that changes how you think about Netflix's business:
roughly 80% of content watched on Netflix comes from recommendations on the
homepage. Users do not search for titles. The homepage sells the viewing decision.

This means the recommendation system is not a feature — it is the product.
Getting it wrong costs subscribers.

### The Two-Stage Funnel

Recommending from 15,000 titles to a personalized homepage of ~40 visible cards
in under 500 milliseconds requires a two-stage architecture.

**Stage 1: Candidate Generation (millions → thousands)**

This stage runs offline (or near-real-time), not at request time.
The goal is to reduce the recommendation universe from 15,000 titles to
a few thousand that are worth considering for this user.

Techniques used in parallel:

```
Collaborative filtering:
  "Users with similar taste to you also watched these titles."
  Matrix factorization (ALS) on the user-item interaction matrix.
  Runs as a batch job every few hours.

Content-based filtering:
  "Because you watched Stranger Things, here are other sci-fi/horror titles."
  Uses title metadata embeddings (genre, cast, director, tone).

Trending candidates:
  "Top 10 in your country right now"
  Updated every few hours from real-time stream event counts.

Continue watching:
  Deterministic: titles with >5% watched and <95% watched.
  Trivially generated per user.

Recently released:
  New content the user has not seen.
  Simple recency filter + genre match.
```

Each candidate source produces its list independently.
The union is the candidate set — typically a few thousand titles per user.

**Stage 2: Ranking (thousands → ~40 shown)**

The ranking model scores each candidate against the user's full feature vector.
This is where the heavy ML lives.

```
Input features for ranking model:

User features:
  - Viewing history (last 50 titles watched, encoded as embeddings)
  - Explicit ratings (thumbs up/down — increasingly rare)
  - Time of day (9 PM Friday vs. 7 AM Tuesday suggest different moods)
  - Device type (mobile = shorter content; TV = movie or long episode)
  - Account age and engagement level
  - "Thumb fatigue" indicator: if a user rates everything 5 stars,
    their ratings carry less signal than a selective rater

Item features:
  - Title embeddings (from content + viewing behavior)
  - Popularity in user's region (last 24h stream count)
  - Freshness (days since added to platform)
  - Predicted completion rate for this user type
  - Thumbnail click-through rate (different thumbnails shown to different users)

Context features:
  - Day of week, time of day
  - Whether user has watched in the last 3 days
  - Session length so far

Output:
  Relevance score: float [0.0, 1.0] per (user, title) pair
  The top ~200 titles by score become visible on the homepage rows.
```

### Homepage Row Assembly

The homepage is not one ranked list. It is a collection of named rows, each
computed by a different algorithm:

```
"Continue Watching"        → deterministic, user-specific
"Top 10 in [Country]"      → regional, updated every few hours
"Because You Watched X"    → content-based, per seed title
"Trending Now"             → global popularity signal
"New Releases"             → recency filter + genre affinity
"For You" / "My List"      → collaborative filtering output
"Award-Winning Films"      → editorial + engagement signal
```

Each row is computed independently by its own service,
cached in Redis per user, and assembled at request time.

### The Event Pipeline Feeding Recommendations

```
User watches an episode
        │
        │ Every 30 seconds: heartbeat event
        ▼
┌─────────────────────────────────────────────────────┐
│  KAFKA  (topic: viewing-events)                      │
│                                                      │
│  { user_id, title_id, episode_id,                    │
│    timestamp, percent_watched,                       │
│    device_type, country }                            │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────┴─────────────────┐
         │                           │
         ▼                           ▼
┌──────────────────┐     ┌────────────────────────────┐
│  REAL-TIME       │     │  BATCH FEATURE PIPELINE     │
│  STREAM PROCESSOR│     │  (Spark, runs every 4h)     │
│  (Flink)         │     │                             │
│                  │     │  - Update user history      │
│  "Top 10" counts │     │  - Retrain collab filter    │
│  Trending signals│     │  - Refresh embeddings       │
│  Session context │     │  - Score all candidates     │
└────────┬─────────┘     └─────────────┬───────────────┘
         │                             │
         ▼                             ▼
┌─────────────────────────────────────────────────────┐
│  REDIS  (ranked recommendation lists per user)       │
│                                                      │
│  Key: "recs:{user_id}:trending"   → [title_ids...]   │
│  Key: "recs:{user_id}:for_you"    → [title_ids...]   │
│  Key: "recs:{user_id}:continue"   → [title_ids...]   │
│  TTL:  30 minutes (refreshed on next pipeline run)   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
              Homepage API reads these lists
              at request time and assembles
              the personalized homepage
```

### Thumbnail Personalization

One underappreciated detail: not everyone sees the same thumbnail for the same title.

Netflix A/B tests which artwork drives higher click-through for different user segments.
A user who watches many romance films might see a title's romantic subplot prominently
featured in the thumbnail. An action fan sees the explosion scene.

This is a separate ML model (artwork personalization) layered on top of the
recommendation system. It explains why two accounts in the same household
sometimes see visually different presentations of the same title.

---

## 6. View Count and Play Events at Scale

When 100 million users are simultaneously streaming, each player sends a heartbeat
event every 10 seconds. The raw numbers:

```
100,000,000 streams
× 1 heartbeat per 10 seconds
= 10,000,000 events per second (10M events/sec)

Each event payload:
  { user_id: 8 bytes, title_id: 8 bytes, timestamp: 8 bytes,
    percent_watched: 4 bytes, quality_level: 2 bytes,
    buffer_events: variable ~ 20 bytes average }

  ~50 bytes per event × 10M/sec = ~500 MB/sec of inbound event data

Per day:
  10M events/sec × 86,400 sec = 864 billion events/day
  At 50 bytes each = ~43 TB of raw event data per day
```

Writing 10 million database rows per second is not feasible with any traditional
relational database. The solution is a three-tier aggregation pipeline:

### Tier 1: Kafka (Ingest Buffer)

All heartbeat events go to Kafka. Kafka provides:
- Buffering against downstream processing slowdowns
- Durability (events are not lost if a consumer falls behind)
- Replay capability (reprocess events after a bug fix)
- Decoupling of producers (player apps) from consumers (analytics, ML, billing)

```
Player Apps  ──── heartbeat ──▶  Kafka  topic: "playback-events"
                                        partitioned by user_id
                                        replication factor: 3
                                        retention: 7 days
```

### Tier 2: Redis (Real-Time Aggregation)

Flink stream processors consume from Kafka and maintain running counters in Redis:

```python
# Conceptual stream processor logic (runs in Flink)

def process_heartbeat_event(event):
    title_id = event["title_id"]
    country  = event["country"]

    # Increment global stream count for this title (last 24h)
    redis.incr(f"stream_count:24h:{title_id}")
    redis.expire(f"stream_count:24h:{title_id}", 86400)

    # Increment country-specific count (for Top 10 lists)
    redis.incr(f"stream_count:24h:{country}:{title_id}")
    redis.expire(f"stream_count:24h:{country}:{title_id}", 86400)

    # Update "currently watching" gauge per title (windowed count)
    # Used to display "X people watching now" on title detail page
    redis.zadd("currently_watching", {title_id: event["timestamp"]})
    # Trim entries older than 5 minutes
    redis.zremrangebyscore(
        "currently_watching",
        0,
        event["timestamp"] - 300
    )
```

The Redis aggregates are what power "Top 10 in your country right now."
These lists are recomputed every few hours by sorting the stream count keys.

### Tier 3: Persistent Storage (Hourly Batch)

The raw Kafka events are aggregated by an hourly Spark job and written to
columnar storage (Parquet on S3 + Spark SQL / Hive). These serve:
- Billing verification (were subscribers watching? Were they charged correctly?)
- Long-term analytics (what content drives retention over 6 months?)
- Model training (the ground truth for recommendation model training)
- Business reporting (viewed hours per title, regional engagement)

```
Design principle:
  The critical path (heartbeat → Kafka) never touches a database.
  Kafka absorbs all write load.
  Redis handles real-time derived views (counts, top lists).
  Persistent DB is updated asynchronously — never blocking playback.
```

---

## 7. The Homepage API — Personalization at Scale

250 million subscribers means 250 million potentially different homepages.
You cannot precompute them all. But you also cannot compute them from scratch
on every request — that would require running ML inference for 15,000 titles
in under 500 milliseconds.

The solution is a *row-based architecture* with aggressive per-row caching.

### Row-Based Decomposition

Rather than computing one monolithic "homepage for user X," the system
decomposes the request into ~10 independent row computations:

```
GET /homepage?user_id=12345
         │
         │ Fan-out to 10+ row services (parallel)
         ▼
┌────────────────────────────────────────────────────────────────────┐
│  Row fetches fire in parallel (all start simultaneously)           │
│                                                                    │
│  ┌─────────────────────┐   ┌─────────────────────┐                │
│  │  Continue Watching  │   │  Top 10 (US)         │                │
│  │  Redis lookup:      │   │  Redis lookup:       │                │
│  │  homepage:12345:    │   │  homepage:12345:     │                │
│  │  continue_watching  │   │  top10_country       │                │
│  │  TTL: 5 minutes     │   │  TTL: 4 hours        │                │
│  └─────────────────────┘   └─────────────────────┘                │
│                                                                    │
│  ┌─────────────────────┐   ┌─────────────────────┐                │
│  │  Because You Watched│   │  New This Week       │                │
│  │  "Stranger Things"  │   │  Redis lookup:       │                │
│  │  Redis lookup:      │   │  homepage:12345:     │                │
│  │  homepage:12345:    │   │  new_releases        │                │
│  │  byw_tt12345        │   │  TTL: 6 hours        │                │
│  │  TTL: 30 minutes    │   │                      │                │
│  └─────────────────────┘   └─────────────────────┘                │
│                                                                    │
│  ... 6 more row types fetched in parallel ...                      │
└────────────────────────────────────────────────────────────────────┘
         │
         │ All rows complete (parallel, ~20-40ms)
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  ASSEMBLY SERVICE                                                 │
│                                                                  │
│  1. Order rows by relevance model output                         │
│     (which row type is most engaging for this user?)             │
│  2. Hydrate title metadata for each card                         │
│     (title name, runtime, rating, artwork URL)                   │
│  3. Select personalized artwork per title (if A/B test active)   │
│  4. Truncate rows to display count (typically 20 per row)        │
│  5. Return serialized JSON response                              │
└──────────────────────────────────────────────────────────────────┘
```

### Cache Key Strategy

```
Redis key format: homepage:{user_id}:{row_type}

Examples:
  homepage:83291057:continue_watching   → TTL: 5 minutes  (changes often)
  homepage:83291057:top10_US            → TTL: 4 hours    (updated infrequently)
  homepage:83291057:for_you             → TTL: 30 minutes (refreshed by ML pipeline)
  homepage:83291057:byw_tt98765432      → TTL: 30 minutes (per seed title)
  homepage:83291057:new_releases        → TTL: 6 hours    (new content drops daily)

Value format (JSON):
  {
    "row_type":   "for_you",
    "row_title":  "Picked For You",
    "items": [
      { "title_id": "tt98765432", "artwork_variant": "B", "score": 0.94 },
      { "title_id": "tt12398765", "artwork_variant": "A", "score": 0.91 },
      ...
    ],
    "generated_at": 1741300000,
    "expires_at":   1741301800
  }
```

### Cache Miss Handling

When a user's row cache is empty (first visit, or TTL expired with no refresh):

```
Cache miss for "for_you" row:
  1. Recommendation service called synchronously
  2. Fetches user's feature vector from feature store
  3. Runs lightweight ranking over pre-computed candidate set
     (full ML inference was already done in the background batch job)
  4. Returns top 100 scored titles within ~50ms
  5. Result written to Redis before response is sent
  6. Subsequent requests in the TTL window hit cache

Note: the heavyweight ML (candidate generation, full model training)
      never runs synchronously on the request path.
      Only lightweight re-ranking does.
```

### Title Hydration — The Second Fan-Out

Row data contains title IDs and scores, not full title objects.
Assembly requires hydrating each title ID into its display metadata.

```python
# Parallel title hydration (conceptual)

async def hydrate_titles(title_ids: list[str]) -> list[TitleMetadata]:
    # Check Redis for each title_id in batch
    cached = await redis.mget([f"title:{tid}" for tid in title_ids])

    results = []
    missing = []
    for title_id, cached_val in zip(title_ids, cached):
        if cached_val:
            results.append(json.loads(cached_val))
        else:
            missing.append(title_id)

    if missing:
        # Fetch from title metadata service (backed by DynamoDB)
        # Batch request — one network call for all missing IDs
        fetched = await title_service.batch_get(missing)
        for title in fetched:
            await redis.setex(f"title:{title.id}", 3600, json.dumps(title))
            results.append(title)

    return results

# Title metadata cache hit rate is typically >99%
# (15,000 titles, each cached for 1 hour, extremely hot dataset)
```

The full homepage request timeline:

```
t=0ms     Request arrives at Homepage API
t=1ms     User session validated (JWT check)
t=2ms     Fan-out: 10 row Redis lookups start in parallel
t=15ms    All row cache hits return (Redis @ <2ms per key)
t=16ms    Title hydration: batch Redis MGET for ~200 title IDs
t=22ms    All title metadata returned from Redis
t=24ms    Artwork variant selection (personalization lookup)
t=28ms    Response assembled and serialized
t=30ms    Response sent to client

Total: ~30ms server-side computation
Network (CDN + TLS): adds 50-200ms depending on geography
Client rendering: 200-400ms
──────────────────────────────────────────────────────────
First frame visible: < 500ms (goal met)
```

---

## 8. Data Numbers — The Full Picture

These numbers tie the architecture together. In an interview, citing specifics
demonstrates you have thought about the system at production scale.

```
STORAGE
────────────────────────────────────────────────────────────────
One title after all transcoding variants:        ~1 petabyte
  (120+ video variants × avg ~8 GB per variant
   + audio tracks + subtitles + thumbnails)

Full library (~15,000 titles) estimate:          ~15 exabytes
  (this is distributed across object storage + OCAs globally)

Kafka event retention (7 days):
  10M events/sec × 86,400 sec/day × 7 days × 50 bytes ≈ 300 TB

Redis (recommendation caches):
  250M users × 10 row types × ~5 KB per row = ~12.5 TB
  Served by a large Redis cluster; hot keys only, LRU eviction

User viewing history (Cassandra / NoSQL):
  250M users × 1,000 titles per history × 50 bytes = ~12.5 TB


THROUGHPUT
────────────────────────────────────────────────────────────────
Playback heartbeat events:       10 million/second (peak)
Homepage API requests:           ~1-2 million/second (peak)
CDN video segment requests:      hundreds of millions/second
  (each 4-sec segment = one HTTPS GET; 100M streams = 25M req/sec)
Kafka ingest rate:               500 MB/sec - 1 GB/sec


LATENCY TARGETS
────────────────────────────────────────────────────────────────
Time to first frame (play button → picture): < 500ms
Video segment request from OCA:              < 5ms
Homepage API response (server-side):         < 50ms
Recommendation cache refresh (background):   < 2 minutes
CDN cache miss + origin fetch:               50-200ms


RELIABILITY
────────────────────────────────────────────────────────────────
Availability target:       99.99% (52 min downtime/year)
CDN hit rate:              > 95% globally; > 99.9% for new releases
Redundancy:                Multi-AZ in AWS; multiple OCA per ISP
Playback success rate:     > 99.9% of play attempts start without error
```

---

## 9. What You Would Say in an Interview

If asked "Design Netflix" in a 45-minute interview, you would not cover everything
above. You scope, you prioritize, you go deep on the interesting problems.

### The 5 Key Design Decisions

```
1. TRANSCODE ONCE, SERVE EVERYWHERE
   Encode every title into 120+ variants at upload time.
   Amortize the cost across all future playbacks.
   Trade: high upfront compute cost, massive storage; gain: instant serve,
   no per-user transcoding.

2. ADAPTIVE BITRATE IS THE RELIABILITY MECHANISM
   Split video into 4-second segments. Client picks quality per segment.
   No single quality level is "the video" — quality is a continuous parameter.
   This is why Netflix rarely shows a buffering spinner.

3. PUT CONTENT INSIDE ISPS (OPEN CONNECT)
   The best CDN is one that bypasses the internet entirely.
   By placing OCAs inside ISPs, Netflix eliminates the last-mile
   congestion point and makes transit costs disappear for ISPs.
   The CDN is a business arrangement as much as a technical one.

4. RECOMMENDATIONS AS A TWO-STAGE FUNNEL
   Never run expensive ML inference on the request path.
   Candidate generation runs offline; light re-ranking runs online.
   Cache the outputs aggressively — most users' recommendations
   do not change minute-to-minute.

5. NEVER WRITE TO A DATABASE DURING PLAYBACK
   The heartbeat event path is: player → Kafka → done.
   No database, no latency spike, no write contention.
   Aggregation happens downstream, asynchronously.
   The critical path does exactly one thing: acknowledge the event.
```

### Common Follow-Up Questions

```
Q: How do you handle a popular new release that is not yet on the OCA?
A: Netflix pre-positions new releases to OCAs before launch as part of the
   scheduled fill. For a major release, this happens 24-48 hours before
   the premiere time. The OCAs do not wait for user demand.

Q: What happens if the Kafka cluster falls behind during peak load?
A: Heartbeat events are not critical for real-time playback — they are
   telemetry. If Kafka lags, the player keeps playing. Events may arrive
   late to the downstream consumers, but playback is never gated on Kafka
   acknowledgment. Redis counters (for "Top 10") might lag a few minutes.

Q: How does the system handle a 100 million subscriber spike — say,
   the finale of a major series?
A: Three mechanisms work together:
   (a) OCAs pre-positioned with the content handle >95% of traffic.
   (b) AWS auto-scaling handles the origin and API tier spike.
   (c) Recommendation caches insulate the ML infrastructure from request spikes.
   Netflix has handled events like this repeatedly and publishes post-mortems.

Q: How does billing work — is it per view or per month?
A: Netflix is subscription-based; billing is not per-play.
   The heartbeat events are used for content licensing compliance
   (some licensing contracts are based on viewed hours per territory)
   and for engineering analytics, not for charging users per play.

Q: How does Netflix prevent account sharing at scale?
A: This is an operational/policy problem as much as a technical one.
   Technically: devices per account limits, IP geolocation checks,
   device fingerprinting, and concurrent stream limits (plan-dependent).
   A concurrent stream limit is enforced by a distributed counter:
   Redis INCR on "active_streams:{account_id}" at play start,
   DECR at stop (or on heartbeat timeout).

Q: Why not use WebRTC for low-latency streaming?
A: WebRTC is optimized for interactive real-time communication (video calls),
   not one-way high-bandwidth streaming. HLS/DASH with ABR is better suited
   for pre-encoded, high-quality, fault-tolerant video delivery.
   Netflix does not need sub-second latency — 2-3 second playback startup
   is the target, with a 30-second buffer maintained during playback.
```

---

## Architecture Summary Diagram

```
  STUDIO
    │ 100 GB source file
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  INGEST & TRANSCODING                                                        │
│  Queue ──▶ Worker Fleet (120+ parallel jobs) ──▶ S3 Object Storage         │
│  Result: 1 petabyte of video segments per title across all variants         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ segments + manifests
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  CDN — OPEN CONNECT                                                          │
│                                                                              │
│  ISP Datacenter A         ISP Datacenter B         ISP Datacenter C         │
│  ┌───────────────┐        ┌───────────────┐        ┌───────────────┐        │
│  │  OCA Node(s)  │        │  OCA Node(s)  │        │  OCA Node(s)  │        │
│  │  Pre-positioned│       │  Pre-positioned│       │  Pre-positioned│       │
│  │  popular titles│       │  popular titles│       │  popular titles│       │
│  └───────┬───────┘        └───────┬───────┘        └───────┬───────┘        │
│          │                        │                        │                 │
│          └──────────── >95% of video segment requests ─────┘                │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │ <5% cache misses only
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NETFLIX ORIGIN  (AWS)                                                       │
│  API Gateway ──▶ Homepage API ──▶ Redis (row caches)                        │
│             ──▶ Playback API  ──▶ License check, manifest serve             │
│             ──▶ Auth Service  ──▶ JWT validation, account state             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                      ┌────────────────┼─────────────────┐
                      ▼                ▼                  ▼
              ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
              │  KAFKA       │  │  REDIS       │  │  CASSANDRA /     │
              │              │  │  CLUSTER     │  │  DYNAMO          │
              │  Playback    │  │              │  │                  │
              │  heartbeats  │  │  Recs cache  │  │  User history    │
              │  View events │  │  Title meta  │  │  Title metadata  │
              │  User actions│  │  Top 10 lists│  │  Account data    │
              └──────┬───────┘  └──────────────┘  └──────────────────┘
                     │
         ┌───────────┼───────────────────┐
         ▼           ▼                   ▼
  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐
  │  FLINK      │ │  SPARK       │ │  ML PLATFORM        │
  │  (real-time)│ │  (batch)     │ │                     │
  │  Stream     │ │  Hourly agg  │ │  Collaborative      │
  │  counts for │ │  to Parquet/ │ │  filtering          │
  │  Top 10     │ │  S3          │ │  Ranking models     │
  │  Trending   │ │  Training    │ │  Artwork A/B        │
  │  signals    │ │  data prep   │ │  → Redis output     │
  └─────────────┘ └──────────────┘ └─────────────────────┘
```

---

## Navigation

| | |
|---|---|
| ← Previous | [Twitter Feed](./twitter.md) |
| ➡️ Next | [Uber Ride-Sharing](./uber.md) |
| 🏠 Home | [README.md](../README.md) |
