# 🎯 API Versioning Standards — Interview Preparation

> This file prepares you to discuss API versioning like a working engineer.
> Not just definitions — but real-world usage, trade-offs, and production scenarios.

---

# 🔹 Basic Level Questions (0–2 Years)

**Q1: What is a breaking change in an API, and why does it require a new version?**

<details>
<summary>💡 Show Answer</summary>

A breaking change is any modification that causes existing clients to fail or behave incorrectly without any changes on their side. Examples include removing a field from a response, renaming a field (user_name → username), changing a field's type, or making an optional request parameter required.

Breaking changes require a new version because clients have already built against the existing contract. Bumping to /v2 lets v1 clients keep working while new clients adopt the improved interface. The rule of thumb: when in doubt, treat it as breaking — an unnecessary version bump costs less than silently breaking clients.

</details>

<br>

**Q2: What are the three main API versioning strategies and which one is recommended for most cases?**

<details>
<summary>💡 Show Answer</summary>

The three strategies are:
- URL versioning: /v1/users — explicit, cache-friendly, easy to test and route
- Header versioning: API-Version: 2024-01-01 — clean URLs, used by Stripe and GitHub
- Query parameter versioning: /users?version=2 — generally avoided, pollutes the query string and breaks caching

URL versioning is recommended for most public APIs. It is visible in browser tools and logs, works with every HTTP client without special configuration, and makes routing straightforward in proxies and gateways. Header versioning is preferred when you ship an SDK and want to pin versions per API key, as Stripe does.

</details>

<br>

**Q3: What is the difference between a deprecated endpoint and a sunset endpoint?**

<details>
<summary>💡 Show Answer</summary>

A deprecated endpoint is still functional but scheduled for removal. It should respond with Deprecation: true and Sunset headers indicating the removal date, and ideally include a warning in the response body pointing to the migration guide. Clients can still use it but should not depend on it long-term.

A sunset endpoint has been removed. It should return 410 Gone — not 404, which implies the resource never existed. The 410 status tells clients the endpoint existed and was intentionally removed, which helps them distinguish a bug from a planned removal.

</details>

<br>

**Q4: Which changes are safe to make without bumping the API version?**

<details>
<summary>💡 Show Answer</summary>

Non-breaking changes that are safe within the current version include: adding a new field to a response (clients that don't know it just ignore it), adding a new optional request parameter, adding a new endpoint entirely, relaxing validation to accept more input formats, and improving error messages while keeping the same error code and status.

Adding a new enum value is technically non-breaking but can cause problems for strict parsers that reject unknown values — treat it carefully. The safe pattern is additive changes only: never remove, rename, or change the type of existing fields within a version.

</details>

<br>

**Q5: How do you communicate to clients that an endpoint is being deprecated?**

<details>
<summary>💡 Show Answer</summary>

There are two layers. First, use HTTP headers on every response from the deprecated endpoint: Deprecation: true, Sunset: with an RFC 7231 date, and a Link header pointing to the migration docs with rel="successor-version". Second, include a _warnings field in the response body with a human-readable message and a link — this surfaces the deprecation even in clients that do not inspect headers.

Internal APIs should give at least 3 months notice. Public APIs typically get 6–12 months, and major public APIs can require 12–24 months. Communicate through changelogs, email, and dashboard alerts in addition to the in-response signals.

</details>

<br>

---

# 🔹 Intermediate Level Questions (2–5 Years)

**Q6: How does header versioning work in practice, and what caching problem does it introduce?**

<details>
<summary>💡 Show Answer</summary>

With header versioning the URL stays unchanged and the version is passed in a header like API-Version: 2 or, in Stripe's model, Stripe-Version: 2024-06-20. The advantage is clean URLs and fine-grained control — Stripe pins the version to the API key created at a given date, so old integrations keep working indefinitely without any client changes.

The caching problem: CDNs and reverse proxies cache by URL by default. Two requests to /users with different API-Version headers would get the same cached response. The fix is to set Vary: API-Version in the response, instructing caches to key on that header as well. Forgetting Vary causes one version's response to be served to clients expecting another version — a hard-to-debug production issue.

</details>

<br>

**Q7: Walk through how you would implement multiple API versions side by side in FastAPI.**

<details>
<summary>💡 Show Answer</summary>

In FastAPI you create separate router modules for each version under a routers/v1 and routers/v2 directory. Each router defines the same resource paths but with version-appropriate schemas and logic. You register both routers on the main app with a prefix:

app.include_router(users_v1.router, prefix="/v1")
app.include_router(users_v2.router, prefix="/v2")

For the deprecated v1 router you add a middleware or a dependency that injects the Deprecation and Sunset headers into every response. The v2 router has no such middleware. This way the versioning concern is centralized — individual endpoint handlers stay clean.

A common mistake is sharing database models between versions without an adapter layer. When v2 changes a field name or adds a column, that change must not affect v1 responses. Use separate Pydantic response schemas per version even if the underlying ORM model is shared.

</details>

<br>

**Q8: What should a good API migration guide include?**

<details>
<summary>💡 Show Answer</summary>

A migration guide should have four sections. First, a summary of what changed — renamed fields, removed endpoints, changed authentication mechanism, changed pagination model. Second, a step-by-step section showing the v1 and v2 patterns side by side for each change, so developers can do a targeted find-and-replace rather than reading prose. Third, a timeline table with the deprecation date and the sunset date clearly marked. Fourth, links to changelog entries and a contact channel for questions.

Common mistakes: docs that list what changed without showing the before/after code, and migration guides with no date — clients often do not prioritize migration until the sunset date appears in the docs.

</details>

<br>

**Q9: Why should you avoid v1.1 or v1.2 in URL versioning?**

<details>
<summary>💡 Show Answer</summary>

Minor version bumps in the URL imply that clients need to update their base URL to get a change, but by definition a minor change should be non-breaking and backward compatible. If it is non-breaking, clients do not need to change anything — so there is no reason to create a new URL. If it is breaking, it should be v2, not v1.1.

Allowing minor versions in URLs creates confusion about which version is current, proliferates URL combinations clients must test against, and signals inconsistency in what counts as "breaking." The clean rule is: one integer major version in the URL, no minor/patch — minor and patch releases are deployed transparently within the current version.

</details>

<br>

**Q10: How does Stripe's API versioning model work, and what problem does it solve?**

<details>
<summary>💡 Show Answer</summary>

Stripe uses date-based header versioning where each API key is pinned to the version active on the date it was created. A key created in 2023 always uses the 2023-01-15 API behavior unless the developer explicitly upgrades it in the dashboard. Stripe ships changes continuously behind new version dates without ever breaking existing integrations.

This solves the "library update breaks old code" problem common with URL versioning. When you upgrade a REST client library that bumps the URL from /v1 to /v2, your integration might break immediately. With Stripe's model you upgrade the version in the dashboard only when you have tested the changes, fully decoupling library updates from behavioral changes. The trade-off is operational complexity — Stripe maintains behavior compatibility for dozens of version dates simultaneously.

</details>

<br>

---

# 🔹 Advanced Level Questions (5+ Years)

**Q11: How do you coordinate API version deprecation across multiple teams or microservices?**

<details>
<summary>💡 Show Answer</summary>

The key is making deprecation observable and actionable at every layer. On the API side: ship Deprecation and Sunset headers and track version usage per client via API key or client ID in access logs. Build a dashboard showing call volume by version — this tells you which clients are still on v1 and at what rate. Deprecation without usage data leads to either premature sunset (breaking clients) or indefinite support (technical debt).

On the consumer side: add a CI check or a lint rule that flags Deprecation headers in integration test runs and fails with a link to the migration guide. Integrate with your changelog or changelog-as-code tooling so teams get Slack notifications when their dependencies add deprecation signals. Set a hard sunset date in a public calendar and escalate to team leads two months before removal. For internal APIs where you own all consumers, prefer the "upgrade all consumers first, then delete" pattern over the parallel-version approach entirely.

</details>

<br>

**Q12: What is the API lifecycle model and how should it influence your CI/CD pipeline?**

<details>
<summary>💡 Show Answer</summary>

The lifecycle is: alpha → beta → stable (v1) → deprecated → sunset (410 Gone). Each stage has different contract guarantees. Alpha is internal only with no backward compatibility promise. Beta is early access — changes are communicated and feedback is solicited, but breaking changes are still possible with short notice. Stable means no breaking changes within the version, ever. Deprecated is functional but actively being retired. Sunset means the endpoint is gone.

In CI/CD: your pipeline should gate stable releases with a contract test (e.g., Pact or schema comparison) that fails if a diff introduces a breaking change against the current version's schema. For beta endpoints you might allow drift with a warning. For deprecated endpoints the pipeline should track call volume via a metrics gate — do not sunset until traffic is below a threshold. Automate the 410 response at sunset date using a feature flag or a deployment toggle rather than a code change.

</details>

<br>

**Q13: How would you handle a situation where a critical security fix requires a breaking change in the current stable version?**

<details>
<summary>💡 Show Answer</summary>

Security fixes are the one legitimate exception to the "never break within a version" rule, but the process still matters. First, evaluate whether the fix can be introduced non-breakingly — for example, accepting both the old and new authentication formats for a transition period, with the old format logging a warning. This is often possible and buys migration time.

If the change must be immediately breaking: issue an emergency advisory directly to all API consumers with a short but explicit timeline (days to weeks, not months). Deploy the fix behind a feature flag or header toggle if possible to give a narrow migration window. Update the API version simultaneously so clients know to test against the new contract. Post-incident, document why the security issue could not be resolved non-breakingly — this is input for future schema design to avoid similar situations.

</details>

<br>

**Q14: What is backward compatibility testing in CI and how do you implement it?**

<details>
<summary>💡 Show Answer</summary>

Backward compatibility testing verifies that a new code deployment does not change the observable contract of an existing API version. The practical approach is to store a snapshot of the OpenAPI schema for each stable version in the repository. On every pull request, generate the current schema and diff it against the snapshot using a tool like openapi-diff or a custom script. The CI step fails if the diff contains any of: removed fields, changed field types, removed endpoints, changed required parameters, or changed status code semantics.

Consumer-driven contract testing with Pact goes further: each consuming service publishes a pact (a record of what requests it makes and what responses it expects). The provider runs these pacts on every build. This catches breaking changes that schema diffing might miss, like a change in enum values or pagination behavior. The trade-off is setup cost — the Pact broker infrastructure and the discipline to keep pacts current. For smaller teams, schema snapshotting plus a disciplined code review process is often sufficient.

</details>

<br>
