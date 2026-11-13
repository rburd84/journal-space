# Stillspace — Administrator Guide (Draft)

**Audience:** Stillspace beta administrator. **Status:** Pre-launch operating draft. Do not use against a production database until hosting and recovery checks are approved.

## Responsibilities
Manage a small invitation-only beta (planned: five testers and one administrator), monitor availability, protect user data, record tester feedback, and control deployments. The current application does not expose a full administrator dashboard.

## 1. Pre-launch approval checklist
- Confirm GitHub tests pass, including backend and frontend suites.
- Run PostgreSQL signed-JWT HTTP tests locally with a disposable `stillspace_test` database.
- Confirm Render Hobby resource plans, charges, PostgreSQL backups and retention.
- Configure Clerk sign-in methods, production issuer, authorized frontend origin, and publishable key.
- Configure Render API and frontend environment variables without committing secrets.
- Confirm PostgreSQL 18 migrations finish before the API accepts requests.
- Check health endpoint, signed-in navigation, invitation restrictions, and cross-account isolation.
- Test the app on desktop and mobile browsers.
- Approve the privacy/welcome text, feedback contact, and beta dates before inviting users.

## 2. Hosting and environment
The proposed `render.yaml` defines a Render static site, FastAPI web service, and PostgreSQL database. Service auto-deploy is disabled. **Also disable Blueprint Auto Sync in Render.** Do not provision, merge, or deploy without explicit approval.

Backend settings: `STILLSPACE_ENV=production`, `DATABASE_URL`, `CLERK_ISSUER`, `CLERK_AUTHORIZED_PARTIES`, `CORS_ALLOWED_ORIGINS`.

Frontend build settings: `VITE_CLERK_PUBLISHABLE_KEY`, `VITE_API_ORIGIN`. Vite embeds these at build time. `CLERK_AUTHORIZED_PARTIES` and `CORS_ALLOWED_ORIGINS` must match the actual HTTPS frontend origin. Never put credentials in GitHub.

## 3. Manage invitations
The repository contains an administrator CLI, `app.users.admin`, with these commands, run **only in the explicitly selected environment**:

```powershell
uv run python -m app.users.admin invite tester@example.com
uv run python -m app.users.admin list
uv run python -m app.users.admin revoke tester@example.com
```

The CLI normalizes email addresses. Invitations can be pending, redeemed, or revoked. Revoking a redeemed invitation does **not** disable the account. The CLI has no `disable` command; disabling an account requires a separately reviewed administrative procedure. Never edit user rows casually.

**Operational safety:** Check `DATABASE_URL` before any CLI operation. Run against a disposable database during rehearsal; do not run invitation commands against production until launch approval.

## 4. Access controls
- Clerk JWTs are verified by the backend, including issuer and authorized-party checks.
- Only invited, verified-email users may redeem invitations for new Stillspace accounts.
- Disabled users receive access denial.
- Journal and entry operations enforce per-account ownership.
- Do not remove automated tests, authorization checks, or migration history as part of cleanup.

## 5. Database and backups
- Local PostgreSQL 18 backup and restore were verified with sample journal content and ownership. This is **not** a hosted backup test.
- Confirm Render's actual backup/PITR entitlement and retention before provisioning.
- Establish periodic off-platform encrypted backups and a documented restoration rehearsal before accepting sensitive writing.
- Never commit `.db`, `.dump`, or backup files. Deleting a committed database from the latest branch does not erase its Git history.
- Use `uv run alembic upgrade head` only with a verified target database and approved deployment plan.

## 6. Release procedure
1. Review the change branch and GitHub Actions results.
2. Approve the exact merge.
3. Review Render Blueprint service sizes, environment variables, database cost, and Auto Sync.
4. Explicitly approve provisioning and deployment separately.
5. Confirm migrations and `/health`.
6. Perform real hosted sign-in, invitation, isolation, persistence, and routing checks with test-only accounts.
7. Invite testers only after the acceptance checklist passes.

## 7. Incidents and feedback
- For a failed login, verify invited email and Clerk configuration without requesting passwords or one-time codes.
- For a 401/403, check token/authorization configuration and invitation status; never bypass access controls.
- For a save error, ask the tester to preserve their text before refreshing.
- Record issue description, time, browser, steps, and severity; avoid collecting private journal contents.
- Pause new invitations if a privacy or data-loss issue is suspected. Preserve logs and coordinate recovery before making database changes.

## 8. Known limitations
Entry deletion is permanent; no 30-day recovery feature exists. Hosted backups, account-departure retention, production Clerk settings, and beta feedback workflow remain to be verified or finalized. The user guide must not promise features that have not been tested.

_Last reviewed against the repository: November 2026. Review operational details before production use._
