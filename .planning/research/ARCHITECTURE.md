# Architecture Research

**Domain:** Deployment topology — existing Dockerized FastAPI + Postgres app onto free PaaS + managed Postgres
**Researched:** 2026-08-09
**Confidence:** HIGH (platform mechanics verified against current docs/changelogs/community threads, dated 2024–2026)

This is not a system-design document — the application architecture (routers → business modules → SQLAlchemy → Postgres, per `.planning/codebase/ARCHITECTURE.md`) is fixed and out of scope. This document covers only how that existing container integrates with a free-tier cloud topology.

## Platform Recommendation (decided, not a menu)

**Render (free web service) + Supabase (free Postgres)**, because:

- **Fly.io has no free tier anymore.** Removed for new accounts in 2024; a new signup gets a 2-hour/7-day trial, then requires a credit card. Disqualified by the "presupuesto cero estricto" constraint.
- **Railway's free tier is not "free," it's $1/month of credit** after a one-time $5 trial — not enough to keep a Postgres + web service pair running continuously. Disqualified for the same reason.
- **Render's free web service tier is genuinely free indefinitely**: 750 instance-hours/month (covers one always-listed service), Docker support via a Dockerfile, free TLS + subdomain. Trade-off: spins down after 15 min of inactivity, ~30–60s cold start on the next request. Acceptable for a graded demo, not for a real product.
- **Render's own free Postgres is not viable as the database**: it expires 30 days after creation (14-day grace period, then data is deleted). A thesis defense with no fixed date cannot depend on a 30-day clock.
- **Supabase's free Postgres is durable** (no expiry) but **pauses after 7 days of inactivity** (resumable from the dashboard in one click, no data loss). This is a known, already-referenced choice: `.env.example` and `README.md` already say "producción en Supabase" — this research confirms that choice is sound and documents the two things that make it work in practice (see Pitfalls below).

This pairing is two separate free services from two separate vendors — normal for this tier of hosting, and irrelevant to the app since it only ever sees one `DATABASE_URL`.

## System Overview

```
┌────────────────────────────┐        HTTPS :443        ┌──────────────────────────────────────┐
│  Cliente (navegador /       │ ────────────────────────▶│  Render — Edge / Reverse Proxy        │
│  celular en portería)       │◀──────────────────────── │  (terminates TLS, sets X-Forwarded-*) │
└────────────────────────────┘                            └───────────────┬───────────────────────┘
                                                                            │ HTTP (private, internal to Render)
                                                                            ▼
                                                        ┌────────────────────────────────────────────┐
                                                        │  Render — Web Service (free, 1 instance)    │
                                                        │  Docker container from existing Dockerfile  │
                                                        │  entrypoint:                                │
                                                        │   1. alembic upgrade head                   │
                                                        │   2. python -m app.seed   (idempotente)     │
                                                        │   3. uvicorn app.main:app --host 0.0.0.0     │
                                                        │      --port $PORT --proxy-headers            │
                                                        │      --forwarded-allow-ips="*"               │
                                                        │  serves: API routers + StaticFiles("/")      │
                                                        └───────────────┬───────────────────────────────┘
                                                                        │ TLS, public internet
                                                                        │ Session Pooler (IPv4, port 5432)
                                                                        ▼
                                                        ┌────────────────────────────────────────────┐
                                                        │  Supabase — Postgres 16 gestionado (free)   │
                                                        │  14 tablas, esquema vía Alembic              │
                                                        │  pausa tras 7 días de inactividad            │
                                                        └────────────────────────────────────────────┘
```

There is no separate static host and no CDN in front of the app: the same FastAPI process that answers `/api/*` also serves `app/static/` via `StaticFiles(directory=..., html=True)` mounted at `/`. See "Serving the frontend" below for why that stays as-is.

### Component Responsibilities

| Component | Responsibility | Notes for this deployment |
|-----------|----------------|----------------------------|
| Render Edge (reverse proxy) | TLS termination, subdomain routing, sets `X-Forwarded-Proto` / `X-Forwarded-For` | Managed by Render; not configurable, just needs to be trusted correctly by uvicorn |
| Render Web Service (1 instance, free) | Runs the existing Docker image, binds `$PORT`, restarts on crash, sleeps after 15 min idle | Same `Dockerfile`; only the start command changes (adds `alembic` + `seed` before `uvicorn`, reads `$PORT`) |
| FastAPI app (unchanged) | Routers, business logic, `StaticFiles` mount — see `.planning/codebase/ARCHITECTURE.md` | No code changes required beyond `app/main.py` reading `$PORT` and startup command adding `--proxy-headers` |
| Supabase Session Pooler | IPv4-reachable Postgres endpoint, holds a persistent backend connection per client (session mode) | This is the connection string that goes in `DATABASE_URL` — not the "Direct connection" one |
| Supabase Postgres | Durable storage, 14 tables, schema owned by Alembic | Free tier: 500MB–1GB depending on plan snapshot at signup, no daily backups guaranteed |

## Sub-Question Answers

### 1. Where do migrations run?

**At container start, chained before `uvicorn` in the entrypoint — same pattern the project already uses in `docker-compose.yml`** (`alembic upgrade head && uvicorn ...`). This is not a compromise for this project — it's the *only* option Render's free tier allows:

- **Build step: no.** The Docker build has no network access to the database (and shouldn't — build-time and deploy-time secrets are different concerns). Not viable regardless of platform.
- **Release/pre-deploy command: not available on Render's free tier.** Render's `preDeployCommand` (the direct analog of Heroku's release phase) is documented as available "for paid web services, private services, and background workers" — free web services are excluded. Same for Render's Shell/SSH access, needed for a manual one-off `alembic upgrade head`: also paid-only.
- **Container start: the only remaining option, and it's fine here.** The project already does this locally. The one real risk — two instances racing on `alembic upgrade head` — cannot happen on Render's free tier because **free web services are hard-capped at one instance** (no horizontal scaling, no zero-downtime blue/green with two containers alive at once on this tier).

**What breaks if two instances *did* run it concurrently** (relevant if this project is ever promoted to a paid multi-instance tier — worth a one-line comment in the entrypoint script for that future reader): Postgres DDL is transactional per-statement, so the two `alembic upgrade head` runs race to `INSERT` the same row into `alembic_version` or to `CREATE TABLE`/`ALTER TABLE` the same object. One wins, the other gets a duplicate-object or serialization error and the container crashes on boot — a loud, safe failure (not data corruption), but an avoidable one. The standard fix if/when this becomes real is wrapping the migration call in a Postgres advisory lock (`pg_advisory_lock`) in `alembic/env.py` so only one instance runs it while the other blocks and then no-ops. Not needed now — noting it so a future scale-up doesn't get surprised.

**Seed also belongs in this same chain** (see Q4) — `alembic upgrade head && python -m app.seed && uvicorn ...` — for the same reason: it's idempotent, cheap (a handful of `SELECT`/`INSERT`s), and there is no other execution point available on this tier.

### 2. Secrets: platform vs `.env`

Today: `.env` (gitignored) read by `pydantic-settings` (`app/config.py`, `env_file=".env"`). On Render:

- **Set `DATABASE_URL` and `JWT_SECRET` as environment variables in the Render dashboard** (Environment tab on the service), not as a committed file. Render injects them into the container's environment at runtime; `pydantic-settings`' `BaseSettings` already reads from the process environment as well as `.env` (env vars take precedence when both are present), so **no code change is needed** — `.env` simply won't exist in the container and the dashboard-set vars fill the same names.
- **`ADMIN_DOCUMENTO` / `ADMIN_CONTRASENA`** (used only by `app/seed.py`) go in the same place, since the seed step now runs as part of container boot rather than a manual local invocation.
- Do **not** bake secrets into the Dockerfile or a `render.yaml` blueprint committed to the repo — Render's own guidance is to leave those as `sync: false` placeholders and fill the value once in the dashboard. A `JWT_SECRET` that ends up in git history is a secret that has to be rotated the moment anyone notices, and the repo is public.
- `DATABASE_URL`'s value itself changes shape versus local dev: locally it points at `db:5432` (the compose service); on Render it must be **Supabase's Session Pooler connection string** (see Pitfalls), not the "Direct connection" string Supabase shows first in its dashboard.

### 3. Behind Render's reverse proxy — uvicorn flags and port

- **Bind to `$PORT`, not a hardcoded `8000`.** Render sets `PORT` in the container environment (default `10000` if unset, but it will be set) and expects the process to listen there. The current Dockerfile hardcodes `--port 8000` in `CMD` — that needs to become `--port ${PORT:-8000}` (keeping `8000` as the local/compose fallback) or be moved out of `CMD` into an entrypoint script that reads the env var, since Docker's exec-form `CMD` does not expand `$PORT` on its own.
- **Add `--proxy-headers --forwarded-allow-ips="*"`.** uvicorn's `--proxy-headers` is meant to trust `X-Forwarded-Proto`/`X-Forwarded-For` from the connecting peer, but it only trusts peers matching `--forwarded-allow-ips` (default `127.0.0.1`). Render's edge does **not** connect over loopback — it connects from Render's internal network, whose address isn't fixed — so the default trusts nothing and the flag has no effect unless `--forwarded-allow-ips="*"` is also set. `"*"` is safe specifically because Render's container has no other ingress path (nothing else can reach the app's port), so there's no untrusted peer to spoof the header.
- **What breaks if this is wrong:** every request looks like plain HTTP to the app internally (`request.url.scheme == "http"` even though the browser used HTTPS), because Render terminates TLS at its edge and forwards over the private network. Concretely for this app: the browser-facing URL is still `https://…onrender.com` regardless (so `getUserMedia`'s secure-context check for the QR scanner is unaffected — that depends on what the *browser* loaded, not on uvicorn's proxy headers). What *is* affected: any code that inspects `request.url.scheme` or builds absolute URLs (none currently in this codebase, but worth getting right before it's needed), and `request.client.host` — without the flag it reports Render's internal proxy address for every request, not the real client IP, which matters if audit logging (`app/auditoria.py`) is ever extended to record source IP.

### 4. Running `python -m app.seed` as a one-off

Render's free tier has **no Shell/SSH access and no one-off job runner** (both are paid-only features — the same restriction that rules out a separate release-phase migration command in Q1). The seed script already declares itself idempotent ("correrlo dos veces no duplica nada" — verified: every insert in `sembrar()` is guarded by a `SELECT ... filter_by` existence check first). That makes the correct move **the same one as migrations: fold it into the entrypoint, after `alembic upgrade head`, before `uvicorn` starts.** It runs on every boot (including every cold-start wake after 15 min idle), does a handful of cheap `SELECT`s, and is a true no-op after the first successful run. No platform feature is needed at all — the idempotency already built into the script is what makes this work without a "run once" mechanism.

### 5. Static frontend: same app vs separate static host

**No reason to split it for this deployment — keep it as-is.** Splitting would mean:
- A second free service to provision, deploy, and keep in sync with API changes (Render static sites are free and simple, but it's still a second moving part with its own build/deploy step).
- Cross-origin requests from the static site to the API, which means CORS configuration that doesn't exist today, plus cookies/auth headers now crossing an origin boundary — new attack surface and new failure modes for zero user-facing benefit at this scale (one demo, one grader, no meaningful traffic).
- The QR scanner's secure-context requirement is already satisfied by Render's HTTPS on the single origin — splitting doesn't unlock anything there.

The only real argument *for* splitting (serving static assets from a CDN edge instead of the app's single instance) doesn't apply: this app has a handful of KB of HTML/JS, not a media-heavy frontend, and the single Render instance already serves it fine. Splitting here is complexity with no payoff — same conclusion the project already reached in `PROJECT.md` about not running a self-managed proxy.

### 6. What the deployment diagram should show

For the UML deployment diagram (`diagrama de despliegue`) deliverable, the topology above maps directly to nodes/artifacts/protocols:

**Nodes** (physical/execution environments — `<<device>>` or `<<execution environment>>`):
- `<<device>> Cliente` — navegador de escritorio o celular
- `<<execution environment>> Render Web Service` — contenedor Docker, instancia única, free tier
- `<<execution environment>> Supabase Postgres` — instancia Postgres 16 gestionada

**Artifacts** (deployed inside each node):
- Inside the Render node: `skilledguard-api.image` (the Docker image built from the existing `Dockerfile`), containing the FastAPI app, Alembic migration scripts, and `app/static/` assets
- Inside the Supabase node: the schema/database itself (14 tables), not usually drawn as a separate artifact beyond the node

**Communication paths / protocols** (labeled associations between nodes):
- Cliente ↔ Render: `HTTPS (TLS 1.2+, puerto 443)`
- Render ↔ Supabase: `PostgreSQL wire protocol over TLS (sslmode=require), puerto 5432, vía Session Pooler (IPv4)` — worth labeling explicitly as *pooler*, not direct connection, since that's the non-obvious part a grader reading the diagram wouldn't otherwise know to ask about

This is a two-node deployment diagram, not three — resist the urge to draw Render's reverse proxy as its own node with its own box; it's an internal implementation detail of the Render node, not a separately deployed artifact this project controls or configures (beyond the two uvicorn flags in Q3). Drawing it as a third node overstates what's actually being deployed and invites questions about a component that has no artifact of its own here.

## Patterns to Follow

### Pattern 1: Migrate-and-seed-at-boot, guarded by idempotency

**What:** Chain `alembic upgrade head && python -m app.seed && uvicorn ...` as the container's start command instead of any of migrate/seed as separate lifecycle steps.
**When to use:** Single-instance deployments on platforms without a release-phase/one-off-job feature (i.e., exactly this Render free-tier case).
**Trade-off:** Every cold-start pays a small fixed cost (a few `SELECT`s + an `alembic` no-op check) — negligible next to the 30–60s proxy cold-start itself. Stops being safe the moment the app runs on more than one instance without an advisory lock (not a concern on this tier, but don't copy this pattern forward blindly if the project ever moves to paid/multi-instance).

### Pattern 2: Connect to managed Postgres via its pooler, not its direct address

**What:** Use Supabase's **Session Pooler** connection string (IPv4, port 5432, supports prepared statements) for `DATABASE_URL`, not the "Direct connection" string Supabase surfaces first.
**When to use:** Any persistent, long-lived backend process (this FastAPI app, holding its own SQLAlchemy connection pool) connecting to Supabase from a host without guaranteed IPv6 egress — which includes Render.
**Trade-off:** None meaningful at this scale — Session mode behaves like a normal persistent connection from the app's point of view. (Supabase's *Transaction* pooler is the wrong mode here: it doesn't support prepared statements and is meant for short-lived/serverless callers, not a long-running app with its own pool.)

## Anti-Patterns to Avoid

### Anti-Pattern 1: Supabase's "Direct connection" string on Render

**What people do:** Copy the first connection string Supabase's dashboard shows (`db.<ref>.supabase.co:5432`) into `DATABASE_URL`.
**Why it's wrong:** That hostname resolves **only to an IPv6 address**. Render (like most PaaS free tiers) doesn't guarantee outbound IPv6, so the connection fails with `ENETUNREACH`/network-unreachable errors that look like a firewall or credentials problem but are actually a DNS/protocol mismatch. This is a documented, recurring issue specific to the Render/Railway + Supabase combination, not a hypothetical.
**Instead:** Use the Session Pooler connection string (has an IPv4 address, same host format but through Supabase's Supavisor pooler).

### Anti-Pattern 2: Treating the free-tier cold start as a bug to "fix"

**What people do:** Try to keep the Render free instance always warm with an external cron pinger, or upgrade to a paid plan "just to be safe" before the demo.
**Why it's wrong:** Violates the project's explicit zero-budget constraint for no real benefit — a 30–60s cold start once, before the demo starts, is a non-issue if the presenter opens the URL a minute before starting to talk. Engineering around it (external keep-alive pingers, extra scheduled jobs) adds moving parts to a project whose stated goal this cycle is "entregar y sustentar," not build more infrastructure.
**Instead:** Warm the app manually (open the URL) a minute or two before the demo. Apply the same manual-warm-up to Supabase if it's been more than 7 days since the last request (dashboard "resume," one click, near-instant — it's not a cold boot, just an unpause).

### Anti-Pattern 3: Committing a filled-in `render.yaml` or `.env` with real secrets for "reproducibility"

**What people do:** Commit a Render Blueprint (`render.yaml`) with `DATABASE_URL`/`JWT_SECRET` values inline, reasoning that it documents the deployment.
**Why it's wrong:** The repository is public (per `PROJECT.md`, this is an already-known constraint of this project). A committed secret is compromised the moment the commit is pushed, not the moment someone notices.
**Instead:** If a Blueprint is used at all, declare the secret keys with `sync: false` (Render prompts for the value once, in the dashboard, at Blueprint creation) — or skip the Blueprint entirely and configure the one service by hand in the dashboard, which is simpler for a single-service project like this one anyway.

## Scaling Considerations

Not meaningfully applicable — this is a one-grader, one-demo deployment, and the "Out of Scope" section of `PROJECT.md` already rules out anything beyond the free tier. The only table worth keeping is what actually changes between "works for a demo" and "would need real engineering," in case the roadmap needs to flag it:

| Concern | This project (free tier, 1 instance) | If it ever needed to scale |
|---------|----------------------------------------|------------------------------|
| Concurrent migrations | Impossible — free tier caps at 1 instance | Add `pg_advisory_lock` around the migration step |
| Cold starts | Manual warm-up before demo | Paid "always on" plan removes the 15-min sleep |
| DB availability | Manual resume from Supabase dashboard if paused >7 days | Paid Supabase plan removes the pause |
| Static asset serving | Same app, same instance | CDN in front, only if asset volume grows well beyond a few KB of HTML/JS |

## Build Order Implications for the Roadmap

The four things below have a real dependency order — later steps need the DATABASE_URL / uvicorn changes from earlier ones to be verifiable at all:

1. **Code changes first, no external dependency:** entrypoint reads `$PORT`, adds `--proxy-headers --forwarded-allow-ips="*"`, chains `alembic upgrade head && python -m app.seed && uvicorn ...`. This is verifiable locally against the existing `docker-compose.yml` before touching any cloud account.
2. **Provision Supabase**, get the **Session Pooler** connection string (not Direct), confirm `psql`/local connection works from a machine outside Supabase's network (proves IPv4 pooler reachability before Render is even in the picture).
3. **Provision Render web service**, point it at the branch that actually has this code (`develop` — `main` is still the retired .NET tree per `PROJECT.md`; this is a repository-hygiene decision that has to land before or alongside this step, otherwise Render deploys the wrong branch by default). Set `DATABASE_URL` (Supabase pooler string), `JWT_SECRET`, `ADMIN_DOCUMENTO`, `ADMIN_CONTRASENA` in the dashboard.
4. **First deploy → verify `/salud` returns 200, verify the seeded admin can log in, verify the QR scanner works from an actual phone against the `https://…onrender.com` URL** (this last check is the one that actually validates the HTTPS/secure-context requirement flagged in `PROJECT.md` — it can't be verified any earlier in the sequence).

## Sources

- [Deploy for Free – Render Docs](https://render.com/docs/free)
- [Render changelog: free PostgreSQL instances now expire after 30 days](https://render.com/changelog/free-postgresql-instances-now-expire-after-30-days-previously-90)
- [Render changelog: pre-deploy command](https://render.com/changelog/predeploy-command) — paid-only, confirmed via Render community/docs
- [SSH and Shell Access – Render Docs](https://render.com/docs/ssh) — free tier excluded
- [Web Services – Render Docs](https://render.com/docs/web-services) — `$PORT` binding
- [Uvicorn Settings docs](https://uvicorn.dev/settings/) — `--proxy-headers`, `--forwarded-allow-ips`
- [FastAPI: Behind a Proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy/)
- [Supabase Troubleshooting: IPv4/IPv6 compatibility](https://supabase.com/docs/guides/troubleshooting/supabase--your-network-ipv4-and-ipv6-compatibility-cHe3BP)
- [Supabase Troubleshooting: Supavisor FAQ (session vs transaction pooler)](https://supabase.com/docs/guides/troubleshooting/supavisor-faq-YyP5tI)
- [Supabase: connecting to Postgres](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Fly.io free tier status, 2026 (removed for new accounts)](https://www.saaspricepulse.com/blog/flyio-free-tier-2026)
- [Railway free tier, 2026 ($1/mo after trial)](https://www.saaspricepulse.com/tools/railway)
- Existing codebase: `docker-compose.yml` (already runs `alembic upgrade head && uvicorn ...`), `app/seed.py` (idempotency verified by reading), `app/config.py` (`pydantic-settings` env precedence), `.env.example` (Supabase already the stated production DB), `README.md` (confirms Supabase intent)

---
*Architecture research for: SkilledGuard deployment topology (free PaaS + managed Postgres)*
*Researched: 2026-08-09*
