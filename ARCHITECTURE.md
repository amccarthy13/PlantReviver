# PlantReviver — Architecture

A plant-watering tracker for iOS, backed by a dedicated Python API. This
document is the source of truth for the system's shape and the decisions
behind it. Premium (AI + weather) features are architected in from the start
but ship behind an entitlement gate that stays open until launch.

---

## 1. Decisions log

These are settled. Anything not listed here is open.

| Area | Decision | Rationale |
|---|---|---|
| Client | SwiftUI + SwiftData (local source of truth) | Native; drives an **offline-first** architecture (see §11) |
| Sync model | **Offline-first**: local store is authoritative for the UI; background sync reconciles with the API | App fully works offline; changes queue and sync on reconnect. Chosen for the experience — cheap here because data is single-user and low-conflict |
| Backend language | Python 3.12 | Requested |
| Web framework | FastAPI + Uvicorn (Gunicorn in prod) | Async, typed, fast to build |
| ORM / migrations | SQLAlchemy 2.0 (async) + Alembic | Mature, explicit migrations, no shortcuts |
| Schemas / validation | Pydantic v2 (+ pydantic-settings for config) | First-class with FastAPI |
| Database | PostgreSQL (managed) | Relational data fits; JSONB where flex is needed |
| DB driver + pooling | `asyncpg` via SQLAlchemy async engine, with a tuned connection pool (`pool_size`, `max_overflow`, `pool_pre_ping`) | Non-blocking DB access; pooling avoids per-request connect cost |
| Concurrency model | Fully async end-to-end: async routes, async SQLAlchemy, `httpx.AsyncClient` for all external calls | Performance practice; no sync calls blocking the event loop |
| Service topology | Single **modular monolith** (bounded modules in one FastAPI app) | Solo project; logical seams allow later extraction — microservices would be pure overhead |
| Client repo | Same monorepo, `ios/` | No technical need to split; atomic API+client commits; path-filtered CI |
| Rate limiting | `slowapi` (in-memory now, Redis later) | Per-user/IP request throttling — §12 |
| Admin dashboard | **SQLAdmin** mounted at `/admin` | Auto-generated CRUD over existing models; in-process, free — §12 |
| Hosting | **Render** | Managed Postgres, background workers, cron, and Key Value (Redis) are all first-class — the "later" pieces need no provider switch |
| Object storage | Cloudflare R2 (S3-compatible) | Photo storage with **no egress fees**; pre-signed uploads |
| Auth | Sign in with Apple → app-issued JWT (access + refresh) | No passwords; Apple manages identity |
| Payments | StoreKit 2 + App Store Server API + Server Notifications V2 | Apple requires IAP for digital subscriptions |
| AI (premium) | Claude vision (identification + care guidance) | Strong vision + structured care output |
| Weather (premium) | OpenWeather One Call API | Simple server-side integration, cheap at low volume |
| Push | APNs, token-based auth (.p8 key) | Standard, no cert rotation |
| Background jobs | **None at launch** — synchronous request handling | Deferred; Render adds workers/cron later without rearchitecture |
| Caching | **None at launch** — DB is the source of truth | Deferred; Render Key Value (Redis) added when needed |
| CI/CD | GitHub Actions → Render (backend), Xcode Cloud/Fastlane → TestFlight (iOS) | Standard, low-ops |
| Infrastructure-as-Code | **Terraform** (Render + Cloudflare providers), state in HCP Terraform free tier | **Learning goal** — not strictly necessary at this scale, but makes infra reproducible and version-controlled |
| Repo layout | Monorepo: `backend/` (now), `infra/terraform/` (now), `ios/` (next) | One place, shared docs |

### Deliberately deferred (designed for, not built yet)
- Background job runner (reminders, weather recompute) → Render **Background Worker** + **Cron Job**.
- Redis caching / rate-limit store → Render **Key Value**.
- These have seams in the code (a `jobs/` package, a cache interface) so turning
  them on is additive.

---

## 2. System overview

```
                    ┌───────────────────────────┐
                    │   iOS app (SwiftUI)         │
                    │   SwiftData local cache     │
                    └──────────────┬──────────────┘
                                   │ HTTPS (JSON, JWT bearer)
                                   ▼
        ┌──────────────────────────────────────────────────┐
        │        FastAPI backend (Render Web Service)        │
        │                                                    │
        │  Routers → Services → Repositories → SQLAlchemy    │
        │                                                    │
        │  Auth │ Plants │ Sync │ Photos │ Notifications   │
        │  Subscriptions │ AI* │ Weather*   (*premium-gated) │
        └───┬──────────┬───────────┬───────────┬────────────┘
            │          │           │           │
            ▼          ▼           ▼           ▼
     ┌───────────┐ ┌────────┐ ┌─────────┐ ┌──────────────────┐
     │ Postgres  │ │  R2     │ │  APNs   │ │ External APIs     │
     │ (Render)  │ │ (photos)│ │ (push)  │ │ Apple StoreKit /  │
     └───────────┘ └────────┘ └─────────┘ │ Claude / Weather  │
                                          └──────────────────┘
```

Everything is synchronous request/response at launch. No queue, no cache, no
worker — the deferred boxes attach to the same Postgres and codebase later.

---

## 3. Backend layering

A clean, testable layering. No business logic in routers, no HTTP in services.

```
app/
  main.py                 # FastAPI app factory, middleware, router mounting
  config.py               # pydantic-settings (env-driven)
  db.py                   # async engine (asyncpg) + tuned connection pool, session dependency
  deps.py                 # shared FastAPI dependencies (current_user, entitlements)
  security.py             # JWT issue/verify, Apple token verification

  models/                 # SQLAlchemy ORM models (tables)
  schemas/                # Pydantic request/response models
  repositories/           # DB access, one per aggregate
  services/               # business logic, one per bounded module
  routers/                # HTTP endpoints, thin
  integrations/           # Apple, Claude, OpenWeather, R2, APNs clients
  jobs/                   # (placeholder) future background tasks

migrations/               # Alembic
tests/
```

**Rule:** router → service → repository → model. Services depend on interfaces
from `integrations/`, so external calls are mockable in tests.

---

## 4. Services (bounded modules)

| Service | Responsibility | Premium |
|---|---|---|
| **AuthService** | Verify Sign in with Apple identity token against Apple's public keys; create/load user; issue + refresh app JWTs; account deletion | No |
| **PlantService** | Plant CRUD; watering-date logic from preset (7/10/14/30 defaults + custom) or custom interval; per-user editable presets; record `watering_events` | No |
| **SyncService** | Offline-first sync endpoints: incremental pull (`/sync/changes`) and idempotent batch push (`/sync/push`); composes the other services (see §11) | No |
| **PhotoService** | Issue pre-signed R2 upload URLs; store photo metadata; (thumbnails later) | No |
| **NotificationService** | Device-token registry; compute due/overdue; send APNs (synchronous at launch; scheduled later) | No |
| **SubscriptionService** | Verify StoreKit transactions via App Store Server API; ingest Server Notifications V2 webhook; maintain `subscriptions` + `entitlements` as source of truth | No (but powers premium) |
| **AIService** | `POST /ai/identify` — species + suggested watering interval + care tips via Claude vision. Gated. | **Yes** |
| **WeatherService** | Fetch forecast for a plant's location; adjust watering intervals seasonally. Gated. | **Yes** |

Premium endpoints call `require_entitlement(user, Feature.SMART_WATERING)`.
The gate defaults to granted-for-all until the paywall launches, then flips to
subscription-checked — a one-line change, no rearchitecture.

---

## 5. Data model

All user-owned, syncable tables carry `id` (UUID, **client-generated**),
`updated_at`, and `deleted_at?` (tombstone) — the columns the offline-first sync
engine relies on (see §11). Omitted below for brevity where marked *(+sync)*.

```
users              id, apple_user_id (unique), email?, created_at,
                   disabled_at? (ban), deleted_at?
plants (+sync)     id, user_id → users, name, species_id? → species,
                   primary_photo_id? → photos, watering_interval_days?,
                   next_watering_date?, last_watered_at?, notes, created_at
watering_events    id, plant_id → plants, watered_at, source (manual|auto),
  (+sync)          created_at    # append-only; deletes rare but tombstoned
presets (+sync)    id, user_id → users, days, is_custom
photos (+sync)     id, plant_id → plants, storage_key, thumb_key?, status, created_at
species            id, common_name, scientific_name, default_interval_days, care_json   # library, server-only
subscriptions      id, user_id → users, product_id, status, expires_at,
                   original_transaction_id, environment (sandbox|production)
entitlements       id, user_id → users, feature, active, source              # derived
devices            id, user_id → users, apns_token, platform, last_seen
usage_counters     id, user_id → users, feature, period, count               # per-user quota (§12)
                     unique(user_id, feature, period)
```

**Modeling decisions:**
- `watering_events` is a **log**, not just `last_watered_at`. Cheap now; unlocks
  history, streaks, and AI signals later.
- `entitlements` is **derived** from `subscriptions` but stored explicitly so
  every premium check is a single indexed lookup.
- `species` starts as a **seeded table** (from a bundled dataset); becomes
  admin-editable later. Client can also ship a copy for offline browse.
- Soft-delete users (`deleted_at`) to satisfy Apple's account-deletion
  requirement while allowing grace-period reversal.
- **Client-generated UUID primary keys** on syncable rows so the app can create
  records offline and the server accepts the id as-is — makes writes idempotent
  and retry-safe. `updated_at` + `deleted_at` tombstones drive incremental sync
  (see §11).

---

## 6. Auth flow (lightweight, no passwords)

1. iOS runs Sign in with Apple → gets an Apple **identity token** (JWT).
2. App sends it to `POST /auth/apple`.
3. Backend verifies signature against Apple's public keys, validates `aud`/`iss`,
   extracts the stable `sub` → upserts a `User` (`apple_user_id = sub`).
4. Backend issues its own **access JWT** (short-lived, ~1h) + **refresh JWT**
   (long-lived, rotated). App stores them in the Keychain.
5. Subsequent requests use `Authorization: Bearer <access>`; `POST /auth/refresh`
   rotates when it expires.

No password store, no email verification, no session server. Just Apple identity
+ our own stateless JWTs.

---

## 7. Premium / subscription architecture

Built now, gate opens later.

1. App purchases via **StoreKit 2**, receives a signed transaction.
2. App posts it to `POST /subscriptions/verify`; SubscriptionService validates
   with the **App Store Server API** and records `subscriptions` + `entitlements`.
3. **Apple → `POST /webhooks/app-store`** (Server Notifications V2) keeps state
   fresh for renewals, cancellations, refunds, billing retries — independent of
   the app being open.
4. `entitlements` is the single gate for AIService and WeatherService.

Free tier: manual tracking, presets, notes, photos, local due-warnings.
Premium tier: AI identification, weather/season-aware smart watering, richer
notifications.

---

## 8. External integrations

| Integration | Purpose | Secret |
|---|---|---|
| Sign in with Apple | Identity | Apple public keys (fetched), app bundle id |
| App Store Server API | Subscription verification | Apple `.p8` key, key id, issuer id |
| APNs | Push notifications | Apple `.p8` key (token auth) |
| Cloudflare R2 | Photo storage | R2 access key/secret, bucket |
| Claude (Anthropic) | Plant identification + care | API key |
| OpenWeather | Forecasts | API key |

All secrets live in **Render environment secrets** — never in the repo or the
app binary. AI/weather keys are only ever used server-side.

---

## 9. Deployment

**Environments:** `dev` (local), `staging`, `prod` — with separate Apple
StoreKit **sandbox vs. production** subscription environments (tracked by
`subscriptions.environment`).

**Backend (Render):**
- Dockerized FastAPI, deployed as a **Web Service** provisioned by Terraform.
- **Managed Postgres** with automated backups + point-in-time recovery.
- DB migrations (Alembic) run as a deploy step, gated.
- Secrets in Render env groups.
- *Later, same Terraform:* a **Background Worker** + **Cron Job** for reminders
  and weather recompute, and **Key Value** for caching.

**iOS:** Xcode Cloud or Fastlane → **TestFlight** → **App Store**. Requires the
**Apple Developer Program ($99/yr)**.

**Infrastructure-as-Code (Terraform):** All cloud resources are declared in
`infra/terraform/` rather than clicked together in dashboards. This is a
learning goal — at this scale you *could* provision by hand — but it keeps
infra reproducible, reviewable, and destroyable.

- **Providers:** `render` (web service, Postgres, env groups; later worker /
  cron / Key Value) and `cloudflare` (R2 bucket + lifecycle rules). Optionally
  `github` for repo secrets.
- **State:** remote in **HCP Terraform** (free tier) — gives locking and a run
  history without standing up your own state bucket. (Alternative: an S3-backend
  pointed at an R2 bucket, if you'd rather keep everything on Cloudflare.)
- **Layout** — reusable modules, one directory per environment:

  ```
  infra/terraform/
    versions.tf              # required_providers, backend config
    modules/
      render_service/        # web service + env + Postgres wiring
      r2_bucket/             # Cloudflare R2 bucket + lifecycle
    environments/
      staging/               # main.tf, terraform.tfvars, backend workspace
      prod/
  ```

- **Secrets stay out of state where possible:** API keys are set as Render env
  secrets / TF variables marked `sensitive`, sourced from a `*.auto.tfvars`
  that is git-ignored (or from HCP Terraform variable sets). Never commit real
  keys; commit an `*.tfvars.example` template.
- **Workflow:** `terraform plan` in CI on PRs (posted for review), `terraform
  apply` gated on merge to the environment branch. Deferred infra (worker,
  cron, Key Value) is added by uncommenting/adding a module — no rearchitecture.

**CI/CD:** GitHub Actions → lint + type-check (ruff, mypy) + tests → build image
→ deploy to staging → promote to prod. Terraform plan/apply runs as its own
gated workflow.

**Observability (part of no-shortcuts):**
- Structured JSON logging.
- Error tracking via Sentry.
- Alerting on webhook failures and APNs errors (expand when workers land).

**Security / compliance baseline:**
- TLS everywhere; JWT rotation; per-user rate limiting (in-app middleware now,
  Redis-backed later).
- Account deletion + data export (App Store requirements).
- Privacy policy + App Privacy labels once photos/location are collected.

**Rough cost:** ~$7 Render web service + ~$7–19 managed Postgres + ~$0–5 R2 +
per-use AI/weather (pennies at low volume) + $99/yr Apple ≈ **$20–35/mo**.

---

## 10. Build order

1. **Infra skeleton** — monorepo, `backend/` scaffold, Dockerfile,
   `infra/terraform/` (Render web service + Postgres + R2 via Terraform),
   GitHub Actions, health check deploying to staging. Terraform is the sole
   source of truth for infra.
2. **AuthService** — Sign in with Apple verification + JWT issue/refresh + user
   accounts + deletion.
3. **PlantService** — plant CRUD, watering-date logic, presets,
   `watering_events`.
4. **SyncService + iOS client** — `/sync/changes` + `/sync/push` on the backend;
   SwiftData local store + outbox + sync engine on the client (offline-first,
   §11).
5. **PhotoService** — pre-signed R2 uploads + metadata.
6. **NotificationService** — device registry + APNs + synchronous due-warnings.
7. **SubscriptionService** — StoreKit verify + webhook + entitlement gate
   (defaults open).
8. **AIService + WeatherService** — behind the premium gate.
9. **Launch premium** — flip the gate to subscription-checked, configure
   StoreKit products, ship the paywall.

Fully server-backed app by step 6; premium plumbing already present so steps
7–9 are additive.

---

## 11. Sync & offline (offline-first)

The app is **offline-first**: the local SwiftData store is the source of truth
for everything the UI reads and writes. Every user action — add a plant, mark
watered, edit notes — commits locally and succeeds instantly, with or without
connectivity. A background sync engine reconciles with the API when the network
is available. This is deliberately more than the app strictly needs; it's cheap
here because the data is single-user and low-conflict.

### Client responsibilities

- **Local writes always win locally.** The UI never blocks on the network.
- **Outbox / mutation queue.** Each local change is enqueued as a pending
  mutation and retried (with backoff) until the server acknowledges it.
- **Sync cursor.** The client stores the last-synced timestamp and pulls only
  changes since then.
- **Reachability-driven flush.** Sync triggers on app foreground, on regaining
  connectivity, and periodically.

### Server responsibilities (API)

- **Accept client-generated UUIDs** on create; upsert semantics keyed by id so a
  retried request never double-inserts (**idempotent writes**).
- **`GET /sync/changes?since=<cursor>`** — returns all rows (across the user's
  plants, watering_events, presets, photos) with `updated_at > cursor`,
  including tombstoned (`deleted_at`) rows, plus a new cursor.
- **`POST /sync/push`** — accepts a batch of client mutations, applies them
  idempotently, returns per-item results and the authoritative rows.
- These live in a thin **SyncService** that composes the existing services
  rather than duplicating their logic.

### Conflict resolution

- **Plants / presets:** last-write-wins by `updated_at`. Adequate — edits are
  rare and single-user.
- **watering_events:** append-only and keyed by client UUID, so two devices
  simply **union** their events; no real conflict exists. This is why the event
  log (not just `last_watered_at`) matters for sync, not only history.
- **Deletes:** propagated as tombstones (`deleted_at`), never hard-deletes, so a
  deletion can't be resurrected by a stale offline copy.

### Reliability note

SwiftData is durable (SQLite/Core Data underneath) and fine for this. If its
newer APIs ever prove limiting, **GRDB** is the fallback for direct SQLite
control — not a preemptive switch.

---

## 12. Abuse & cost safeguards

Three distinct mechanisms, each solving a different problem — don't conflate
them. Applied as defense in depth, outermost layer first.

### The three mechanisms

| Mechanism | Protects against | Unit | Scope |
|---|---|---|---|
| **Rate limiting** | bursts / DDoS / hammering | requests **per time** | per-user + per-IP |
| **Quota** | sustained **cost** abuse | total **per period** | per-user |
| **Circuit breaker** | catastrophic runaway (bug/attack) | global **hard ceiling** | whole system |

A rate limit doesn't cap cost (staying just under the limit still runs up a
bill) — that's the quota's job. Per-user quotas don't stop a server-side loop
bug — that's the circuit breaker's job. The expensive paths get all three, plus
**input constraints** (size/type/count) as a preventative fourth layer.

### Layers (outermost first)

1. **Edge — Cloudflare in front of Render:** DDoS protection, coarse IP rate
   limits, request body-size cap, WAF. Free tier; Cloudflare is already in the
   stack for R2. *(Requires routing the API through a Cloudflare-proxied custom
   domain — recommended, low cost.)*
2. **Auth gate:** every endpoint requires a valid Apple-issued JWT. One Apple ID
   ≈ one account, so mass account creation is hard.
3. **App rate limiter:** `slowapi`, in-memory backend at launch (single
   instance); swap to its Redis backend when scaling to multiple instances.
4. **Business quotas + entitlement gate:** premium-gating AI means only paying
   users reach it and revenue offsets cost; per-user usage is still capped.
5. **External-cost guard:** per-user quota → global circuit breaker →
   **provider budget caps** (hard billing limits + alerts set in the Anthropic /
   OpenWeather consoles — the backstop outside our code).
6. **Storage constraints:** pre-signed uploads with size/type limits + lifecycle
   cleanup.

### AI cost control (the only meaningfully variable cost)

R2 has no egress fees and Render is mostly flat, so AI is the spend to guard.
Four independent gates must *all* fail for a runaway bill:

- **Premium entitlement gate** — only subscribers reach AIService.
- **Per-user quota** — a Postgres `usage_counters` table (`user_id, feature,
  period, count`), checked-and-incremented atomically **before** the provider
  call. Durable and multi-instance-safe with no Redis.
- **Global circuit breaker** — an `AI_ENABLED` env-var kill switch (instant
  manual shutoff) plus a global monthly counter that auto-disables AI past a
  hard threshold.
- **Provider budget cap** — hard spend limit in the Anthropic dashboard.
- **Result caching** — cache identification results by **image content hash** so
  re-submitting the same photo never re-bills.

### Image upload constraints

- Pre-signed R2 URL with a `content-length-range` (e.g. ≤10 MB) + content-type
  allowlist + short expiry.
- Client downscales before upload; server validates type on the confirm step.
- Per-plant / per-user photo count caps.
- R2 lifecycle rule purges orphaned/`pending` uploads.

### Request hygiene

- Body-size limit (edge + app).
- **Max batch size on `POST /sync/push`**; pagination caps on reads.
- Pydantic validation rejects malformed payloads (already in place).
- `disabled_at` flag on `users` as an instant per-account ban.

### Ships at launch vs deferred

- **At launch:** auth gate, `slowapi` in-memory rate limits, Postgres-backed
  quotas, `AI_ENABLED` kill switch, provider budget caps, upload constraints,
  sync batch cap, ban flag.
- **Deferred (with scale):** Cloudflare edge layer (when a custom domain lands),
  Redis-backed rate limiting (when multi-instance). Both are additive.

### Admin dashboard

Operator control (view users, ban via `disabled_at`, delete, inspect
subscriptions / entitlements / usage) is provided by **SQLAdmin** mounted at
`/admin` on the same FastAPI app — auto-generated CRUD over the existing models,
no extra service or cost. Users and entitlements are editable (so you can ban an
account or manually grant premium); everything else is read-only.

- Protected by a **separate admin login** (`AuthenticationBackend`, env-var
  credentials distinct from user JWT auth) — set a strong `ADMIN_PASSWORD` and
  `ADMIN_SESSION_SECRET` in prod, and ideally IP-restrict `/admin` at the edge.
- Lives in `app/admin/` (`auth.py`, `views.py`, `setup.py`).
