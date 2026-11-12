"""Fail-closed validation of production-only deployment configuration.

No production settings are required for local development or unit tests.
"""

import os
from urllib.parse import urlsplit

from sqlalchemy.engine import make_url


def _https_origin(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return (
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
            and parsed.path in ("", "/")
            and not parsed.query
            and not parsed.fragment
        )
    except ValueError:
        return False


def validate_production_configuration() -> None:
    """Validate settings when STILLSPACE_ENV=production; never log values."""
    environment = os.getenv("STILLSPACE_ENV", "development").strip().lower()
    if environment not in {"development", "test", "production"}:
        raise RuntimeError("Invalid STILLSPACE_ENV")
    if environment != "production":
        return

    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError("Production DATABASE_URL is required")
    try:
        if make_url(database_url).get_backend_name() != "postgresql":
            raise RuntimeError("Production requires PostgreSQL")
    except (ValueError, AttributeError) as error:
        raise RuntimeError("Invalid production DATABASE_URL") from error

    issuer = os.getenv("CLERK_ISSUER", "").strip()
    if not _https_origin(issuer):
        raise RuntimeError("Production CLERK_ISSUER must be an HTTPS origin")

    origins = [value.strip() for value in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if value.strip()]
    parties = [value.strip() for value in os.getenv("CLERK_AUTHORIZED_PARTIES", "").split(",") if value.strip()]
    if not origins or not all(_https_origin(value) for value in origins):
        raise RuntimeError("Production CORS_ALLOWED_ORIGINS must contain HTTPS origins")
    if not parties or not all(_https_origin(value) for value in parties):
        raise RuntimeError("Production CLERK_AUTHORIZED_PARTIES must contain HTTPS origins")
    if set(origins) != set(parties):
        raise RuntimeError("Production CORS and Clerk authorized origins must match")
