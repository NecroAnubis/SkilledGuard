# Stack Research: Free-Tier Deployment (FastAPI + Docker + PostgreSQL)

**Domain:** Zero-cost PaaS hosting for a containerized FastAPI app with managed Postgres, needs to survive a live graded demo
**Researched:** 2026-08-09
**Confidence:** MEDIUM-HIGH (platform limits verified against official docs/changelogs where cited; some numbers only found in secondary sources — flagged per item)

## Recommended Stack

### Core Technologies

| Technology | Plan | Purpose | Why Recommended |
|------------|------|---------|-----------------|
| **Render** — Web Service (Docker) | Free (750 instance-hrs/mo) | Runs the existing Dockerfile, terminates TLS, gives `*.onrender.com` HTTPS subdomain automatically | Only mainstream Docker PaaS still open to **new** signups with a real always-free web-service tier in Aug 2026. No credit card needed. [Confidence: HIGH — official docs + changelog] |
| **Supabase** — Postgres | Free (500MB DB, shared compute) | Managed PostgreSQL 16-compatible, matches what the app already expects (`psycopg`, `DATABASE_URL`) | README already claims it; unlike Render's own free Postgres it does **not get deleted after 30 days** — only *paused* after 7 days of inactivity, recoverable for up to a year. [Confidence: HIGH — official docs] |
| **cron-job.org** (or a public-repo **GitHub Actions** scheduled workflow) | Free | Pings `GET /salud` every ~10 min | Turns Render's 15-min sleep into a non-issue and simultaneously keeps the Supabase project inside its "active" 7-day window — one ping mitigates both platforms' idle-out risk. [Confidence: HIGH — mechanism is standard, widely documented] |

### Why not the "obvious" alternatives

The instinct is to reach for Fly.io, Railway, Koyeb, or Vercel — verified in 2026 that **none of them give a real always-free Docker web service anymore**:

- **Koyeb**: Mistral AI acquired Koyeb in February 2026 and **closed the free tier to new signups** as part of folding the product into "Mistral Compute" for enterprise/GPU workloads. Existing accounts keep free access; a *new* account created today cannot get one. [Confidence: HIGH — TechCrunch coverage of the acquisition + Koyeb's own pricing page shows no free compute plan, only a "Free 5h/day" Postgres dev tier]
- **Fly.io**: killed permanent free allowances for new orgs in 2024; today new accounts get a $5 trial credit or "2 VM-hours / 7 days," not a perpetual free tier. [Confidence: HIGH — Fly's own pricing docs + multiple 2026 comparison posts agree]
- **Railway**: 30-day trial with $5 credit, then reverts to a "Free" plan that is really **$1/month of usage credit** — not enough to run one container 24/7 for a full month, so it silently stops being zero-cost. [Confidence: MEDIUM — Railway's own trial docs confirm the $5/30-day trial mechanics; the "$1/mo after trial" figure is corroborated by two independent secondary sources but not quoted verbatim from Railway's pricing page]
- **Vercel**: now runs Dockerfiles, but only as *serverless Vercel Functions* — stateless, scale-to-zero after 5 minutes idle, with execution-duration limits. It's built for request/response functions, not a persistent FastAPI process with SQLAlchemy's connection pool and an Alembic migration step at boot. Wrong execution model for this app. [Confidence: HIGH — Vercel's own docs/changelog]
- **Render's own free Postgres**: real, but free databases **expire 30 days after creation** and are hard-deleted after a 14-day grace period unless upgraded to paid. Since this project has "no sustentación date defined," a DB with a 44-day death clock is a trap — use Supabase for the DB, Render only for compute. [Confidence: HIGH — official Render changelog]

### Secondary / fallback option

| Technology | Purpose | When to use it instead |
|------------|---------|-------------------------|
| **Hugging Face Spaces — Docker SDK** | Alternative compute host | If Render's 750h/mo or bandwidth limits ever become a problem. Free CPU-basic Docker Spaces only sleep after **48 hours** of inactivity (vs. Render's 15 min), so the cold-start risk is far lower and a keep-alive ping becomes optional insurance rather than a requirement. Gives an automatic HTTPS subdomain (`*.hf.space`) too. Downside: culturally branded as an ML-demo host, which may prompt an odd question in the sustentación ("¿por qué Hugging Face para un backend normal?"); Render reads as a more conventional cloud PaaS for the written report. [Confidence: HIGH — official HF docs]

## Installation / Configuration

No new packages — the app is already Dockerized. This is platform configuration, not code:

```bash
# Render Web Service settings
# - Environment: Docker (uses the existing Dockerfile as-is)
# - Region: any (Oregon/Frankfurt are default free options)
# - Health check path: /salud   (already implemented, matches Docker healthcheck)
```

```bash
# Environment variables to set in Render's dashboard (never commit these)
DATABASE_URL=postgresql+psycopg://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?sslmode=require
JWT_SECRET=<generate a strong random value, not the local dev one>
JWT_EXPIRACION_MINUTOS=60
ADMIN_DOCUMENTO=<seed value for first run only>
ADMIN_CONTRASENA=<seed value for first run only>
```

**Critical detail on the `DATABASE_URL`:** use Supabase's **Session Pooler** connection string (port `5432`, host `*.pooler.supabase.com`), not the "Direct connection" string Supabase shows first. Render's platform does **not support outbound IPv6**, and Supabase's Direct Connection is IPv6-only unless you pay for the IPv4 add-on (~$4/mo — violates the zero-cost constraint). The Session Pooler is IPv4 and, unlike the Transaction Pooler (port `6543`), preserves full session/prepared-statement semantics — needed for Alembic's DDL statements. Add `sslmode=require` (Supabase requires SSL). [Confidence: HIGH for the IPv4/IPv6 mechanics — official Supabase troubleshooting docs; MEDIUM for "session pooler over transaction pooler for Alembic specifically" — Supabase's own guidance says "use Direct Connection for migrations," it does not explicitly bless Session Pooler as the IPv4 substitute for migrations, but it does explicitly say Session Pooler is "recommended as an alternative to Direct Connection for IPv4 networks," which is exactly Render's situation]

**Migrations on deploy:** don't reach for Render's "pre-deploy command" feature — whether it's available on the *free* instance tier could not be confirmed from official docs (it's documented for paid services only). The app already solves this: `docker-compose.yml` runs `alembic upgrade head` before `uvicorn` starts in the container's own entrypoint. Keep that exact entrypoint unchanged for Render — it runs migrations on every container start regardless of platform, which is more portable than any platform-specific hook. [Confidence: HIGH — reuses an already-working, verified pattern instead of an unverified platform feature]

**Start command (uvicorn, proxy headers):**

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips="*"
```

Render assigns `$PORT` itself and puts its own edge proxy in front of every container — the container is never reached directly from the public internet, only from Render's proxy. That's why `--forwarded-allow-ips="*"` is the pragmatic choice here (Render doesn't publish a fixed, documentable internal proxy IP to pin instead). This makes `X-Forwarded-For`/`X-Forwarded-Proto` trusted so `/salud` and audit logs record the real client IP instead of Render's internal address. [Confidence: MEDIUM — the uvicorn flag mechanics are HIGH-confidence (official uvicorn docs), but "safe to trust `*` specifically because Render's architecture prevents direct container access" is inferred/architectural reasoning, not a sentence pulled verbatim from Render's docs]

**Keep-alive ping (do this — it is not optional given the demo requirement):**

```yaml
# .github/workflows/keep-alive.yml (public repo → free, unlimited Actions minutes)
name: keep-alive
on:
  schedule:
    - cron: "*/10 * * * *"   # every 10 min, well under Render's 15-min sleep threshold
  workflow_dispatch: {}       # manual "warm it up now" button before the live demo
jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - run: curl -fsS https://<your-app>.onrender.com/salud
```

`/salud` already checks the DB per the app's existing health endpoint, so this single ping keeps **both** Render's compute and the Supabase project inside their "active" windows. Run `workflow_dispatch` manually ~5 minutes before the live sustentación as a final safety net.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|--------------------------|
| Render (compute) | Hugging Face Spaces (Docker SDK) | If Render's 750h/mo free budget or its 15-min sleep proves flaky in practice; HF's 48h sleep window is strictly safer for a demo, at the cost of looking less like a "normal" cloud deploy in the written report |
| Supabase (Postgres) | Neon | Neon's free compute auto-suspends after idle and **auto-resumes on the next connection** (no manual dashboard click), which is arguably safer than Supabase's pause (which needs a manual "Resume" click in the dashboard and does not resume itself on a stray connection attempt). Not the top pick only because the project's own README/docs already reference Supabase — switching adds unnecessary churn this cycle. [Confidence: MEDIUM — Neon's autosuspend/auto-resume-on-connect behavior is well documented for its free tier; not independently re-verified in this pass] |
| GitHub Actions cron ping | cron-job.org / UptimeRobot free monitor | Use these if the repo becomes private (GitHub Actions free minutes apply to public repos; private repos have a monthly cap) or if you want a status dashboard/alerting on downtime |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| Koyeb (new signup) | Free tier closed to new accounts since the Mistral AI acquisition (Feb 2026); you cannot get one today | Render |
| Fly.io | No perpetual free tier since 2024; new accounts get a 7-day/$5 trial, then billing starts | Render |
| Railway "Free" plan | $1/month usage credit does not cover a container running 24/7 for a month — it will ask for a card or suspend | Render |
| Vercel for the API container | Serverless-function execution model (5-min idle scale-down, execution duration caps, stateless) is the wrong shape for a persistent FastAPI + SQLAlchemy pool + boot-time Alembic migration | Render |
| Render's free managed Postgres | Hard-expires 30 days after creation, deleted 14 days after that unless upgraded to paid — incompatible with an indefinite "no sustentación date yet" timeline | Supabase (or Neon) |
| Supabase Direct Connection string on Render | It's IPv6-only unless you pay for the IPv4 add-on; Render has no outbound IPv6 → connection will fail | Supabase Session Pooler connection string (IPv4, port 5432) |

## Version Compatibility

| Component | Compatible With | Notes |
|-----------|------------------|-------|
| psycopg[binary] 3.2.3 (already in `requirements.txt`) | Supabase Session Pooler (PgBouncer session mode) | Session mode preserves full protocol/prepared-statement support that psycopg/SQLAlchemy expect; the Transaction Pooler (port 6543) does not, and can break Alembic DDL or SQLAlchemy's session assumptions |
| Alembic 1.14.0 | Any of the above Postgres hosts | No changes needed — it's a standard `postgresql://` connection string either way, only host/port/sslmode change |
| uvicorn 0.34.0 `--proxy-headers` | Render's edge proxy | Flag already exists in this uvicorn version; no upgrade needed |

## Sources

- [Render — Deploy for Free (official docs)](https://render.com/docs/free) — free web service limits, spin-down behavior (Confidence: HIGH)
- [Render — Free PostgreSQL instances now expire after 30 days (official changelog)](https://render.com/changelog/free-postgresql-instances-now-expire-after-30-days-previously-90) — free DB expiration policy (Confidence: HIGH)
- [Render — Outbound IP Addresses (official docs)](https://render.com/docs/outbound-ip-addresses) / Render community discourse thread on Supabase IPv6 issues — no outbound IPv6 (Confidence: MEDIUM-HIGH, mechanics confirmed by official docs + corroborated by a live community bug report)
- [Render — Run migrations and other tasks with the pre-deploy command (changelog)](https://render.com/changelog/predeploy-command) — pre-deploy feature exists but free-tier availability unconfirmed (Confidence: MEDIUM)
- [Supabase — Free Project Pausing (official docs)](https://supabase.com/docs/guides/platform/free-project-pausing) — 7-day inactivity pause, manual resume, 1-year restore window (Confidence: HIGH)
- [Supabase — Connect to your database (official docs)](https://supabase.com/docs/guides/database/connecting-to-postgres) — Direct vs. Transaction Pooler vs. Session Pooler, IPv4/IPv6, migrations guidance (Confidence: HIGH)
- [Supabase — Dedicated IPv4 Address for Ingress (official docs)](https://supabase.com/docs/guides/platform/ipv4-address) — IPv4 add-on cost and dual-stack behavior (Confidence: HIGH)
- [Koyeb — Scale-to-Zero (official docs)](https://www.koyeb.com/docs/run-and-scale/scale-to-zero) — free instance 1h idle timeout, Deep Sleep 1–5s cold start, Light Sleep not on free tier (Confidence: HIGH, but tier itself now closed to new users)
- [TechCrunch — Mistral AI buys Koyeb (Feb 2026)](https://techcrunch.com/2026/02/17/mistral-ai-buys-koyeb-in-first-acquisition-to-back-its-cloud-ambitions/) + Koyeb's own pricing page (no free compute plan visible) — free tier closed to new signups (Confidence: HIGH)
- [Fly.io — Resource Pricing (official docs)](https://fly.io/docs/about/pricing/) — no perpetual free allowance for new orgs (Confidence: HIGH)
- [Railway — Free Trial (official docs)](https://docs.railway.com/pricing/free-trial) — $5/30-day trial mechanics (Confidence: HIGH); "$1/mo after trial" figure (Confidence: MEDIUM, secondary sources)
- [Vercel — Run Docker containers / Dockerfile support (official changelog + blog)](https://vercel.com/changelog/run-docker-containers-inside-vercel-sandbox) — serverless-function execution model, 5-min idle scale-down (Confidence: HIGH)
- [Hugging Face — Docker Spaces (official docs)](https://huggingface.co/docs/hub/en/spaces-sdks-docker) / Spaces Overview docs — 48h inactivity pause on free CPU-basic hardware (Confidence: HIGH)
- [Uvicorn — Settings (official docs)](https://uvicorn.dev/settings/) — `--proxy-headers` / `--forwarded-allow-ips` semantics (Confidence: HIGH)
- Oracle Cloud Always Free ARM limits halved to 2 OCPU/12GB (effective Aug 18, 2026) — researched but **not part of the recommendation**, since the project already ruled out running its own VPS/Caddy; noted only in case that constraint is revisited (Confidence: MEDIUM — corroborated by multiple 2026 posts, not cross-checked against Oracle's own docs page directly)

---
*Stack research for: zero-cost Docker + managed Postgres deployment*
*Researched: 2026-08-09*
