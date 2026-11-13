# Stillspace

**A calm, personal journaling web application.**

> **Project status:** Invitation-only private-beta preparation. **Not deployed or approved for real-user private data.** This README documents the source snapshot reviewed in November 2026, not features planned for a future
> release.

## What Stillspace does

Stillspace helps people organize their writing into journals and return to their entries over time. The current
application provides:

- **Dashboard:** Journal and entry summaries, recent writing, and guidance when the account is empty.
- **Journals:** Create, rename, archive, restore, and browse journals.
- **Entries:** Create and edit writing; save drafts and publish entries.
- **Reading and organization:** Read entries, mark favorites, and filter or browse entries by journal and status.
- **Responsive interface:** Desktop sidebar and compact mobile navigation. Real-device acceptance testing remains
  outstanding.

**Important:** Entry deletion is currently **permanent**. The proposed 30-day Recently Deleted recovery feature has
**not** been implemented.

## Technology

| Layer                 | Current implementation                                                      |
|-----------------------|-----------------------------------------------------------------------------|
| Frontend              | React 19, Vite 8, React Router, Tailwind CSS 4, Base UI / shadcn components |
| Backend               | Python 3.14+, FastAPI, Pydantic, SQLAlchemy                                 |
| Development database  | SQLite or PostgreSQL (`stillspace_test` for isolated tests)                    |
| Dependency management | `uv` for Python; npm for frontend                                           |
| Tests                 | pytest (backend), Vitest (frontend)                                           |

## Project layout

```text
app/
  main.py                  # FastAPI application and routes
  core/                    # Database and shared dependencies
  journals/                # Journal domain, API, services, repositories
  entries/                 # Entry domain, API, services, repositories
  users/                   # Reserved/incomplete user functionality
  analytics/ goals/ habits/ moods/ prompts/  # Not part of current beta feature set
frontend/
  src/
    App.jsx                # Client-side routes
    components/            # App shell, navigation, reusable UI
    pages/                 # Home, Journals, Entries, Editor, Reader
    lib/api.js             # Some shared API calls
  package.json
  vite.config.js
tests/                     # Existing backend tests
pyproject.toml             # Python dependencies and project metadata
```

Some folders are scaffolding and do **not** mean the corresponding features are available.

## Running locally

### Prerequisites

- Python **3.14 or newer**
- [`uv`](https://docs.astral.sh/uv/)
- Node.js and npm compatible with the installed Vite version

### 1. Start the backend

From the project root:

```bash
uv sync
uv run uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000` by default. Useful development endpoints:

- `http://127.0.0.1:8000/health` — health response
- `http://127.0.0.1:8000/docs` — interactive FastAPI API documentation

Local development defaults to SQLite unless `DATABASE_URL` is set. Production requires PostgreSQL and Alembic migrations (`uv run alembic upgrade head`); never rely on automatic table creation for deployment.

### 2. Start the frontend

In another terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open the local address printed by Vite (commonly `http://localhost:5173`). Vite proxies requests beginning with `/api`
to the FastAPI server at `http://127.0.0.1:8000`, removing the `/api` prefix.

### 3. Run checks

From the project root:

```bash
uv run pytest
```

From `frontend/`:

```bash
npm run lint
npm run build
```

These are documented commands from the project configuration. **Their success has not been verified as part of this
documentation pass.**

## How the application works

1. The React frontend presents dashboard, journal, list, editor, and reader views.
2. The frontend makes HTTP requests to FastAPI; during local development, Vite forwards `/api/...` requests to the
   backend.
3. FastAPI routes delegate journal and entry operations to service and repository layers.
4. SQLAlchemy persists journals and entries to the configured SQLite or PostgreSQL database.
5. Entries belong to journals through `journal_id`; journals carry a `user_id` field.

### Current browser routes

| Path                               | Purpose                |
|------------------------------------|------------------------|
| `/`                                | Home dashboard         |
| `/journals`                        | Journal management     |
| `/entries`                         | Entry browsing         |
| `/journals/:journalId/entries`     | Entries in one journal |
| `/entries/new`                     | New entry              |
| `/journals/:journalId/entries/new` | New entry in a journal |
| `/entries/:entryId`                | Read entry             |
| `/entries/:entryId/edit`           | Edit entry             |

## Authentication, privacy, and beta limitations

- Clerk JWT authentication and per-account journal/entry authorization are implemented.
- Invitation records gate first-login account creation; disabled users are rejected.
- Signed-JWT PostgreSQL HTTP tests cover invitation redemption, token rejection, and cross-account isolation.
- Entry deletion is **permanent**; a 30-day Recently Deleted feature is **not implemented**.
- Local PostgreSQL 18 backup/restore was tested with sample journal content and ownership, then the disposable data and restore databases were cleaned up. This does **not** verify hosted backups.
- No production deployment or hosted acceptance test has been completed. Do not invite real users or store sensitive journals until these checks pass.

## Render Hobby deployment plan (not deployed)

The repository includes a proposed `render.yaml` Blueprint for a static Vite frontend, paid FastAPI web service, and paid PostgreSQL 18. The workspace subscription is intended to be **Render Hobby**; the Blueprint specifies paid resource sizes separately. Hosting incurs charges if provisioned.

Before provisioning: review Render pricing and service plans; confirm Python 3.14 compatibility; configure the production Clerk instance; enter HTTPS frontend/backend origins and credentials; verify backup retention and recovery; and disable Blueprint Auto Sync. Services have automatic deployment disabled in the Blueprint. Creating a Blueprint or changing Render settings requires explicit approval.

Backend environment: `STILLSPACE_ENV=production`, `DATABASE_URL` (from Render PostgreSQL), `CLERK_ISSUER`, `CLERK_AUTHORIZED_PARTIES`, and `CORS_ALLOWED_ORIGINS`. The latter two must match the frontend's HTTPS origin. The application normalizes PostgreSQL connection URLs to the installed psycopg 3 driver, including during Alembic migrations.

Frontend build environment: `VITE_CLERK_PUBLISHABLE_KEY` and `VITE_API_ORIGIN` (HTTPS backend origin, without `/api`). Vite embeds these at build time. Do not commit secrets.

Release checks: `uv run pytest`, `uv run alembic heads`, `npm ci`, `npm run lint`, `npm test`, and `npm run build`. The opt-in PostgreSQL HTTP tests require a local disposable `TEST_DATABASE_URL` pointing to `stillspace_test`; they must never target production. Hosted acceptance must additionally verify authentication, invitation gating, authorization, migrations, persistence, frontend routes, and backups.

## Planned beta scope

The intended first beta is five invited testers and one administrator for 30 days after launch approval. Desktop/mobile browser acceptance, welcome/privacy copy, feedback workflow, and user manual remain to be finalized.

## Beta guides

- [Tester User Guide](docs/TESTER_GUIDE.md) — sign-in, journals, writing, favorites, and permanent deletion.
- [Administrator Guide](docs/ADMIN_GUIDE.md) — invitations, deployment approval, security, backups, and incident handling.

Both are pre-launch drafts pending hosted acceptance and final contact details.

## Documentation roadmap

- **Private Beta Readiness & Release Plan:** Decisions, risks, stages, budget, and launch gates (drafted separately).
- **Technical Inventory:** Source-based review of identity, database, API, tests, and frontend.
- **Stillspace User Guide:** Step-by-step instructions for testers; to be finalized after beta workflows and screenshots
  stabilize.

## Development policy

Current work is in **read-only assessment and documentation mode**. No authentication integration, database migration,
hosting change, or new journaling feature should be treated as authorized by this README.

