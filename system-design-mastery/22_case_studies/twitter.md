# Twitter — Full System Design Walkthrough

> The interviewer says: "Design Twitter."
> Two words. Forty-five minutes. Hundreds of moving parts.
> Where do you start?

This walkthrough builds Twitter's architecture from requirements to a full system diagram —
focusing on the hardest problems: the home timeline, the celebrity problem, and feed delivery at scale.

---

## 1. What We Are Designing — Scope It First

"Design Twitter" is too large for 45 minutes. Scope it immediately.

```
IN scope (core features):
  - Tweet creation:    POST /tweet — create a 280-char tweet, optionally with media
  - Home timeline:     GET /timeline — see tweets from accounts you follow
  - Follower graph:    follow/unfollow a user
  - User search:       find accounts by username
  - Tweet search:      find tweets by keyword or hashtag

OUT of scope (explicitly park these):
  - Direct messages (DM)
  - Twitter Spaces (audio)
  - Ads platform
  - Trending topics algorithm
  - Recommendation ("For You") tab
  - Mobile push notifications (mention briefly, then defer)
```

**Say this out loud in the interview:**
```
"I'll focus on tweet creation, the home timeline, and tweet search.
 These cover the core read/write path and the interesting scaling challenges.
 We can add DMs or recommendations if time allows."
```

---

## 2. Scale — Numbers to Design Around

```
Users:
  300 million monthly active users (MAU)
  100 million daily active users (DAU)

Tweets:
  500 million new tweets per day
  500M / 86,400 sec ≈ 5,800 tweets/second (average)
  Peak: ~3× average = ~17,000 tweets/second

Reads (timeline fetches):
  Read:write ratio = 100:1
  → 580,000 timeline reads/second (average)
  → ~1.7 million reads/second (peak)

Follow graph:
  Average user follows 200 accounts
  Average user has 200 followers
  Celebrity accounts: 10M–80M followers

Media (images/video):
  ~20% of tweets have images  → 100M images/day → ~1,200 images/sec
  ~5% of tweets have video    → 25M videos/day  → ~300 videos/sec

Storage:
  Tweet metadata: 500M × 140 bytes  ≈ 70 GB/day  → 25 TB/year
  Media:          100M images × 200 KB = 20 TB/day
                  25M videos × 5 MB   = 125 TB/day
```

This is a **massively read-heavy** system. The home timeline is the core challenge.

---

## 3. The Core Challenge — The Home Timeline

When you open Twitter, you see a feed of tweets from people you follow.
How do you build that feed efficiently at 580,000 reads per second?

Two fundamentally different approaches exist.

---

### Approach A: Push Model (Fan-out on Write)

When a user tweets, immediately push the tweet ID into every follower's timeline cache.

```
User A (500 followers) tweets:
                                     ┌──▶ Follower 1's feed cache  (append tweet_id)
                                     ├──▶ Follower 2's feed cache  (append tweet_id)
  User A tweets ──▶ Fan-out worker──▶├──▶ Follower 3's feed cache  (append tweet_id)
                                     ├──▶ ...
                                     └──▶ Follower 500's feed cache (append tweet_id)

Read path:
  GET /timeline for User B:
    1. Read User B's feed cache (Redis sorted set)
    2. Fetch tweet content for each tweet_id
    3. Return timeline  ← very fast, pre-computed
```

**Pro:** Timeline reads are instant — data is pre-computed.

**Con:** Write amplification. A celebrity with 80M followers triggers 80M cache writes per tweet. At Beyonce's tweet rate, the fan-out queue catches fire.

---

### Approach B: Pull Model (Fan-out on Read)

Do nothing on write. Compute the timeline at read time.

```
GET /timeline for User B:
  1. Fetch User B's follow list:  [user_1, user_5, user_42, ...]
  2. For each followed user, fetch their recent tweets
  3. Merge + sort by timestamp
  4. Return top 20 results

Data flow:
  User B's follows ──▶ fetch tweets from each user ──▶ merge sort ──▶ return
```

**Pro:** Write path is simple — just store the tweet.

**Con:** Read path is expensive. If you follow 1,000 accounts, timeline generation requires 1,000 DB reads + a merge sort. At 580,000 timeline reads/second, this is catastrophic.

---

### Approach C: Hybrid (what Twitter actually uses)

Use push for most users, pull for celebrities.

```
Define:
  "Normal user"    = fewer than 10,000 followers
  "Celebrity"      = 10,000+ followers (Katy Perry, Elon Musk, etc.)

On tweet creation:
  If author is a normal user:
    → Fan-out to all followers' feed caches  (push model)
       Manageable: 500 followers × 1,000 req/sec = 500K writes/sec (fast, async)

  If author is a celebrity:
    → Store tweet only in author's tweet table  (pull model)
       Skip the fan-out entirely

On timeline read:
  1. Read user's pre-computed feed cache       (contains normal users' tweets)
  2. Fetch followed celebrities' recent tweets  (pull from their tweet tables)
  3. Merge the two sets and sort by timestamp
  4. Return the merged timeline

Result:
  Normal user's tweet lands in your cache instantly.
  Lady Gaga's tweet is fetched on-demand when you load your timeline.
  Lady Gaga's 80M fan-out: avoided entirely.
  Timeline read cost: cheap cache read + ~5 celebrity fetches = manageable.
```

**The celebrity threshold is a tunable parameter — not a hard rule.**

---

## 4. Data Model

### User Table (PostgreSQL — relational, low volume)
```sql
CREATE TABLE users (
    user_id       BIGINT PRIMARY KEY,       -- Snowflake ID
    username      VARCHAR(50)  UNIQUE NOT NULL,
    display_name  VARCHAR(100) NOT NULL,
    bio           VARCHAR(160),
    avatar_url    VARCHAR(512),
    follower_count INT DEFAULT 0,           -- denormalized counter
    following_count INT DEFAULT 0,          -- denormalized counter
    tweet_count   INT DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL,
    is_verified   BOOLEAN DEFAULT false,
    is_celebrity  BOOLEAN DEFAULT false     -- fan-out optimization flag
);
```

### Tweet Table (Cassandra / DynamoDB — high write volume)
```
Table: tweets
  PK:  tweet_id  (Snowflake ID — sortable by time, globally unique)
  Attributes:
    user_id       BIGINT        who wrote it
    content       VARCHAR(280)  tweet text
    media_urls    LIST<STRING>  S3 URLs for images/video
    reply_to_id   BIGINT        NULL if original tweet
    retweet_of_id BIGINT        NULL if original tweet
    like_count    INT           eventually consistent counter
    retweet_count INT           eventually consistent counter
    created_at    TIMESTAMP

Partition strategy (Cassandra):
  Partition key: user_id
  Cluster key:   tweet_id DESC  (newest first within a user's tweets)

  → Fetching a user's recent tweets = single partition scan
  → Extremely fast for timeline construction
```

### Follow Table (Cassandra — high read volume, graph queries)
```
Table: follows
  PK:    (follower_id, followee_id)  — "does A follow B?"

Table: user_followers
  PK:    followee_id
  Sort:  follower_id
  → "who follows this user?" (fan-out target list)

Table: user_following
  PK:    follower_id
  Sort:  followee_id
  → "who does this user follow?" (timeline construction)
```

### Feed Table (Redis — pre-computed timeline cache)
```
Redis Sorted Set per user:
  Key:    "feed:{user_id}"
  Member: tweet_id
  Score:  timestamp (epoch ms) — sorts newest first

Example:
  ZADD feed:12345 1709900123456 "tweet_99887"
  ZADD feed:12345 1709899100000 "tweet_99234"

  ZREVRANGE feed:12345 0 19    → top 20 tweet IDs (newest first)

  Max size: keep last 1,000 tweet IDs per user
  If > 1,000: ZREMRANGEBYRANK to trim oldest entries

Memory:
  100M active users × 1,000 tweet IDs × 8 bytes = 800 GB
  Use Redis Cluster: 10 nodes × 80 GB each = feasible
```

---

## 5. The Timeline Service — Deep Dive

```
GET /v1/timeline?user_id=12345&cursor=<last_tweet_id>

Timeline Service:

Step 1: Get user's feed from Redis
        tweet_ids = ZREVRANGE "feed:12345" 0 49  (fetch 50 IDs)
        → ["tweet_99887", "tweet_99234", "tweet_98001", ...]

Step 2: Hydrate tweets
        MGET tweets:99887 tweets:99234 tweets:98001 ...
        (Redis also caches hot tweet objects by tweet_id)
        Cache miss → fetch from Cassandra in parallel (async fan-out)

Step 3: Fetch celebrity tweets (pull model)
        celebrity_ids = get_followed_celebrities(user_id=12345)
        → [katy_perry_id, elonmusk_id]
        For each celebrity:
          latest_tweets = Cassandra.get("tweets by {celebrity_id} LIMIT 10")

Step 4: Merge and rank
        merged = merge_sort(cached_feed, celebrity_tweets)
        → sort by created_at DESC
        → deduplicate retweets
        → apply basic quality filter (spam scores, blocked users)
        → take top 20

Step 5: Cursor pagination
        Return last tweet_id as cursor for next page
        Next request: GET /timeline?cursor=tweet_98001
          → Redis: ZREVRANGEBYSCORE "feed:12345" (tweet_98001_score) -inf LIMIT 50

Step 6: Cache the hydrated result briefly
        Store fully hydrated timeline in Redis for 30 seconds.
        Rapid refreshers (pull-to-refresh spammers) hit cache, not DB.
```

---

## 6. The Celebrity Problem

This deserves its own section. It is the most common Twitter deep-dive.

```
Lady Gaga: 80 million followers
She tweets at 2 AM.

Fan-out on write (naive approach):
  80,000,000 Redis ZADD operations
  At 100,000 writes/second → 800 seconds = 13 minutes to complete fan-out
  The tweet appears in followers' feeds up to 13 minutes late.
  This is unacceptable.

Real-world data point:
  Twitter's 2013 Superbowl outage was partly caused by
  Beyonce fan-out storms. This exact problem.

The hybrid fix:
  Celebrities skip the fan-out entirely.
  Their tweets are fetched on-demand at timeline read time.

  Cost of celebrity pull:
    User follows 5 celebrities on average.
    5 Cassandra reads per timeline request.
    At 580,000 reads/sec: 2.9M Cassandra reads/sec from celebrity tweets alone.
    These reads are on hot partitions → cache them heavily.

  Celebrity tweet cache:
    Redis: "celeb_tweets:{celebrity_id}" → last 100 tweet IDs
    TTL: 60 seconds (celebrity tweets change infrequently)
    At 10,000 celebrities × 100 tweet IDs × 8 bytes = 8 MB → trivial

Celebrity threshold management:
  Run a daily job:
    SELECT user_id FROM users WHERE follower_count > 10000
    UPDATE users SET is_celebrity = true WHERE user_id = ...

  Fan-out service checks is_celebrity flag before deciding push vs pull.
  Threshold is configurable — tune based on fan-out queue depth metrics.
```

---

## 7. Tweet Storage — Metadata vs Media

```
Tweet metadata:
  Fast writes, key-value access, time-series queries.
  → Cassandra (partitioned by user_id, clustered by tweet_id)
  → Snowflake IDs (timestamp-embedded, globally unique, monotonically increasing)

  Snowflake ID format (64-bit):
    [ 41 bits: timestamp (ms since epoch) ]
    [  5 bits: datacenter ID              ]
    [  5 bits: worker ID                  ]
    [ 12 bits: sequence number per ms     ]

  → Sorts by time naturally (no ORDER BY timestamp needed)
  → Generated by each app server independently (no coordination)
  → Supports 4,096 unique IDs per ms per worker (4M/sec)

Media (images, videos):
  Write-once, read-many. Never updated after upload.
  → Object storage (S3 / GCS)
  → CDN in front (CloudFront / Fastly) for global low-latency delivery

  Upload flow:
    1. Client requests presigned S3 upload URL from Media Service
    2. Client uploads directly to S3 (bypasses app servers)
    3. S3 triggers Lambda/event → Media Processing Service
    4. Processing: resize images (4 sizes), transcode video (360p/720p/1080p)
    5. Store processed URLs in Tweet record
    6. CDN caches processed media at edge nodes

  Video transcoding:
    Use adaptive bitrate streaming (HLS / DASH)
    Player selects quality based on network speed
    Segment size: 2-6 seconds for fast seek performance
```

---

## 8. Search — Finding Tweets

Standard B-tree database indexes cannot efficiently handle full-text search at Twitter's scale.

```
The problem:
  Users search "earthquake" and expect results in milliseconds.
  "earthquake" might appear in 500,000 tweets from the last 24 hours.
  A LIKE '%earthquake%' query on Cassandra is a full table scan.

Solution: Elasticsearch with inverted index.

How an inverted index works:
  tweet_id  content
  ──────────────────────────────────────
  101       "Big earthquake in Tokyo"
  102       "Earthquake news coverage"
  103       "Tokyo tourism tips"

  Inverted index:
  word          → [tweet_ids]
  "earthquake"  → [101, 102]
  "tokyo"       → [101, 103]
  "big"         → [101]

  Query "earthquake tokyo":
    intersect([101, 102], [101, 103]) = [101]
    → Return tweet 101

Search architecture:
  Write path:
    Tweet created ──▶ Kafka topic "tweets" ──▶ Search Indexer ──▶ Elasticsearch

  Read path:
    GET /search?q=earthquake&since=1h
      ──▶ Search Service ──▶ Elasticsearch query
          ──▶ [tweet_ids] ──▶ hydrate from tweet cache ──▶ return results

Elasticsearch cluster sizing:
  Index recent tweets only (last 7 days) for "live" search
  Archive older tweets to S3 + separate cold index
  At 500M tweets/day × 7 days = 3.5B indexed documents
  Each document ~200 bytes → 700 GB index
  3 primary shards × 3 replicas = 9 Elasticsearch nodes

Relevance ranking signals:
  - Recency (time decay)
  - Engagement (likes + retweets)
  - Author follower count
  - Personal network boost (if author is followed by you)
```

---

## 9. Notifications — Async Event Processing

Notifications must be decoupled from the core tweet/follow path.
Blocking a tweet on notification delivery is unacceptable.

```
Events that trigger notifications:
  tweet_liked        → notify tweet author
  tweet_retweeted    → notify tweet author
  user_mentioned     → notify mentioned user
  user_followed      → notify followed user
  reply_received     → notify parent tweet author

Architecture:

Core Services ──▶ Kafka ──▶ Notification Fan-out ──▶ Delivery Workers
                              Service
                              (consumer group)

Notification Fan-out Service:
  1. Consume event from Kafka (guaranteed at-least-once delivery)
  2. Look up user notification preferences (push? email? SMS?)
  3. Rate-limit: max 20 notifications per user per minute (anti-spam)
  4. Deduplicate: "5 people liked your tweet" → batched notification
  5. Enqueue to delivery queues (one per channel)

Delivery Workers:
  Push notifications:  APNs (iOS), FCM (Android)
  Email:               SendGrid / SES
  SMS:                 Twilio (for account security only)

Batching logic:
  Don't send 80M separate "Lady Gaga liked your tweet" notifications.
  Aggregate: "Lady Gaga and 12,345 others liked your tweet"

  Window: collect events for 30 seconds → send single notification
  Redis key: "notif_batch:{user_id}:{event_type}:{tweet_id}"
    INCR on each event, EXPIRE 30 seconds
    At expiry: send batched notification, clear key

Push notification at scale:
  100M DAU × 10 notifications/day = 1B pushes/day
  1B / 86,400 sec ≈ 11,500 pushes/second
  APNs rate limit: ~500K/sec per certificate (use multiple certs + connection pools)
```

---

## 10. Full Architecture Diagram

Everything together.

```
    ┌──────────────────────────────────────────────────────────────────────────┐
    │                             CLIENTS                                       │
    │                    iOS / Android / Web / Third-party API                 │
    └───────────────────────────────┬──────────────────────────────────────────┘
                                    │ HTTPS
                        ┌───────────▼──────────────┐
                        │    CDN (CloudFront)        │  Static assets, media,
                        │    Global Edge Nodes       │  hot tweet images/video
                        └───────────┬───────────────┘
                                    │ dynamic requests
                        ┌───────────▼──────────────┐
                        │    API Gateway             │  Rate limiting (1K req/min
                        │    (Kong / AWS API GW)     │  per user), auth tokens,
                        └───────────┬───────────────┘  routing
                                    │
         ┌──────────────────────────┼──────────────────────────────┐
         │                          │                               │
┌────────▼──────────┐   ┌──────────▼──────────┐   ┌───────────────▼──────────┐
│   Tweet Service   │   │  Timeline Service    │   │    User Service           │
│                   │   │                      │   │                           │
│  POST /tweet      │   │  GET /timeline       │   │  GET/POST /user           │
│  - validate       │   │  - Redis feed cache  │   │  - profile CRUD           │
│  - media upload   │   │  - celebrity pull    │   │  - follow/unfollow        │
│  - store tweet    │   │  - hydrate tweets    │   │  - search users           │
│  - fan-out        │   │  - merge + sort      │   │                           │
└────────┬──────────┘   └──────────┬──────────┘   └────────────────────────── ┘
         │                         │
         ▼                         ▼
┌────────────────┐       ┌───────────────────────────────────────────────────┐
│  Fan-out       │       │                   REDIS CLUSTER                    │
│  Service       │       │                                                    │
│                │       │  "feed:{user_id}"       sorted set, tweet IDs     │
│  Checks        │──────▶│  "tweet:{tweet_id}"     hydrated tweet object     │
│  is_celebrity  │       │  "celeb_tweets:{id}"    celebrity tweet cache     │
│  Push vs Pull  │       │  "user:{user_id}"       user profile cache        │
└────────┬───────┘       └──────────────────────────────────────────────────┘
         │                         │ cache miss
         │               ┌─────────▼───────────────────────────────────────┐
         │               │              CASSANDRA CLUSTER                   │
         │               │                                                  │
         │               │  tweets (user_id, tweet_id, content, media_urls) │
         │               │  follows (follower_id, followee_id)              │
         │               │  user_followers (followee_id → [follower_ids])   │
         │               └──────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            KAFKA                                             │
│                                                                              │
│  topic: tweets          topic: follows       topic: engagements             │
│  (new tweets)           (follow events)      (likes, RTs, replies)          │
└────────────┬────────────────────────┬──────────────────┬────────────────────┘
             │                        │                  │
    ┌────────▼────────┐   ┌───────────▼──────┐  ┌───────▼──────────────────┐
    │ Search Indexer   │   │ Notification Fan- │  │  Analytics / Metrics     │
    │                  │   │ out Service       │  │                          │
    │ Elasticsearch    │   │                   │  │  ClickHouse (OLAP)       │
    │ (tweet full-text)│   │ APNs / FCM        │  │  Trend detection         │
    └──────────────────┘   │ Email / SMS       │  │  Engagement counters     │
                           └───────────────────┘  └──────────────────────────┘

                         MEDIA PIPELINE
                         ──────────────
    Client ──presigned URL──▶ S3 Upload ──▶ Lambda trigger ──▶ FFmpeg/Sharp
                                               (event)         transcoding
                                                            ──▶ S3 (processed)
                                                            ──▶ CDN cache warm
```

---

## Trade-offs Summary

```
Decision                        Gain                         Cost
──────────────────────────────  ───────────────────────────  ──────────────────────────
Hybrid push/pull timeline       Celebrities don't DDoS        Timeline merge adds latency
                                fan-out workers               (< 10ms, acceptable)

Redis sorted set for feed        O(log N) insert/fetch         Memory cost:
                                Pre-computed timeline          ~800 GB for 100M users

Cassandra for tweets             Linear horizontal scale       No ad-hoc queries;
                                High write throughput          analytics need separate DB

Snowflake IDs                    Time-sortable without         Requires worker ID
                                ORDER BY, globally unique      coordination

Elasticsearch for search         Fast full-text, relevance     Eventual consistency:
                                ranking, facets                new tweets indexed ~2s delay

Kafka for fan-out                Absorbs tweet burst spikes    Fan-out latency ~seconds
                                Durable, replayable            (not milliseconds)

Async notifications              Core path unblocked           Notification may arrive
                                Batching reduces spam          seconds after event
```

---

## Navigation

| | |
|---|---|
| Previous | [22 — URL Shortener](./url_shortener.md) |
| Next | [22 — Netflix Design](./netflix.md) |
| Home | [README.md](../README.md) |
