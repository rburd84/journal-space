# Stillspace

**A calm, personal journaling web application.**

> **Project status:** Local development / private-beta preparation. **Not ready for public deployment or real-user
private data.** This README documents the source snapshot reviewed in November 2026, not features planned for a future
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
| Development database  | SQLite (`journal.db`)                                                       |
| Dependency management | `uv` for Python; npm for frontend                                           |
| Tests                 | pytest (backend)                                                            |

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

The backend currently uses `sqlite:///./journal.db` and creates tables on startup. This is **development-only**
behavior, not a production migration strategy.

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
4. SQLAlchemy persists journals and entries to the local SQLite database.
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

## Security and privacy limitations

**Do not expose this development build to untrusted users or store real testers' sensitive journals in it.**

- The frontend currently uses a **shared hardcoded development user ID**.
- The API has **no enforced authentication or per-user ownership checks** for journal and entry operations.
- Some requests accept a browser-supplied `user_id` or resource ID; these are **not proof of ownership**.
- SQLite is configured for local development; production migrations, backups, and restore procedures have not been
  verified.
- Deleted entries are removed permanently, without a recovery window.

These are release blockers, not features to work around by obscuring the website URL.

## Planned invitation-only private beta (not yet implemented)

The agreed initial beta scope is **five invited testers plus one administrator**, running for **30 days** after launch
approval. Planned requirements include:

- Invitation-only passwordless email-code authentication, with individual account sessions.
- Server-side authorization for **every** journal and entry operation.
- PostgreSQL hosting, versioned migrations, tested backups and restore procedures.
- A **30-day Recently Deleted** recovery period for entries and a separate account-departure retention procedure.
- A first-login welcome/privacy acknowledgment and improved empty-state guidance.
- Desktop and mobile browser acceptance testing.
- A dedicated email address for tester feedback.

Preferred providers under evaluation: **Clerk** for authentication, **Render** for hosting, and the existing GoDaddy
domain / Microsoft 365 mailbox. Provider capabilities and final costs still need verification. None of these
integrations should be assumed active.

## Documentation roadmap

- **Private Beta Readiness & Release Plan:** Decisions, risks, stages, budget, and launch gates (drafted separately).
- **Technical Inventory:** Source-based review of identity, database, API, tests, and frontend.
- **Stillspace User Guide:** Step-by-step instructions for testers; to be finalized after beta workflows and screenshots
  stabilize.

## Development policy

Current work is in **read-only assessment and documentation mode**. No authentication integration, database migration,
hosting change, or new journaling feature should be treated as authorized by this README.

