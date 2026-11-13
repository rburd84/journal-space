"""Normalize PostgreSQL URLs for the installed psycopg 3 driver."""

from sqlalchemy.engine import make_url


def normalize_database_url(value: str) -> str:
    """Keep URL components intact while selecting psycopg 3 for PostgreSQL."""
    url = make_url(value)
    if url.drivername in ("postgres", "postgresql", "postgresql+psycopg2"):
        url = url.set(drivername="postgresql+psycopg")
    return url.render_as_string(hide_password=False)
