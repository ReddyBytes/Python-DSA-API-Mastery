<a id="top"></a>

# API Versioning and Standards

> Srinivas manages a platform with 14 API consumers across 6 teams. One Friday afternoon, a teammate renamed a response field from `user_name` to `username` — "just cleanup." By Monday morning, three mobile apps crashed in production and the partner integration team filed an incident. That rename was a breaking change. Srinivas spent the next week building the versioning and deprecation system his platform should have had from day one.

## Table of Contents

- [1. Why Versioning is Hard](#1-why-versioning-is-hard)
  - [The Discipline Problem](#the-discipline-problem)
- [2. What Counts as a Breaking Change](#2-what-counts-as-a-breaking-change)
  - [Breaking Changes](#breaking-changes)
  - [Non-Breaking Changes](#non-breaking-changes)
- [3. Versioning Strategies](#3-versioning-strategies)
  - [URL Versioning](#url-versioning)
  - [Header Versioning](#header-versioning)
  - [Query Parameter Versioning](#query-parameter-versioning)
  - [When to Use Each](#when-to-use-each)
- [4. Deprecation Strategy](#4-deprecation-strategy)
  - [The Five Steps](#the-five-steps)
- [5. Version Lifecycle](#5-version-lifecycle)
  - [Lifecycle Stages](#lifecycle-stages)
- [6. Migration Guide](#6-migration-guide)
  - [Migration Guide Template](#migration-guide-template)
- [7. Common Mistakes](#7-common-mistakes)
- [8. Summary](#8-summary)
- [Practice Questions](#practice-questions)

[Back to Top](#top)

# 1. Why Versioning is Hard

<a id="1-why-versioning-is-hard"></a>

Srinivas tells new engineers on his team: "Your API is a public contract. The moment you ship it and a client integrates, every behavior becomes load-bearing." The field name, the data type, the status code for an error — changing any of it can silently break a mobile app that you don't control, a partner integration you didn't know existed, or a script running in a customer's CI pipeline.

The challenge: you have to evolve your API (fix mistakes, add features, retire old designs) while keeping existing clients working.

## The Discipline Problem

<a id="the-discipline-problem"></a>

Versioning is not primarily a technical problem. It is a communication and discipline problem. The technical mechanism is easy. The hard part is:

- Deciding what counts as a breaking change
- Committing to a deprecation timeline and sticking to it
- Actually telling your consumers about changes before they happen

Srinivas keeps a versioning checklist posted in the team's shared channel. Before any PR that touches API contracts, engineers must answer three questions: "Does this break existing callers? Did we tell them? When does the old version die?"

[Back to Top](#top)

# 2. What Counts as a Breaking Change

<a id="2-what-counts-as-a-breaking-change"></a>

## Breaking Changes

<a id="breaking-changes"></a>

**Breaking changes** — existing clients will fail or behave incorrectly without code changes on their end:

```
Removing a field from a response
Renaming a field  (user_name → username)
Changing a field's type  (int → string, string → array)
Changing a field from optional to required in a request
Removing an endpoint
Changing an endpoint's URL
Changing authentication mechanisms
Changing the meaning of a status code
Making validation stricter  (previously accepted "2024/01/15", now requires ISO 8601)
Changing pagination behavior  (offset to cursor)
```

## Non-Breaking Changes

<a id="non-breaking-changes"></a>

**Non-breaking changes** — existing clients continue to work without any changes:

```
Adding a new field to a response  (clients that don't know about it ignore it)
Adding a new optional parameter to a request
Adding a new endpoint
Adding a new enum value  (be careful — strict enum parsers may break)
Relaxing validation  (accepting more formats)
Adding a new HTTP method to an existing resource
Improving error messages  (as long as the error code/status doesn't change)
```

When in doubt, treat it as breaking. The cost of a false negative (silent breakage) is much higher than the cost of a false positive (unnecessary version bump).

```
                     BREAKING CHANGE DECISION TREE

  Does the change remove/rename/retype anything?
       |                        |
      YES                      NO
       |                        |
  BREAKING                Does it make validation stricter?
                               |              |
                              YES            NO
                               |              |
                           BREAKING       Does it change behavior/meaning?
                                              |              |
                                             YES            NO
                                              |              |
                                          BREAKING      NON-BREAKING
```

[Back to Top](#top)

# 3. Versioning Strategies

<a id="3-versioning-strategies"></a>

## URL Versioning

<a id="url-versioning"></a>

`/v1/users`, `/v2/users` — the most common approach. The version is in the URL path.

```
GET /v1/users/42
GET /v2/users/42
```

Pros:
- Immediately visible in logs, browser history, network traces
- Easy to test by changing the URL
- Easy to route at the API gateway level
- Simple for developers to understand and use

Cons:
- Breaks the REST principle that a URL identifies a resource (the resource didn't change, just its representation)
- Duplicate routes in your codebase if you maintain both versions

**This is the right default.** Use URL versioning unless you have a specific reason not to. Srinivas chose URL versioning for all his platform's public APIs because every team — mobile, web, partner integrations — could immediately see which version they were calling just by reading the URL.

## Header Versioning

<a id="header-versioning"></a>

Version is passed in a custom request header or the `Accept` header.

```
GET /users/42
API-Version: 2024-01-01
```

```
GET /users/42
Accept: application/vnd.myapi.v2+json
```

Stripe uses date-based header versioning. Each API key is pinned to the version active when it was created. You can upgrade explicitly.

Pros:
- URLs stay clean and stable
- Can version at a fine-grained level (per-request, not per-client)

Cons:
- Not visible in browser — harder to test manually
- Requires custom header handling in every client
- Logs don't show version unless you explicitly propagate it
- Caching is harder (Vary header required)

**Use this when:** you have a sophisticated developer audience, you want fine-grained version control per request, or you are Stripe.

## Query Parameter Versioning

<a id="query-parameter-versioning"></a>

```
GET /users/42?version=2
```

Avoid this. It pollutes the query string, interferes with caching, and mixes routing concerns with filter concerns. Some legacy APIs use it; don't design new ones this way.

## When to Use Each

<a id="when-to-use-each"></a>

| Scenario | Recommendation |
|---|---|
| Public API, broad audience | URL versioning |
| Internal API, controlled consumers | URL versioning or no versioning (just coordinate) |
| SDK-based API (like Stripe) | Header versioning with per-key pinning |
| Microservices internal calls | URL versioning or contract testing instead of versioning |

```
  VERSIONING STRATEGY COMPARISON

  Strategy        | Visibility | Ease | Caching | REST-pure
  ────────────────┼────────────┼──────┼─────────┼──────────
  URL  /v1/...    | High       | Easy | Simple  | No
  Header          | Low        | Hard | Complex | Yes
  Query param     | Medium     | Easy | Broken  | No
                                                   
  Winner for most teams: URL versioning
```

[Back to Top](#top)

# 4. Deprecation Strategy

<a id="4-deprecation-strategy"></a>

Removing a version is as important as adding one. Without a deprecation process, you accumulate dead weight forever. Srinivas learned this when he inherited a platform running 5 "active" API versions — two of which had zero traffic but nobody was brave enough to delete.

## The Five Steps

<a id="the-five-steps"></a>

**Step 1 — Signal deprecation in the response headers.** Start adding these headers the moment you decide a version or endpoint will be retired:

```
Deprecation: true
Sunset: Sat, 01 Jun 2025 00:00:00 GMT
Link: <https://api.example.com/docs/migration/v1-to-v2>; rel="successor-version"
```

`Deprecation` and `Sunset` are IETF standards (RFC 8594). Well-built API clients can detect them and surface warnings to developers automatically.

**Step 2 — Return a warning in the response body** for developers who aren't watching headers:

```json
{
  "data": { "..." : "..." },
  "_warnings": [
    {
      "code": "endpoint_deprecated",
      "message": "GET /v1/users is deprecated. Migrate to GET /v2/users by 2025-06-01.",
      "docs": "https://api.example.com/docs/migration/v1-to-v2"
    }
  ]
}
```

**Step 3 — Notify registered developers directly.** Email every developer who has made a call to the deprecated endpoint in the last 30 days. Give them the migration guide. Give them the deadline.

**Step 4 — Maintain a minimum deprecation window.** Internal APIs: 3 months minimum. Public APIs: 6-12 months minimum. High-profile public APIs (like Twitter, Stripe): 12-24 months. The window should reflect how long it realistically takes your consumers to notice, prioritize, and ship the migration.

**Step 5 — Log and monitor usage.** Track which clients are still calling deprecated endpoints as the sunset date approaches. Reach out individually to the top consumers.

```
  DEPRECATION TIMELINE (Public API)

  Month 0          Month 3           Month 9          Month 12
    |                 |                 |                 |
    v                 v                 v                 v
  Announce      Add headers       Final notice       SUNSET
  deprecation   + body warnings   to remaining       (410 Gone)
                + email blast     consumers
```

[Back to Top](#top)

# 5. Version Lifecycle

<a id="5-version-lifecycle"></a>

## Lifecycle Stages

<a id="lifecycle-stages"></a>

```
alpha --> beta --> v1 (stable) --> deprecated --> sunset
```

**Alpha:** Internal use only. Breaking changes without notice. Not advertised publicly.

**Beta:** Available to early access developers. Breaking changes possible, but communicated. Use beta to gather real-world feedback before locking in a contract.

**v1 (stable):** Public, versioned, stable contract. Breaking changes require a new major version. This is when the deprecation policy applies.

**Deprecated:** Still functional. Headers and warnings signal that retirement is coming. Migration guide is available.

**Sunset:** Endpoint removed or returns `410 Gone`. Clients must have migrated.

Communicate the lifecycle clearly in your docs. Developers need to know what to expect from a "beta" endpoint vs a "v1" endpoint.

```
  VERSION LIFECYCLE STATE MACHINE

  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  alpha   │────>│   beta   │────>│ v1 stable│
  └──────────┘     └──────────┘     └──────────┘
       |                |                 |
       | (can die       | (can die        v
       |  quietly)      |  with notice) ┌──────────────┐
       v                v               │  deprecated  │
    [removed]        [removed]          └──────────────┘
                                              |
                                              v
                                        ┌──────────┐
                                        │  sunset  │
                                        └──────────┘
                                              |
                                              v
                                        410 Gone
```

Srinivas stamps every endpoint in his OpenAPI spec with its lifecycle stage. His gateway reads the annotation and automatically injects the correct deprecation headers when an endpoint moves to "deprecated" status.

[Back to Top](#top)

# 6. Migration Guide

<a id="6-migration-guide"></a>

When you release v2, write a migration guide before you announce it. Srinivas enforces a rule: no version bump PR gets merged without an accompanying migration guide PR. The guide should contain:

## Migration Guide Template

<a id="migration-guide-template"></a>

```markdown
## Migrating from v1 to v2

## What changed
- `user_name` renamed to `username` on all user objects
- Pagination changed from offset to cursor-based on all list endpoints
- `GET /v1/users` removed — use `GET /v2/users`
- Authentication changed from API key query param to Bearer token header

## Step-by-step migration

#### 1. Update authentication
v1:  GET /v1/users?api_key=YOUR_KEY
v2:  GET /v2/users
     Authorization: Bearer YOUR_KEY

#### 2. Update field references
Find every place in your code that reads `user.user_name` and
replace with `user.username`.

#### 3. Update pagination
v1 offset-based:
  GET /v2/users?page=2&per_page=20

v2 cursor-based:
  GET /v2/users?cursor=eyJpZCI6MjB9&limit=20
  # cursor comes from the previous response: response.next_cursor

## Timeline
- v1 deprecated: 2024-03-01
- v1 sunset: 2025-03-01
- Questions: api-support@example.com
```

A migration guide that is honest about the changes (including breaking ones) builds trust even when the changes are painful.

[Back to Top](#top)

# 7. Common Mistakes

<a id="7-common-mistakes"></a>

| Mistake | Why It Fails | Fix |
|---------|-------------|-----|
| Renaming a field without a new version | Existing clients break silently | Always version-bump for renames |
| No deprecation headers | Clients have no automated warning | Add RFC 8594 headers from day one |
| Sunset date too short | Consumers cannot migrate in time | 6 months minimum for public APIs |
| Maintaining too many active versions | Codebase becomes unmaintainable | Limit to 2 active major versions |
| Versioning by feature instead of globally | Clients must track per-endpoint versions | Version the entire API surface together |
| No migration guide | Developers guess at changes and fail | Write the guide before announcing the bump |
| Using query param versioning | Caching breaks, concerns mix | Use URL versioning instead |
| Skipping beta stage | First stable version has design mistakes | Ship beta, gather feedback, then lock v1 |

[Back to Top](#top)

# 8. Summary

<a id="8-summary"></a>

| Concept | Key Point |
|---------|-----------|
| Breaking vs non-breaking | Removing/renaming/retyping = breaking. Adding = safe. When in doubt, treat as breaking. |
| URL versioning | Default choice. Visible, simple, gateway-friendly. |
| Header versioning | For sophisticated SDKs (Stripe model). Clean URLs but hidden version. |
| Deprecation headers | RFC 8594: `Deprecation: true` + `Sunset` date. Add them immediately. |
| Deprecation window | Internal: 3 months. Public: 6-12 months. High-profile: 12-24 months. |
| Lifecycle stages | alpha -> beta -> v1 -> deprecated -> sunset. Communicate clearly. |
| Migration guides | Write before announcing. Include what changed + step-by-step + timeline. |
| Version discipline | Not a technical problem — a communication and process problem. |

Learning Priority:

**Must Learn** — Core concept, daily use, interview essential:
breaking change definition, URL versioning (/v1/ /v2/), deprecation headers (RFC 8594)

**Should Learn** — Important for real projects, comes up regularly:
header versioning trade-offs, API lifecycle (alpha/beta/v1/deprecated/sunset), migration guides

**Good to Know** — Useful in specific situations, not always tested:
query parameter versioning, version sunset communication

**Reference** — Know it exists, look up syntax when needed:
canary deployment coordination, backward compatibility testing in CI

[Back to Top](#top)

# Practice Questions

<a id="practice-questions"></a>

> **Practice:** [Q65 - api-versioning-strategies](../api_practice_questions_100.md#q65--interview--api-versioning-strategies)

> **Practice:** [Q14 - api-versioning-url](../api_practice_questions_100.md#q14--thinking--api-versioning-url)

> **Practice:** [Q100 - design-api-versioning-system](../api_practice_questions_100.md#q100--design--design-api-versioning-system)

> **Practice:** [Q90 - design-versioning-breaking-change](../api_practice_questions_100.md#q90--design--design-versioning-breaking-change)

> **Practice:** [Q80 - explain-backward-compatibility](../api_practice_questions_100.md#q80--interview--explain-backward-compatibility)

[Back to Top](#top)

## Navigation

**[Back to README](../README.md)**

| Prev | Next |
|------|------|
| [FastAPI](../07_fastapi/README.md) | [API Performance and Scaling](../09_api_performance_scaling/theory.md) |

**Related Topics:** [REST Best Practices](../03_rest_best_practices/theory.md) | [Error Handling Standards](../06_error_handling_standards/theory.md) | [API Design Patterns](../16_api_design_patterns/theory.md)
