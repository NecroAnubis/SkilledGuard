# Codebase Concerns

**Analysis Date:** 2026-08-09

## Tech Debt

**Redundant report data processing:**
- Issue: `app/reportes.py` function `_filas()` is called twice per Excel report request — once to build the data rows and again in `generar_excel()` to calculate column widths (line 52)
- Files: `app/reportes.py`
- Impact: O(n) redundant list traversal for every report download; linearly scales memory pressure as result sets grow
- Fix approach: Calculate column widths in a single pass or cache `_filas()` result

**State assumption in movement history:**
- Issue: `app/porteria.py::estados_de_todos()` (lines 29–54) uses `func.max(AuditoriaNegocio.id)` to find the latest movement, assuming IDs are monotonically increasing
- Files: `app/porteria.py`
- Impact: Breaks silently if database is resharded, migrated, or backfilled out-of-order; equipment state becomes unreliable without error signal
- Fix approach: Use `order_by(AuditoriaNegocio.id.desc()).limit(1)` per device or add explicit `created_at` DESC ordering with tie-breaking

**Hardcoded catalog dependencies:**
- Issue: `app/seed.py` seeds `TipoRegistro` with names "Ingreso" and "Salida" (lines 51–54), but `app/porteria.py::registrar()` (line 105) searches for these names at runtime; if a catalog entry is renamed or missing, equipment registration silently fails
- Files: `app/porteria.py` (line 105), `app/seed.py` (lines 51–54)
- Impact: Catalog name changes (e.g., renaming to Spanish variants or fixing typos) break the portería system without clear error messages
- Fix approach: Use enum-backed IDs or add a startup check that validates required catalog entries exist

**Column width calculation in report Excel:**
- Issue: Excel column widths are calculated per-request at render time (line 52–55 in `reportes.py`), and the formula `ancho / 1.8` is a heuristic without explanation
- Files: `app/reportes.py` (line 52–55)
- Impact: Performance regression on large datasets; column width math is cargo-culted and may not handle non-ASCII text (ñ, accents) correctly
- Fix approach: Pre-calculate widths or use auto-fit after data insertion; document the 1.8 scaling factor

## Known Bugs

**Session lifetime not explicitly bounded:**
- Symptoms: Database connections can remain open indefinitely if an endpoint crashes or times out
- Files: `app/database.py` (lines 8–9)
- Trigger: Long-running queries, network partition, or client disconnect
- Workaround: Docker restart; production should set statement timeout at database level

**Concurrent movement registration race condition unlikely but possible:**
- Symptoms: Two simultaneous requests for the same device in quick succession (< row lock acquisition time) may both pass state validation before the first commits
- Files: `app/porteria.py::registrar()` (line 101)
- Trigger: Double-click on submit, network retry, or two security staff scanning same device simultaneously
- Workaround: Frontend debounce; backend row-level locking mitigates but does not guarantee prevention under high concurrency

**PDF text truncation silent:**
- Symptoms: Long observation text in equipment movement reports is silently truncated to `int(ancho / 1.8)` characters with "…" appended
- Files: `app/reportes.py` (lines 110–111)
- Trigger: Equipment entries with detailed observations > ~30 characters
- Workaround: Shorten observations; use Excel export for full text

## Security Considerations

**No rate limiting on authentication:**
- Risk: Brute force attacks on the login endpoint are not throttled
- Files: `app/routers/auth.py` (lines 16–33)
- Current mitigation: Generic error message ("Documento o contraseña incorrectos") prevents user enumeration
- Recommendations: Add fail2ban-style rate limiting (e.g., `slowapi` package) on `/auth/login` endpoint; lock accounts after N failed attempts

**Weak password complexity validation:**
- Risk: Passwords are only validated for minimum length (8 bytes) and bcrypt byte limit (72 bytes); no checks for complexity
- Files: `app/schemas.py` (lines 48–57), `app/security.py` (lines 31–32)
- Current mitigation: bcrypt work factor (default 12) makes brute force computationally expensive
- Recommendations: Add regex-based complexity checks (require uppercase, number, special character) in `UsuarioCrear` schema validation

**JWT token expiration not enforced on refresh:**
- Risk: Tokens expire server-side at 60 minutes (configurable), but there is no refresh token mechanism; users must re-login, which could be inconvenient or lead to workarounds (e.g., storing credentials)
- Files: `app/config.py` (line 12), `app/security.py` (line 40)
- Current mitigation: Short expiration window reduces attack window if token is leaked
- Recommendations: Implement refresh token pattern with longer lifetime for automatic re-authentication; or extend token lifetime for known-good security contexts

**Docker container secrets exposure risk:**
- Risk: `.env` file is not committed (good), but docker-compose.yml exposes `JWT_SECRET` via environment variable (lines 24–28); CI logs or container inspect could leak it
- Files: `docker-compose.yml` (lines 24–28), `.github/workflows/ci.yml` (line 28)
- Current mitigation: Secrets are extracted from `.env` at runtime, not hardcoded; CI uses test-only secrets
- Recommendations: Use Docker secrets or external vault (e.g., HashiCorp Vault) for production; never log environment variables in CI

**No CORS or CSRF protection:**
- Risk: API endpoints do not restrict origin or validate CSRF tokens; frontend SPA could be compromised to make requests on behalf of users
- Files: `app/main.py` (no CORS middleware)
- Current mitigation: OAuth2 bearer token scheme requires `Authorization` header (not sent by browser form submissions)
- Recommendations: Add FastAPI CORS middleware with explicit allowed origins; add CSRF token validation if frontend uses cookie-based auth

## Performance Bottlenecks

**Report generation loops N times for column width:**
- Problem: Excel report generation calls `_filas(movimientos)` twice — once to build data (line 48) and once to measure widths (line 52)
- Files: `app/reportes.py` (lines 48–52)
- Cause: Column width logic requires the full dataset to measure text length; no pre-calculation or caching
- Improvement path: Refactor `_filas()` to return both data and calculated widths; or cache result with TTL for duplicate requests within seconds

**PDF report scalability limited by memory:**
- Problem: PDF library renders entire dataset in memory before serializing; no streaming or pagination
- Files: `app/reportes.py` (lines 92–119)
- Cause: FPDF and openpyxl both load entire workbook/PDF into RAM
- Improvement path: For > 5000 rows, delegate to background job (e.g., Celery) that streams to disk; return download link instead of synchronous response

**Equipment state query inefficient for large fleets:**
- Problem: `estados_de_todos()` (line 29–54 in porteria.py) queries max ID per device; without composite index on `(id_dispositivo, id DESC)`, this is a full table scan
- Files: `app/porteria.py` (lines 36–47)
- Cause: No database index hint; depends on implicit query plan optimization
- Improvement path: Add index on `AuditoriaNegocio(id_dispositivo, id DESC)` in Alembic migration; or refactor to use window functions `ROW_NUMBER() OVER (PARTITION BY id_dispositivo ORDER BY id DESC)`

## Fragile Areas

**Row-level locking without timeout:**
- Files: `app/porteria.py` (line 101)
- Why fragile: `with_for_update()` blocks indefinitely waiting for lock; no timeout configured; if a prior transaction crashes mid-lock, the row is locked until connection timeout
- Safe modification: Wrap in try-except, set database-level statement timeout, or use `nowait=True` with fallback retry logic
- Test coverage: No tests for concurrent movement registration; `test_porteria.py` is single-threaded

**Catalog existence validation at runtime only:**
- Files: `app/porteria.py` (line 105)
- Why fragile: If `TipoRegistro` entries are deleted or their names change, the system continues to accept movement requests but they fail to commit with a cryptic FK or NULL error
- Safe modification: Add startup health check in `main.py` that validates all required catalog entries; fail fast on misconfiguration
- Test coverage: Seed test (`test_seed.py`) checks idempotency but not that all expected catalogs exist

**Audit logging success not guaranteed:**
- Files: `app/routers/usuarios.py` (lines 63–70), `app/auditoria.py` (lines 45–77)
- Why fragile: Audit log is recorded *after* the main operation commits (line 70 in usuarios.py), so if the audit write fails, the original action already succeeded. This violates "all or nothing" semantics
- Safe modification: Record audit log *before* commit, or use a single transaction for both
- Test coverage: Tests verify audit entries exist but not the "audit write fails" scenario

**No cascade delete on foreign keys:**
- Files: `app/models.py` (FK definitions)
- Why fragile: If a user is deleted via raw SQL or bulk operation outside the API, their associated `UsuarioRol`, `Dispositivo`, `AuditoriaNegocio`, `LogSistema` records become orphaned
- Safe modification: Add `cascade="delete"` to relationship definitions in models; or implement soft-delete (is_deleted flag)
- Test coverage: No test for deletion cleanup

## Scaling Limits

**Report file size unbounded:**
- Current capacity: Limit of 5000 rows per report (`MAXIMO_FILAS` in reportes.py line 24); with 7 columns per row, ~350 KB Excel file
- Limit: Excel hard limit is 1.048M rows; PDF rendering runs out of memory around 50K rows (depends on machine RAM)
- Scaling path: Implement async report generation with S3 or filesystem storage; return presigned URL instead of streaming

**Database connection pool not sized for load:**
- Current capacity: Default SQLAlchemy pool size is 5 connections
- Limit: Under 10 concurrent requests, pool exhaustion is unlikely; above 20, requests will queue or timeout
- Scaling path: Configure `pool_size` and `max_overflow` in `create_engine()` call (app/database.py line 8); or add connection pooler (pgBouncer)

**Single JWT secret per environment:**
- Current capacity: One shared secret for all tokens and all instances
- Limit: Key rotation requires re-issuing all active tokens (downtime event); no way to stagger rollout
- Scaling path: Implement key versioning (JWK Set endpoint); sign tokens with primary key, accept both primary and previous key for verification

## Dependencies at Risk

**fpdf2 fork maintenance risk:**
- Risk: fpdf2 (version 2.8.2 in requirements.txt) is a community fork of FPDF; library maintenance is volunteer-driven and updates are infrequent
- Impact: PDF rendering bugs or security vulnerabilities (e.g., file inclusion via malicious strings) have slow patch cycles
- Migration plan: Evaluate ReportLab or Weasyprint as alternatives; or accept the risk and add security review to PR process for report generation changes

**qrcode library encoding issues:**
- Risk: qrcode[pil] (version 8.0) relies on PIL/Pillow for image encoding; if Pillow has a security issue, all QR generation is affected
- Impact: Malformed QR content could trigger buffer overflow or DoS
- Migration plan: Audit Pillow version regularly; consider pure-Python QR renderer (pyzbar) for critical deployments

**PostgreSQL version pinned loosely:**
- Risk: docker-compose uses `postgres:16-alpine`; no pin to specific patch version (e.g., 16.1, 16.2)
- Impact: Docker image updates could pull a new minor version with behavioral changes or regressions
- Migration plan: Pin to exact version `postgres:16.2-alpine`; test upgrades in CI before merging

## Missing Critical Features

**No soft-delete or audit trail for deletions:**
- Problem: The system can delete users, roles, and devices via API, but there is no audit trail of what was deleted or undo capability
- Blocks: Compliance requirements for data retention; recovery from accidental deletion
- Fix approach: Implement soft-delete (add `is_deleted` flag to models); or archive to separate "deleted" schema; log full record state before DELETE

**No multi-tenancy or organization support:**
- Problem: All users and equipment are in one global namespace; no way to segment by department or location
- Blocks: Scaling to multi-site or multi-customer deployments
- Fix approach: Add `organization_id` FK to `Usuario`, `Dispositivo`, etc.; namespace all queries by org

**No backup or disaster recovery automation:**
- Problem: Database backups are not automated; no restore procedure documented
- Blocks: Recovery from data loss or corruption
- Fix approach: Set up PostgreSQL WAL archiving to S3 (or Supabase backups if migrating); document recovery steps

## Test Coverage Gaps

**No concurrent request testing:**
- What's not tested: Race conditions in movement registration, connection pool exhaustion, lock timeouts
- Files: `tests/test_porteria.py` (single-threaded), `app/porteria.py` (row locking logic)
- Risk: Concurrent double-scan or simultaneous admin actions could corrupt state silently
- Priority: High

**No error handling in report generation:**
- What's not tested: Empty result sets, out-of-memory scenarios, encoding errors in PDF/Excel for non-ASCII text
- Files: `tests/test_reportes.py`, `app/reportes.py`
- Risk: Reports fail without clear error message; user sees generic 500 error
- Priority: Medium

**No database connection failure scenarios:**
- What's not tested: Timeout, connection drop, Postgres restart during request, pool exhaustion
- Files: `tests/` (no failure injection tests)
- Risk: Unhandled exceptions leak raw SQL errors or cause hanging requests
- Priority: Medium

**No seed idempotency in production scenario:**
- What's not tested: Calling seed after partial data load (some catalogs exist, others missing)
- Files: `app/seed.py`, `tests/test_seed.py`
- Risk: Seed could fail halfway through and leave database in inconsistent state
- Priority: Low

**No JWT expiration or token refresh tests:**
- What's not tested: Expired token handling, refresh token flow (if implemented)
- Files: `tests/test_auth.py`, `app/security.py`
- Risk: Token expiration handling may be broken but not caught by tests
- Priority: Medium

---

*Concerns audit: 2026-08-09*
