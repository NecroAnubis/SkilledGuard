# Technology Stack

**Analysis Date:** 2026-08-09

## Languages

**Primary:**
- Python 3.12 - Backend API and business logic

**Secondary:**
- None (frontend is static HTML/CSS/JavaScript served as static files)

## Runtime

**Environment:**
- Python 3.12-slim (Docker base image per `Dockerfile`)

**Package Manager:**
- pip (Python package installer)
- Lockfile: `requirements.txt` (pinned versions) and `requirements-dev.txt`

## Frameworks

**Core:**
- FastAPI 0.115.6 - HTTP API framework with automatic OpenAPI documentation
- Uvicorn 0.34.0 - ASGI server to run FastAPI application
- SQLAlchemy 2.0.36 - ORM for database access and models

**Database Migration:**
- Alembic 1.14.0 - Database schema versioning and migrations

**Testing:**
- pytest 8.3.4 - Test runner and framework (dev only)
- httpx 0.28.1 - HTTP client for testing (dev only)

**Development Tools:**
- Ruff 0.8.6 - Python linter and formatter

## Key Dependencies

**Critical:**
- psycopg[binary] 3.2.3 - PostgreSQL adapter for Python; enables SQLAlchemy database connection
- pydantic 2.10.4 - Data validation and serialization for request/response schemas
- pydantic-settings 2.7.0 - Environment configuration management (reads from `.env`)

**Security & Authentication:**
- bcrypt 4.2.1 - Password hashing (used in `app/security.py`)
- PyJWT 2.10.1 - JWT token creation and verification for stateless authentication

**File Generation & Utilities:**
- qrcode[pil] 8.0 - QR code generation (used in `app/qr.py`)
- openpyxl 3.1.5 - Excel spreadsheet generation for reports (used in `app/reportes.py`)
- fpdf2 2.8.2 - PDF report generation (used in `app/reportes.py`)
- python-multipart 0.0.20 - Multipart form data parsing for file uploads

## Configuration

**Environment:**
- Method: `.env` file via `pydantic-settings`
- Location: `.env` (not committed; use `.env.example` as template)
- Critical variables:
  - `DATABASE_URL`: PostgreSQL connection string
  - `JWT_SECRET`: Secret key for signing JWT tokens (required; no default)
  - `JWT_EXPIRACION_MINUTOS`: Token lifetime in minutes (default: 60)
  - `ADMIN_DOCUMENTO`: Initial admin user ID (for seeding only)
  - `ADMIN_CONTRASENA`: Initial admin password (for seeding only)

**Build:**
- Dockerfile uses Python 3.12-slim base
- Multi-layer build optimized for Docker caching
- Non-root user (`appuser`) for security isolation

## Platform Requirements

**Development:**
- Python 3.12
- Docker + Docker Compose (for local PostgreSQL)
- pip/virtualenv

**Production:**
- Python 3.12 runtime or Docker container
- PostgreSQL 16+ (database server)
- Environment variables configured via deployment platform

## Database

**Type & Version:**
- PostgreSQL 16-alpine (per `docker-compose.yml`)

**Connection:**
- Default local: `postgresql+psycopg://skilledguard:skilledguard@db:5432/skilledguard`
- Production: Configure via `DATABASE_URL` environment variable
- Pool configuration: `pool_pre_ping=True` (tests connection before use)

**Schema Management:**
- Managed by SQLAlchemy ORM models in `app/models.py`
- Migrations tracked in `alembic/versions/` directory
- Auto-migration on startup: `alembic upgrade head` (per `docker-compose.yml`)

## Health Checks

**API Health Endpoint:**
- `GET /salud` - Returns `{"estado": "ok", "base_de_datos": "ok"}` only if database is reachable
- Used by Docker healthcheck (interval: 15s, start_period: 30s, retries: 3)

---

*Stack analysis: 2026-08-09*
