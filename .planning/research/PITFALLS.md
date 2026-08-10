# Pitfalls Research

**Domain:** Deploying a working student FastAPI + PostgreSQL app to a free-tier PaaS and defending it live (sustentación ADSO/SENA)
**Researched:** 2026-08-10
**Confidence:** MEDIUM — core facts (Render Postgres 30-day expiry, `getUserMedia` secure-context rule, Supabase pause policy) confirmed against official docs/changelogs; several platform specifics (exact cold-start seconds, iOS PWA behavior) come from single blog sources and should be re-verified by actually timing the chosen platform once selected, not trusted blindly.

## Critical Pitfalls

### Pitfall 1: The service is asleep when the instructor clicks the link

**What goes wrong:**
Free web-service tiers stop the container after a window of no inbound traffic. The first request after that window pays a "cold start" — the evaluator's browser spins for tens of seconds with nothing visible, which reads as "broken" in an oral defense, not "slow."

**Why it happens:**
Free compute is oversold by sleeping idle containers. Concrete numbers found:
- **Render** (free web service): sleeps after **15 minutes** of no inbound traffic; cold start on wake is roughly **30–60 seconds**. 750 free compute-hours/month shared across free services.
- **Koyeb** (free instance): scales to zero after **1 hour** idle, and this **cannot be disabled** on the free tier; wake is faster, **~1–5 seconds**.
- **Fly.io**: no longer has a real free tier since 2024 — new accounts get a $5 / 7-day trial only. Not viable as "the" host for a project with no fixed defense date.
- **Railway**: same story — $5 one-time trial (30 days), then $1/month credit. Not durable enough to sit idle for weeks between defense scheduling and the actual event.

This means the platform choice itself is part of the pitfall: Render is the most commonly recommended zero-cost Docker host, but its 15-minute/30-60s sleep is the single biggest live-demo risk in this project.

**How to avoid:**
- Treat "wake it up before walking into the room" as a mandatory pre-demo step, not optional: load the app's own URL (not just `/health`, hit a real DB-backed endpoint like login) **5–10 minutes before** the defense starts, and again right before presenting, so the 15-minute Render window never elapses mid-defense.
- If the instructor might poke around after the formal demo (common in ADSO defenses — they click things), keep the tab open and interact with it periodically instead of ending the demo, since Render's 15-min clock resets on every hit.
- A ping-based keep-alive (e.g., a free external cron like cron-job.org hitting `/health` every 10 minutes) works but only during the exact hours you expect to need it — running it 24/7 for weeks burns into the 750 free-hours/month cap for no benefit, since nobody is watching the app between sessions. Turn it on the day of the defense, not before.
- Do not rely on the browser tab you tested with days earlier being "still warm" — sleep state does not persist across sessions.

**Warning signs:**
First request of any test session taking noticeably longer than subsequent ones is the sleep/wake cycle working exactly as designed — that's the signal to always do a warm-up hit as the literal first action of any demo rehearsal or the real defense.

**Phase to address:** Deployment phase (choosing/configuring the PaaS) and the demo-rehearsal phase (building the warm-up-before-presenting habit into the actual script).

---

### Pitfall 2: The camera never opens because the page isn't a secure context

**What goes wrong:**
`getUserMedia()` — the API the QR scanner depends on — is unavailable, not just denied, in insecure contexts. On a non-secure origin, `navigator.mediaDevices` itself is `undefined`, so the scanner code throws before it even gets to ask for permission. This is the exact risk PROJECT.md already flags, and it is the single point of failure for the demo's centerpiece feature.

**Why it happens:**
A "secure context" is HTTPS, `file://`, or `localhost` specifically — nothing else. Concretely, this breaks the scanner in three situations a student is likely to hit while preparing:
- Testing from a phone against the machine's **local IP** (e.g., `http://192.168.1.x:8000`) — this is *not* localhost and *not* HTTPS, so it fails even though it "worked on my laptop" (laptop's `localhost` is the exception; the phone's request to that IP is not).
- A **self-signed certificate** used to fake HTTPS locally — browsers on desktop may let you click through an "unsafe" warning, but the underlying context still may not register as secure the same way, and mobile browsers are far less forgiving of self-signed certs.
- Any deployment where the public URL is plain `http://` — sleeping this until the PaaS's HTTPS is confirmed working is not cosmetic, it is the feature.

**How to avoid:**
- Confirm the deployed URL is `https://` (the PaaS should terminate TLS automatically — Render, Koyeb, etc. all do this for free) and that FastAPI/uvicorn is not redirecting or mixing content back to `http://` anywhere (check `--proxy-headers` below, Pitfall 9).
- Never demo the scanner against a local IP or a bare `http://` tunnel. If a local rehearsal is needed before deploy, use a tunnel that gives real HTTPS (e.g., `ngrok http 8000`, free tier) rather than a self-signed cert.
- Test the actual failure mode once on purpose (open the deployed `http://` variant if the PaaS exposes one, or the raw IP) so you recognize the exact error (`mediaDevices is undefined` / permission prompt never appears) and don't confuse it with a different bug during rehearsal.

**Warning signs:**
No camera permission prompt appears at all (not even a "denied" state) — that is the signature of an insecure-context failure, distinct from a permissions problem, and means the fix is the URL/protocol, not the app code.

**Phase to address:** Deployment phase (HTTPS must be live before this is testable) and QR-scanner verification phase (explicit test from a real phone against the real HTTPS URL, not assumed from desktop testing).

---

### Pitfall 3: The scanner worked in rehearsal but fails on the actual iPhone in the room

**What goes wrong:**
iOS Safari has camera behavior that diverges from desktop Chrome in ways that only show up on a real device, which is exactly the device most likely to be used to "prove it works on a phone" during the defense.

**Why it happens:**
- iOS Safari only prompts for camera access over genuine HTTPS with a trusted certificate; a self-signed cert has to be manually installed as a trusted profile on the device or Safari blocks it silently rather than showing a clear error.
- `getUserMedia` support on iOS Safari only exists from **iOS 14.3 onward** — an older or un-updated device (a classmate's phone borrowed on the day) can simply not have the API at all.
- If the page was ever "Added to Home Screen" and is opened as an installed PWA in standalone mode, camera access can fail even though the exact same URL works fine in a normal Safari tab — the browser doesn't show the permission prompt in that mode.

**How to avoid:**
- Test on the specific phone that will be used in the defense, in a normal Safari tab (not an installed/home-screen icon), at least once before the day itself.
- If borrowing a device is a possibility, confirm iOS version is 14.3+ beforehand — don't discover this live.
- Since the deployment target is a real PaaS with a real CA-issued certificate (not self-signed), the certificate-trust problem should not apply in production — but it's worth explicitly ruling out during rehearsal so it's not confused with a code bug if something does go wrong.

**Warning signs:**
Scanner works on Android/desktop Chrome but the exact same URL fails silently on an iPhone — check standalone/home-screen mode and iOS version before suspecting the backend.

**Phase to address:** QR-scanner verification phase — explicit checklist item to test on a physical iPhone in a plain Safari tab, not just Android/desktop.

---

### Pitfall 4: The database is paused and "restoring" while the instructor watches

**What goes wrong:**
Free managed Postgres tiers suspend the database after inactivity, separately from the web service sleeping. If the DB was last touched more than the platform's inactivity window ago (which is very likely between rehearsal and the actual defense — these gaps are often days or weeks per PROJECT.md's "sin fecha definida"), the first query after the gap pays a restore cost on top of whatever the web service's own cold start already costs.

**Why it happens, with real numbers:**
- **Supabase** free-tier projects pause after **7 days** of no activity. Restoring is a one-click action from the dashboard and reportedly takes **a couple of minutes** — but it requires a human to notice and click restore; it does not resume automatically from just an incoming app request the way compute cold starts do. Left alone past **90 days** paused, the automatic restore button is disabled entirely and the project's infrastructure (including its unique connection URL) can be released, which is a much bigger recovery than "wait a minute."
- **Render** free Postgres does not "pause and resume" — it **expires 30 days after creation** and is deleted after a further 14-day grace period if not upgraded. This is worse for a project with no fixed defense date: the database has a hard expiration clock from the day it's created, unrelated to whether the defense has happened yet.
- **Neon** free tier scales compute to zero on idle but reports a genuinely fast cold start (roughly 300–800ms to reinitialize, under a second to first query) — closer to "invisible" than Render's or Supabase's behavior, because Neon's scale-to-zero is designed to be transparent per-request rather than requiring a manual restore click.

**How to avoid:**
- Do not assume "the DB is up because I deployed it once." Whichever provider is chosen, know its specific inactivity clock and build the defense-day checklist around it:
  - If Supabase: check the dashboard for a "paused" banner **the day before** the defense, not the hour before, since restoring is manual and you don't want that discovery to happen live.
  - If Render Postgres: track the 30-day creation date explicitly (calendar reminder) since the DB dies on a schedule independent of demo activity — a defense delayed past that window without anyone re-provisioning means arriving to a deleted database.
  - If Neon: the scale-to-zero cold start is fast enough that a simple pre-demo warm-up query (same login hit that wakes the web service) is sufficient, no separate dashboard check needed.
- Whatever is chosen, do one full "pause → wake → time it" dry run at least once so the actual number (not the blog-post number) is known and can be built into the pre-demo warm-up buffer.

**Warning signs:**
A login or first query that used to be instant taking multiple seconds, or a dashboard banner saying "paused"/"suspended" — check the DB provider's dashboard directly rather than assuming it's an app bug.

**Phase to address:** Deployment phase (this is a factor in *which* managed Postgres to pick, not just a footnote) and demo-rehearsal phase (the pre-demo warm-up sequence must wake DB and web service both, in the right order).

---

### Pitfall 5: The deployed system has an admin login and nothing else to show

**What goes wrong:**
Right now, `app/seed.py` seeds catalog tables (`TipoDocumento`, `TipoDispositivo`, `TipoRegistro`, `TipoAccion`, `Rol`) and exactly **one admin user** — no sample `Dispositivo` records, no porteria movement history, no non-admin users (vigilante role) to log in as. A freshly deployed, freshly migrated database is, functionally, an empty shell with a login screen. An evaluator who logs in sees empty tables everywhere: no devices to scan, no history for the reports feature, no audit trail to point at as evidence the system works under real use.

**Why it happens:**
Seed scripts get written early to make local dev/tests possible (this is exactly what the current `seed.py` does — it exists for bootstrapping, not for demoing), and nobody circles back to build a second, richer seed meant for showing the system off. It's easy to mistake "the seed script runs without error" for "the demo data is ready."

**How to avoid:**
- Build a **separate demo-seed step** (can extend `seed.py` or be a standalone script run once against the deployed DB) that creates:
  - A handful of `Dispositivo` records across different `TipoDispositivo` values, with realistic names (not "Test Device 1", "asdf") — e.g., "Portátil Dell Latitude 5420 — Serie XJ4821", "Videobeam Epson PowerLite".
  - A mix of **states**: some devices currently "out" (salida registered, no entrada), some "in", so the porteria screen and the state-validation logic (double-entry/double-exit prevention) have something to actually demonstrate.
  - Enough `AuditoriaNegocio` / movement history (several days' worth, spread out, not all timestamped seconds apart) that the reports feature produces a report that looks like real operational data, not three rows.
  - At least one non-admin user with the vigilante role, with credentials the presenter has memorized, to show the role-based access difference live (this is a validated requirement — "control de acceso por rol" — and it's much more convincing demonstrated than described).
- Do **not** seed with obviously fake placeholder text (evaluators notice "Equipo 1", "asdasd", "prueba prueba") — a rubric evaluator reading realistic Spanish device names and observations reads as a system that's been used, not a shell that was populated five minutes ago (even though it was).

**Warning signs:**
Logging into the deployed instance and finding every list view empty or filled with single-word test strings is the exact state to catch and fix *before* the defense, not during it.

**Phase to address:** A dedicated demo-data-preparation phase, run **after** deployment is stable (so the seed targets the real managed DB) and **before** the rehearsal phase (so rehearsal happens against realistic data, not the empty shell).

---

### Pitfall 6: Migrations fail (or silently don't run) against the fresh managed database

**What goes wrong:**
The first deploy to a brand-new managed Postgres instance is the first time the full Alembic migration chain runs against a truly empty database. If this step is missed, misconfigured, or fails partway, the app either won't boot (foreign-key/table errors) or boots but 500s on the first real request.

**Why it happens, common causes found:**
- **Migrations never explicitly run as a deploy step.** It's easy to assume the app "will just work" once deployed, forgetting `alembic upgrade head` has to be run against the *new* database — this is a distinct action from the app starting, and PaaS platforms don't do it automatically unless it's wired into the start command or a release/predeploy hook.
- **Wrong `DATABASE_URL` or `sslmode`.** A managed Postgres connection failure often surfaces as what looks like a migration error, when the real problem is the connection string (host/port/sslmode) is wrong for the new provider — this project already has `sslmode=require` intended from the shelved `feature/https-produccion` branch; make sure it's actually applied to the deployed config.
- **Connecting through a pooler instead of the direct connection.** If the chosen Postgres provider offers a pooled connection endpoint (e.g., Supabase's Supavisor on port 6543) alongside a direct one (port 5432), Alembic/DDL operations should go through the **direct** connection — pooled/transaction-mode connections don't support the session-level behavior migrations rely on, and can fail in confusing ways.
- **Local and prod migration history diverging** — if a migration file was edited after being applied locally, the "head" alembic expects and what's recorded in a fresh DB's `alembic_version` won't line up cleanly.

**How to avoid:**
- Make `alembic upgrade head` an explicit, visible step in the deploy process (a Render "pre-deploy command", a startup script, or a documented manual step run once against the new DB) — not something assumed to happen implicitly.
- Verify with `alembic current` against the deployed DB matches the repo's latest revision before considering deploy successful.
- Point the app's `DATABASE_URL` at the **direct** connection string if the provider distinguishes pooled vs. direct, and confirm `sslmode=require` is set for managed Postgres providers that require it.
- Do this check *before* seeding demo data (Pitfall 5) — seeding against a DB with missing tables will fail in ways that are easy to misdiagnose as a seed bug.

**Warning signs:**
The app returns 500s that mention missing tables/relations, or `alembic current` returns nothing/an unexpected revision when checked against the deployed database.

**Phase to address:** Deployment phase — migrations should be verified as their own checklist item, separate from "the container started."

---

### Pitfall 7: A secret leaks in the public repo and nobody notices until it's exploited

**What goes wrong:**
This repository is public. Any credential that ends up committed — even briefly, even later deleted — is fetchable forever by anyone who clones or forks, because deleting a file in a later commit does not remove it from git history. Automated bots scan public GitHub repos for exposed credentials continuously; leaked secrets get harvested within minutes of being pushed, not "if someone happens to look."

**Why it happens:**
The current state is actually good — `.env` is correctly gitignored (only `.env.example` is tracked), and `docker-compose.yml` sources `JWT_SECRET` from the environment rather than hardcoding it (confirmed: `JWT_SECRET: ${JWT_SECRET:?falta JWT_SECRET; copia .env.example a .env}`). The risk at this stage is not "current tracked files" but **git history** (was a real secret ever committed and later removed?) and **the deployment step itself** (does the PaaS dashboard's env var configuration, or a CI log, echo a secret anywhere visible?).

**How to avoid:**
- Run **gitleaks** (`gitleaks detect -v --source . --log-opts="--all"`) against the **full git history**, not just the current tree — this is what catches "committed once in sprint 1, removed in sprint 2" patterns that a simple file listing won't show. It's a single free binary, no account, fits the zero-budget constraint, and runs in seconds.
- If gitleaks finds a historical hit: the fix is **not** just deleting the file again. Rotate the actual credential (issue a new `JWT_SECRET`, change any DB password that was ever exposed) *and* rewrite history (e.g., `git filter-repo` or, given this is a student project with a small history, consider a clean fresh repo) — rewriting history without rotating the credential leaves the old secret still valid if anyone already grabbed it.
- Double-check the CI workflow (`.github/workflows/ci.yml`, already flagged in CONCERNS.md as using test-only secrets) doesn't echo env vars into logs, and that whatever secret is set in the PaaS dashboard for production is **different** from any value that ever appeared in `.env.example` or a test fixture.
- Do this scan **once, deliberately, right before making any final delivery** — not as an ongoing worry, a single clean pre-delivery pass is sufficient at this project's scale.

**Warning signs:**
Any commit message like "remove secret", "fix credentials", "oops .env" in the log history is a strong signal to check that commit's parent for what was actually exposed, even though it's "already fixed."

**Phase to address:** Repo-hygiene phase, run as a discrete checklist item before final delivery — cheap, fast, and the cost of skipping it (a leaked DB credential on a public academic repo) is disproportionate to the five minutes it takes.

---

### Pitfall 8: The classroom network drops and there's no plan B

**What goes wrong:**
The demo depends on a live cloud deployment reachable over whatever network the defense room has (institutional wifi, mobile hotspot, or nothing). Classroom/institutional networks are exactly the kind that block outbound ports, throttle, or simply go down at the worst moment — and a defense is a fixed, unrepeatable time slot, not a deploy that can be retried later.

**Why it happens:**
Because the whole point of this milestone is a cloud-hosted demo (chosen deliberately over `localhost`, per PROJECT.md, precisely because the QR scanner needs real HTTPS from a phone), there's no built-in fallback the way a purely local demo would have. A live demo with a single network dependency and no rehearsed alternative is a single point of failure for the entire defense.

**How to avoid:**
- Have the app also runnable **locally via `docker-compose up`** as the literal fallback — this already exists (validated requirement: "Empaquetado con Docker y docker-compose"). Rehearse switching to it: does the presenter's laptop have Docker running and the images pulled *in advance*, so a fallback doesn't itself require downloading anything on the day?
- Since the QR scanner needs a secure context and `localhost` is HTTPS-exempt, the **local fallback still lets the scanner work — but only from the same machine's browser**, not from a phone (a phone hitting the laptop's `localhost` doesn't count; see Pitfall 2). So the offline plan B should include: presenter's own laptop camera as the scanning device, or a pre-recorded short video/screen-capture clip of the scanner working against the cloud deployment, ready to play if live network access is unavailable at all.
- Bring a personal mobile hotspot as a secondary network path if institutional wifi is unreliable — cheap insurance, zero recurring cost.
- Actually rehearse the fallback once, not just plan it on paper — know how long "switch to local mode" takes under time pressure.

**Warning signs:**
Not testing on the actual room's network beforehand (or a network with similar restrictions) is itself the warning sign — "it works on my home wifi" says nothing about an institution's network policies.

**Phase to address:** Demo-rehearsal phase — the offline plan B and its rehearsal are a required deliverable in PROJECT.md's Active requirements, not optional polish.

---

### Pitfall 9: The reverse-proxy headers are wrong, and HTTPS-dependent logic silently misbehaves

**What goes wrong:**
Behind a PaaS's edge proxy, uvicorn needs to be told to trust `X-Forwarded-Proto`/`X-Forwarded-For` headers via `--proxy-headers` (and `--forwarded-allow-ips`, which defaults to trusting only `127.0.0.1`). Without this, the app can see the *internal* connection as plain `http://` even though the public-facing URL is `https://` — which can quietly break anything that branches on scheme (secure cookies, redirect logic, or any accidental assumption the app makes about being served over TLS).

**Why it happens:**
This is exactly the leftover the shelved `feature/https-produccion` branch already identified as still relevant after switching from a self-managed Caddy proxy to a PaaS (per PROJECT.md's Context section: "de esta última solo conservan sentido `--proxy-headers` en uvicorn y `sslmode=require`"). It's an easy detail to drop when re-scoping a deployment plan from "my own reverse proxy" to "PaaS handles TLS for me," because it feels like it should no longer be the app's problem — but the app still needs to be told what happened upstream.

**How to avoid:**
- Set the production start command explicitly with `--proxy-headers --forwarded-allow-ips='*'` (or scoped to the PaaS's known proxy IP range if the provider documents one) rather than assuming defaults are fine behind a PaaS proxy.
- This has no visible symptom in casual testing (the browser padlock is already green because *external* TLS termination happened correctly) — it only matters for app-side logic that inspects the scheme/protocol, so it's easy to ship without noticing anything wrong until something scheme-dependent is added later.

**Warning signs:**
None obvious from the outside — this is a "verify it's configured correctly" item, not something that announces itself as broken. Treat it as a deploy checklist item rather than something to wait to discover.

**Phase to address:** Deployment phase — carry the two still-relevant pieces of `feature/https-produccion` (`--proxy-headers` flag, `sslmode=require`) forward explicitly rather than letting the whole branch get dropped along with the Caddy proxy it was really about.

---

### Pitfall 10: The documentation says the system does things it doesn't, and the evaluator finds the gap

**What goes wrong:**
The README currently claims "producción en Supabase" over a deployment that, per PROJECT.md, does not exist yet. `plan-de-trabajo.md` describes the project as being in week 1 and lists as pending things that are already done. In an oral defense, an evaluator who cross-checks a documentation claim against the live system (clicking the link, asking "show me that") and finds it doesn't match costs far more than the missing feature itself would have — it reframes every other claim in the document as suspect, including the ones that are true. A missing feature is a scope gap; a false claim is a credibility problem, and evaluators grade credibility.

**Why it happens:**
Documentation gets written aspirationally, ahead of the work ("we're deploying to Supabase" written as a plan, then never corrected once the plan changed), or gets written once early and never revisited as the project's actual state moved past it. This project already has two concrete instances of this on record (the README's Supabase claim, `plan-de-trabajo.md`'s stale status), which means the pattern is not hypothetical here — it's already present and needs an active correction pass, not just vigilance going forward.

**How to avoid:**
- Do a literal line-by-line pass of every doc in `docs/` and the README against the **actual current deployed system**, right before delivery — not against what was planned, what was true three sprints ago, or what's aspirational for "later."
- For every factual claim ("runs in production," "deployed on X," "supports Y"), verify it by actually doing the thing described (open the link, run the command, click through the feature) rather than trusting it was true when written.
- Prefer removing a claim entirely over leaving a stale one — "not yet documented" reads as an oversight; "documented and wrong" reads as either carelessness or dishonesty, and an evaluator can't tell which, so both get penalized.
- This is explicitly one of the Active requirements already ("La documentación del repositorio describe el sistema tal como está, sin afirmaciones que la realidad no respalde") — treat it as a hard gate on delivery, not a nice-to-have polish pass.

**Warning signs:**
Any doc sentence written in future/aspirational tense ("we will deploy...", "planned to support...") that's survived past the point where it should have been updated to past/present tense is a candidate for this pitfall — grep for tentative language as a first pass.

**Phase to address:** Documentation phase — explicitly scoped as a verification pass against the live system, scheduled *after* deployment is stable (so there's something real to verify claims against) and *before* final delivery.

---

### Pitfall 11: The evaluator opens the repo and lands on the retired .NET implementation

**What goes wrong:**
GitHub's `main` branch is still the original C#/ASP.NET Core implementation from before the sprint-1 rewrite; all current work lives on `develop`. Anyone opening the public repo URL — including an evaluator doing due diligence before or after the live defense — lands on the retired codebase by default, sees `SkilledGuard.sln`, `CódigoBackend/`, `Base_de_Datos/`, and reasonably concludes either the wrong project or an abandoned one.

**Why it happens:**
The rewrite migrated the code but nobody repointed GitHub's default-branch setting, which is a separate, easy-to-forget action from merging work into `develop`.

**How to avoid:**
- In repo Settings → Branches, change the default branch pointer to `develop` (or promote `develop` to `main` and retarget, whichever fits the team's branching convention) before delivery. This does not delete the old branch or its history — it only changes what a fresh visitor sees first and what new PRs target by default.
- Anyone who already has a local clone tracking the old default needs to update their local tracking branch after the switch, but that's a one-time note, not a blocker to making the change.
- Consider whether the legacy `.NET` artifacts (`SkilledGuard.sln`, `CódigoBackend/`, `Base_de_Datos/`) should be archived/removed from whatever becomes the default branch's tree, since even a correctly-defaulted branch that still contains dead C# files sitting alongside the real Python app reads as clutter to an evaluator browsing the repo.

**Warning signs:**
Opening the repository's public URL in a private/incognito browser window (to bypass any locally cached branch state) and seeing anything other than the current FastAPI project is the direct test.

**Phase to address:** Repo-hygiene phase — a five-minute settings change with disproportionate impact on first impressions; do it early enough that it's not forgotten in the rush before delivery.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|------------------|
| External cron pinging `/health` to prevent PaaS sleep | Zero-cost way to avoid cold starts | Burns free compute-hour quota (Render: 750h/month shared) for no benefit outside demo windows; can also mask a real "is it actually serving traffic" check if `/health` doesn't touch the DB | Only during the defense window itself (hours, not weeks); never left running continuously for a project with no fixed defense date |
| Current seed script (catalogs + one admin only) | Fast, idempotent, good for local dev/tests | Deployed system looks empty to an evaluator — see Pitfall 5 | Acceptable for dev/CI seeding; never acceptable as the demo-day dataset |
| Storing secrets as PaaS dashboard env vars instead of a vault | Zero cost, zero setup, matches project scale | None significant at this scale — a solo academic project has no team-secret-rotation problem a vault would solve | Always acceptable here; do not over-engineer with a vault for a project this size |
| Skipping a rehearsed offline fallback because "the deploy usually works" | Saves rehearsal time | A single unrepeatable defense slot with no plan B if the classroom network fails | Never acceptable given the defense is a fixed, non-retryable event |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|-----------------|-------------------|
| Render/Koyeb (or similar) reverse proxy + uvicorn | Leaving `--proxy-headers`/`--forwarded-allow-ips` at defaults, so the app can't reliably see it's being served over HTTPS internally | Set `--proxy-headers --forwarded-allow-ips=<proxy CIDR or '*'>` explicitly on the production start command |
| Supabase/Neon (or similar) managed Postgres + Alembic | Pointing migrations at a pooled/transaction-mode connection string (e.g., Supabase's port 6543) | Use the **direct** connection string (e.g., port 5432) for `alembic upgrade head`; reserve the pooler for the app's normal runtime queries if used at all |
| Managed Postgres + `sslmode` | Omitting `sslmode=require` when the managed provider requires TLS on the connection, surfacing as an opaque connection error that looks like a migration bug | Carry forward `sslmode=require` from the already-drafted `feature/https-produccion` branch into the final `DATABASE_URL` |
| Public GitHub repo + any secret-bearing history | Assuming "the file is gone now" means the secret is safe | Scan **full git history** with gitleaks before delivery; rotate any credential that was ever exposed regardless of whether the file was later removed |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|-----------------|
| Free-tier PaaS sleep window elapsing mid-defense | First request after a pause (coffee break, long Q&A tangent) hangs for tens of seconds | Warm-up hit immediately before presenting; keep interacting with the app if there's a gap in the demo flow | Render: any gap over 15 min idle; Koyeb: over 1 hour |
| Stacked cold starts (web service + DB both asleep) | Combined delay noticeably worse than either alone, first request can take the sum of both wake times | Warm the web service first, let its first DB query itself act as the DB warm-up, then wait for both to settle before presenting | Whenever both have been idle past their respective thresholds simultaneously (very likely after any multi-day gap) |
| Managed Postgres hard expiration (Render: 30 days) independent of usage | Database is simply gone on defense day if provisioned too early relative to a not-yet-scheduled defense | Track the provisioning date; re-provision/reseed if the defense date slips past the expiration window, or pick a provider (e.g., Neon) whose free tier doesn't hard-expire on a calendar clock | 30 days after DB creation on Render specifically, regardless of whether the demo has happened |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Assuming "no `.env` in the working tree" means no secret exposure | A secret committed once and later removed is still retrievable from git history by anyone who clones the public repo | Run gitleaks against full history, not just current files, before delivery |
| No rate limiting on `/auth/login` (already flagged in CONCERNS.md) combined with a public repo announcing the URL | Once the deployed URL is shared publicly (as it will be, for the defense), it becomes a discoverable brute-force target, however unlikely a real attacker cares about a student project | Low-cost mitigation already identified in CONCERNS.md (`slowapi`) is worth applying given the app will briefly be a public, indexed URL, not just a private demo |
| Reusing the same secret value across `.env.example`, test fixtures, and the real deployed `JWT_SECRET` | If a test-only secret pattern happens to match what's used in production, a leak in a "harmless" test context still compromises production | Generate a fresh, unique `JWT_SECRET` specifically for the deployed environment, distinct from any example/test value that appears anywhere in the repo |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|--------------|-------------------|
| Evaluator logs in to an empty system (only catalogs + admin seeded) | Reads as "not actually built," undermining validated work the evaluator can't see evidence of | Rich, realistic demo seed data — see Pitfall 5 |
| First camera permission prompt happens live, mid-sentence | Adds an awkward pause and a moment where things could visibly go wrong in front of the evaluator | Grant/confirm camera permission for the demo browser/device once *before* the defense starts, so the live moment is just scanning, not also negotiating permissions |
| Report download triggers a cold query against a just-woken database | A "simple" report click hangs unexpectedly right after the warm-up sequence if the DB wasn't included in it | Include at least one report generation in the pre-demo warm-up sequence, not just login |

## "Looks Done But Isn't" Checklist

- [ ] **HTTPS scanner demo:** Works from a laptop's Chrome ≠ works from an evaluator's phone — verify on an actual phone (Android *and* iOS Safari specifically) against the real public URL, not `localhost` or a local IP.
- [ ] **"Deployed backend":** Container starts and responds to `/health` ≠ migrations ran — verify `alembic current` against the deployed DB matches the repo's latest head, and that `/health` (or an equivalent) actually touches the database, not just confirms the process is alive.
- [ ] **"Producción en Supabase" (or whatever the final doc claims):** Written in a doc ≠ actually true — click the link, confirm the deployment exists and is the one being demoed, before delivery.
- [ ] **Seed data:** Seed script runs without error ≠ demo-ready — verify it produces multiple realistically-named `Dispositivo` records in mixed in/out states, spread-out movement history, and a non-admin user to log in as.
- [ ] **Public repo secrets:** No `.env` visible in the file listing ≠ no secret ever leaked — run gitleaks against full git history, not just the current tree.
- [ ] **Default branch:** `develop` has all the real work ≠ a visitor sees it — open the repo URL in a private browser window and confirm what actually loads first.
- [ ] **Offline plan B:** A plan exists on paper ≠ it works under time pressure — actually rehearse switching to the local `docker-compose` fallback once, with the clock running.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|-----------------|------------------|
| Render free Postgres expired (30-day clock) before defense | MEDIUM | Re-provision a new free Postgres instance, re-run `alembic upgrade head`, re-run the demo-seed script; consider switching to a provider without a hard calendar expiration (e.g., Neon) if the defense date is likely to keep slipping |
| Secret found in git history via gitleaks | HIGH | Rotate the actual credential first (new `JWT_SECRET`, new DB password) — this alone neutralizes the risk even before history is cleaned; then rewrite history (`git filter-repo`) or start a fresh repo if the history is small enough that this is simpler |
| Camera fails live on the exact device being used | LOW | Fall back to the presenter's own laptop camera against the deployed HTTPS URL, or play a short pre-recorded clip of the scanner working — both should be prepared *before* the defense, not improvised during it |
| Classroom network is unusable at defense time | LOW–MEDIUM | Switch to the rehearsed local `docker-compose up` fallback (already validated as a project capability); scanning from a phone won't work against `localhost` (see Pitfall 2), so the fallback demo uses the presenter's own machine as the scanning device |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|----------------|
| PaaS sleep / cold start during demo | Deployment phase + demo-rehearsal phase | Timed cold-start test on the chosen platform; warm-up sequence written into the actual demo script |
| `getUserMedia` needs a secure context | Deployment phase (HTTPS live) + QR-scanner verification phase | Scanner tested from a real phone against the deployed `https://` URL, confirmed no camera prompt failure |
| iOS Safari specifics (version, standalone mode, cert trust) | QR-scanner verification phase | Explicit test on a physical iPhone in a normal Safari tab (not home-screen/standalone) |
| Managed Postgres pause/expiration | Deployment phase | Pause→wake (or expiration-tracking) behavior of the chosen provider tested once and timed; provisioning date logged if using a provider with a hard expiry |
| Empty/unrealistic demo data | Demo-data-preparation phase (after deployment, before rehearsal) | Deployed instance manually inspected: multiple devices in mixed states, spread-out history, non-admin login available |
| Alembic migration failure on fresh managed DB | Deployment phase | `alembic current` checked against deployed DB immediately after first deploy, before any seeding |
| Leaked secrets in public repo | Repo-hygiene phase | gitleaks full-history scan run clean; any historical hit followed by credential rotation, confirmed |
| Classroom network failure | Demo-rehearsal phase | Offline `docker-compose` fallback actually rehearsed once under time pressure, not just documented |
| Reverse-proxy headers (`--proxy-headers`) | Deployment phase | Production start command explicitly includes `--proxy-headers`/`--forwarded-allow-ips`; carried forward from `feature/https-produccion` |
| Documentation overclaiming | Documentation phase (after deployment is stable, before final delivery) | Every factual claim in `docs/` and README individually re-verified against the live deployed system |
| Public repo defaults to retired .NET branch | Repo-hygiene phase | Repo URL opened in a private browser window, confirmed it shows the current FastAPI project |

## Sources

- [Do Web Services on a free tier go to sleep after some time inactive? — Render community](https://render.discourse.group/t/do-web-services-on-a-free-tier-go-to-sleep-after-some-time-inactive/3303) (MEDIUM)
- [Free PostgreSQL instances now expire after 30 days — Render official changelog](https://render.com/changelog/free-postgresql-instances-now-expire-after-30-days-previously-90) (HIGH — official source)
- [Deploy for Free — Render Docs](https://render.com/docs/free) (HIGH — official source)
- [Koyeb Scale-to-Zero docs](https://www.koyeb.com/docs/run-and-scale/scale-to-zero) (MEDIUM)
- [Koyeb Free Tier Cold Start behavior — Runhooks](https://runhooks.app/blog/keeping-koyeb-free-tier-awake/) (LOW)
- [Project Pausing — Supabase official docs](https://supabase.com/docs/guides/platform/free-project-pausing) (HIGH — official source)
- [Supabase connection pooling / Supavisor docs](https://supabase.com/docs/guides/troubleshooting/supavisor-and-connection-terminology-explained-9pr_ZO) (HIGH — official source)
- [Neon free tier and scale-to-zero — multiple 2026 reviews](https://medium.com/@philmcc/neon-postgres-review-serverless-postgresql-that-actually-scales-to-zero-ee14d4e109ba) (LOW, cross-checked against Neon's own pricing page framing)
- [7 Fly.io Alternatives in 2026: Real Pricing After the Free Tier Died](https://expresstech.io/7-fly-io-alternatives-in-2026-real-pricing-after-the-free-tier-died/) (MEDIUM)
- [Railway Free Trial — official docs](https://docs.railway.com/pricing/free-trial) (HIGH — official source)
- [MDN: Secure contexts](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Secure_Contexts) (HIGH — official source)
- [MDN: MediaDevices.getUserMedia()](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia) (HIGH — official source)
- [WebRTC Safari: The 2025 Developer's Guide — VideoSDK](https://www.videosdk.live/developer-hub/webrtc/webrtc-safari) (LOW)
- [Apple Developer Forums — WebRTC getUserMedia in standalone](https://developer.apple.com/forums/thread/89981) (LOW, primary-source forum but unofficial)
- [Uvicorn Settings docs — proxy headers](https://uvicorn.dev/settings/) (HIGH — official source)
- [Alembic autogenerate migrations docs](https://alembic.sqlalchemy.org/en/latest/autogenerate.html) (HIGH — official source)
- [Accidentally Pushed a `.env` Secret to a Public GitHub Repo? — DEV Community](https://dev.to/kashafabdullah/accidentally-pushed-a-env-secret-to-a-public-github-repo-heres-what-to-do-33i3) (LOW)
- [Why 28 million credentials leaked on GitHub in 2025 — Snyk](https://snyk.io/articles/state-of-secrets/) (MEDIUM)
- [Gitleaks vs TruffleHog 2026 comparison](https://appsecsanta.com/sast-tools/gitleaks-vs-trufflehog) (LOW)
- [GitHub Docs — Branches](https://docs.github.com/en/pull-requests/reference/branches) (HIGH — official source)
- Direct inspection of this project's own repository (`/home/nekro/SkilledGuard`): `git ls-files` confirms only `.env.example` is tracked (not `.env`); `docker-compose.yml` sources `JWT_SECRET` from environment, not hardcoded; `git branch -a` confirms `main` and `develop` are separate, divergent branches; `app/seed.py` inspected directly and confirmed to seed only catalog tables + one admin user, no demo devices or movement history (HIGH — primary source, this codebase)

---
*Pitfalls research for: Free-tier PaaS deployment and live academic defense of a working FastAPI + PostgreSQL system*
*Researched: 2026-08-10*
